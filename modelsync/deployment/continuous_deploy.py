"""
Continuous deployment based on metrics for ModelSync
"""

import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from modelsync.utils.helpers import ensure_directory, write_json_file, read_json_file

class DeploymentRule:
    """Represents a deployment rule based on metrics"""
    
    def __init__(
        self,
        name: str,
        branch: str,
        metric_name: str,
        threshold: float,
        operator: str,  # "greater_than", "less_than", "equals"
        deployment_target: str,
        deployment_config: Dict[str, Any]
    ):
        self.name = name
        self.branch = branch
        self.metric_name = metric_name
        self.threshold = threshold
        self.operator = operator
        self.deployment_target = deployment_target
        self.deployment_config = deployment_config
        self.created_at = datetime.now().isoformat()
        self.last_checked = None
        self.triggered_count = 0
    
    def check_condition(self, metrics: Dict[str, float]) -> bool:
        """Check if deployment condition is met"""
        if self.metric_name not in metrics:
            return False
        
        value = metrics[self.metric_name]
        
        if self.operator == "greater_than":
            return value > self.threshold
        elif self.operator == "less_than":
            return value < self.threshold
        elif self.operator == "equals":
            return abs(value - self.threshold) < 0.001
        elif self.operator == "greater_equal":
            return value >= self.threshold
        elif self.operator == "less_equal":
            return value <= self.threshold
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary"""
        return {
            "name": self.name,
            "branch": self.branch,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "operator": self.operator,
            "deployment_target": self.deployment_target,
            "deployment_config": self.deployment_config,
            "created_at": self.created_at,
            "last_checked": self.last_checked,
            "triggered_count": self.triggered_count
        }

class DeploymentManager:
    """Manages continuous deployment based on metrics"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.deploy_dir = self.repo_path / ".modelsync" / "deployment"
        self.rules_file = self.deploy_dir / "rules.json"
        self.deployments_file = self.deploy_dir / "deployments.json"
        self.rules: List[DeploymentRule] = []
        self.deployments: List[Dict[str, Any]] = []
        ensure_directory(str(self.deploy_dir))
        self._load_data()
    
    def _load_data(self):
        """Load deployment data"""
        rules_data = read_json_file(str(self.rules_file)) or []
        self.rules = [self._rule_from_dict(rule) for rule in rules_data]
        
        self.deployments = read_json_file(str(self.deployments_file)) or []
    
    def _save_data(self):
        """Save deployment data"""
        rules_data = [rule.to_dict() for rule in self.rules]
        write_json_file(str(self.rules_file), rules_data)
        write_json_file(str(self.deployments_file), self.deployments)
    
    def _rule_from_dict(self, rule_data: Dict[str, Any]) -> DeploymentRule:
        """Create rule from dictionary"""
        rule = DeploymentRule(
            name=rule_data["name"],
            branch=rule_data["branch"],
            metric_name=rule_data["metric_name"],
            threshold=rule_data["threshold"],
            operator=rule_data["operator"],
            deployment_target=rule_data["deployment_target"],
            deployment_config=rule_data["deployment_config"]
        )
        rule.created_at = rule_data.get("created_at", rule.created_at)
        rule.last_checked = rule_data.get("last_checked")
        rule.triggered_count = rule_data.get("triggered_count", 0)
        return rule
    
    def add_deployment_rule(
        self,
        name: str,
        branch: str,
        metric_name: str,
        threshold: float,
        operator: str,
        deployment_target: str,
        deployment_config: Dict[str, Any]
    ) -> bool:
        """Add a new deployment rule"""
        
        # Check if rule name already exists
        if any(rule.name == name for rule in self.rules):
            print(f"❌ Rule '{name}' already exists")
            return False
        
        rule = DeploymentRule(
            name=name,
            branch=branch,
            metric_name=metric_name,
            threshold=threshold,
            operator=operator,
            deployment_target=deployment_target,
            deployment_config=deployment_config
        )
        
        self.rules.append(rule)
        self._save_data()
        
        print(f"✅ Added deployment rule: {name}")
        return True
    
    def check_deployment_rules(
        self,
        branch: str,
        metrics: Dict[str, float],
        model_id: str = None
    ) -> List[Dict[str, Any]]:
        """Check all deployment rules for a branch"""
        
        triggered_rules = []
        
        for rule in self.rules:
            if rule.branch != branch:
                continue
            
            if rule.check_condition(metrics):
                print(f"🚀 Deployment rule triggered: {rule.name}")
                
                # Update rule stats
                rule.last_checked = datetime.now().isoformat()
                rule.triggered_count += 1
                
                # Execute deployment
                deployment_result = self._execute_deployment(rule, metrics, model_id)
                
                triggered_rules.append({
                    "rule_name": rule.name,
                    "branch": branch,
                    "metrics": metrics,
                    "model_id": model_id,
                    "deployment_result": deployment_result,
                    "triggered_at": datetime.now().isoformat()
                })
        
        if triggered_rules:
            self._save_data()
        
        return triggered_rules
    
    def _execute_deployment(
        self,
        rule: DeploymentRule,
        metrics: Dict[str, float],
        model_id: str = None
    ) -> Dict[str, Any]:
        """Execute deployment based on rule"""
        
        deployment_id = f"{rule.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        deployment_data = {
            "id": deployment_id,
            "rule_name": rule.name,
            "branch": rule.branch,
            "model_id": model_id,
            "metrics": metrics,
            "deployment_target": rule.deployment_target,
            "config": rule.deployment_config,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }
        
        try:
            if rule.deployment_target == "docker":
                result = self._deploy_docker(deployment_data)
            elif rule.deployment_target == "kubernetes":
                result = self._deploy_kubernetes(deployment_data)
            elif rule.deployment_target == "api_endpoint":
                result = self._deploy_api_endpoint(deployment_data)
            elif rule.deployment_target == "mlflow":
                result = self._deploy_mlflow(deployment_data)
            else:
                result = {"status": "error", "message": f"Unknown deployment target: {rule.deployment_target}"}
            
            deployment_data.update(result)
            deployment_data["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            deployment_data["status"] = "failed"
            deployment_data["error"] = str(e)
            deployment_data["failed_at"] = datetime.now().isoformat()
            result = {"status": "failed", "error": str(e)}
        
        # Save deployment record
        self.deployments.append(deployment_data)
        self._save_data()
        
        return result
    
    def _deploy_docker(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy using Docker"""
        config = deployment_data["config"]
        
        # Build Docker image
        build_cmd = config.get("build_command", "docker build -t {image_name} .")
        image_name = config.get("image_name", "modelsync-model")
        
        build_cmd = build_cmd.format(image_name=image_name)
        
        try:
            result = subprocess.run(build_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return {"status": "failed", "error": result.stderr}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
        
        # Run Docker container
        run_cmd = config.get("run_command", "docker run -d -p {port}:8000 {image_name}")
        port = config.get("port", "8000")
        
        run_cmd = run_cmd.format(image_name=image_name, port=port)
        
        try:
            result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return {"status": "failed", "error": result.stderr}
            
            container_id = result.stdout.strip()
            return {"status": "success", "container_id": container_id, "port": port}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _deploy_kubernetes(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy using Kubernetes"""
        config = deployment_data["config"]
        
        # Apply Kubernetes manifests
        manifest_path = config.get("manifest_path")
        if not manifest_path:
            return {"status": "error", "message": "No manifest path specified"}
        
        try:
            result = subprocess.run(f"kubectl apply -f {manifest_path}", shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return {"status": "failed", "error": result.stderr}
            
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _deploy_api_endpoint(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to API endpoint"""
        config = deployment_data["config"]
        endpoint = config.get("endpoint")
        
        if not endpoint:
            return {"status": "error", "message": "No endpoint specified"}
        
        # Prepare deployment payload
        payload = {
            "model_id": deployment_data["model_id"],
            "metrics": deployment_data["metrics"],
            "config": config
        }
        
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            if response.status_code == 200:
                return {"status": "success", "response": response.json()}
            else:
                return {"status": "failed", "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _deploy_mlflow(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy using MLflow"""
        config = deployment_data["config"]
        
        # MLflow deployment commands
        model_uri = config.get("model_uri")
        if not model_uri:
            return {"status": "error", "message": "No model URI specified"}
        
        try:
            # Register model in MLflow
            register_cmd = f"mlflow models serve -m {model_uri} -p {config.get('port', '5000')}"
            result = subprocess.run(register_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"status": "failed", "error": result.stderr}
            
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def list_deployment_rules(self) -> List[Dict[str, Any]]:
        """List all deployment rules"""
        return [rule.to_dict() for rule in self.rules]
    
    def get_deployments(self, branch: str = None) -> List[Dict[str, Any]]:
        """Get deployment history"""
        if branch:
            return [d for d in self.deployments if d.get("branch") == branch]
        return self.deployments
    
    def remove_deployment_rule(self, name: str) -> bool:
        """Remove a deployment rule"""
        for i, rule in enumerate(self.rules):
            if rule.name == name:
                del self.rules[i]
                self._save_data()
                print(f"✅ Removed deployment rule: {name}")
                return True
        
        print(f"❌ Rule '{name}' not found")
        return False
