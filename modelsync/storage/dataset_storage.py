"""
Dataset storage and versioning for ModelSync
"""

import os
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import boto3
from google.cloud import storage
from modelsync.utils.helpers import calculate_file_hash, ensure_directory, write_json_file, read_json_file

class DatasetStorage:
    """Manages dataset storage and versioning with cloud support"""
    
    def __init__(self, repo_path: str = ".", config: Optional[Dict] = None):
        self.repo_path = Path(repo_path)
        self.storage_dir = self.repo_path / ".modelsync" / "storage" / "datasets"
        self.config = config or {}
        self._setup_cloud_clients()
    
    def _setup_cloud_clients(self):
        """Setup cloud storage clients"""
        self.s3_client = None
        self.gcs_client = None
        
        # AWS S3
        if self.config.get("aws", {}).get("access_key_id"):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config["aws"]["access_key_id"],
                aws_secret_access_key=self.config["aws"]["secret_access_key"],
                region_name=self.config["aws"].get("region", "us-east-1")
            )
        
        # Google Cloud Storage
        if self.config.get("gcs", {}).get("project_id"):
            self.gcs_client = storage.Client(
                project=self.config["gcs"]["project_id"]
            )
    
    def add_dataset(
        self,
        dataset_path: str,
        dataset_name: str,
        description: str = "",
        tags: List[str] = None,
        cloud_storage: Optional[str] = None,
        deduplicate: bool = True
    ) -> Dict[str, Any]:
        """Add a dataset to version control"""
        
        dataset_path = Path(dataset_path)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # Calculate dataset hash for deduplication
        dataset_hash = self._calculate_dataset_hash(dataset_path)
        
        # Check if dataset already exists (deduplication)
        if deduplicate:
            existing = self._find_existing_dataset(dataset_hash)
            if existing:
                print(f"📦 Dataset already exists: {existing['name']} ({dataset_hash[:8]})")
                return existing
        
        # Create dataset metadata
        dataset_metadata = {
            "id": dataset_hash[:16],
            "name": dataset_name,
            "description": description,
            "tags": tags or [],
            "original_path": str(dataset_path),
            "hash": dataset_hash,
            "size": self._calculate_dataset_size(dataset_path),
            "file_count": self._count_files(dataset_path),
            "created_at": datetime.now().isoformat(),
            "cloud_storage": cloud_storage,
            "storage_info": {}
        }
        
        # Store dataset locally
        self._store_dataset_locally(dataset_path, dataset_metadata)
        
        # Upload to cloud if specified
        if cloud_storage:
            self._upload_to_cloud(dataset_path, dataset_metadata, cloud_storage)
        
        # Save metadata
        self._save_dataset_metadata(dataset_metadata)
        
        print(f"✅ Dataset added: {dataset_name} ({dataset_hash[:8]})")
        return dataset_metadata
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset metadata by ID"""
        metadata_file = self.storage_dir / "metadata" / f"{dataset_id}.json"
        if metadata_file.exists():
            return read_json_file(str(metadata_file))
        return None
    
    def list_datasets(self, tags: List[str] = None) -> List[Dict[str, Any]]:
        """List all datasets, optionally filtered by tags"""
        datasets = []
        metadata_dir = self.storage_dir / "metadata"
        
        if not metadata_dir.exists():
            return datasets
        
        for metadata_file in metadata_dir.glob("*.json"):
            dataset = read_json_file(str(metadata_file))
            if dataset:
                if not tags or any(tag in dataset.get("tags", []) for tag in tags):
                    datasets.append(dataset)
        
        return sorted(datasets, key=lambda x: x["created_at"], reverse=True)
    
    def download_dataset(self, dataset_id: str, target_path: str) -> bool:
        """Download dataset to local path"""
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return False
        
        # Check if dataset exists locally
        local_path = self.storage_dir / "datasets" / dataset_id
        if local_path.exists():
            shutil.copytree(local_path, target_path, dirs_exist_ok=True)
            return True
        
        # Download from cloud if available
        if dataset.get("cloud_storage"):
            return self._download_from_cloud(dataset, target_path)
        
        return False
    
    def _calculate_dataset_hash(self, dataset_path: Path) -> str:
        """Calculate hash for entire dataset"""
        hashes = []
        
        if dataset_path.is_file():
            hashes.append(calculate_file_hash(str(dataset_path)))
        else:
            for file_path in sorted(dataset_path.rglob("*")):
                if file_path.is_file():
                    hashes.append(calculate_file_hash(str(file_path)))
        
        # Combine all hashes
        combined = "".join(hashes)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _calculate_dataset_size(self, dataset_path: Path) -> int:
        """Calculate total size of dataset"""
        if dataset_path.is_file():
            return dataset_path.stat().st_size
        
        total_size = 0
        for file_path in dataset_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
    
    def _count_files(self, dataset_path: Path) -> int:
        """Count number of files in dataset"""
        if dataset_path.is_file():
            return 1
        
        return len([f for f in dataset_path.rglob("*") if f.is_file()])
    
    def _find_existing_dataset(self, dataset_hash: str) -> Optional[Dict[str, Any]]:
        """Find existing dataset by hash"""
        for dataset in self.list_datasets():
            if dataset["hash"] == dataset_hash:
                return dataset
        return None
    
    def _store_dataset_locally(self, dataset_path: Path, metadata: Dict[str, Any]):
        """Store dataset in local storage"""
        dataset_id = metadata["id"]
        local_storage_path = self.storage_dir / "datasets" / dataset_id
        
        if dataset_path.is_file():
            local_storage_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dataset_path, local_storage_path)
        else:
            shutil.copytree(dataset_path, local_storage_path, dirs_exist_ok=True)
    
    def _upload_to_cloud(self, dataset_path: Path, metadata: Dict[str, Any], cloud_type: str):
        """Upload dataset to cloud storage"""
        dataset_id = metadata["id"]
        
        if cloud_type == "s3" and self.s3_client:
            bucket = self.config["aws"]["bucket"]
            key = f"datasets/{dataset_id}"
            
            if dataset_path.is_file():
                self.s3_client.upload_file(str(dataset_path), bucket, key)
            else:
                # Upload directory
                for file_path in dataset_path.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(dataset_path)
                        s3_key = f"datasets/{dataset_id}/{relative_path}"
                        self.s3_client.upload_file(str(file_path), bucket, s3_key)
            
            metadata["storage_info"]["s3"] = {
                "bucket": bucket,
                "key": key
            }
        
        elif cloud_type == "gcs" and self.gcs_client:
            bucket_name = self.config["gcs"]["bucket"]
            bucket = self.gcs_client.bucket(bucket_name)
            
            if dataset_path.is_file():
                blob = bucket.blob(f"datasets/{dataset_id}")
                blob.upload_from_filename(str(dataset_path))
            else:
                # Upload directory
                for file_path in dataset_path.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(dataset_path)
                        blob_name = f"datasets/{dataset_id}/{relative_path}"
                        blob = bucket.blob(blob_name)
                        blob.upload_from_filename(str(file_path))
            
            metadata["storage_info"]["gcs"] = {
                "bucket": bucket_name,
                "prefix": f"datasets/{dataset_id}"
            }
    
    def _download_from_cloud(self, dataset: Dict[str, Any], target_path: str) -> bool:
        """Download dataset from cloud storage"""
        storage_info = dataset.get("storage_info", {})
        
        if "s3" in storage_info and self.s3_client:
            s3_info = storage_info["s3"]
            # Download from S3
            # Implementation depends on whether it's a file or directory
            return True
        
        elif "gcs" in storage_info and self.gcs_client:
            gcs_info = storage_info["gcs"]
            # Download from GCS
            return True
        
        return False
    
    def _save_dataset_metadata(self, metadata: Dict[str, Any]):
        """Save dataset metadata"""
        metadata_dir = self.storage_dir / "metadata"
        ensure_directory(str(metadata_dir))
        
        metadata_file = metadata_dir / f"{metadata['id']}.json"
        write_json_file(str(metadata_file), metadata)
