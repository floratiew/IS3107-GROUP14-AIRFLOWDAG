import pandas as pd

def feature_engineering(hdb):
    #get age of flat at resale year
    hdb['flat_age_at_resale'] = hdb['year'] - hdb['lease_commence_date']

    #converty storey_range to mean_storey
    hdb['storey_mean'] = hdb['storey_range'].str.extract(r'(\d+)\s+TO\s+(\d+)').astype(float).mean(axis=1)

    #binary indicator if flat is a high floor
    hdb['is_high_floor'] = (hdb['storey_mean'] > 12).astype(int)

    #binary indicator if flat is a big unit 
    hdb['is_big_unit'] = (hdb['floor_area_sqm'] > 110).astype(int)

    #school quality score for each cluster, comprising of percentage of schools with SAP, gifted, IP programmes and are autonomous 
    hdb['school_quality'] = hdb[['sap_ind_pct', 'autonomous_ind_pct', 'gifted_ind_pct', 'ip_ind_pct']].sum(axis=1)

    #converting town to region: 
    town_to_region = {
        #core central
        'DOWNTOWN CORE': 'Core Central Region',
        'MARINA BAY': 'Core Central Region',
        'MARINA CENTRE': 'Core Central Region',
        'RAFFLES PLACE': 'Core Central Region',
        'TANJONG PAGAR': 'Core Central Region',
        'OUTRAM': 'Core Central Region',
        'SENTOSA': 'Core Central Region',
        'ROCHOR': 'Core Central Region',
        'ORCHARD': 'Core Central Region',
        'NEWTON': 'Core Central Region',
        'RIVER VALLEY': 'Core Central Region',
        'BUKIT TIMAH': 'Core Central Region',
        'HOLLAND ROAD': 'Core Central Region',
        'TANGLIN': 'Core Central Region',
        'NOVENA': 'Core Central Region',
        'THOMSON': 'Core Central Region',
        'CENTRAL AREA': 'Core Central Region',


        #rest of central
        'BISHAN': 'Rest of Central Region',
        'BUKIT MERAH': 'Rest of Central Region',
        'GEYLANG': 'Rest of Central Region',
        'KALLANG/WHAMPOA': 'Rest of Central Region',
        'MARINE PARADE': 'Rest of Central Region',
        'QUEENSTOWN': 'Rest of Central Region',
        'SOUTHERN ISLANDS': 'Rest of Central Region',
        'TOA PAYOH': 'Rest of Central Region',
        'POTONG PASIR': 'Rest of Central Region',
        'TIONG BAHRU': 'Rest of Central Region',
        'REDHILL': 'Rest of Central Region',
        'SERANGOON': 'Rest of Central Region',
        'ANG MO KIO': 'Rest of Central Region',
        'PAYA LEBAR': 'Rest of Central Region',

        #north
        'CENTRAL WATER CATCHMENT': 'North Region',
        'LIM CHU KANG': 'North Region',
        'MANDAI': 'North Region',
        'SEMBAWANG': 'North Region',
        'SIMPANG': 'North Region',
        'SUNGEI KADUT': 'North Region',
        'WOODLANDS': 'North Region',
        'YISHUN': 'North Region',

        #north east
        'HOUGANG': 'North-East Region',
        'PUNGGOL': 'North-East Region',
        'SELETAR': 'North-East Region',
        'SENGKANG': 'North-East Region',
        'NORTH-EASTERN ISLANDS': 'North-East Region',
        'JALAN KAYU': 'North-East Region',
        'COMPASSVALE': 'North-East Region',
        'BUANGKOK': 'North-East Region',
        'ANCHORVALE': 'North-East Region',
        'FERNVALE': 'North-East Region',
        'RIVERVALE': 'North-East Region',

        #east
        'BEDOK': 'East Region',
        'CHANGI': 'East Region',
        'CHANGI BAY': 'East Region',
        'PASIR RIS': 'East Region',
        'TAMPINES': 'East Region',
        'EAST COAST': 'East Region',
        'SIGLAP': 'East Region',
        'TANAH MERAH': 'East Region',

        #west
        'BUKIT BATOK': 'West Region',
        'BUKIT PANJANG': 'West Region',
        'BOON LAY': 'West Region',
        'PIONEER': 'West Region',
        'CHOA CHU KANG': 'West Region',
        'CLEMENTI': 'West Region',
        'JURONG EAST': 'West Region',
        'JURONG WEST': 'West Region',
        'TENGAH': 'West Region',
        'TUAS': 'West Region',
        'WESTERN ISLANDS': 'West Region',
        'WESTERN WATER CATCHMENT': 'West Region',
        'BENOI': 'West Region',
        'GHIM MOH': 'West Region',
        'GUL': 'West Region',
        'PANDAN GARDENS': 'West Region',
        'JURONG ISLAND': 'West Region',
        'KENT RIDGE': 'West Region',
        'NANYANG': 'West Region',
        'PASIR LABA': 'West Region',
        'TEBAN GARDENS': 'West Region',
        'TOH TUCK': 'West Region',
        'TUAS SOUTH': 'West Region',
        'WEST COAST': 'West Region'
    }
    hdb['region'] = hdb['town'].str.upper().map(lambda x: town_to_region.get(x, 'Others'))

    #one-hot encoding region
    hdb = pd.get_dummies(hdb, columns=['region'], drop_first=True)

    #frequency encoding town
    town_freq = hdb['town'].value_counts()
    hdb['town_encoded'] = hdb['town'].map(town_freq)

    #drop columns
    hdb.drop(columns=['postal_code','address', 'storey_range'], inplace=True)
    
    return hdb