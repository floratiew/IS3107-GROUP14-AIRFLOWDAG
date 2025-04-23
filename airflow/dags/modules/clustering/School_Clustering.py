import os
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def cluster_schools_and_visualize_with_features(
    schools_df,
    k,
    geo_weight=2,
    preprocessor=None,
    output_map_path='clustering_data/school_clusters_map.html'
):
    geo_features = ['latitude', 'longitude']
    categorical_features = ['type_code', 'mainlevel_code', 'nature_code', 'session_code']
    binary_features = ['sap_ind', 'autonomous_ind', 'gifted_ind', 'ip_ind']

    avail_cat_features = [f for f in categorical_features if f in schools_df.columns]
    avail_bin_features = [f for f in binary_features if f in schools_df.columns]

    for feat in avail_bin_features:
        if schools_df[feat].dtype == 'object':
            schools_df[feat] = schools_df[feat].map({'Y': 1, 'N': 0}).fillna(0).astype(int)

    required_columns = geo_features + avail_cat_features + avail_bin_features
    clean_df = schools_df.dropna(subset=required_columns)

    weighted_df = pd.DataFrame()
    for feature in geo_features:
        for i in range(int(geo_weight)):
            weighted_df[f"{feature}_{i}"] = clean_df[feature]
    for feature in avail_cat_features + avail_bin_features:
        weighted_df[feature] = clean_df[feature]

    if preprocessor is None:
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        geo_columns = [f"{feature}_{i}" for feature in geo_features for i in range(int(geo_weight))]

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, geo_columns),
                ('cat', categorical_transformer, avail_cat_features)
            ],
            remainder='passthrough'
        )
        preprocessor.fit(weighted_df)

    feature_matrix = preprocessor.transform(weighted_df)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(feature_matrix)

    clean_df['cluster'] = cluster_labels

    colors = plt.cm.rainbow(np.linspace(0, 1, k))
    color_map = {
        i: '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
        for i, (r, g, b, _) in enumerate(colors)
    }

    singapore_map = folium.Map(location=[1.3521, 103.8198], zoom_start=12, tiles='CartoDB positron')

    metrics = ['school_name']
    agg_dict = {'school_name': 'count'}
    for feat in avail_bin_features:
        metrics.append(feat)
        agg_dict[feat] = 'sum'

    cluster_stats = clean_df.groupby('cluster')[metrics].agg(agg_dict).rename(columns={'school_name': 'school_count'})
    for feat in avail_bin_features:
        cluster_stats[f'{feat}_pct'] = (cluster_stats[feat] / cluster_stats['school_count'] * 100).round(1)

    geo_centers = clean_df.groupby('cluster')[['latitude', 'longitude']].mean()
    geo_centers.columns = ['cluster_center_lat', 'cluster_center_lng']
    cluster_full_stats = pd.concat([cluster_stats, geo_centers], axis=1)

    cat_distributions = {}
    for feat in avail_cat_features:
        cat_values = clean_df[feat].unique()
        for val in cat_values:
            val_counts = clean_df[clean_df[feat] == val].groupby('cluster').size()
            for cluster_id in cluster_stats.index:
                cluster_total = cluster_stats.loc[cluster_id, 'school_count']
                val_count = val_counts.get(cluster_id, 0)
                cat_distributions[(cluster_id, feat, val)] = (val_count / cluster_total * 100)

    for _, school in clean_df.iterrows():
        cluster_id = school['cluster']
        color = color_map[cluster_id]
        popup_text = f"<b>{school.get('school_name', 'School')}</b><br>Cluster: {cluster_id}<br>"
        for field in avail_cat_features:
            if field in school and not pd.isna(school[field]):
                popup_text += f"{field.replace('_', ' ').title()}: {school[field]}<br>"
        for field in avail_bin_features:
            if field in school and school[field]:
                popup_text += f"{field.replace('_', ' ').title()}: Yes<br>"
        if 'address' in school and not pd.isna(school['address']):
            popup_text += f"Address: {school['address']}<br>"

        folium.CircleMarker(
            location=[school['latitude'], school['longitude']],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(singapore_map)

    for cluster_id, stats in cluster_full_stats.iterrows():
        popup_html = f"""
        <div style="min-width: 300px;">
            <h3>Cluster {cluster_id} Statistics</h3>
            <table style="width:100%; border-collapse: collapse;">
                <tr><td><b>Number of Schools:</b></td><td>{stats['school_count']}</td></tr>
                <tr><td><b>Center Coordinates:</b></td><td>{stats['cluster_center_lat']:.4f}, {stats['cluster_center_lng']:.4f}</td></tr>
        """
        for feat in avail_bin_features:
            if f'{feat}_pct' in stats:
                popup_html += f"""
                <tr>
                    <td><b>{feat.replace('_', ' ').title()} Schools:</b></td>
                    <td>{stats[feat]} ({stats[f'{feat}_pct']}%)</td>
                </tr>
                """
        popup_html += "</table><br><h4>Categorical Feature Distributions:</h4>"
        for feat in avail_cat_features:
            popup_html += f"<h5>{feat.replace('_', ' ').title()}:</h5><table style='width:100%; border-collapse: collapse;'>"
            feature_values = {
                key[2]: pct for key, pct in cat_distributions.items() if key[0] == cluster_id and key[1] == feat
            }
            sorted_values = sorted(feature_values.items(), key=lambda x: x[1], reverse=True)
            for val, pct in sorted_values:
                popup_html += f"<tr><td>{val}</td><td>{pct:.1f}%</td></tr>"
            popup_html += "</table><br>"
        popup_html += "</div>"

        folium.Marker(
            location=[stats['cluster_center_lat'], stats['cluster_center_lng']],
            popup=folium.Popup(popup_html, max_width=400),
            icon=folium.Icon(color='black', icon='info-sign'),
            tooltip=f"Cluster {cluster_id} Center - Click for details"
        ).add_to(singapore_map)

        folium.Circle(
            location=[stats['cluster_center_lat'], stats['cluster_center_lng']],
            radius=300,
            color=color_map[cluster_id],
            fill=True,
            fill_color=color_map[cluster_id],
            fill_opacity=0.2,
            weight=3
        ).add_to(singapore_map)

    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 250px;
        background-color: white; border:2px solid grey; z-index:9999; font-size:12px;
        padding: 10px; border-radius: 5px;">
        <p><b>School Clusters</b></p>
    '''
    for i in range(k):
        legend_html += f'<p><i class="fa fa-circle" style="color:{color_map[i]}"></i> Cluster {i} ({cluster_stats.loc[i, "school_count"]} schools)</p>'
    legend_html += '<p><i class="fa fa-map-marker" style="color:black"></i> Cluster Center (click for details)</p></div>'

    singapore_map.get_root().html.add_child(folium.Element(legend_html))

    # Ensure the output folder exists
    os.makedirs(os.path.dirname(output_map_path), exist_ok=True)

    # Save the map to HTML
    singapore_map.save(output_map_path)
    print(f"Interactive map saved to {output_map_path}")

    # Return final results
    cluster_stats_df = cluster_full_stats.reset_index()
    # result_df = clean_df.merge(
    #     cluster_stats_df,
    #     left_on='cluster',
    #     right_on='cluster',
    #     how='left'
    # )

    return clean_df, cluster_stats_df, cat_distributions