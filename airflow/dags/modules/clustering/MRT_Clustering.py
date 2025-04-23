import pandas as pd
import folium
import random
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import os

def cluster_mrt_stations(
        df, 
        cluster_output_path='"clustering_data/mrt_cluster_id.csv', 
        cluster_info_path='clustering_data/mrt_cluster_stats.csv'
    ):
    
    # Aggregating exits to station-level centers
    centroid_df = df.groupby('STATION_NA').agg({
        'longitude': 'mean',
        'latitude': 'mean'
    }).reset_index()

    X = centroid_df[['longitude', 'latitude']]
    best_k = 2
    best_score = -1

    for k in range(2, 30 + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        if score > best_score:
            best_k = k
            best_score = score

    print(f"Optimal number of clusters determined by silhouette score: {best_k}")

    def cluster_and_add_column(data, k):
        X = data[['longitude', 'latitude']]
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        data[f'cluster_{k}'] = kmeans.fit_predict(X)
        return data

    def plot_folium_map(data, k, singapore_center=[1.3521, 103.8198], zoom_start=11):
        m = folium.Map(location=singapore_center, zoom_start=zoom_start)

        random.seed(42)
        cluster_colors = {i: f'#{random.randint(0, 0xFFFFFF):06x}' for i in range(k)}

        for _, row in data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                popup=f"{row['STATION_NA']} (Cluster {row[f'cluster_{k}']})",
                color=cluster_colors[row[f'cluster_{k}']],
                fill=True,
                fill_opacity=0.7
            ).add_to(m)

        return m

    for k in [best_k, 15, 20, 25]:
        centroid_df = cluster_and_add_column(centroid_df, k)

    maps = {}
    for k in [best_k, 15, 20, 25]:
        m = plot_folium_map(centroid_df, k)
        maps[k] = m
        os.makedirs('clustering_data', exist_ok=True)
        m.save(f'clustering_data/mrt_clusters_k_{k}.html')

    print("Maps saved for visual validation.")

    # Based on visual judgement, 25 clusters is appriopriate
    mrt_data_25_clusters = centroid_df[['STATION_NA', 'longitude', 'latitude', 'cluster_25']]

    # Create clusters_info dataframe with the cluster number, lat, long, and number of stations
    clusters_info = centroid_df.groupby('cluster_25').agg(
        cluster_lat=('latitude', 'mean'),
        cluster_long=('longitude', 'mean'),
        num_stations=('STATION_NA', 'count')
    ).reset_index()

    # Save cluster results
    mrt_data_25_clusters.to_csv(cluster_output_path, index=False)
    clusters_info.to_csv(cluster_info_path, index=False)

    return mrt_data_25_clusters, clusters_info