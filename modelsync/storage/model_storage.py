"""
Model storage and versioning for ModelSync
"""

import os
import json
import shutil
import pickle
import joblib
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import torch
import tensorflow as tf
from modelsync.utils.helpers import calculate_file_hash, ensure_directory, write_json_file, read_json_file

class ModelStorage:
    """Manages model storage and versioning with automatic checkpoints"""
    
    def __init__(self, repo_path: str = ".", config: Optional[Dict] = None):
        self.repo_path = Path(repo_path)
        self.storage_dir = self.repo_path / ".modelsync" / "storage" / "models"
        self.checkpoints_dir = self.storage_dir / "checkpoints"
        self.config = config or {}
        self._setup_directories()
    
    def _setup_directories(self):
        """Setup storage directories"""
        for dir_path in [self.storage_dir, self.checkpoints_dir]:
            ensure_directory(str(dir_path))
    
    def add_model(
        self,
        model_path: str,
        model_name: str,
        framework: str,
        metrics: Dict[str, float],
        hyperparameters: Dict[str, Any],
        training_info: Dict[str, Any],
        auto_checkpoint: bool = True,
        checkpoint_interval: int = 10
    ) -> Dict[str, Any]:
        """Add a model to version control with automatic checkpointing"""
        
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Calculate model hash
        model_hash = calculate_file_hash(str(model_path))
        
        # Create model metadata
        model_metadata = {
            "id": model_hash[:16],
            "name": model_name,
            "framework": framework,
            "path": str(model_path),
            "hash": model_hash,
            "size": model_path.stat().st_size,
            "metrics": metrics,
            "hyperparameters": hyperparameters,
            "training_info": training_info,
            "created_at": datetime.now().isoformat(),
            "checkpoints": [],
            "auto_checkpoint": auto_checkpoint,
            "checkpoint_interval": checkpoint_interval
        }
        
        # Store model
        self._store_model(model_path, model_metadata)
        
        # Create initial checkpoint if auto_checkpoint is enabled
        if auto_checkpoint:
            self._create_checkpoint(model_metadata, "initial")
        
        # Save metadata
        self._save_model_metadata(model_metadata)
        
        print(f"✅ Model added: {model_name} ({model_hash[:8]})")
        return model_metadata
    
    def create_checkpoint(
        self,
        model_id: str,
        checkpoint_name: str,
        metrics: Optional[Dict[str, float]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a checkpoint for a model"""
        
        model = self.get_model(model_id)
        if not model:
            print(f"❌ Model not found: {model_id}")
            return None
        
        checkpoint_data = {
            "id": f"{model_id}_{checkpoint_name}",
            "model_id": model_id,
            "name": checkpoint_name,
            "created_at": datetime.now().isoformat(),
            "metrics": metrics or model.get("metrics", {}),
            "path": ""
        }
        
        # Copy model to checkpoint directory
        checkpoint_path = self.checkpoints_dir / model_id / checkpoint_name
        ensure_directory(str(checkpoint_path))
        
        model_path = Path(model["path"])
        if model_path.is_file():
            shutil.copy2(model_path, checkpoint_path / model_path.name)
            checkpoint_data["path"] = str(checkpoint_path / model_path.name)
        else:
            shutil.copytree(model_path, checkpoint_path, dirs_exist_ok=True)
            checkpoint_data["path"] = str(checkpoint_path)
        
        # Add checkpoint to model metadata
        model["checkpoints"].append(checkpoint_data)
        self._save_model_metadata(model)
        
        print(f"✅ Checkpoint created: {checkpoint_name} for {model['name']}")
        return checkpoint_data
    
    def rollback_to_checkpoint(
        self,
        model_id: str,
        checkpoint_name: str
    ) -> bool:
        """Rollback model to a specific checkpoint"""
        
        model = self.get_model(model_id)
        if not model:
            print(f"❌ Model not found: {model_id}")
            return False
        
        # Find checkpoint
        checkpoint = None
        for cp in model["checkpoints"]:
            if cp["name"] == checkpoint_name:
                checkpoint = cp
                break
        
        if not checkpoint:
            print(f"❌ Checkpoint not found: {checkpoint_name}")
            return False
        
        # Restore model from checkpoint
        checkpoint_path = Path(checkpoint["path"])
        model_path = Path(model["path"])
        
        if checkpoint_path.is_file():
            shutil.copy2(checkpoint_path, model_path)
        else:
            if model_path.exists():
                shutil.rmtree(model_path)
            shutil.copytree(checkpoint_path, model_path)
        
        print(f"✅ Model rolled back to checkpoint: {checkpoint_name}")
        return True
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model metadata by ID"""
        metadata_file = self.storage_dir / "metadata" / f"{model_id}.json"
        if metadata_file.exists():
            return read_json_file(str(metadata_file))
        return None
    
    def list_models(self, framework: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all models, optionally filtered by framework"""
        models = []
        metadata_dir = self.storage_dir / "metadata"
        
        if not metadata_dir.exists():
            return models
        
        for metadata_file in metadata_dir.glob("*.json"):
            model = read_json_file(str(metadata_file))
            if model and (not framework or model.get("framework") == framework):
                models.append(model)
        
        return sorted(models, key=lambda x: x["created_at"], reverse=True)
    
    def compare_models(self, model_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple models by metrics"""
        models = [self.get_model(mid) for mid in model_ids if self.get_model(mid)]
        
        if len(models) < 2:
            return {"error": "Need at least 2 models to compare"}
        
        comparison = {
            "models": [{"id": m["id"], "name": m["name"]} for m in models],
            "metrics_comparison": {},
            "best_model": None
        }
        
        # Compare metrics
        all_metrics = set()
        for model in models:
            all_metrics.update(model.get("metrics", {}).keys())
        
        for metric in all_metrics:
            values = []
            for model in models:
                value = model.get("metrics", {}).get(metric, 0)
                values.append(value)
            
            comparison["metrics_comparison"][metric] = {
                "values": values,
                "best": max(values) if values else 0,
                "worst": min(values) if values else 0,
                "average": sum(values) / len(values) if values else 0
            }
        
        # Find best model (highest average score)
        best_score = -1
        for i, model in enumerate(models):
            avg_score = sum(model.get("metrics", {}).values()) / len(model.get("metrics", {})) if model.get("metrics") else 0
            if avg_score > best_score:
                best_score = avg_score
                comparison["best_model"] = model["id"]
        
        return comparison
    
    def _store_model(self, model_path: Path, metadata: Dict[str, Any]):
        """Store model in storage directory"""
        model_id = metadata["id"]
        storage_path = self.storage_dir / "models" / model_id
        
        if model_path.is_file():
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(model_path, storage_path)
        else:
            shutil.copytree(model_path, storage_path, dirs_exist_ok=True)
    
    def _create_checkpoint(self, model_metadata: Dict[str, Any], checkpoint_name: str):
        """Create automatic checkpoint"""
        self.create_checkpoint(
            model_metadata["id"],
            checkpoint_name,
            model_metadata.get("metrics", {})
        )
    
    def _save_model_metadata(self, metadata: Dict[str, Any]):
        """Save model metadata"""
        metadata_dir = self.storage_dir / "metadata"
        ensure_directory(str(metadata_dir))
        
        metadata_file = metadata_dir / f"{metadata['id']}.json"
        write_json_file(str(metadata_file), metadata)
    
    def load_model(self, model_id: str, framework: str) -> Any:
        """Load model object based on framework"""
        model = self.get_model(model_id)
        if not model:
            return None
        
        model_path = Path(model["path"])
        
        if framework == "pytorch":
            return torch.load(model_path)
        elif framework == "tensorflow":
            return tf.keras.models.load_model(model_path)
        elif framework == "sklearn":
            return joblib.load(model_path)
        elif framework == "pickle":
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
