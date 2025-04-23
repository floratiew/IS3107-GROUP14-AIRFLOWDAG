import requests
import pandas as pd
import time
from datetime import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_HDB_data(ONEMAP_TOKEN):
    dataset_id = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
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

    # Convert columns to appropriate data type
    df['resale_price'] = pd.to_numeric(df['resale_price'])
    df['floor_area_sqm'] = pd.to_numeric(df['floor_area_sqm'])
    df['lease_commence_date'] = pd.to_numeric(df['lease_commence_date'])

    # Add years_from_lease_commence column
    df['years_from_lease'] = datetime.now().year - df['lease_commence_date']

    # Extract years and months from remaining_lease
    years = df['remaining_lease'].str.extract(r'(\d+)\s+year[s]?')[0].astype(float)
    months = df['remaining_lease'].str.extract(r'(\d+)\s+month[s]?')[0].fillna(0).astype(float)

    # Calculate total months
    df['remaining_lease_months'] = (years * 12) + months

    # Split month column to year and month
    df[['year', 'month']] = df['month'].str.split('-', expand=True).astype(int)

    # Drop _id and remaining_lease column
    df.drop(columns=['_id', 'remaining_lease'], inplace=True)

    # Getting the latitudes and longtitudes of each unit using parallel processing
    df['address'] = df['block'].str.strip() + ' ' + df['street_name'].str.strip()
    df.drop(columns=['block', 'street_name'], inplace=True)
    df_unique_addresses = df[['address']].drop_duplicates().reset_index(drop=True)

    address_coords = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(get_lat_lon, addr, ONEMAP_TOKEN): addr for addr in df_unique_addresses['address']}
        for future in as_completed(futures):
            addr = futures[future]
            lat, lon, postal = future.result()
            address_coords[addr] = (lat, lon, postal)
    
    # Mapping back the results in the correct order
    df_unique_addresses['latitude'] = df_unique_addresses['address'].map(lambda x: address_coords.get(x, (None, None, None))[0])
    df_unique_addresses['longitude'] = df_unique_addresses['address'].map(lambda x: address_coords.get(x, (None, None, None))[1])
    df_unique_addresses['postal_code'] = df_unique_addresses['address'].map(lambda x: address_coords.get(x, (None, None, None))[2])
    
    # Joining this data back to the main HDB data
    # df = df.merge(df_unique_addresses, on='address', how='left')
    # df = df.dropna(subset=['latitude', 'longitude'])

    return df, df_unique_addresses

def get_lat_lon(search_val, ONEMAP_TOKEN):
    retries = 3
    url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={quote(search_val)}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
    headers = {
        "Authorization": f"Bearer {ONEMAP_TOKEN}"
    }
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    lat = float(results[0]["LATITUDE"])
                    lon = float(results[0]["LONGITUDE"])
                    postal = results[0].get("POSTAL", None)
                    return lat, lon, postal
                else:
                    print(f"No results for address {search_val}")
                    return None, None, None
            else:
                print(f"Non-200 status code for address {search_val}: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"Timeout for address {search_val} (attempt {attempt + 1}/{retries})")
        except Exception as e:
            print(f"Error for address {search_val} (attempt {attempt + 1}/{retries}): {e}")
        time.sleep(0.5 * (attempt + 1))
    
    print(f"Failed all retries for address {search_val}")
    return None, None, None