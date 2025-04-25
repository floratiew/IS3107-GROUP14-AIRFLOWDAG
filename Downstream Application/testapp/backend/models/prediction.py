import os
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.neighbors import BallTree
import json

import os
import sys

# Add the parent directory to sys.path to allow importing from sibling packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gcs_service import GCSService
from services.geocoding_service import GeocodingService

class HDBPricePredictor:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.gcs_service = GCSService(credentials_path)
        self.geocoding_service = GeocodingService()
        
        # The model_dir will be set when files are downloaded
        self.model_dir = None
        
        # Model and data
        self.model = None
        self.model_columns = None
        self.df_stocks = None
        self.df_unemp = None
        self.df_mrt = None
        self.df_schools = None
    
    def load_model(self):
        """Load model and required datasets"""
        if self.model:
            print("Model already loaded")
            return True
            
        try:
            # Download all necessary files from GCS to temporary directory
            downloaded_files = self.gcs_service.download_model_files()
            
            # Set model_dir to the temporary directory used by GCSService
            self.model_dir = self.gcs_service.temp_dir
            print(f"Using temporary directory for model files: {self.model_dir}")
            
            # Load XGBoost model
            model_path = os.path.join(self.model_dir, "hdb_xgb_model.json")
            self.model = XGBRegressor()
            self.model.load_model(model_path)
            
            # Load model columns
            columns_path = os.path.join(self.model_dir, "model_columns.json")
            with open(columns_path, "r") as f:
                self.model_columns = json.load(f)
            
            # Load datasets
            self._load_datasets()
            
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def _load_datasets(self):
        """Load required datasets"""
        try:
            # Load stock data
            stock_path = os.path.join(self.model_dir, "stock.csv")
            self.df_stocks = pd.read_csv(stock_path)
            
            # Load unemployment data
            unemp_path = os.path.join(self.model_dir, "unemployment.csv")
            self.df_unemp = pd.read_csv(unemp_path)
            
            # Load MRT cluster data
            mrt_path = os.path.join(self.model_dir, "mrt_clustered.csv")
            self.df_mrt = pd.read_csv(mrt_path)
            
            # Load school cluster data
            schools_path = os.path.join(self.model_dir, "schools_clustered.csv")
            self.df_schools = pd.read_csv(schools_path)
            
            # Preprocess datasets
            self._preprocess_datasets()
            
            return True
        except Exception as e:
            print(f"Error loading datasets: {str(e)}")
            return False
    
    def _preprocess_datasets(self):
        """Preprocess datasets for prediction"""
        # Fill NaN values first
        self.df_schools = self.df_schools.fillna(0)
        self.df_mrt = self.df_mrt.fillna(0)
        
        # Rename columns for consistency
        self.df_schools = self.df_schools.rename(columns={'cluster': 'school_cluster'})
        self.df_mrt = self.df_mrt.rename(columns={'STATION_NA': 'station_name', 'cluster_25': 'mrt_cluster'})
        
        # Calculate primary school count
        self.df_schools['primary_schoool_count'] = (self.df_schools['mainlevel_code'] == 'PRIMARY').astype(int)
    
    def predict(self, input_dict):
        """Predict HDB resale price based on input dictionary"""
        if not self.model:
            success = self.load_model()
            if not success:
                raise Exception("Failed to load model")
        
        try:
            # Create DataFrame from input
            df = pd.DataFrame([input_dict])
            
            # Feature engineering
            df = self._engineer_features(df)
            
            # Align with model columns
            df_encoded = self._align_with_model_columns(df)
            
            # Debug: Print the features being passed to the model
            print("\n=== FEATURES PASSED TO MODEL ===")
            for col in df_encoded.columns:
                print(f"{col}: {df_encoded[col].values[0]}")
            print("===============================\n")
            
            # Make prediction
            predicted_price = self.model.predict(df_encoded)[0]
            
            # Return only the predicted price
            return {
                "price": float(predicted_price)
            }
        except Exception as e:
            print(f"Error predicting price: {str(e)}")
            raise
    
    def _engineer_features(self, df):
        """Apply feature engineering to input data"""
        try:
            # Fill NaN values
            df = df.fillna(0)
            
            # Calculate years from lease
            df['years_from_lease'] = df['year'] - df['lease_commence_date']
            
            # Extract remaining lease months
            try:
                # Check if remaining_lease is NaN or empty
                if pd.isna(df['remaining_lease'].iloc[0]) or df['remaining_lease'].iloc[0] == '':
                    print("Warning: remaining_lease is NaN or empty, using default value")
                    df['remaining_lease_months'] = 0
                else:
                    # Try to extract years and months with a more flexible regex
                    extracted = df['remaining_lease'].str.extract(r'(\d+)\s*years?\s*(\d*)\s*months?').iloc[0]
                    
                    # Handle case where months might be missing
                    years = int(extracted[0]) if not pd.isna(extracted[0]) else 0
                    months = int(extracted[1]) if not pd.isna(extracted[1]) and extracted[1] != '' else 0
                    
                    df['remaining_lease_months'] = years * 12 + months
                    print(f"Successfully extracted remaining lease: {years} years and {months} months")
            except Exception as e:
                print(f"Error extracting remaining lease: {str(e)}")
                df['remaining_lease_months'] = 0
            
            df.drop(columns=['remaining_lease'], inplace=True)
            
            # Create address and get coordinates
            df['address'] = df['block'].str.strip() + ' ' + df['street_name'].str.strip()
            try:
                lat, lon, postal = self.geocoding_service.get_lat_lon(df['address'].iloc[0])
                df['latitude'] = lat if lat is not None else 0
                df['longitude'] = lon if lon is not None else 0
            except Exception as e:
                print(f"Error getting coordinates: {str(e)}")
                df['latitude'] = 0
                df['longitude'] = 0
            
            df.drop(columns=['block', 'street_name'], inplace=True)
            
            # Add macro indicators
            try:
                df['average_close'] = self.df_stocks.loc[
                    (self.df_stocks['Year'] == df.at[0, 'year']) & 
                    (self.df_stocks['Month'] == df.at[0, 'month']),
                    'Average_Close'
                ].values[0]
            except Exception as e:
                print(f"Error getting stock data: {str(e)}")
                df['average_close'] = 0
            
            try:
                df['unemployment_rate'] = self.df_unemp.loc[
                    (self.df_unemp['Year'] == df.at[0, 'year']) & 
                    (self.df_unemp['Month'] == df.at[0, 'month']),
                    'Unemployment Rate'
                ].values[0]
            except Exception as e:
                print(f"Error getting unemployment data: {str(e)}")
                df['unemployment_rate'] = 0
            
            # Rename macro columns
            df = df.rename(columns={'Average_Close': 'average_close', 'Unemployment Rate': 'unemployment_rate'})
        except Exception as e:
            print(f"Error in _engineer_features: {str(e)}")
            # Set default values for essential columns
            df['years_from_lease'] = 0
            df['remaining_lease_months'] = 0
            df['latitude'] = 0
            df['longitude'] = 0
            df['average_close'] = 0
            df['unemployment_rate'] = 0
        
        # Find nearest school cluster
        df = self._add_nearest_school_cluster(df)
        
        # Find nearest MRT cluster
        df = self._add_nearest_mrt_cluster(df)
        
        # Additional feature engineering
        df['flat_age_at_resale'] = df['year'] - df['lease_commence_date']
        
        # Extract storey mean with error handling
        try:
            # Check if storey_range is NaN or empty
            if pd.isna(df['storey_range'].iloc[0]) or df['storey_range'].iloc[0] == '':
                print("Warning: storey_range is NaN or empty, using default value")
                df['storey_mean'] = 6  # Default to middle floor
            else:
                # Try to extract storey range with a more flexible regex
                extracted = df['storey_range'].str.extract(r'(\d+)\s*TO\s*(\d+)').astype(float)
                if extracted.isna().any().any():
                    print("Warning: Could not extract storey range properly, using default value")
                    df['storey_mean'] = 6
                else:
                    df['storey_mean'] = extracted.mean(axis=1)
                    print(f"Successfully extracted storey mean: {df['storey_mean'].iloc[0]}")
        except Exception as e:
            print(f"Error extracting storey mean: {str(e)}")
            df['storey_mean'] = 6
        
        df['is_high_floor'] = (df['storey_mean'] > 12).astype(int)
        df['is_big_unit'] = (df['floor_area_sqm'] > 110).astype(int)
        df['school_quality'] = df[['sap_ind_pct', 'autonomous_ind_pct', 'gifted_ind_pct', 'ip_ind_pct']].sum(axis=1)
        
        # Region mapping
        df['town'] = df['town'].str.replace('/', '_')
        town_to_region = {
            "ANG MO KIO": "Rest of Central Region",
            "KALLANG_WHAMPOA": "Rest of Central Region",
            "BISHAN": "Rest of Central Region",
            "BUKIT MERAH": "Rest of Central Region",
            "GEYLANG": "Rest of Central Region",
            "MARINE PARADE": "Rest of Central Region",
            "QUEENSTOWN": "Rest of Central Region",
            "SERANGOON": "Rest of Central Region",
            "TOA PAYOH": "Rest of Central Region",
            
            "SEMBAWANG": "North Region",
            "WOODLANDS": "North Region",
            "YISHUN": "North Region",
            
            "HOUGANG": "North-East Region",
            "PUNGGOL": "North-East Region",
            "SENGKANG": "North-East Region",
            
            "BEDOK": "East Region",
            "PASIR RIS": "East Region",
            "TAMPINES": "East Region",
            
            "BUKIT BATOK": "West Region",
            "BUKIT PANJANG": "West Region",
            "CHOA CHU KANG": "West Region",
            "CLEMENTI": "West Region",
            "JURONG EAST": "West Region",
            "JURONG WEST": "West Region"
        }
        df['region'] = df['town'].str.upper().map(lambda x: town_to_region.get(x, 'Others'))
        
        return df
    
    def _add_nearest_school_cluster(self, df):
        """Find and add nearest school cluster information"""
        try:
            # Get cluster centroids
            cluster_centroids = self.df_schools.groupby('school_cluster').agg({
                'cluster_center_lat': 'first',
                'cluster_center_lng': 'first',
                'school_count': 'first',
                'sap_ind_pct': 'mean',
                'autonomous_ind_pct': 'mean',
                'gifted_ind_pct': 'mean',
                'ip_ind_pct': 'mean',
                'primary_schoool_count': 'sum'
            }).reset_index()
            
            # Fill any NaN values
            cluster_centroids = cluster_centroids.fillna(0)
            
            # Calculate nearest cluster
            df_coords = np.radians(df[['latitude', 'longitude']])
            cluster_coords = np.radians(cluster_centroids[['cluster_center_lat', 'cluster_center_lng']])
            school_tree = BallTree(cluster_coords, metric='haversine')
            school_dist, school_idx = school_tree.query(df_coords, k=1)
            
            # Add cluster information
            df['nearest_school_cluster'] = cluster_centroids.iloc[school_idx.flatten()]['school_cluster'].values
            df = df.merge(cluster_centroids, left_on='nearest_school_cluster', right_on='school_cluster', how='left')
            df['distance_to_nearest_school'] = school_dist.flatten() * 6371000  # Convert to meters
            
            # Clean up
            df.drop(columns=['cluster_center_lat', 'cluster_center_lng', 'school_cluster'], inplace=True)
        except Exception as e:
            print(f"Error in _add_nearest_school_cluster: {str(e)}")
            # Add default values if there's an error
            df['nearest_school_cluster'] = 0
            df['distance_to_nearest_school'] = 0
            df['school_count'] = 0
            df['sap_ind_pct'] = 0
            df['autonomous_ind_pct'] = 0
            df['gifted_ind_pct'] = 0
            df['ip_ind_pct'] = 0
            df['primary_schoool_count'] = 0
        
        return df
    
    def _add_nearest_mrt_cluster(self, df):
        """Find and add nearest MRT cluster information"""
        try:
            # Get cluster centroids
            mrt_centroids = self.df_mrt.groupby('mrt_cluster').agg({
                'cluster_lat': 'first',
                'cluster_long': 'first'
            }).reset_index()
            
            # Fill any NaN values
            mrt_centroids = mrt_centroids.fillna(0)
            
            # Calculate nearest cluster
            df_coords = np.radians(df[['latitude', 'longitude']])
            mrt_coords = np.radians(self.df_mrt[['cluster_lat', 'cluster_long']])
            mrt_tree = BallTree(mrt_coords, metric='haversine')
            mrt_dist, mrt_idx = mrt_tree.query(df_coords, k=1)
            
            # Add cluster information
            df['nearest_mrt_cluster'] = mrt_centroids.iloc[mrt_idx.flatten()]['mrt_cluster'].values
            df = df.merge(mrt_centroids, left_on='nearest_mrt_cluster', right_on='mrt_cluster', how='left')
            df['distance_to_nearest_mrt'] = mrt_dist.flatten() * 6371000  # Convert to meters
            
            # Clean up
            df.drop(columns=['cluster_lat', 'cluster_long', 'mrt_cluster'], inplace=True)
        except Exception as e:
            print(f"Error in _add_nearest_mrt_cluster: {str(e)}")
            # Add default values if there's an error
            df['nearest_mrt_cluster'] = 0
            df['distance_to_nearest_mrt'] = 0
        
        return df
    
    def _align_with_model_columns(self, df):
        """Align DataFrame with model columns"""
        # One-hot encode categorical variables
        df_encoded = pd.get_dummies(df, columns=['region', 'town', 'flat_type', 'flat_model'], drop_first=False)
        
        # Align with model columns
        df_encoded = df_encoded.reindex(columns=self.model_columns, fill_value=0)
        
        return df_encoded
    
    def predict_with_variations(self, input_dict):
        """Predict HDB resale price with variations of key parameters"""
        if not self.model:
            success = self.load_model()
            if not success:
                raise Exception("Failed to load model")
        
        try:
            # Get base prediction
            base_prediction = self.predict(input_dict)
            base_price = base_prediction["price"]
            
            # Create variations
            variations = []
            
            # 1. Flat Model Variations
            flat_model_variations = self._get_flat_model_variations(input_dict, base_price)
            variations.append({
                "parameter": "flat_model",
                "title": "Flat Model Impact",
                "description": "How different flat models affect the price",
                "base_value": input_dict.get("flat_model", ""),
                "variations": flat_model_variations
            })
            
            # 2. Lease Commencement Year Variations
            lease_year_variations = self._get_lease_year_variations(input_dict, base_price)
            variations.append({
                "parameter": "lease_commence_date",
                "title": "Lease Commencement Year Impact",
                "description": "How different lease commencement years affect the price",
                "base_value": input_dict.get("lease_commence_date", 0),
                "variations": lease_year_variations
            })
            
            # 3. Floor Area Variations
            floor_area_variations = self._get_floor_area_variations(input_dict, base_price)
            variations.append({
                "parameter": "floor_area_sqm",
                "title": "Floor Area Impact",
                "description": "How different floor areas affect the price",
                "base_value": input_dict.get("floor_area_sqm", 0),
                "variations": floor_area_variations
            })
            
            # 4. Storey Range Variations
            storey_variations = self._get_storey_variations(input_dict, base_price)
            variations.append({
                "parameter": "storey_range",
                "title": "Storey Range Impact",
                "description": "How different storey ranges affect the price",
                "base_value": input_dict.get("storey_range", ""),
                "variations": storey_variations
            })
            
            return {
                "base_prediction": base_price,
                "variations": variations
            }
        except Exception as e:
            print(f"Error predicting price with variations: {str(e)}")
            raise
    
    def _get_flat_model_variations(self, input_dict, base_price):
        """Generate variations for different flat models"""
        flat_models = [
            "Improved", "New Generation", "Model A", "Standard", "Simplified", 
            "Premium Apartment", "Maisonette", "Apartment", "DBSS"
        ]
        
        # Filter out the current flat model
        current_model = input_dict.get("flat_model", "")
        models_to_test = [model for model in flat_models if model != current_model] 
        
        variations = []
        for model in models_to_test:
            try:
                # Create a copy of the input dict with the new flat model
                variation_dict = input_dict.copy()
                variation_dict["flat_model"] = model
                
                # Get prediction for this variation
                variation_prediction = self.predict(variation_dict)
                variation_price = variation_prediction["price"]
                
                # Calculate percentage difference
                price_diff_pct = ((variation_price - base_price) / base_price) * 100
                
                variations.append({
                    "value": model,
                    "price": float(variation_price),
                    "difference": float(variation_price - base_price),
                    "percentage_difference": float(price_diff_pct)
                })
            except Exception as e:
                print(f"Error creating flat model variation for {model}: {str(e)}")
        
        return variations
    
    def _get_lease_year_variations(self, input_dict, base_price):
        """Generate variations for different lease commencement years"""
        current_year = input_dict.get("lease_commence_date", 1990)
        
        # Create variations in sorted order: -15, -10, -5, +5, +10, +15

        year_variations = [
            current_year - 15,
            current_year - 10,
            current_year - 5,
            current_year + 5,
            current_year + 10,
            current_year + 15
        ]

        
        variations = []
        for year in year_variations:
            # Skip invalid years
            if year < 1960 or year > 2023:
                continue
                
            try:
                # Create a copy of the input dict with the new lease year
                variation_dict = input_dict.copy()
                variation_dict["lease_commence_date"] = year
                
                # Get prediction for this variation
                variation_prediction = self.predict(variation_dict)
                variation_price = variation_prediction["price"]
                
                # Calculate percentage difference
                price_diff_pct = ((variation_price - base_price) / base_price) * 100
                
                variations.append({
                    "value": year,
                    "price": float(variation_price),
                    "difference": float(variation_price - base_price),
                    "percentage_difference": float(price_diff_pct)
                })
            except Exception as e:
                print(f"Error creating lease year variation for {year}: {str(e)}")
        
        return variations
    
    def _get_floor_area_variations(self, input_dict, base_price):
        """Generate variations for different floor areas"""
        current_area = input_dict.get("floor_area_sqm", 90)
        
        # Create variations in sorted order: -30%, -20%,-10%, +10%, +20%, +30%
        area_variations = [
            round(current_area * 0.7),
            round(current_area * 0.8),
            round(current_area * 0.9),
            round(current_area * 1.1),
            round(current_area * 1.2),
            round(current_area * 1.3)
        ]
        
        variations = []
        for area in area_variations:
            # Skip invalid areas
            if area < 30 or area > 200:
                continue
                
            try:
                # Create a copy of the input dict with the new floor area
                variation_dict = input_dict.copy()
                variation_dict["floor_area_sqm"] = area
                
                # Get prediction for this variation
                variation_prediction = self.predict(variation_dict)
                variation_price = variation_prediction["price"]
                
                # Calculate percentage difference
                price_diff_pct = ((variation_price - base_price) / base_price) * 100
                
                variations.append({
                    "value": area,
                    "price": float(variation_price),
                    "difference": float(variation_price - base_price),
                    "percentage_difference": float(price_diff_pct)
                })
            except Exception as e:
                print(f"Error creating floor area variation for {area}: {str(e)}")
        
        return variations
    
    def _get_storey_variations(self, input_dict, base_price):
        """Generate variations for different storey ranges"""
        current_storey = input_dict.get("storey_range", "07 TO 09")
        
        # Define some common storey ranges
        storey_ranges = [
            "01 TO 03", "04 TO 06", "07 TO 09", "10 TO 12", 
            "13 TO 15", "16 TO 18", "19 TO 21", "22 TO 24"
        ]
        
        # Filter out the current storey range
        ranges_to_test = [sr for sr in storey_ranges if sr != current_storey]  # Limit to 4 variations
        
        variations = []
        for storey_range in ranges_to_test:
            try:
                # Create a copy of the input dict with the new storey range
                variation_dict = input_dict.copy()
                variation_dict["storey_range"] = storey_range
                
                # Get prediction for this variation
                variation_prediction = self.predict(variation_dict)
                variation_price = variation_prediction["price"]
                
                # Calculate percentage difference
                price_diff_pct = ((variation_price - base_price) / base_price) * 100
                
                variations.append({
                    "value": storey_range,
                    "price": float(variation_price),
                    "difference": float(variation_price - base_price),
                    "percentage_difference": float(price_diff_pct)
                })
            except Exception as e:
                print(f"Error creating storey range variation for {storey_range}: {str(e)}")
        
        return variations
