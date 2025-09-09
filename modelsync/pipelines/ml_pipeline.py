"""
ML Pipeline integration for ModelSync
"""

import json
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
import pandas as pd
import numpy as np
from modelsync.utils.helpers import ensure_directory, write_json_file, read_json_file

# ML Framework imports
try:
    import sklearn
    from sklearn.pipeline import Pipeline as SklearnPipeline
    from sklearn.base import BaseEstimator, TransformerMixin
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

class PipelineStep:
    """Represents a single step in an ML pipeline"""
    
    def __init__(
        self,
        name: str,
        step_type: str,
        function: Callable,
        parameters: Dict[str, Any],
        framework: str = "custom"
    ):
        self.name = name
        self.step_type = step_type  # data_preprocessing, feature_engineering, model_training, evaluation
        self.function = function
        self.parameters = parameters
        self.framework = framework
        self.created_at = datetime.now().isoformat()
    
    def execute(self, data: Any, context: Dict[str, Any] = None) -> Any:
        """Execute this pipeline step"""
        try:
            # Prepare parameters
            params = self.parameters.copy()
            if context:
                params.update(context)
            
            # Execute function
            if self.framework == "sklearn" and SKLEARN_AVAILABLE:
                return self._execute_sklearn_step(data, params)
            elif self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
                return self._execute_tensorflow_step(data, params)
            elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
                return self._execute_pytorch_step(data, params)
            else:
                return self._execute_custom_step(data, params)
        
        except Exception as e:
            print(f"❌ Error executing step '{self.name}': {e}")
            raise
    
    def _execute_sklearn_step(self, data: Any, params: Dict[str, Any]) -> Any:
        """Execute sklearn pipeline step"""
        if hasattr(self.function, 'fit'):
            # It's a transformer/estimator
            if hasattr(self.function, 'transform'):
                # Transformer
                if not hasattr(self.function, 'fitted_'):
                    self.function.fit(data)
                return self.function.transform(data)
            else:
                # Estimator
                return self.function.fit(data, **params)
        else:
            # Regular function
            return self.function(data, **params)
    
    def _execute_tensorflow_step(self, data: Any, params: Dict[str, Any]) -> Any:
        """Execute TensorFlow pipeline step"""
        return self.function(data, **params)
    
    def _execute_pytorch_step(self, data: Any, params: Dict[str, Any]) -> Any:
        """Execute PyTorch pipeline step"""
        return self.function(data, **params)
    
    def _execute_custom_step(self, data: Any, params: Dict[str, Any]) -> Any:
        """Execute custom pipeline step"""
        return self.function(data, **params)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary for serialization"""
        return {
            "name": self.name,
            "step_type": self.step_type,
            "framework": self.framework,
            "parameters": self.parameters,
            "created_at": self.created_at,
            "function_name": self.function.__name__ if hasattr(self.function, '__name__') else str(self.function)
        }

class MLPipeline:
    """ML Pipeline with versioning support"""
    
    def __init__(self, name: str, repo_path: str = "."):
        self.name = name
        self.repo_path = Path(repo_path)
        self.pipeline_dir = self.repo_path / ".modelsync" / "pipelines" / name
        self.steps: List[PipelineStep] = []
        self.metadata = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "steps": [],
            "executions": [],
            "version": "1.0.0"
        }
        self._setup_pipeline()
    
    def _setup_pipeline(self):
        """Setup pipeline directory"""
        ensure_directory(str(self.pipeline_dir))
        self._load_metadata()
    
    def _load_metadata(self):
        """Load pipeline metadata"""
        metadata_file = self.pipeline_dir / "metadata.json"
        if metadata_file.exists():
            self.metadata = read_json_file(str(metadata_file))
            self._load_steps()
    
    def _load_steps(self):
        """Load pipeline steps from metadata"""
        self.steps = []
        for step_data in self.metadata.get("steps", []):
            # Note: In a real implementation, you'd need to reconstruct the function
            # This is a simplified version
            step = PipelineStep(
                name=step_data["name"],
                step_type=step_data["step_type"],
                function=None,  # Would need to be reconstructed
                parameters=step_data["parameters"],
                framework=step_data["framework"]
            )
            step.created_at = step_data["created_at"]
            self.steps.append(step)
    
    def add_step(
        self,
        name: str,
        step_type: str,
        function: Callable,
        parameters: Dict[str, Any] = None,
        framework: str = "custom"
    ) -> 'MLPipeline':
        """Add a step to the pipeline"""
        
        step = PipelineStep(
            name=name,
            step_type=step_type,
            function=function,
            parameters=parameters or {},
            framework=framework
        )
        
        self.steps.append(step)
        self.metadata["steps"].append(step.to_dict())
        self._save_metadata()
        
        print(f"✅ Added step '{name}' to pipeline '{self.name}'")
        return self
    
    def execute(
        self,
        data: Any,
        context: Dict[str, Any] = None,
        save_results: bool = True
    ) -> Any:
        """Execute the entire pipeline"""
        
        execution_id = f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        execution_data = {
            "id": execution_id,
            "pipeline_name": self.name,
            "started_at": datetime.now().isoformat(),
            "steps_executed": [],
            "results": {},
            "status": "running"
        }
        
        try:
            current_data = data
            context = context or {}
            
            for i, step in enumerate(self.steps):
                print(f"🔄 Executing step {i+1}/{len(self.steps)}: {step.name}")
                
                step_start = datetime.now()
                current_data = step.execute(current_data, context)
                step_end = datetime.now()
                
                execution_data["steps_executed"].append({
                    "step_name": step.name,
                    "step_type": step.step_type,
                    "started_at": step_start.isoformat(),
                    "completed_at": step_end.isoformat(),
                    "duration_seconds": (step_end - step_start).total_seconds()
                })
            
            execution_data["status"] = "completed"
            execution_data["completed_at"] = datetime.now().isoformat()
            execution_data["results"]["final_output"] = str(type(current_data))
            
            if save_results:
                self._save_execution(execution_data)
            
            print(f"✅ Pipeline '{self.name}' executed successfully")
            return current_data
        
        except Exception as e:
            execution_data["status"] = "failed"
            execution_data["error"] = str(e)
            execution_data["failed_at"] = datetime.now().isoformat()
            
            if save_results:
                self._save_execution(execution_data)
            
            print(f"❌ Pipeline '{self.name}' failed: {e}")
            raise
    
    def get_step(self, name: str) -> Optional[PipelineStep]:
        """Get a specific step by name"""
        for step in self.steps:
            if step.name == name:
                return step
        return None
    
    def remove_step(self, name: str) -> bool:
        """Remove a step from the pipeline"""
        for i, step in enumerate(self.steps):
            if step.name == name:
                del self.steps[i]
                self.metadata["steps"] = [s for s in self.metadata["steps"] if s["name"] != name]
                self._save_metadata()
                print(f"✅ Removed step '{name}' from pipeline '{self.name}'")
                return True
        
        print(f"❌ Step '{name}' not found in pipeline '{self.name}'")
        return False
    
    def get_executions(self) -> List[Dict[str, Any]]:
        """Get all pipeline executions"""
        executions_dir = self.pipeline_dir / "executions"
        if not executions_dir.exists():
            return []
        
        executions = []
        for execution_file in executions_dir.glob("*.json"):
            execution = read_json_file(str(execution_file))
            if execution:
                executions.append(execution)
        
        return sorted(executions, key=lambda x: x["started_at"], reverse=True)
    
    def _save_metadata(self):
        """Save pipeline metadata"""
        metadata_file = self.pipeline_dir / "metadata.json"
        write_json_file(str(metadata_file), self.metadata)
    
    def _save_execution(self, execution_data: Dict[str, Any]):
        """Save execution data"""
        executions_dir = self.pipeline_dir / "executions"
        ensure_directory(str(executions_dir))
        
        execution_file = executions_dir / f"{execution_data['id']}.json"
        write_json_file(str(execution_file), execution_data)
        
        # Update pipeline metadata
        self.metadata["executions"].append(execution_data["id"])
        self._save_metadata()

class PipelineManager:
    """Manages ML pipelines"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.pipelines_dir = self.repo_path / ".modelsync" / "pipelines"
        ensure_directory(str(self.pipelines_dir))
    
    def create_pipeline(self, name: str) -> MLPipeline:
        """Create a new ML pipeline"""
        if self.pipeline_exists(name):
            raise ValueError(f"Pipeline '{name}' already exists")
        
        pipeline = MLPipeline(name, str(self.repo_path))
        print(f"✅ Created pipeline: {name}")
        return pipeline
    
    def get_pipeline(self, name: str) -> Optional[MLPipeline]:
        """Get an existing pipeline"""
        if not self.pipeline_exists(name):
            return None
        
        return MLPipeline(name, str(self.repo_path))
    
    def pipeline_exists(self, name: str) -> bool:
        """Check if pipeline exists"""
        return (self.pipelines_dir / name).exists()
    
    def list_pipelines(self) -> List[str]:
        """List all pipelines"""
        if not self.pipelines_dir.exists():
            return []
        
        return [d.name for d in self.pipelines_dir.iterdir() if d.is_dir()]
    
    def delete_pipeline(self, name: str) -> bool:
        """Delete a pipeline"""
        if not self.pipeline_exists(name):
            print(f"❌ Pipeline '{name}' not found")
            return False
        
        import shutil
        shutil.rmtree(self.pipelines_dir / name)
        print(f"✅ Deleted pipeline: {name}")
        return True
