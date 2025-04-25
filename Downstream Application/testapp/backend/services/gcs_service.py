from google.cloud import storage
import os
import json
import tempfile
import hashlib
import time
import shutil
from datetime import datetime, timedelta

class GCSService:
    def __init__(self, credentials_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.client = storage.Client()
        self.bucket_name = "is3107-project-bucket"
        
        # Create a unique session ID
        session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # Create a temporary directory for caching files with session ID
        self.temp_dir = tempfile.mkdtemp(prefix=f"hdb_model_cache_{session_id}_")
        print(f"Created session-based cache directory: {self.temp_dir}")
        
        # Keep track of downloaded files and their metadata
        self.cache_metadata = {}
    
    def __del__(self):
        """Clean up temporary directory when the service is destroyed"""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary cache directory: {self.temp_dir}")
        except Exception as e:
            print(f"Error cleaning up temporary directory: {str(e)}")
    
    def _get_blob_metadata(self, source_blob_name):
        """Get metadata for a blob in the bucket"""
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.reload()
        return {
            'updated': blob.updated,
            'size': blob.size,
            'md5_hash': blob.md5_hash
        }
    
    def _is_cache_valid(self, cache_path, source_blob_name):
        """Check if the cached file is still valid within the current session"""
        # Check if file exists on disk
        if not os.path.exists(cache_path):
            return False
            
        # Check if file exists in cache metadata for this session
        if source_blob_name not in self.cache_metadata:
            return False
            
        # For session-based caching, we don't check expiry time
        # The cache is valid as long as it exists in the current session
        return True
    
    def download_file(self, source_blob_name, destination_file_name=None):
        """Downloads a blob from the bucket or uses cached version if available."""
        # If no destination is provided, use the temp directory
        if destination_file_name is None:
            # Create a filename based on the source blob name
            filename = os.path.basename(source_blob_name)
            destination_file_name = os.path.join(self.temp_dir, filename)
        
        # Check if we have a valid cached version
        if self._is_cache_valid(destination_file_name, source_blob_name):
            print(f"Using cached version of {source_blob_name} at {destination_file_name}")
            return destination_file_name
        
        # Download the file
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
        
        # Download the file
        blob.download_to_filename(destination_file_name)
        print(f"Downloaded {source_blob_name} to {destination_file_name}")
        
        # Update cache metadata
        self.cache_metadata[source_blob_name] = {
            'path': destination_file_name,
            'time': time.time(),
            'metadata': self._get_blob_metadata(source_blob_name)
        }
        
        return destination_file_name
    
    def download_model_files(self, local_dir=None):
        """Downloads all necessary model files to a temporary directory."""
        # If local_dir is None, use the temp directory
        if local_dir is None:
            local_dir = self.temp_dir
        
        files_to_download = [
            ("models/hdb_xgb_model.json", f"{local_dir}/hdb_xgb_model.json"),
            ("models/model_columns.json", f"{local_dir}/model_columns.json"),
            ("datasets/stock.csv", f"{local_dir}/stock.csv"),
            ("datasets/unemployment.csv", f"{local_dir}/unemployment.csv"),
            ("temporary/mrt_clustered.csv", f"{local_dir}/mrt_clustered.csv"),
            ("temporary/schools_clustered.csv", f"{local_dir}/schools_clustered.csv")
        ]
        
        downloaded_files = {}
        
        for source, dest in files_to_download:
            try:
                file_path = self.download_file(source, dest)
                downloaded_files[source] = file_path
            except Exception as e:
                print(f"Error downloading {source}: {str(e)}")
                raise
        
        return downloaded_files
    
    def list_blobs(self, prefix=None):
        """Lists all the blobs in the bucket with the given prefix."""
        bucket = self.client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        
        return [blob.name for blob in blobs]
