#!/usr/bin/env python3
"""
Exemplo completo de workflow de IA com ModelSync
"""

import os
import sys
import json
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modelsync.core.versioning import ModelSyncRepo
from modelsync.storage.dataset_storage import DatasetStorage
from modelsync.storage.model_storage import ModelStorage
from modelsync.experiments.branching import ExperimentManager
from modelsync.pipelines.ml_pipeline import PipelineManager
from modelsync.deployment.continuous_deploy import DeploymentManager
from modelsync.collaboration.audit import CollaborationManager

def create_sample_data():
    """Create sample dataset for demonstration"""
    print("📊 Creating sample dataset...")
    
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X = np.random.randn(n_samples, n_features)
    y = (X[:, 0] + X[:, 1] + np.random.randn(n_samples) * 0.1 > 0).astype(int)
    
    # Create DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    # Save dataset
    dataset_path = "sample_dataset.csv"
    df.to_csv(dataset_path, index=False)
    
    print(f"✅ Dataset created: {dataset_path} ({len(df)} samples, {len(df.columns)-1} features)")
    return dataset_path

def train_model(X_train, X_test, y_train, y_test, hyperparams):
    """Train a model with given hyperparameters"""
    model = RandomForestClassifier(
        n_estimators=hyperparams.get('n_estimators', 100),
        max_depth=hyperparams.get('max_depth', None),
        random_state=42
    )
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred)
    }
    
    return model, metrics

def demonstrate_ai_workflow():
    """Demonstrate complete AI workflow with ModelSync"""
    print("🚀 ModelSync AI Workflow Demo")
    print("=" * 50)
    
    # 1. Initialize ModelSync repository
    print("\n1️⃣ Initializing ModelSync repository...")
    repo = ModelSyncRepo()
    if not repo.is_initialized():
        repo.init("AI Researcher", "researcher@example.com")
    
    # 2. Create and version dataset
    print("\n2️⃣ Managing datasets...")
    dataset_path = create_sample_data()
    
    dataset_storage = DatasetStorage()
    dataset_info = dataset_storage.add_dataset(
        dataset_path=dataset_path,
        dataset_name="Sample Classification Dataset",
        description="Synthetic binary classification dataset",
        tags=["synthetic", "classification", "binary"]
    )
    print(f"✅ Dataset versioned: {dataset_info['name']} ({dataset_info['id'][:8]})")
    
    # 3. Create experiment branches
    print("\n3️⃣ Setting up experiment branches...")
    experiment_manager = ExperimentManager()
    
    # Create different experiment branches
    branches = ["baseline", "feature_engineering", "hyperparameter_tuning"]
    for branch in branches:
        try:
            experiment_manager.create_branch(branch)
            print(f"✅ Created branch: {branch}")
        except ValueError:
            print(f"⚠️  Branch {branch} already exists")
    
    # 4. Run experiments on different branches
    print("\n4️⃣ Running experiments...")
    
    # Load dataset
    df = pd.read_csv(dataset_path)
    X = df.drop('target', axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Experiment configurations
    experiments = {
        "baseline": {
            "hyperparams": {"n_estimators": 100, "max_depth": None},
            "description": "Baseline Random Forest"
        },
        "feature_engineering": {
            "hyperparams": {"n_estimators": 150, "max_depth": 10},
            "description": "Feature engineering with more trees"
        },
        "hyperparameter_tuning": {
            "hyperparams": {"n_estimators": 200, "max_depth": 15},
            "description": "Tuned hyperparameters"
        }
    }
    
    model_storage = ModelStorage()
    
    for branch_name, config in experiments.items():
        print(f"\n🔬 Running experiment on branch: {branch_name}")
        
        # Train model
        model, metrics = train_model(X_train, X_test, y_train, y_test, config["hyperparams"])
        
        # Save model
        model_path = f"model_{branch_name}.pkl"
        import joblib
        joblib.dump(model, model_path)
        
        model_info = model_storage.add_model(
            model_path=model_path,
            model_name=f"RF_{branch_name}",
            framework="sklearn",
            metrics=metrics,
            hyperparameters=config["hyperparams"],
            training_info={
                "train_size": len(X_train),
                "test_size": len(X_test),
                "features": list(X.columns)
            }
        )
        
        # Add experiment to branch
        branch = experiment_manager.get_branch(branch_name)
        if branch:
            experiment_data = branch.add_experiment(
                experiment_name=f"exp_{branch_name}",
                model_id=model_info["id"],
                dataset_id=dataset_info["id"],
                hyperparameters=config["hyperparams"],
                metrics=metrics,
                description=config["description"]
            )
            print(f"✅ Experiment added: {experiment_data['name']}")
            print(f"   Metrics: {metrics}")
    
    # 5. Compare experiments
    print("\n5️⃣ Comparing experiments...")
    comparison = experiment_manager.compare_branches(branches, "accuracy")
    
    if "error" not in comparison:
        print(f"🏆 Best branch: {comparison['best_branch']}")
        print(f"📊 Comparison results:")
        for branch_data in comparison["branches"]:
            print(f"   • {branch_data['name']}: {branch_data['avg_metric_value']:.4f} accuracy")
    
    # 6. Setup deployment rules
    print("\n6️⃣ Setting up deployment...")
    deployment_manager = DeploymentManager()
    
    # Add deployment rule for best performing model
    deployment_manager.add_deployment_rule(
        name="high_accuracy_deploy",
        branch="hyperparameter_tuning",
        metric_name="accuracy",
        threshold=0.85,
        operator="greater_than",
        deployment_target="docker",
        deployment_config={
            "image_name": "modelsync-demo",
            "port": "8000"
        }
    )
    print("✅ Deployment rule added")
    
    # 7. Setup collaboration
    print("\n7️⃣ Setting up collaboration...")
    collaboration_manager = CollaborationManager()
    
    # Add team members
    collaboration_manager.add_user("alice", "alice@example.com", "admin")
    collaboration_manager.add_user("bob", "bob@example.com", "contributor")
    collaboration_manager.add_user("charlie", "charlie@example.com", "viewer")
    
    print("✅ Team members added")
    
    # 8. Create ML pipeline
    print("\n8️⃣ Creating ML pipeline...")
    pipeline_manager = PipelineManager()
    
    pipeline = pipeline_manager.create_pipeline("classification_pipeline")
    
    # Add pipeline steps (simplified for demo)
    def preprocess_data(data):
        return data  # Placeholder
    
    def train_model_step(data, **params):
        return data  # Placeholder
    
    pipeline.add_step("preprocess", "data_preprocessing", preprocess_data, {}, "custom")
    pipeline.add_step("train", "model_training", train_model_step, {}, "custom")
    
    print("✅ ML pipeline created")
    
    # 9. Show repository status
    print("\n9️⃣ Repository status...")
    status = repo.status()
    print(f"📊 Branch: {status['branch']}")
    print(f"📁 Tracked files: {status['total_tracked']}")
    print(f"📋 Staged files: {status['total_staged']}")
    
    # 10. Show audit trail
    print("\n🔟 Audit trail...")
    audit_log = collaboration_manager.audit_log
    recent_actions = audit_log.get_audit_trail()[:5]
    
    if recent_actions:
        print("📝 Recent actions:")
        for action in recent_actions:
            print(f"   • {action['action']} by {action['user']} at {action['timestamp']}")
    
    print("\n🎉 AI Workflow Demo completed successfully!")
    print("\n📚 What was demonstrated:")
    print("   ✅ Dataset versioning with deduplication")
    print("   ✅ Model versioning with checkpoints")
    print("   ✅ Experiment branching and comparison")
    print("   ✅ ML pipeline creation")
    print("   ✅ Deployment rules setup")
    print("   ✅ Collaboration and audit logging")
    print("   ✅ Complete AI project versioning")
    
    print("\n🚀 Next steps:")
    print("   • Start web interface: modelsync web")
    print("   • View experiments: modelsync experiment list")
    print("   • Check models: modelsync model list")
    print("   • View datasets: modelsync dataset list")

def cleanup():
    """Clean up demo files"""
    print("\n🧹 Cleaning up demo files...")
    demo_files = [
        "sample_dataset.csv",
        "model_baseline.pkl",
        "model_feature_engineering.pkl", 
        "model_hyperparameter_tuning.pkl"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed: {file}")

if __name__ == "__main__":
    try:
        demonstrate_ai_workflow()
    finally:
        cleanup()
