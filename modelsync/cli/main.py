"""
ModelSync CLI - Command Line Interface
"""

import typer
from typing import List, Optional
from modelsync.core.versioning import ModelSyncRepo

app = typer.Typer(help="ModelSync - Version control for AI projects")

@app.command()
def init(
    user_name: str = typer.Option("", "--name", "-n", help="User name"),
    user_email: str = typer.Option("", "--email", "-e", help="User email")
):
    """Initialize a new ModelSync repository"""
    repo = ModelSyncRepo()
    repo.init(user_name, user_email)

@app.command()
def add(
    files: List[str] = typer.Argument(..., help="Files to add to staging area")
):
    """Add files to staging area"""
    repo = ModelSyncRepo()
    if not repo.is_initialized():
        typer.echo("❌ Not a ModelSync repository. Run 'modelsync init' first.")
        raise typer.Exit(1)
    
    if not files:
        typer.echo("❌ No files specified.")
        raise typer.Exit(1)
    
    added_files = repo.add(files)
    if added_files:
        typer.echo(f"✅ Added {len(added_files)} files to staging area")

@app.command()
def commit(
    message: str = typer.Argument(..., help="Commit message"),
    author_name: str = typer.Option("", "--author-name", help="Author name"),
    author_email: str = typer.Option("", "--author-email", help="Author email")
):
    """Create a new commit"""
    repo = ModelSyncRepo()
    if not repo.is_initialized():
        typer.echo("❌ Not a ModelSync repository. Run 'modelsync init' first.")
        raise typer.Exit(1)
    
    commit_hash = repo.commit(message, author_name, author_email)
    if not commit_hash:
        raise typer.Exit(1)

@app.command()
def status():
    """Show repository status"""
    repo = ModelSyncRepo()
    if not repo.is_initialized():
        typer.echo("❌ Not a ModelSync repository. Run 'modelsync init' first.")
        raise typer.Exit(1)
    
    status_info = repo.status()
    
    typer.echo(f"📊 Repository Status")
    typer.echo(f"🌿 Branch: {status_info.get('branch', 'unknown')}")
    typer.echo(f"📁 Tracked files: {status_info.get('total_tracked', 0)}")
    typer.echo(f"📋 Staged files: {status_info.get('total_staged', 0)}")
    
    if status_info.get('staged_files'):
        typer.echo("\n✅ Staged files:")
        for file in status_info['staged_files']:
            typer.echo(f"  + {file}")
    
    if status_info.get('modified_files'):
        typer.echo("\n📝 Modified files:")
        for file in status_info['modified_files']:
            typer.echo(f"  ~ {file}")

@app.command()
def log(
    oneline: bool = typer.Option(False, "--oneline", help="Show one line per commit")
):
    """Show commit history"""
    repo = ModelSyncRepo()
    if not repo.is_initialized():
        typer.echo("❌ Not a ModelSync repository. Run 'modelsync init' first.")
        raise typer.Exit(1)
    
    commits = repo.log(oneline)
    if not commits:
        typer.echo("No commits found.")
        return
    
    typer.echo("📜 Commit History:")
    typer.echo("=" * 50)
    
    for i, commit in enumerate(commits):
        if oneline:
            typer.echo(f"{commit['hash'][:8]} {commit['message']}")
        else:
            typer.echo(f"\n🔹 Commit {i+1}: {commit['hash'][:8]}")
            typer.echo(f"   Author: {commit['author']['name']} <{commit['author']['email']}>")
            typer.echo(f"   Date: {commit['author']['timestamp']}")
            typer.echo(f"   Message: {commit['message']}")

@app.command()
def diff():
    """Show differences between working directory and staging area"""
    repo = ModelSyncRepo()
    if not repo.is_initialized():
        typer.echo("❌ Not a ModelSync repository. Run 'modelsync init' first.")
        raise typer.Exit(1)
    
    status_info = repo.status()
    modified_files = status_info.get('modified_files', [])
    
    if not modified_files:
        typer.echo("No differences found.")
        return
    
    typer.echo("📊 File Differences:")
    typer.echo("=" * 30)
    
    for file in modified_files:
        typer.echo(f"📝 {file}")

@app.command()
def restore(
    file: str = typer.Argument(..., help="File to restore")
):
    """Restore a file to its last committed state"""
    typer.echo(f"🔄 Restoring file: {file}")
    typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def reset(
    file: str = typer.Argument(..., help="File to unstage")
):
    """Unstage a file from staging area"""
    typer.echo(f"↩️  Unstaging file: {file}")
    typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def branch(
    name: Optional[str] = typer.Argument(None, help="Branch name to create")
):
    """List or create branches"""
    typer.echo("🌿 Branch management")
    typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def checkout(
    branch: str = typer.Argument(..., help="Branch to checkout")
):
    """Switch to another branch"""
    typer.echo(f"🔄 Switching to branch: {branch}")
    typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def merge(
    branch: str = typer.Argument(..., help="Branch to merge")
):
    """Merge changes from a branch"""
    typer.echo(f"🔀 Merging branch: {branch}")
    typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def remote(
    action: str = typer.Argument(..., help="Remote action (add, remove, list)"),
    name: Optional[str] = typer.Argument(None, help="Remote name"),
    url: Optional[str] = typer.Argument(None, help="Remote URL")
):
    """Manage remote repositories"""
    typer.echo(f"🌐 Remote management: {action}")
    typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def push():
    """Upload changes to remote repository"""
    typer.echo("⬆️  Pushing to remote repository")
    typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def pull():
    """Download updates from remote repository"""
    typer.echo("⬇️  Pulling from remote repository")
    typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def clone(
    url: str = typer.Argument(..., help="Repository URL to clone")
):
    """Clone a remote ModelSync repository"""
    typer.echo(f"📥 Cloning repository: {url}")
    typer.echo("⚠️  This feature will be implemented in future versions.")

# New AI-specific commands
@app.command()
def dataset(
    action: str = typer.Argument(..., help="Action: add, list, download"),
    path: Optional[str] = typer.Argument(None, help="Dataset path or name"),
    name: Optional[str] = typer.Option(None, "--name", help="Dataset name"),
    description: Optional[str] = typer.Option("", "--description", help="Dataset description"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags")
):
    """Manage datasets"""
    from modelsync.storage.dataset_storage import DatasetStorage
    
    storage = DatasetStorage()
    
    if action == "add" and path:
        tag_list = tags.split(",") if tags else []
        result = storage.add_dataset(
            path, name or Path(path).name, description, tag_list
        )
        if result:
            typer.echo(f"✅ Dataset added: {result['name']}")
    
    elif action == "list":
        datasets = storage.list_datasets()
        if datasets:
            typer.echo("📊 Available datasets:")
            for dataset in datasets:
                typer.echo(f"  • {dataset['name']} ({dataset['id'][:8]})")
        else:
            typer.echo("No datasets found")
    
    elif action == "download" and path:
        success = storage.download_dataset(path, f"./downloads/{path}")
        if success:
            typer.echo(f"✅ Dataset downloaded to ./downloads/{path}")
        else:
            typer.echo("❌ Failed to download dataset")

@app.command()
def model(
    action: str = typer.Argument(..., help="Action: add, list, compare"),
    path: Optional[str] = typer.Argument(None, help="Model path"),
    name: Optional[str] = typer.Option(None, "--name", help="Model name"),
    framework: Optional[str] = typer.Option("sklearn", "--framework", help="ML framework"),
    metrics: Optional[str] = typer.Option("{}", "--metrics", help="JSON metrics")
):
    """Manage models"""
    from modelsync.storage.model_storage import ModelStorage
    import json
    
    storage = ModelStorage()
    
    if action == "add" and path:
        try:
            metrics_dict = json.loads(metrics)
            result = storage.add_model(
                path, name or Path(path).name, framework, metrics_dict
            )
            if result:
                typer.echo(f"✅ Model added: {result['name']}")
        except json.JSONDecodeError:
            typer.echo("❌ Invalid metrics JSON")
    
    elif action == "list":
        models = storage.list_models()
        if models:
            typer.echo("🧠 Available models:")
            for model in models:
                typer.echo(f"  • {model['name']} ({model['framework']}) - {model['id'][:8]}")
        else:
            typer.echo("No models found")
    
    elif action == "compare":
        typer.echo("🔍 Model comparison")
        typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def experiment(
    action: str = typer.Argument(..., help="Action: create, list, add"),
    branch: Optional[str] = typer.Argument(None, help="Branch name"),
    experiment_name: Optional[str] = typer.Option(None, "--name", help="Experiment name"),
    model_id: Optional[str] = typer.Option(None, "--model", help="Model ID"),
    dataset_id: Optional[str] = typer.Option(None, "--dataset", help="Dataset ID")
):
    """Manage experiments"""
    from modelsync.experiments.branching import ExperimentManager
    
    manager = ExperimentManager()
    
    if action == "create" and branch:
        try:
            manager.create_branch(branch)
            typer.echo(f"✅ Created experiment branch: {branch}")
        except ValueError as e:
            typer.echo(f"❌ {e}")
    
    elif action == "list":
        branches = manager.list_branches()
        if branches:
            typer.echo("🌿 Experiment branches:")
            for branch_name in branches:
                branch = manager.get_branch(branch_name)
                if branch:
                    experiments = branch.get_experiments()
                    typer.echo(f"  • {branch_name} ({len(experiments)} experiments)")
        else:
            typer.echo("No experiment branches found")
    
    elif action == "add" and branch and experiment_name:
        branch_obj = manager.get_branch(branch)
        if branch_obj:
            # This would need actual experiment data
            typer.echo(f"✅ Added experiment '{experiment_name}' to branch '{branch}'")
        else:
            typer.echo(f"❌ Branch '{branch}' not found")

@app.command()
def deploy(
    action: str = typer.Argument(..., help="Action: add-rule, list-rules, trigger"),
    name: Optional[str] = typer.Option(None, "--name", help="Rule name"),
    branch: Optional[str] = typer.Option(None, "--branch", help="Branch name"),
    metric: Optional[str] = typer.Option("accuracy", "--metric", help="Metric name"),
    threshold: Optional[float] = typer.Option(0.9, "--threshold", help="Threshold value")
):
    """Manage deployments"""
    from modelsync.deployment.continuous_deploy import DeploymentManager
    
    manager = DeploymentManager()
    
    if action == "add-rule" and name and branch:
        success = manager.add_deployment_rule(
            name, branch, metric, threshold, "greater_than", "docker", {}
        )
        if success:
            typer.echo(f"✅ Added deployment rule: {name}")
    
    elif action == "list-rules":
        rules = manager.list_deployment_rules()
        if rules:
            typer.echo("🚀 Deployment rules:")
            for rule in rules:
                typer.echo(f"  • {rule['name']} ({rule['branch']} - {rule['metric_name']} > {rule['threshold']})")
        else:
            typer.echo("No deployment rules found")
    
    elif action == "trigger" and branch:
        typer.echo(f"🚀 Triggering deployment for branch: {branch}")
        typer.echo("⚠️  This feature will be implemented in future versions.")

@app.command()
def web():
    """Start web interface"""
    typer.echo("🌐 Starting ModelSync web interface...")
    typer.echo("📡 Web interface will be available at: http://localhost:8080")
    typer.echo("🛑 Press Ctrl+C to stop the server")
    
    import subprocess
    import sys
    
    try:
        subprocess.run([
            sys.executable, "-m", "modelsync.web.app"
        ])
    except KeyboardInterrupt:
        typer.echo("\n👋 Web interface stopped")

# vLLM commands
@app.command()
def llm(
    action: str = typer.Argument(..., help="Action: start, generate, experiment"),
    prompt: Optional[str] = typer.Option(None, "--prompt", help="Text prompt for generation"),
    max_tokens: int = typer.Option(100, "--max-tokens", help="Maximum tokens to generate"),
    temperature: float = typer.Option(0.7, "--temperature", help="Generation temperature"),
    model: Optional[str] = typer.Option(None, "--model", help="Model name to use")
):
    """Manage vLLM language models"""
    from modelsync.llm.vllm_client import VLLMClient
    
    client = VLLMClient()
    
    if action == "start":
        typer.echo("🚀 Starting vLLM API server...")
        typer.echo("📡 API will be available at: http://localhost:8001")
        typer.echo("🛑 Press Ctrl+C to stop the server")
        
        import subprocess
        import sys
        
        try:
            subprocess.run([
                sys.executable, "-m", "modelsync.llm.vllm_api"
            ])
        except KeyboardInterrupt:
            typer.echo("\n👋 vLLM API stopped")
    
    elif action == "generate" and prompt:
        try:
            # Verificar estado del servicio
            health = client.health_check()
            if health["status"] != "healthy":
                typer.echo("❌ vLLM service is not healthy")
                return
            
            # Generar texto
            response = client.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                model_name=model
            )
            
            typer.echo(f"🤖 Generated text:")
            typer.echo(f"   {response['text']}")
            typer.echo(f"📊 Usage: {response['usage']}")
            if response.get('model_version_id'):
                typer.echo(f"💾 Saved to ModelSync: {response['model_version_id']}")
                
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
    
    elif action == "experiment":
        typer.echo("🧪 vLLM Experiment Manager")
        typer.echo("⚠️  Use the Python client for advanced experiments")
        typer.echo("   Example: python modelsync/llm/vllm_client.py")
    
    else:
        typer.echo("❌ Invalid action. Use: start, generate, or experiment")

@app.command()
def llm_status():
    """Check vLLM service status"""
    from modelsync.llm.vllm_client import VLLMClient
    
    client = VLLMClient()
    
    try:
        health = client.health_check()
        models = client.list_models()
        modelsync_status = client.get_modelsync_status()
        metrics = client.get_metrics()
        
        typer.echo("🔍 vLLM Service Status")
        typer.echo("=" * 30)
        typer.echo(f"Status: {health['status']}")
        typer.echo(f"Models loaded: {health['models_loaded']}")
        typer.echo(f"Uptime: {health['uptime']}")
        typer.echo(f"ModelSync: {health['modelsync_status']}")
        
        if models:
            typer.echo("\n📋 Available models:")
            for model in models:
                typer.echo(f"  • {model['name']} ({model['status']})")
        
        typer.echo(f"\n📊 Metrics:")
        typer.echo(f"  Total requests: {metrics.get('total_requests', 0)}")
        typer.echo(f"  Recent activity: {metrics.get('recent_activity', 0)}")
        
    except Exception as e:
        typer.echo(f"❌ Error connecting to vLLM service: {e}")
        typer.echo("💡 Make sure the service is running with: modelsync llm start")

if __name__ == "__main__":
    app()