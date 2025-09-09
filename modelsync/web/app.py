"""
Web application for ModelSync visualization
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

# Import ModelSync components
from modelsync.experiments.branching import ExperimentManager
from modelsync.storage.model_storage import ModelStorage
from modelsync.storage.dataset_storage import DatasetStorage
from modelsync.deployment.continuous_deploy import DeploymentManager
from modelsync.collaboration.audit import CollaborationManager

app = FastAPI(title="ModelSync Web Interface", version="1.0.0")

# Setup templates and static files
templates = Jinja2Templates(directory="modelsync/web/templates")
app.mount("/static", StaticFiles(directory="modelsync/web/static"), name="static")

# Initialize managers
experiment_manager = ExperimentManager()
model_storage = ModelStorage()
dataset_storage = DatasetStorage()
deployment_manager = DeploymentManager()
collaboration_manager = CollaborationManager()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard"""
    
    # Get summary data
    branches = experiment_manager.list_branches()
    models = model_storage.list_models()
    datasets = dataset_storage.list_datasets()
    deployments = deployment_manager.get_deployments()
    
    # Get recent activity
    recent_activity = []
    for branch in branches[:5]:  # Last 5 branches
        branch_obj = experiment_manager.get_branch(branch)
        if branch_obj:
            experiments = branch_obj.get_experiments()
            for exp in experiments[:3]:  # Last 3 experiments per branch
                recent_activity.append({
                    "type": "experiment",
                    "branch": branch,
                    "name": exp["name"],
                    "timestamp": exp["created_at"],
                    "metrics": exp.get("metrics", {})
                })
    
    # Sort by timestamp
    recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
    
    context = {
        "request": request,
        "branches_count": len(branches),
        "models_count": len(models),
        "datasets_count": len(datasets),
        "deployments_count": len(deployments),
        "recent_activity": recent_activity[:10]
    }
    
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/experiments", response_class=HTMLResponse)
async def experiments_page(request: Request):
    """Experiments page"""
    branches = experiment_manager.list_branches()
    
    # Get detailed branch information
    branch_data = []
    for branch_name in branches:
        branch = experiment_manager.get_branch(branch_name)
        if branch:
            experiments = branch.get_experiments()
            metrics_summary = branch.get_metrics_summary()
            
            branch_data.append({
                "name": branch_name,
                "experiments_count": len(experiments),
                "metrics_summary": metrics_summary,
                "best_experiment": branch.get_best_experiment("accuracy") if experiments else None
            })
    
    context = {
        "request": request,
        "branches": branch_data
    }
    
    return templates.TemplateResponse("experiments.html", context)

@app.get("/experiments/{branch_name}", response_class=HTMLResponse)
async def branch_detail(request: Request, branch_name: str):
    """Branch detail page"""
    branch = experiment_manager.get_branch(branch_name)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    experiments = branch.get_experiments()
    metrics_summary = branch.get_metrics_summary()
    
    context = {
        "request": request,
        "branch": {
            "name": branch_name,
            "experiments": experiments,
            "metrics_summary": metrics_summary
        }
    }
    
    return templates.TemplateResponse("branch_detail.html", context)

@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    """Models page"""
    models = model_storage.list_models()
    
    # Group models by framework
    frameworks = {}
    for model in models:
        framework = model.get("framework", "unknown")
        if framework not in frameworks:
            frameworks[framework] = []
        frameworks[framework].append(model)
    
    context = {
        "request": request,
        "models": models,
        "frameworks": frameworks
    }
    
    return templates.TemplateResponse("models.html", context)

@app.get("/datasets", response_class=HTMLResponse)
async def datasets_page(request: Request):
    """Datasets page"""
    datasets = dataset_storage.list_datasets()
    
    # Calculate total size
    total_size = sum(dataset.get("size", 0) for dataset in datasets)
    
    context = {
        "request": request,
        "datasets": datasets,
        "total_size": total_size
    }
    
    return templates.TemplateResponse("datasets.html", context)

@app.get("/deployments", response_class=HTMLResponse)
async def deployments_page(request: Request):
    """Deployments page"""
    rules = deployment_manager.list_deployment_rules()
    deployments = deployment_manager.get_deployments()
    
    # Group deployments by status
    status_groups = {}
    for deployment in deployments:
        status = deployment.get("status", "unknown")
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(deployment)
    
    context = {
        "request": request,
        "rules": rules,
        "deployments": deployments,
        "status_groups": status_groups
    }
    
    return templates.TemplateResponse("deployments.html", context)

@app.get("/api/experiments")
async def api_experiments():
    """API endpoint for experiments data"""
    branches = experiment_manager.list_branches()
    
    data = []
    for branch_name in branches:
        branch = experiment_manager.get_branch(branch_name)
        if branch:
            experiments = branch.get_experiments()
            data.append({
                "name": branch_name,
                "experiments": experiments,
                "count": len(experiments)
            })
    
    return {"branches": data}

@app.get("/api/metrics/{branch_name}")
async def api_branch_metrics(branch_name: str):
    """API endpoint for branch metrics"""
    branch = experiment_manager.get_branch(branch_name)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    experiments = branch.get_experiments()
    metrics_summary = branch.get_metrics_summary()
    
    return {
        "branch": branch_name,
        "experiments": experiments,
        "metrics_summary": metrics_summary
    }

@app.get("/api/comparison")
async def api_comparison(branches: str = None, metric: str = "accuracy"):
    """API endpoint for branch comparison"""
    if not branches:
        return {"error": "No branches specified"}
    
    branch_list = branches.split(",")
    comparison = experiment_manager.compare_branches(branch_list, metric)
    
    return comparison

@app.post("/api/deploy")
async def api_deploy(
    branch: str = Form(...),
    model_id: str = Form(...),
    metrics: str = Form(...)
):
    """API endpoint to trigger deployment"""
    try:
        metrics_dict = json.loads(metrics)
        triggered_rules = deployment_manager.check_deployment_rules(
            branch, metrics_dict, model_id
        )
        
        return {
            "status": "success",
            "triggered_rules": len(triggered_rules),
            "rules": triggered_rules
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
