"""
Experiment branching and comparison for ModelSync
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from modelsync.utils.helpers import ensure_directory, write_json_file, read_json_file

class ExperimentBranch:
    """Represents an experiment branch"""
    
    def __init__(self, name: str, base_branch: Optional[str] = None, repo_path: str = "."):
        self.name = name
        self.base_branch = base_branch
        self.repo_path = Path(repo_path)
        self.branch_dir = self.repo_path / ".modelsync" / "branches" / name
        self.experiments_dir = self.branch_dir / "experiments"
        self.metrics_file = self.branch_dir / "metrics.json"
        self._setup_branch()
    
    def _setup_branch(self):
        """Setup branch directory structure"""
        ensure_directory(str(self.branch_dir))
        ensure_directory(str(self.experiments_dir))
        
        if not self.metrics_file.exists():
            write_json_file(str(self.metrics_file), {
                "branch_name": self.name,
                "base_branch": self.base_branch,
                "created_at": datetime.now().isoformat(),
                "experiments": [],
                "best_metrics": {},
                "status": "active"
            })
    
    def add_experiment(
        self,
        experiment_name: str,
        model_id: str,
        dataset_id: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, float],
        description: str = ""
    ) -> Dict[str, Any]:
        """Add an experiment to this branch"""
        
        experiment_data = {
            "id": f"{self.name}_{experiment_name}",
            "name": experiment_name,
            "branch": self.name,
            "model_id": model_id,
            "dataset_id": dataset_id,
            "hyperparameters": hyperparameters,
            "metrics": metrics,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Save experiment data
        experiment_file = self.experiments_dir / f"{experiment_name}.json"
        write_json_file(str(experiment_file), experiment_data)
        
        # Update branch metrics
        self._update_branch_metrics(experiment_data)
        
        print(f"✅ Experiment added to branch '{self.name}': {experiment_name}")
        return experiment_data
    
    def _update_branch_metrics(self, experiment: Dict[str, Any]):
        """Update branch-level metrics"""
        branch_data = read_json_file(str(self.metrics_file))
        branch_data["experiments"].append(experiment["id"])
        
        # Update best metrics
        for metric, value in experiment["metrics"].items():
            if metric not in branch_data["best_metrics"]:
                branch_data["best_metrics"][metric] = value
            else:
                # Keep the best value (assuming higher is better)
                if value > branch_data["best_metrics"][metric]:
                    branch_data["best_metrics"][metric] = value
        
        write_json_file(str(self.metrics_file), branch_data)
    
    def get_experiments(self) -> List[Dict[str, Any]]:
        """Get all experiments in this branch"""
        experiments = []
        
        for experiment_file in self.experiments_dir.glob("*.json"):
            experiment = read_json_file(str(experiment_file))
            if experiment:
                experiments.append(experiment)
        
        return sorted(experiments, key=lambda x: x["created_at"], reverse=True)
    
    def get_best_experiment(self, metric: str) -> Optional[Dict[str, Any]]:
        """Get the best experiment for a specific metric"""
        experiments = self.get_experiments()
        if not experiments:
            return None
        
        best_experiment = None
        best_value = float('-inf')
        
        for experiment in experiments:
            value = experiment.get("metrics", {}).get(metric, float('-inf'))
            if value > best_value:
                best_value = value
                best_experiment = experiment
        
        return best_experiment
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics in this branch"""
        experiments = self.get_experiments()
        if not experiments:
            return {}
        
        all_metrics = set()
        for experiment in experiments:
            all_metrics.update(experiment.get("metrics", {}).keys())
        
        summary = {}
        for metric in all_metrics:
            values = [exp.get("metrics", {}).get(metric, 0) for exp in experiments]
            summary[metric] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "std": self._calculate_std(values)
            }
        
        return summary
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

class ExperimentManager:
    """Manages experiment branches and comparisons"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.branches_dir = self.repo_path / ".modelsync" / "branches"
        ensure_directory(str(self.branches_dir))
    
    def create_branch(self, name: str, base_branch: Optional[str] = None) -> ExperimentBranch:
        """Create a new experiment branch"""
        if self.branch_exists(name):
            raise ValueError(f"Branch '{name}' already exists")
        
        branch = ExperimentBranch(name, base_branch, str(self.repo_path))
        print(f"✅ Created experiment branch: {name}")
        return branch
    
    def get_branch(self, name: str) -> Optional[ExperimentBranch]:
        """Get an existing branch"""
        if not self.branch_exists(name):
            return None
        
        return ExperimentBranch(name, repo_path=str(self.repo_path))
    
    def branch_exists(self, name: str) -> bool:
        """Check if branch exists"""
        return (self.branches_dir / name).exists()
    
    def list_branches(self) -> List[str]:
        """List all experiment branches"""
        if not self.branches_dir.exists():
            return []
        
        return [d.name for d in self.branches_dir.iterdir() if d.is_dir()]
    
    def compare_branches(self, branch_names: List[str], metric: str) -> Dict[str, Any]:
        """Compare multiple branches by a specific metric"""
        branches = [self.get_branch(name) for name in branch_names if self.get_branch(name)]
        
        if len(branches) < 2:
            return {"error": "Need at least 2 branches to compare"}
        
        comparison = {
            "metric": metric,
            "branches": [],
            "best_branch": None,
            "worst_branch": None
        }
        
        best_value = float('-inf')
        worst_value = float('inf')
        
        for branch in branches:
            experiments = branch.get_experiments()
            if not experiments:
                continue
            
            # Calculate average metric value for this branch
            values = [exp.get("metrics", {}).get(metric, 0) for exp in experiments]
            avg_value = sum(values) / len(values) if values else 0
            
            branch_data = {
                "name": branch.name,
                "experiment_count": len(experiments),
                "avg_metric_value": avg_value,
                "best_experiment": branch.get_best_experiment(metric)
            }
            
            comparison["branches"].append(branch_data)
            
            if avg_value > best_value:
                best_value = avg_value
                comparison["best_branch"] = branch.name
            
            if avg_value < worst_value:
                worst_value = avg_value
                comparison["worst_branch"] = branch.name
        
        return comparison
    
    def merge_branch(
        self,
        source_branch: str,
        target_branch: str,
        merge_strategy: str = "best_experiment"
    ) -> bool:
        """Merge experiment branch into another branch"""
        
        source = self.get_branch(source_branch)
        target = self.get_branch(target_branch)
        
        if not source or not target:
            print("❌ Source or target branch not found")
            return False
        
        if merge_strategy == "best_experiment":
            # Find best experiment in source branch
            experiments = source.get_experiments()
            if not experiments:
                print("❌ No experiments in source branch")
                return False
            
            # Get best experiment by average score
            best_experiment = None
            best_score = float('-inf')
            
            for experiment in experiments:
                avg_score = sum(experiment.get("metrics", {}).values()) / len(experiment.get("metrics", {})) if experiment.get("metrics") else 0
                if avg_score > best_score:
                    best_score = avg_score
                    best_experiment = experiment
            
            if best_experiment:
                # Add best experiment to target branch
                target.add_experiment(
                    f"{best_experiment['name']}_merged",
                    best_experiment["model_id"],
                    best_experiment["dataset_id"],
                    best_experiment["hyperparameters"],
                    best_experiment["metrics"],
                    f"Merged from {source_branch}: {best_experiment['description']}"
                )
        
        print(f"✅ Merged branch '{source_branch}' into '{target_branch}'")
        return True
    
    def delete_branch(self, name: str) -> bool:
        """Delete an experiment branch"""
        if not self.branch_exists(name):
            print(f"❌ Branch '{name}' not found")
            return False
        
        shutil.rmtree(self.branches_dir / name)
        print(f"✅ Deleted branch: {name}")
        return True
