import requests
from urllib.parse import quote

class GeocodingService:
    def __init__(self):
        self.base_url = "https://www.onemap.gov.sg/api"
        self.token = None
    
    def get_token(self):
        """Get OneMap API token"""
        if self.token:
            return self.token
            
        url = f"{self.base_url}/auth/post/getToken"
        payload = {"email": "Jevan.Koh@u.nus.edu", "password": "JekoP4ssw0rd@123"}
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return self.token
            else:
                print(f"Error getting token: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception getting token: {str(e)}")
            return None
    
    def get_lat_lon(self, search_val):
        """Get latitude and longitude from OneMap API"""
        token = self.get_token()
        if not token:
            return None, None, None
            
        url = f"{self.base_url}/common/elastic/search?searchVal={quote(search_val)}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers)
            results = response.json().get("results", [])
            if results:
                return float(results[0]["LATITUDE"]), float(results[0]["LONGITUDE"]), results[0].get("POSTAL")
        except Exception as e:
            print(f"Error geocoding address: {str(e)}")
            
        # Default to central Singapore if geocoding fails
        return 1.3521, 103.8198, None
