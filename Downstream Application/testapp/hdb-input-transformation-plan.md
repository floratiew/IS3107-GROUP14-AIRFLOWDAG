# HDB Resale Price Prediction: Input Transformation Plan

This document outlines the procedure for transforming web application inputs into a feature array suitable for the pretrained XGBoost model. The transformation process ensures that all inputs from the user interface are converted into the exact format and structure expected by the model.

## Input Sources

1. **User Interface Inputs**:
   - Town/Region (dropdown)
   - Block Number (text)
   - Street Name (text)
   - Flat Type (dropdown)
   - Flat Model (dropdown)
   - Storey Range (dropdown)
   - Floor Area (slider, sqm)
   - Lease Commence Year (text)
   - Remaining Lease (years and months input)
   - Transaction Date (month and year - to be added to UI)

2. **External Data Sources**:
   - School cluster data: `gs://is3107-prroject-bucket/temporary/schools_clustered.csv`
   - MRT cluster data: `gs://is3107-prroject-bucket/temporary/mrt_clustered.csv`
   - Unemployment data: `gs://is3107-project-bucket/datasets/unemployment.csv`
   - Stock market data: `gs://is3107-project-bucket/datasets/stock.csv`

## Transformation Process

### Step 1: Initial Processing

1. **Extract Basic Information**:
   ```python
   def extract_basic_info(user_input):
       # Create a dictionary with basic information
       basic_info = {
           'town': user_input.get('town'),
           'block': user_input.get('block'),
           'street_name': user_input.get('street_name'),
           'flat_type': user_input.get('flat_type'),
           'flat_model': user_input.get('flat_model'),
           'storey_range': user_input.get('storey_range'),
           'floor_area_sqm': float(user_input.get('floor_area_sqm')),
           'lease_commence_date': int(user_input.get('lease_commence_year')),
           'month': user_input.get('transaction_month'),  # Format: YYYY-MM
           'year': int(user_input.get('transaction_year'))
       }
       
       # Calculate remaining lease in months
       years = int(user_input.get('remaining_lease_years', 0))
       months = int(user_input.get('remaining_lease_months', 0))
       basic_info['remaining_lease_months'] = years * 12 + months
       
       return basic_info
   ```

### Step 2: Geocoding

1. **Convert Address to Coordinates**:
   ```python
   def geocode_address(block, street_name, access_token):
       import requests
       
       # Format the address
       search_term = f"{block} {street_name}"
       formatted_address = search_term.replace(' ', '%20')
       
       # Construct URL
       url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={formatted_address}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
       
       headers = {"Authorization": f"Bearer {access_token}"}
       
       try:
           response = requests.get(url, headers=headers)
           response.raise_for_status()
           
           data = response.json()
           
           if data.get('found') > 0:
               result = data['results'][0]
               return {
                   'latitude': float(result['LATITUDE']),
                   'longitude': float(result['LONGITUDE'])
               }
           else:
               return None
       except Exception as e:
           print(f"Error geocoding address: {e}")
           return None
   ```

### Step 3: Find Nearest School and MRT Clusters

1. **Load Cluster Data**:
   ```python
   def load_cluster_data():
       import pandas as pd
       from google.cloud import storage
       
       # Initialize client
       client = storage.Client()
       
       # Load school cluster data
       bucket = client.bucket('is3107-prroject-bucket')
       blob = bucket.blob('temporary/schools_clustered.csv')
       school_clusters = pd.read_csv(blob.download_as_string())
       
       # Load MRT cluster data
       blob = bucket.blob('temporary/mrt_clustered.csv')
       mrt_clusters = pd.read_csv(blob.download_as_string())
       
       return school_clusters, mrt_clusters
   ```

2. **Find Nearest Clusters**:
   ```python
   def find_nearest_clusters(lat, lng, school_clusters, mrt_clusters):
       import numpy as np
       from math import radians, cos, sin, asin, sqrt
       
       def haversine(lat1, lon1, lat2, lon2):
           """Calculate the great circle distance between two points in kilometers"""
           # Convert decimal degrees to radians
           lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
           
           # Haversine formula
           dlon = lon2 - lon1
           dlat = lat2 - lat1
           a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
           c = 2 * asin(sqrt(a))
           r = 6371  # Radius of Earth in kilometers
           return c * r * 1000  # Convert to meters
       
       # Calculate distance to each school cluster
       school_clusters['distance'] = school_clusters.apply(
           lambda row: haversine(lat, lng, row['cluster_center_lat'], row['cluster_center_lng']),
           axis=1
       )
       
       # Find nearest school cluster
       nearest_school = school_clusters.loc[school_clusters['distance'].idxmin()]
       
       # Calculate distance to each MRT cluster
       mrt_clusters['distance'] = mrt_clusters.apply(
           lambda row: haversine(lat, lng, row['cluster_center_lat'], row['cluster_center_lng']),
           axis=1
       )
       
       # Find nearest MRT cluster
       nearest_mrt = mrt_clusters.loc[mrt_clusters['distance'].idxmin()]
       
       return {
           'nearest_school_cluster': int(nearest_school['cluster']),
           'distance_to_nearest_school': float(nearest_school['distance']),
           'school_count': int(nearest_school['school_count']),
           'sap_ind_pct': float(nearest_school.get('sap_ind_pct', 0)),
           'autonomous_ind_pct': float(nearest_school.get('autonomous_ind_pct', 0)),
           'gifted_ind_pct': float(nearest_school.get('gifted_ind_pct', 0)),
           'ip_ind_pct': float(nearest_school.get('ip_ind_pct', 0)),
           'primary_schoool_count': int(nearest_school.get('primary_schoool_count', 0)),
           'nearest_mrt_cluster': int(nearest_mrt['cluster']),
           'distance_to_nearest_mrt': float(nearest_mrt['distance'])
       }
   ```

### Step 4: Get Economic Indicators

1. **Get Unemployment Rate and Stock Index**:
   ```python
   def get_economic_indicators(year, month):
       import pandas as pd
       from google.cloud import storage
       
       # Initialize client
       client = storage.Client()
       bucket = client.bucket('is3107-project-bucket')
       
       # Load unemployment data
       blob = bucket.blob('datasets/unemployment.csv')
       unemployment_df = pd.read_csv(blob.download_as_string())
       
       # Format: Year-Quarter (e.g., 2020-Q1)
       # Extract quarter from month
       quarter = (int(month.split('-')[1]) - 1) // 3 + 1
       quarter_str = f"{year}-Q{quarter}"
       
       # Get unemployment rate
       unemployment_rate = unemployment_df[unemployment_df['quarter'] == quarter_str]['rate'].iloc[0]
       
       # Load stock data
       blob = bucket.blob('datasets/stock.csv')
       stock_df = pd.read_csv(blob.download_as_string())
       
       # Get average stock close price for the month
       stock_df['date'] = pd.to_datetime(stock_df['date'])
       month_filter = (stock_df['date'].dt.year == year) & (stock_df['date'].dt.month == int(month.split('-')[1]))
       average_close = stock_df[month_filter]['value'].mean()
       
       return {
           'unemployment_rate': float(unemployment_rate),
           'average_close': float(average_close)
       }
   ```

### Step 5: Feature Engineering

1. **Apply Feature Engineering**:
   ```python
   def apply_feature_engineering(features_dict):
       # Calculate flat age at resale
       features_dict['flat_age_at_resale'] = features_dict['year'] - features_dict['lease_commence_date']
       
       # Convert storey_range to mean_storey
       storey_range = features_dict['storey_range']
       storey_parts = storey_range.split('TO')
       if len(storey_parts) == 2:
           lower = int(storey_parts[0].strip())
           upper = int(storey_parts[1].strip())
           features_dict['storey_mean'] = (lower + upper) / 2
       else:
           features_dict['storey_mean'] = float(storey_range)
       
       # Binary indicator if flat is a high floor
       features_dict['is_high_floor'] = 1 if features_dict['storey_mean'] > 12 else 0
       
       # Binary indicator if flat is a big unit
       features_dict['is_big_unit'] = 1 if features_dict['floor_area_sqm'] > 110 else 0
       
       # School quality score
       features_dict['school_quality'] = (
           features_dict.get('sap_ind_pct', 0) + 
           features_dict.get('autonomous_ind_pct', 0) + 
           features_dict.get('gifted_ind_pct', 0) + 
           features_dict.get('ip_ind_pct', 0)
       )
       
       # Map town to region
       town_to_region = {
           # Core central
           'DOWNTOWN CORE': 'Core Central Region',
           'MARINA BAY': 'Core Central Region',
           # ... (use full mapping from feature_engineering function)
           
           # Rest of central
           'BISHAN': 'Rest of Central Region',
           'BUKIT MERAH': 'Rest of Central Region',
           'GEYLANG': 'Rest of Central Region',
           'KALLANG/WHAMPOA': 'Rest of Central Region',
           'MARINE PARADE': 'Rest of Central Region',
           'QUEENSTOWN': 'Rest of Central Region',
           'SERANGOON': 'Rest of Central Region',
           'ANG MO KIO': 'Rest of Central Region',
           
           # North
           'SEMBAWANG': 'North Region',
           'WOODLANDS': 'North Region',
           'YISHUN': 'North Region',
           
           # North east
           'HOUGANG': 'North-East Region',
           'PUNGGOL': 'North-East Region',
           'SENGKANG': 'North-East Region',
           
           # East
           'BEDOK': 'East Region',
           'PASIR RIS': 'East Region',
           'TAMPINES': 'East Region',
           
           # West
           'BUKIT BATOK': 'West Region',
           'BUKIT PANJANG': 'West Region',
           'CHOA CHU KANG': 'West Region',
           'CLEMENTI': 'West Region',
           'JURONG EAST': 'West Region',
           'JURONG WEST': 'West Region'
       }
       
       region = town_to_region.get(features_dict['town'].upper(), 'Others')
       
       # One-hot encode region
       features_dict['region_East Region'] = 1 if region == 'East Region' else 0
       features_dict['region_North Region'] = 1 if region == 'North Region' else 0
       features_dict['region_North-East Region'] = 1 if region == 'North-East Region' else 0
       features_dict['region_Rest of Central Region'] = 1 if region == 'Rest of Central Region' else 0
       features_dict['region_West Region'] = 1 if region == 'West Region' else 0
       
       # Town frequency (use a predefined map or default value)
       features_dict['town_sales_freq'] = 100  # Default value, replace with actual data if available
       
       return features_dict
   ```

### Step 6: One-Hot Encoding

1. **Apply One-Hot Encoding for Categorical Variables**:
   ```python
   def apply_one_hot_encoding(features_dict):
       # One-hot encode flat_type
       flat_types = ['1 ROOM', '2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE', 'MULTI-GENERATION']
       for flat_type in flat_types:
           field_name = f"flat_type_{flat_type}"
           features_dict[field_name] = 1 if features_dict['flat_type'] == flat_type else 0
       
       # One-hot encode flat_model
       flat_models = [
           '2-room', '3Gen', 'Adjoined flat', 'Apartment', 'DBSS', 'Improved', 
           'Improved-Maisonette', 'Maisonette', 'Model A', 'Model A-Maisonette', 
           'Model A2', 'Multi Generation', 'New Generation', 'Premium Apartment', 
           'Premium Apartment Loft', 'Premium Maisonette', 'Simplified', 'Standard', 
           'Terrace', 'Type S1', 'Type S2'
       ]
       for model in flat_models:
           field_name = f"flat_model_{model}"
           features_dict[field_name] = 1 if features_dict['flat_model'] == model else 0
       
       # One-hot encode town
       towns = [
           'ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH', 
           'BUKIT PANJANG', 'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG', 
           'CLEMENTI', 'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST', 
           'KALLANG_WHAMPOA', 'MARINE PARADE', 'PASIR RIS', 'PUNGGOL', 
           'QUEENSTOWN', 'SEMBAWANG', 'SENGKANG', 'SERANGOON', 'TAMPINES', 'YISHUN'
       ]
       for town in towns:
           field_name = f"town_{town}"
           features_dict[field_name] = 1 if features_dict['town'].upper() == town else 0
       
       return features_dict
   ```

### Step 7: Create Final Feature Array

1. **Assemble the Final Feature Array**:
   ```python
   def create_feature_array(features_dict):
       # Define all required features in exact order expected by the model
       required_features = [
           'month', 'town', 'flat_type', 'floor_area_sqm', 'flat_model', 
           'lease_commence_date', 'resale_price', 'years_from_lease', 
           'remaining_lease_months', 'year', 'latitude', 'longitude', 
           'average_close', 'unemployment_rate', 'nearest_school_cluster', 
           'school_count', 'sap_ind_pct', 'autonomous_ind_pct', 'gifted_ind_pct', 
           'ip_ind_pct', 'primary_schoool_count', 'distance_to_nearest_school', 
           'nearest_mrt_cluster', 'distance_to_nearest_mrt', 'flat_type_1 ROOM', 
           'flat_type_2 ROOM', 'flat_type_3 ROOM', 'flat_type_4 ROOM', 
           'flat_type_5 ROOM', 'flat_type_EXECUTIVE', 'flat_type_MULTI-GENERATION', 
           'flat_model_2-room', 'flat_model_3Gen', 'flat_model_Adjoined flat', 
           'flat_model_Apartment', 'flat_model_DBSS', 'flat_model_Improved', 
           'flat_model_Improved-Maisonette', 'flat_model_Maisonette', 
           'flat_model_Model A', 'flat_model_Model A-Maisonette', 
           'flat_model_Model A2', 'flat_model_Multi Generation', 
           'flat_model_New Generation', 'flat_model_Premium Apartment', 
           'flat_model_Premium Apartment Loft', 'flat_model_Premium Maisonette', 
           'flat_model_Simplified', 'flat_model_Standard', 'flat_model_Terrace', 
           'flat_model_Type S1', 'flat_model_Type S2', 'town_ANG MO KIO', 
           'town_BEDOK', 'town_BISHAN', 'town_BUKIT BATOK', 'town_BUKIT MERAH', 
           'town_BUKIT PANJANG', 'town_BUKIT TIMAH', 'town_CENTRAL AREA', 
           'town_CHOA CHU KANG', 'town_CLEMENTI', 'town_GEYLANG', 'town_HOUGANG', 
           'town_JURONG EAST', 'town_JURONG WEST', 'town_KALLANG_WHAMPOA', 
           'town_MARINE PARADE', 'town_PASIR RIS', 'town_PUNGGOL', 
           'town_QUEENSTOWN', 'town_SEMBAWANG', 'town_SENGKANG', 'town_SERANGOON', 
           'town_TAMPINES', 'town_YISHUN', 'flat_age_at_resale', 'storey_mean', 
           'is_high_floor', 'is_big_unit', 'school_quality', 'region_East Region', 
           'region_North Region', 'region_North-East Region', 
           'region_Rest of Central Region', 'region_West Region', 'town_sales_freq'
       ]
       
       # Create empty array with placeholder for resale_price
       feature_array = []
       
       for feature in required_features:
           if feature == 'resale_price':
               # Placeholder for resale_price (will be predicted)
               feature_array.append(0)
           elif feature in features_dict:
               feature_array.append(features_dict[feature])
           else:
               # Default to 0 for missing features
               feature_array.append(0)
       
       return feature_array
   ```

### Step 8: Main Transformation Function

1. **Create the Main Function**:
   ```python
   def transform_inputs(user_input):
       """Transform user inputs into feature array for XGBoost prediction"""
       
       # Step 1: Extract basic information
       features = extract_basic_info(user_input)
       
       # Step 2: Geocode address
       access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0Y2I4NWRlNjhjN2M1NDIxNzQ2YTJhZTRhYjk4ZTVmNyIsImlzcyI6Imh0dHA6Ly9pbnRlcm5hbC1hbGItb20tcHJkZXppdC1pdC1uZXctMTYzMzc5OTU0Mi5hcC1zb3V0aGVhc3QtMS5lbGIuYW1hem9uYXdzLmNvbS9hcGkvdjIvdXNlci9wYXNzd29yZCIsImlhdCI6MTc0NDg3MjQzNCwiZXhwIjoxNzQ1MTMxNjM0LCJuYmYiOjE3NDQ4NzI0MzQsImp0aSI6InBGNXJ3TXJwenBqazNSS0kiLCJ1c2VyX2lkIjo2ODg5LCJmb3JldmVyIjpmYWxzZX0.M2ZZJI3epLIGL-EaIdRhHd0ntpwe67KNVJTL1IOC74U'
       coords = geocode_address(features['block'], features['street_name'], access_token)
       if coords:
           features.update(coords)
       else:
           # Default coordinates (central Singapore) if geocoding fails
           features['latitude'] = 1.3521
           features['longitude'] = 103.8198
       
       # Step 3: Find nearest school and MRT clusters
       school_clusters, mrt_clusters = load_cluster_data()
       cluster_info = find_nearest_clusters(features['latitude'], features['longitude'], school_clusters, mrt_clusters)
       features.update(cluster_info)
       
       # Step 4: Get economic indicators
       economic_indicators = get_economic_indicators(features['year'], features['month'])
       features.update(economic_indicators)
       
       # Step 5: Apply feature engineering
       features = apply_feature_engineering(features)
       
       # Step 6: Apply one-hot encoding
       features = apply_one_hot_encoding(features)
       
       # Step 7: Create final feature array
       feature_array = create_feature_array(features)
       
       return feature_array
   ```

### Step 9: Using the Transformation Function with the XGBoost Model

1. **Predict HDB Resale Price**:
   ```python
   def predict_hdb_price(user_input, model_path):
       import xgboost as xgb
       import pickle
       
       # Transform user inputs to feature array
       feature_array = transform_inputs(user_input)
       
       # Load the model
       with open(model_path, 'rb') as f:
           model = pickle.load(f)
       
       # Make prediction
       prediction = model.predict([feature_array])[0]
       
       return prediction
   ```

## Implementation Notes

1. **Caching**:
   - Consider implementing caching for GCS data and API responses to improve performance
   - School/MRT cluster data can be cached in memory
   - Economic indicators can be cached with appropriate expiration

2. **Error Handling**:
   - Implement robust error handling for API calls and GCS access
   - Provide default values for missing data points
   - Log errors for debugging

3. **Validation**:
   - Validate user inputs before processing
   - Ensure all required fields are present
   - Check that values are within reasonable ranges

4. **Performance**:
   - Batch GCS reads where possible
   - Minimize API calls by validating addresses before geocoding
   - Consider precomputing frequently used values

## Testing Strategy

1. **Unit Testing**:
   - Test each transformation function individually
   - Verify correct handling of edge cases and missing data

2. **Integration Testing**:
   - Test the end-to-end transformation process
   - Verify integration with external services (OneMap API, GCS)

3. **Validation Testing**:
   - Compare predictions against known values
   - Ensure predictions are within reasonable ranges

## Example Usage

```python
# Example user input from web form
user_input = {
    'town': 'ANG MO KIO',
    'block': '123',
    'street_name': 'ANG MO KIO AVE 3',
    'flat_type': '4 ROOM',
    'flat_model': 'New Generation',
    'storey_range': '07 TO 09',
    'floor_area_sqm': 90,
    'lease_commence_year': 1990,
    'remaining_lease_years': 60,
    'remaining_lease_months': 0,
    'transaction_year': 2023,
    'transaction_month': '2023-01'
}

# Predict price
predicted_price = predict_hdb_price(user_input, 'models/xgboost_model.pkl')
print(f"Predicted HDB Resale Price: SGD {predicted_price:,.2f}")
```

This comprehensive plan outlines all steps needed to transform user inputs from your web form into the feature array expected by your XGBoost model for HDB resale price prediction.