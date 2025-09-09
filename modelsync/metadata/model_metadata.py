"""
Model metadata management for ModelSync
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from modelsync.utils.helpers import write_json_file, read_json_file, calculate_file_hash

class ModelMetadata:
    """Manages metadata for ML models"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.metadata_dir = self.repo_path / METADATA_DIR / "models"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    def create_model_metadata(
        self,
        model_path: str,
        model_type: str,
        framework: str,
        accuracy: Optional[float] = None,
        loss: Optional[float] = None,
        metrics: Optional[Dict[str, float]] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        dataset_info: Optional[Dict[str, Any]] = None,
        training_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create metadata for a model"""
        
        # Get file information
        file_info = self._get_file_info(model_path)
        
        metadata = {
            "model_id": file_info["hash"][:16],  # Short ID
            "file_path": model_path,
            "file_info": file_info,
            "model_type": model_type,
            "framework": framework,
            "performance": {
                "accuracy": accuracy,
                "loss": loss,
                "metrics": metrics or {}
            },
            "hyperparameters": hyperparameters or {},
            "dataset_info": dataset_info or {},
            "training_info": training_info or {},
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # Save metadata
        metadata_file = self.metadata_dir / f"{metadata['model_id']}.json"
        write_json_file(str(metadata_file), metadata)
        
        return metadata
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific model"""
        metadata_file = self.metadata_dir / f"{model_id}.json"
        if metadata_file.exists():
            return read_json_file(str(metadata_file))
        return None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all models with their metadata"""
        models = []
        for metadata_file in self.metadata_dir.glob("*.json"):
            metadata = read_json_file(str(metadata_file))
            if metadata:
                models.append({
                    "model_id": metadata.get("model_id"),
                    "file_path": metadata.get("file_path"),
                    "model_type": metadata.get("model_type"),
                    "framework": metadata.get("framework"),
                    "accuracy": metadata.get("performance", {}).get("accuracy"),
                    "created_at": metadata.get("created_at")
                })
        return sorted(models, key=lambda x: x["created_at"], reverse=True)
    
    def update_model_metadata(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """Update metadata for a model"""
        metadata = self.get_model_metadata(model_id)
        if not metadata:
            return False
        
        # Update fields
        for key, value in updates.items():
            if key in ["performance", "hyperparameters", "dataset_info", "training_info"]:
                if key not in metadata:
                    metadata[key] = {}
                metadata[key].update(value)
            else:
                metadata[key] = value
        
        metadata["updated_at"] = datetime.now().isoformat()
        
        # Save updated metadata
        metadata_file = self.metadata_dir / f"{model_id}.json"
        write_json_file(str(metadata_file), metadata)
        return True
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information for model"""
        full_path = self.repo_path / file_path
        if not full_path.exists():
            return {}
        
        stat = full_path.stat()
        return {
            "path": str(full_path),
            "name": full_path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "hash": calculate_file_hash(str(full_path)),
            "extension": full_path.suffix
        }

class DatasetMetadata:
    """Manages metadata for datasets"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.metadata_dir = self.repo_path / METADATA_DIR / "datasets"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    def create_dataset_metadata(
        self,
        dataset_path: str,
        dataset_name: str,
        description: str = "",
        data_type: str = "tabular",  # tabular, image, text, audio, etc.
        size: Optional[int] = None,
        features: Optional[List[str]] = None,
        target_column: Optional[str] = None,
        data_schema: Optional[Dict[str, Any]] = None,
        source_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create metadata for a dataset"""
        
        # Get file information
        file_info = self._get_file_info(dataset_path)
        
        metadata = {
            "dataset_id": file_info["hash"][:16],  # Short ID
            "dataset_name": dataset_name,
            "file_path": dataset_path,
            "file_info": file_info,
            "description": description,
            "data_type": data_type,
            "size": size,
            "features": features or [],
            "target_column": target_column,
            "data_schema": data_schema or {},
            "source_info": source_info or {},
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        # Save metadata
        metadata_file = self.metadata_dir / f"{metadata['dataset_id']}.json"
        write_json_file(str(metadata_file), metadata)
        
        return metadata
    
    def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific dataset"""
        metadata_file = self.metadata_dir / f"{dataset_id}.json"
        if metadata_file.exists():
            return read_json_file(str(metadata_file))
        return None
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets with their metadata"""
        datasets = []
        for metadata_file in self.metadata_dir.glob("*.json"):
            metadata = read_json_file(str(metadata_file))
            if metadata:
                datasets.append({
                    "dataset_id": metadata.get("dataset_id"),
                    "dataset_name": metadata.get("dataset_name"),
                    "file_path": metadata.get("file_path"),
                    "data_type": metadata.get("data_type"),
                    "size": metadata.get("size"),
                    "created_at": metadata.get("created_at")
                })
        return sorted(datasets, key=lambda x: x["created_at"], reverse=True)
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information for dataset"""
        full_path = self.repo_path / file_path
        if not full_path.exists():
            return {}
        
        stat = full_path.stat()
        return {
            "path": str(full_path),
            "name": full_path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "hash": calculate_file_hash(str(full_path)),
            "extension": full_path.suffix
        }
