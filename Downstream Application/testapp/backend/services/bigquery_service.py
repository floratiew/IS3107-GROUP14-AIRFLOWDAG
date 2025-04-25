from google.cloud import bigquery
import pandas as pd
import os
import json
import time
import tempfile
import hashlib
import shutil

class BigQueryService:
    def __init__(self, credentials_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.client = bigquery.Client()
        self.project_id = "is3107-project-457501"
        self.dataset_id = "is3107_dataset"
        self.table_id = "hdb_integrated_data"
        
        # Create a temporary directory for caching query results
        session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        self.cache_dir = tempfile.mkdtemp(prefix=f"bigquery_cache_{session_id}_")
        print(f"Created BigQuery cache directory: {self.cache_dir}")
        
        # Cache settings
        self.cache_enabled = True
        self.cache_ttl = 3600  # 1 hour in seconds
        self.cache_metadata = {}
    
    def __del__(self):
        """Clean up temporary directory when the service is destroyed"""
        try:
            if hasattr(self, 'cache_dir') and os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                print(f"Cleaned up BigQuery cache directory: {self.cache_dir}")
        except Exception as e:
            print(f"Error cleaning up cache directory: {str(e)}")
    
    def _get_cache_key(self, query):
        """Generate a cache key for a query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """Get the file path for a cached query result"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_path):
        """Check if a cached result is still valid"""
        if not self.cache_enabled:
            return False
            
        if not os.path.exists(cache_path):
            return False
            
        # Check if cache has expired
        cache_key = os.path.basename(cache_path).split('.')[0]
        if cache_key not in self.cache_metadata:
            return False
            
        cache_time = self.cache_metadata[cache_key]['time']
        if time.time() - cache_time > self.cache_ttl:
            return False
            
        return True
    
    def _save_to_cache(self, cache_key, data):
        """Save query result to cache"""
        if not self.cache_enabled:
            return
            
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
                
            self.cache_metadata[cache_key] = {
                'time': time.time(),
                'path': cache_path
            }
            
            print(f"Saved query result to cache: {cache_path}")
        except Exception as e:
            print(f"Error saving to cache: {str(e)}")
    
    def _load_from_cache(self, cache_key):
        """Load query result from cache"""
        cache_path = self._get_cache_path(cache_key)
        
        if not self._is_cache_valid(cache_path):
            return None
            
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                
            print(f"Loaded query result from cache: {cache_path}")
            return data
        except Exception as e:
            print(f"Error loading from cache: {str(e)}")
            return None
    
    def execute_query(self, query):
        """Execute a BigQuery query with caching"""
        cache_key = self._get_cache_key(query)
        
        # Try to load from cache first
        cached_result = self._load_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        try:
            # Execute query
            print(f"Executing BigQuery query: {query[:100]}...")
            
            # Check if the table exists
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            try:
                self.client.get_table(table_ref)
            except Exception as e:
                print(f"Error: Table {table_ref} does not exist or is not accessible: {str(e)}")
                # Return mock data for development
                return self._get_mock_data_for_query(query)
            
            df = self.client.query(query).to_dataframe()
            result = df.to_dict('records')
            
            # Save to cache
            self._save_to_cache(cache_key, result)
            
            return result
        except Exception as e:
            print(f"Error executing BigQuery query: {str(e)}")
            # Return mock data for development
            return self._get_mock_data_for_query(query)
    
    def _get_mock_data_for_query(self, query):
        """Generate mock data based on the query type for development purposes"""
        print("Generating mock data for development...")
        
        if "year as year" in query:
            # Price trends mock data with town information and statistical measures
            towns = ["ANG MO KIO", "BEDOK", "BISHAN", "TAMPINES", "WOODLANDS"]
            mock_data = []
            
            for year in range(2015, 2024):
                for town in towns:
                    base_price = 350000 + (year - 2015) * 20000
                    # Adjust price based on town
                    if town == "BISHAN":
                        base_price *= 1.2
                    elif town == "WOODLANDS":
                        base_price *= 0.9
                    
                    mock_data.append({
                        "year": year,
                        "town": town,
                        "avg_price": base_price,
                        "min_price": base_price * 0.8,
                        "max_price": base_price * 1.2,
                        "median_price": base_price * 0.95
                    })
            
            return mock_data
        elif "flat_type as flatType" in query:
            # Price distribution mock data with median values
            return [
                {"flatType": "1 ROOM", "averagePrice": 250000, "minPrice": 200000, "maxPrice": 300000, "medianPrice": 240000},
                {"flatType": "2 ROOM", "averagePrice": 320000, "minPrice": 280000, "maxPrice": 380000, "medianPrice": 310000},
                {"flatType": "3 ROOM", "averagePrice": 420000, "minPrice": 350000, "maxPrice": 500000, "medianPrice": 410000},
                {"flatType": "4 ROOM", "averagePrice": 550000, "minPrice": 450000, "maxPrice": 650000, "medianPrice": 530000},
                {"flatType": "5 ROOM", "averagePrice": 680000, "minPrice": 580000, "maxPrice": 780000, "medianPrice": 670000},
                {"flatType": "EXECUTIVE", "averagePrice": 750000, "minPrice": 650000, "maxPrice": 850000, "medianPrice": 740000}
            ]
        elif "floor_area_sqm as floorArea" in query:
            # Price vs area mock data with town information
            towns = ["ANG MO KIO", "BEDOK", "BISHAN", "TAMPINES", "WOODLANDS"]
            mock_data = []
            
            for area in [35, 45, 60, 75, 90, 105, 120, 135]:
                for town in towns:
                    base_price = 250000 + (area - 30) * 5000
                    # Adjust price based on town
                    if town == "BISHAN":
                        base_price *= 1.2
                    elif town == "WOODLANDS":
                        base_price *= 0.9
                    
                    mock_data.append({
                        "floorArea": area,
                        "price": base_price,
                        "town": town
                    })
            
            return mock_data
        elif "town," in query and "averagePrice" in query:
            # Town comparison mock data with statistical measures
            return [
                {"town": "ANG MO KIO", "averagePrice": 480000, "minPrice": 380000, "maxPrice": 580000, "medianPrice": 470000},
                {"town": "BEDOK", "averagePrice": 510000, "minPrice": 410000, "maxPrice": 610000, "medianPrice": 500000},
                {"town": "BISHAN", "averagePrice": 620000, "minPrice": 520000, "maxPrice": 720000, "medianPrice": 610000},
                {"town": "BUKIT MERAH", "averagePrice": 580000, "minPrice": 480000, "maxPrice": 680000, "medianPrice": 570000},
                {"town": "CLEMENTI", "averagePrice": 550000, "minPrice": 450000, "maxPrice": 650000, "medianPrice": 540000},
                {"town": "JURONG EAST", "averagePrice": 490000, "minPrice": 390000, "maxPrice": 590000, "medianPrice": 480000},
                {"town": "TAMPINES", "averagePrice": 520000, "minPrice": 420000, "maxPrice": 620000, "medianPrice": 510000},
                {"town": "TOA PAYOH", "averagePrice": 540000, "minPrice": 440000, "maxPrice": 640000, "medianPrice": 530000}
            ]
        elif "FORMAT_TIMESTAMP('%Y-Q%Q', transaction_date) as quarter" in query:
            # Economic indicators mock data
            return [
                {"quarter": "2021-Q1", "hdbIndex": 150, "stiIndex": 220, "unemploymentRate": 2.8},
                {"quarter": "2021-Q2", "hdbIndex": 155, "stiIndex": 225, "unemploymentRate": 2.7},
                {"quarter": "2021-Q3", "hdbIndex": 160, "stiIndex": 230, "unemploymentRate": 2.6},
                {"quarter": "2021-Q4", "hdbIndex": 165, "stiIndex": 235, "unemploymentRate": 2.5},
                {"quarter": "2022-Q1", "hdbIndex": 170, "stiIndex": 240, "unemploymentRate": 2.4},
                {"quarter": "2022-Q2", "hdbIndex": 175, "stiIndex": 245, "unemploymentRate": 2.3},
                {"quarter": "2022-Q3", "hdbIndex": 180, "stiIndex": 250, "unemploymentRate": 2.2},
                {"quarter": "2022-Q4", "hdbIndex": 185, "stiIndex": 255, "unemploymentRate": 2.1}
            ]
        else:
            # Generic mock data
            return [{"mock_data": True, "message": "This is mock data for development"}]
    
    def get_price_trends(self, towns=None, flat_type=None):
        """Get price trends over time for visualization with support for multiple towns"""
        query = f"""
        SELECT 
            year as year,
            town,
            AVG(resale_price) as avg_price,
            MIN(resale_price) as min_price,
            MAX(resale_price) as max_price,
            APPROX_QUANTILES(resale_price, 100)[OFFSET(50)] as median_price
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE 1=1
        """
        
        if towns:
            if isinstance(towns, list) and len(towns) > 0:
                town_list = "', '".join(towns)
                query += f" AND town IN ('{town_list}')"
            elif not isinstance(towns, list):
                query += f" AND town = '{towns}'"
        
        if flat_type:
            query += f" AND flat_type = '{flat_type}'"
            
        query += """
        GROUP BY year, town
        ORDER BY year, town
        """
        
        return self.execute_query(query)
    
    def get_price_distribution(self, town=None, year=None):
        """Get price distribution by flat type for visualization with median values"""
        query = f"""
        SELECT 
            flat_type as flatType,
            AVG(resale_price) as averagePrice,
            MIN(resale_price) as minPrice,
            MAX(resale_price) as maxPrice,
            PERCENTILE_CONT(resale_price, 0.5) OVER(PARTITION BY flat_type) as medianPrice
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE 1=1
        """
        
        if town:
            query += f" AND town = '{town}'"
        if year:
            query += f" AND year = {year}"
            
        query += """
        GROUP BY flat_type
        ORDER BY averagePrice
        """
        
        return self.execute_query(query)
    
    def get_price_vs_area(self, towns=None, flat_type=None, year=None):
        """Get price vs floor area data for visualization with town information for color coding"""
        query = f"""
        SELECT 
            floor_area_sqm as floorArea,
            resale_price as price,
            town
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE 1=1
        """
        
        if towns:
            if isinstance(towns, list) and len(towns) > 0:
                town_list = "', '".join(towns)
                query += f" AND town IN ('{town_list}')"
            elif not isinstance(towns, list):
                query += f" AND town = '{towns}'"
        
        if flat_type:
            query += f" AND flat_type = '{flat_type}'"
        if year:
            query += f" AND year = {year}"
            
        query += """
        LIMIT 2000
        """
        
        return self.execute_query(query)
    
    def get_town_comparison(self, flat_type=None, year=None):
        """Get town comparison data for visualization with statistical measures"""
        query = f"""
        SELECT 
            town,
            AVG(resale_price) as averagePrice,
            MIN(resale_price) as minPrice,
            MAX(resale_price) as maxPrice,
            APPROX_QUANTILES(resale_price, 100)[OFFSET(50)] as medianPrice
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE 1=1
        """
        
        if flat_type:
            query += f" AND flat_type = '{flat_type}'"
        if year:
            query += f" AND year = {year}"
            
        query += """
        GROUP BY town
        ORDER BY averagePrice DESC
        """
        
        return self.execute_query(query)
    
    def get_economic_indicators(self, town=None):
        """Get economic indicators data for visualization"""
        # This would typically join with economic data tables
        query = f"""
        SELECT 
            CONCAT(CAST(year AS STRING), '-Q', CAST(CEILING(month/3) AS STRING)) as quarter,
            AVG(resale_price) as hdbIndex,
            AVG(average_close) as stiIndex,
            AVG(unemployment_rate) as unemploymentRate
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE 1=1
        """
        
        if town:
            query += f" AND town = '{town}'"
            
        query += """
        GROUP BY quarter
        ORDER BY quarter
        LIMIT 12
        """
        
        result = self.execute_query(query)
        
        # In a real implementation, we would join with actual economic data
        # For now, we'll simulate the STI index and unemployment rate
        for item in result:
            item['stiIndex'] = item['hdbIndex'] * 0.8 + 100  # Simulated correlation
            
        # Calculate unemployment rate (simulated inverse correlation)
        max_index = max([item['hdbIndex'] for item in result])
        for item in result:
            item['unemploymentRate'] = 5 - (item['hdbIndex'] / max_index * 3)
        
        return result
    
    # New visualization methods
    
    def get_price_heatmap(self, year=None):
        """Get price heatmap data by location"""
        query = f"""
        SELECT 
            latitude,
            longitude,
            AVG(resale_price) as price
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        
        if year:
            query += f" AND EXTRACT(YEAR FROM transaction_date) = {year}"
            
        query += """
        GROUP BY latitude, longitude
        """
        
        return self.execute_query(query)
    
    def get_school_quality_impact(self, town=None, year=None):
        """Get data showing impact of school quality on prices"""
        query = f"""
        SELECT 
            school_quality,
            AVG(resale_price) as averagePrice,
            COUNT(*) as count
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE school_quality IS NOT NULL
        """
        
        if town:
            query += f" AND town = '{town}'"
        if year:
            query += f" AND EXTRACT(YEAR FROM transaction_date) = {year}"
            
        query += """
        GROUP BY school_quality
        ORDER BY school_quality
        """
        
        return self.execute_query(query)
    
    def get_lease_impact(self, town=None, flat_type=None):
        """Get data showing impact of remaining lease on prices"""
        query = f"""
        SELECT 
            FLOOR(remaining_lease_months / 12) as remaining_lease_years,
            AVG(resale_price) as averagePrice,
            COUNT(*) as count
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE remaining_lease_months IS NOT NULL
        """
        
        if town:
            query += f" AND town = '{town}'"
        if flat_type:
            query += f" AND flat_type = '{flat_type}'"
            
        query += """
        GROUP BY remaining_lease_years
        ORDER BY remaining_lease_years
        """
        
        return self.execute_query(query)
    
    def get_floor_level_analysis(self, town=None, flat_type=None, year=None):
        """Get data showing impact of floor level on prices"""
        query = f"""
        SELECT 
            storey_mean,
            AVG(resale_price) as averagePrice,
            COUNT(*) as count
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE storey_mean IS NOT NULL
        """
        
        if town:
            query += f" AND town = '{town}'"
        if flat_type:
            query += f" AND flat_type = '{flat_type}'"
        if year:
            query += f" AND EXTRACT(YEAR FROM transaction_date) = {year}"
            
        query += """
        GROUP BY storey_mean
        ORDER BY storey_mean
        """
        
        return self.execute_query(query)
    
    def get_mrt_proximity_analysis(self, town=None, flat_type=None, year=None):
        """Get data showing impact of MRT proximity on prices"""
        query = f"""
        SELECT 
            FLOOR(distance_to_nearest_mrt / 100) * 100 as distance_range,
            AVG(resale_price) as averagePrice,
            COUNT(*) as count
        FROM 
            `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE distance_to_nearest_mrt IS NOT NULL
        """
        
        if town:
            query += f" AND town = '{town}'"
        if flat_type:
            query += f" AND flat_type = '{flat_type}'"
        if year:
            query += f" AND EXTRACT(YEAR FROM transaction_date) = {year}"
            
        query += """
        GROUP BY distance_range
        ORDER BY distance_range
        LIMIT 20
        """
        
        result = self.execute_query(query)
        
        # Format distance ranges for display
        for item in result:
            distance_m = item['distance_range']
            item['distance_label'] = f"{distance_m}-{distance_m + 100}m"
        
        return result
