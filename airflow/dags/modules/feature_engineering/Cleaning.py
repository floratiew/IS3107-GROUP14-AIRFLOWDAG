import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

def cleaning_final_datasets(hdb, schools, mrt):
    # Standardise headers
    hdb = hdb.rename(columns={'Average_Close':'average_close', 'Unemployment Rate':'unemployment_rate'})
    schools = schools.rename(columns={'cluster': 'school_cluster'})
    mrt = mrt.rename(columns={'STATION_NA': 'station_name', 'cluster_25': 'mrt_cluster'})

    # Merge school cluster with HDB data 
    schools['primary_schoool_count'] = (schools['mainlevel_code'] == 'PRIMARY').astype(int)

    # Group by school cluster and compute aggregated features
    cluster_centroids = schools.groupby('school_cluster').agg({
        'cluster_center_lat': 'first',
        'cluster_center_lng': 'first',
        'school_count': 'first',
        'sap_ind_pct': 'mean',
        'autonomous_ind_pct': 'mean',
        'gifted_ind_pct': 'mean',
        'ip_ind_pct': 'mean',
        'primary_schoool_count': 'sum'
    }).reset_index()


    # coordinate conversion 
    hdb_coords = np.radians(hdb[['latitude', 'longitude']])
    cluster_coords = np.radians(cluster_centroids[['cluster_center_lat', 'cluster_center_lng']])

    # spatial indexing with balltree  => balltree creates a spatial index for O(nlogn) nearest neighbor searches instead of o(nsquare) comparisons
    tree = BallTree(cluster_coords, metric='haversine')
    distances, cluster_indices = tree.query(hdb_coords, k=1)

    # Rename nearest_cluster to reflect it's a school cluster
    hdb['nearest_school_cluster'] = cluster_centroids.iloc[cluster_indices.flatten()]['school_cluster'].values

    # Merge school cluster attributes into HDB
    hdb = hdb.merge(
        cluster_centroids,
        left_on='nearest_school_cluster',
        right_on='school_cluster',
        how='left',
        suffixes=('', '_school')
    )

    # Distance to school cluster (in meters)
    hdb['distance_to_nearest_school'] = distances.flatten() * 6371000

    # Drop redundant columns
    hdb.drop(columns=['cluster_center_lat', 'cluster_center_lng','school_cluster'], inplace=True)

    # Merge mrt cluster with hdb
    mrt_centroids = mrt.groupby('mrt_cluster').agg({
        'cluster_lat': 'first',
        'cluster_long': 'first',
    }).reset_index()

    hdb_coords = np.radians(hdb[['latitude', 'longitude']])
    mrt_coords = np.radians(mrt_centroids[['cluster_lat', 'cluster_long']])
    mrt_tree = BallTree(mrt_coords, metric='haversine')
    mrt_distances, mrt_cluster_indices = mrt_tree.query(hdb_coords, k=1)
    hdb['nearest_mrt_cluster'] = mrt_centroids.iloc[mrt_cluster_indices.flatten()]['mrt_cluster'].values

    hdb = hdb.merge(
        mrt_centroids,
        left_on='nearest_mrt_cluster',
        right_on='mrt_cluster',
        how='left',
        suffixes=('', '_mrt')
    )

    hdb['distance_to_nearest_mrt'] = mrt_distances.flatten() * 6371000  # Earth's radius in meters
    hdb.drop(columns=['cluster_lat', 'cluster_long', 'mrt_cluster'], inplace=True)

    #one hot encoding
    encoded = pd.get_dummies(hdb[['flat_type', 'flat_model', 'town']], prefix=['flat_type', 'flat_model', 'town'], drop_first=False).astype('uint8')
    hdb = pd.concat([hdb, encoded], axis=1)

    # Replace slashes characters in column names
    hdb.columns = hdb.columns.str.replace('/', '_')

    return hdb