import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_MRT_data():
    dataset_id = "d_b39d3a0871985372d7e1637193335da5"
    url = "https://api-open.data.gov.sg/v1/public/api/datasets/" + dataset_id + "/poll-download"

    response = requests.get(url)
    json_data = response.json()
    if json_data['code'] != 0:
        print(json_data['errMsg'])
        return None

    url = json_data['data']['url']
    response = requests.get(url)
    geojson = response.json()

    records = []
    for feature in geojson['features']:
        props = feature['properties']
        geom = feature['geometry']
        
        # Using BeautifulSoup to parse HTML in 'Description'
        soup = BeautifulSoup(props['Description'], 'html.parser')
        rows = soup.find_all('tr')[1:]  # skip header row
        record = {row.find_all('th')[0].text.strip(): row.find_all('td')[0].text.strip() for row in rows}
        
        # Adding longitude and latitude coordinates
        record['longitude'] = geom['coordinates'][0]
        record['latitude'] = geom['coordinates'][1]
        
        records.append(record)

    df = pd.DataFrame(records)
    df = df[['STATION_NA', 'EXIT_CODE', 'longitude', 'latitude']]

    # Convert columns to appropriate data type
    df['longitude'] = pd.to_numeric(df['longitude'])
    df['latitude'] = pd.to_numeric(df['latitude'])

    return df