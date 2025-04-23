import requests
import pandas as pd
import time
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_Schools_data(ONEMAP_TOKEN):
    dataset_id = "d_688b934f82c1059ed0a6993d2a829089"
    base_url = "https://data.gov.sg/api/action/datastore_search"
    all_records = []
    limit = 500
    offset = 0
    
    while True:
        url = f"{base_url}?resource_id={dataset_id}&limit={limit}&offset={offset}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            break

        data = response.json()
        records = data['result']['records']
        if not records:
            break 
        all_records.extend(records)
        offset += limit

    df = pd.DataFrame(all_records)
    df = df[['school_name', 'address', 'postal_code', 'type_code', 'nature_code', 'session_code', 'mainlevel_code', 'sap_ind',
             'autonomous_ind', 'gifted_ind', 'ip_ind']]
    df['address'] = df['address'].apply(lambda x: ' '.join(str(x).split()))

    # Converting _ind columns to boolean
    ind_columns = ['sap_ind', 'autonomous_ind', 'gifted_ind', 'ip_ind']
    for col in ind_columns:
        df[col] = df[col].map({'Yes': True, 'No': False})

    # Getting the latitudes and longtitudes of each school using parallel processing
    address_coords = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(get_lat_lon, row['postal_code'], row['school_name'], ONEMAP_TOKEN): row['postal_code']
            for _, row in df.iterrows()
        }
        for future in as_completed(futures):
            addr = futures[future]
            lat, lon = future.result()
            address_coords[addr] = (lat, lon)

    # Mapping back the results in the correct order
    df['latitude'] = df['postal_code'].map(lambda x: address_coords.get(x, (None, None))[0])
    df['longitude'] = df['postal_code'].map(lambda x: address_coords.get(x, (None, None))[1])
    df = df.dropna(subset=['latitude', 'longitude'])

    return df

def get_lat_lon(search_val, secondary_search_val, ONEMAP_TOKEN):
    retries = 3
    url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={quote(search_val)}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
    fallback_url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={quote(secondary_search_val)}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
    headers = {
        "Authorization": f"Bearer {ONEMAP_TOKEN}"
    }
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return float(results[0]["LATITUDE"]), float(results[0]["LONGITUDE"])
                else:
                    print(f"No results for address {search_val}")
                    break
            else:
                print(f"Non-200 status code for address {search_val}: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"Timeout for address {search_val} (attempt {attempt + 1}/{retries})")
        except Exception as e:
            print(f"Error for address {search_val} (attempt {attempt + 1}/{retries}): {e}")
        time.sleep(0.5 * (attempt + 1))
    
    for attempt2 in range(retries + 1):
        try:
            response2 = requests.get(fallback_url, headers=headers, timeout=5)
            if response2.status_code == 200:
                results2 = response2.json().get("results", [])
                if results2:
                    return float(results2[0]["LATITUDE"]), float(results2[0]["LONGITUDE"])
                else:
                    print(f"🔍 No results for address {secondary_search_val}")
                    return None, None
            else:
                print(f"Non-200 status code for address {secondary_search_val}: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"Timeout for address {secondary_search_val} (attempt {attempt2 + 1}/{retries})")
        except Exception as e:
            print(f"Error for address {secondary_search_val} (attempt {attempt2 + 1}/{retries}): {e}")
        time.sleep(0.5 * (attempt2 + 1))
    
    print(f"Failed all retries for address {search_val}")
    return None, None