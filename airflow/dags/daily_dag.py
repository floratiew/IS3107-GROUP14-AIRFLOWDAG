import os
import json
import pandas as pd
from airflow.decorators import dag, task
from airflow import DAG
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from datetime import datetime, timedelta
from apis.HDB_API import get_HDB_data
from apis.MRT_API import get_MRT_data
from apis.Schools_API import get_Schools_data
from apis.Stock_API import get_stock_data
from apis.Unemployment_API import get_unemployment_data
from apis.OneMap_TokenManager import get_token
from modules.clustering.School_Clustering import cluster_schools_and_visualize_with_features
from modules.clustering.MRT_Clustering import cluster_mrt_stations
from modules.feature_engineering.Cleaning import cleaning_final_datasets
from modules.feature_engineering.Feature_Engineering import feature_engineering
from modules.models.XGBoost import train_xgb_model

GCS_BUCKET_NAME = "is3107-project-bucket"
GCP_CONN_ID = "google_cloud_default"
BQ_DATASET = "is3107_dataset"
BQ_TABLE = "hdb_integrated_data"
PROJECT_ID = "is3107-project-457501"

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 3, 
    'retry_delay': timedelta(minutes=5),  
    'email': ['Jevan.Koh@u.nus.edu', 'choeignatius@gmail.com', 'xiangjunooi@u.nus.edu', 'e0970534@u.nus.edu', 'seanlimjingheng@gmail.com'],
    'email_on_failure': True, 
    'email_on_retry': False, 
}

@dag(
    dag_id='daily_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['is3107-project']
)

def my_dag():
    @task
    def start_DAG():
        print("Starting DAG!")

    @task
    def run_hdb_api():
        ONEMAP_TOKEN = get_token()
        df, df_unique_addresses = get_HDB_data(ONEMAP_TOKEN)
        _upload_to_gcs(df, "hdb")
        _upload_to_gcs(df_unique_addresses, "hdb_unique_addresses")

    @task
    def run_mrt_api():
        df = get_MRT_data()
        _upload_to_gcs(df, "mrt")

    @task
    def run_schools_api():
        ONEMAP_TOKEN = get_token()
        df = get_Schools_data(ONEMAP_TOKEN)
        _upload_to_gcs(df, "schools")

    @task
    def run_stock_api():
        df = get_stock_data()
        _upload_to_gcs(df, "stock")

    @task
    def run_unemployment_api():
        df = get_unemployment_data()
        _upload_to_gcs(df, "unemployment")

    # Uploading all initial extracts
    def _upload_to_gcs(df, name):
        os.makedirs("datasets", exist_ok=True)
        local_path = f"datasets/{name}.csv"
        gcs_path = f"datasets/{name}.csv"
        df.to_csv(local_path, index=False)
        hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        hook.upload(bucket_name=GCS_BUCKET_NAME, object_name=gcs_path, filename=local_path)
        print(f"Uploaded {name}.csv to gs://{GCS_BUCKET_NAME}/{gcs_path}")
    
    @task
    def extract_apis_from_gcs():
        """
        Downloads CSVs directly from GCS.
        """
        filenames = ["hdb", "mrt", "schools", "stock", "unemployment"]
        hook = GCSHook(gcp_conn_id=GCP_CONN_ID)

        for name in filenames:
            gcs_path = f"datasets/{name}.csv"
            local_path = f"datasets/{name}.csv"
            hook.download(
                bucket_name=GCS_BUCKET_NAME,
                object_name=gcs_path,
                filename=local_path
            )
            df = pd.read_csv(local_path)
            print(f"{name.upper()} data shape: {df.shape}")
        
        return "Extract from GCS completed."
        
    @task
    def run_school_clustering():
        """
        Downloads schools.csv from GCS, performs clustering, saves results locally and re-uploads the updated dataset to GCS.
        """
        # Downloading schools.csv from GCS
        gcs_path = "datasets/schools.csv"
        local_path = "datasets/schools.csv"
        hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        hook.download(bucket_name=GCS_BUCKET_NAME, object_name=gcs_path, filename=local_path)
        df_schools = pd.read_csv(local_path)

        # Running clustering
        df_schools_cluster_id, df_schools_cluster_stats, cat_distributions = cluster_schools_and_visualize_with_features(
            df_schools,
            k=8,
            output_map_path='clustering_data/school_clusters_map.html'
        )

        # Saving updated school data with cluster labels
        os.makedirs("clustering_data", exist_ok=True)
        output_files = {
            "clustering_data/schools_cluster_id.csv": df_schools_cluster_id,
            "clustering_data/schools_cluster_stats.csv": df_schools_cluster_stats
        }

        for path, df in output_files.items():
            df.to_csv(path, index=False)
            hook.upload(
                bucket_name=GCS_BUCKET_NAME, 
                object_name=path, 
                filename=path
            )
        
        print("Clustering complete. Updated schools dataset uploaded to GCS.")

    @task
    def run_mrt_clustering():
        """
        Downloads mrt.csv from GCS, performs clustering, saves results locally and re-uploads the updated dataset to GCS.
        """
        # Downloading mrt.csv from GCS
        gcs_path = "datasets/mrt.csv"
        local_path = "datasets/mrt.csv"
        hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        hook.download(bucket_name=GCS_BUCKET_NAME, object_name=gcs_path, filename=local_path)
        df_mrt = pd.read_csv(local_path)

        # Running clustering
        df_mrt_cluster_id, df_mrt_cluster_stats = cluster_mrt_stations(df_mrt, cluster_output_path='clustering_data/mrt_cluster_id.csv', cluster_info_path='clustering_data/mrt_cluster_stats.csv')

        # Saving updated MRT data with cluster labels
        os.makedirs("clustering_data", exist_ok=True)
        output_files = {
            "clustering_data/mrt_cluster_id.csv": df_mrt_cluster_id,
            "clustering_data/mrt_cluster_stats.csv": df_mrt_cluster_stats
        }

        for path, df in output_files.items():
            df.to_csv(path, index=False)
            hook.upload(
                bucket_name=GCS_BUCKET_NAME, 
                object_name=path, 
                filename=path
            )
        
        print("Clustering complete. Updated MRT dataset uploaded to GCS.")
    
    @task
    def join_clean_feature_engineering():
        """
        Joins, Cleans, and Feature Engineering is done on the data.
        """
        # Set up GCS hook
        gcs_hook = GCSHook(gcp_conn_id=GCP_CONN_ID)

        # Define paths
        file_map = {
            "hdb": "datasets/hdb.csv",
            "hdb_unique_addresses": "datasets/hdb_unique_addresses.csv",
            "stock": "datasets/stock.csv",
            "unemployment": "datasets/unemployment.csv",
            "mrt_cluster_id": "clustering_data/mrt_cluster_id.csv",
            "mrt_cluster_stats": "clustering_data/mrt_cluster_stats.csv",
            "schools_cluster_id": "clustering_data/schools_cluster_id.csv",
            "schools_cluster_stats": "clustering_data/schools_cluster_stats.csv"
        }

        # Download and load data from GCS
        for name, gcs_path in file_map.items():
            gcs_hook.download(
                bucket_name=GCS_BUCKET_NAME,
                object_name=gcs_path,
                filename=gcs_path
            )

        df_hdb = pd.read_csv(file_map["hdb"])
        df_hdb_addresses = pd.read_csv(file_map["hdb_unique_addresses"])
        df_stock = pd.read_csv(file_map["stock"])
        df_unemployment = pd.read_csv(file_map["unemployment"])
        df_mrt_cluster_id = pd.read_csv(file_map["mrt_cluster_id"])
        df_mrt_cluster_stats = pd.read_csv(file_map["mrt_cluster_stats"])
        df_schools_cluster_id = pd.read_csv(file_map["schools_cluster_id"])
        df_schools_cluster_stats = pd.read_csv(file_map["schools_cluster_stats"])

        # Full outer join on address
        df_hdb = df_hdb.merge(df_hdb_addresses, on="address", how="outer")

        # Left join with stock
        df_hdb = df_hdb.merge(
            df_stock,
            left_on=["year", "month"],
            right_on=["Year", "Month"],
            how="left",
            suffixes=("", "_stock")
        )

        # Left join with unemployment
        df_hdb = df_hdb.merge(
            df_unemployment,
            left_on=["year", "month"],
            right_on=["Year", "Month"],
            how="left",
            suffixes=("", "_unemp")
        )

        # MRT and School clusters (not merged into HDB)
        df_mrt_clustered = df_mrt_cluster_id.merge(df_mrt_cluster_stats, on="cluster_25", how="outer")
        df_schools_clustered = df_schools_cluster_id.merge(df_schools_cluster_stats, on="cluster", how="outer")
        

        # Fix errors in code
        df_hdb['postal_code'] = df_hdb['postal_code'].replace("NIL", pd.NA).astype("string")
        df_hdb.drop(columns=["Year", "Month", "Year_stock", "Month_stock", "Year_unemp", "Month_unemp"], inplace=True, errors="ignore")

        # Final clean of data
        df_all_data = cleaning_final_datasets(df_hdb, df_schools_clustered, df_mrt_clustered)

        # Feature engineering
        df_all_data = feature_engineering(df_all_data)

        # Create a temporary folder
        os.makedirs("temporary", exist_ok=True)
        df_mrt_clustered.to_csv("temporary/mrt_clustered.csv", index=False)
        df_schools_clustered.to_csv("temporary/schools_clustered.csv", index=False)
        print("Temporary files saved for MRT and School clustering.")
        df_all_data.to_csv("temporary/hdb_integrated_data.csv", index=False)

        # Upload MRT clustered to GCS
        gcs_hook.upload(
            bucket_name=GCS_BUCKET_NAME,
            object_name="temporary/mrt_clustered.csv",
            filename="temporary/mrt_clustered.csv"
        )

        # Upload Schools clustered to GCS
        gcs_hook.upload(
            bucket_name=GCS_BUCKET_NAME,
            object_name="temporary/schools_clustered.csv",
            filename="temporary/schools_clustered.csv"
        )

        # Upload Final dataset to GCS
        gcs_hook.upload(
            bucket_name=GCS_BUCKET_NAME,
            object_name="temporary/hdb_integrated_data.csv",
            filename="temporary/hdb_integrated_data.csv"
        )
    
    @task
    def train_and_upload_model():
        bq_hook = BigQueryHook(gcp_conn_id=GCP_CONN_ID, use_legacy_sql=False)
        query = """
            SELECT * FROM `is3107-project-457501.is3107_dataset.hdb_integrated_data`
        """
        df = bq_hook.get_pandas_df(
            sql=query,
            location="asia-southeast1"
        )

        output_model_path = "models/hdb_xgb_model.json"
        output_columns_path = "models/model_columns.json"
        train_xgb_model(df, output_model_path)

        gcs_hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        gcs_hook.upload(
            bucket_name=GCS_BUCKET_NAME,
            object_name="models/hdb_xgb_model.json",
            filename=output_model_path
        )

        gcs_hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        gcs_hook.upload(
            bucket_name=GCS_BUCKET_NAME,
            object_name="models/model_columns.json",
            filename=output_columns_path
        )

        print("Trained XGBoost model using BigQuery data and uploaded to GCS.")
    
    # Initializing DAG
    start_DAG_task = start_DAG()
    
    # Extracting datasets using APIs and pushing them to Google Cloud
    run_hdb_api_task = run_hdb_api()
    run_mrt_api_task = run_mrt_api()
    run_schools_api_task = run_schools_api()
    run_stock_api_task = run_stock_api()
    run_unemployment_api_task = run_unemployment_api()

    # Checking the datasets in Google Cloud
    extract_apis_task = extract_apis_from_gcs()

    # Clustering the School and MRT datasets
    run_school_clustering_task = run_school_clustering()
    run_mrt_clustering_task = run_mrt_clustering()

    # Joining, Cleaning and Feature Engineering for all datasets
    join_clean_feature_engineering_task = join_clean_feature_engineering()

    # Uploading to BigQuery
    bq_upload_task = BigQueryInsertJobOperator(
        task_id="bq_upload_hdb_integrated_data",
        configuration={
            "load": {
                "sourceUris": [f"gs://{GCS_BUCKET_NAME}/temporary/hdb_integrated_data.csv"],
                "destinationTable": {
                    "projectId": PROJECT_ID,
                    "datasetId": BQ_DATASET,
                    "tableId": BQ_TABLE,
                },
                "sourceFormat": "CSV",
                "autodetect": True,
                "writeDisposition": "WRITE_TRUNCATE"
            }
        },
        gcp_conn_id=GCP_CONN_ID
    )

    # Training predictive model, and uploading to GCS.
    train_model_task = train_and_upload_model()

    start_DAG_task >> [
        run_hdb_api_task,
        run_mrt_api_task,
        run_schools_api_task,
        run_stock_api_task,
        run_unemployment_api_task
    ] >> extract_apis_task >> [run_school_clustering_task, run_mrt_clustering_task] >> join_clean_feature_engineering_task >> bq_upload_task >> train_model_task

dag = my_dag()