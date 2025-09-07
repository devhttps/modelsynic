#!/usr/bin/env python3
"""
Exemplo básico de uso do ModelSync
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modelsync.core.versioning import ModelSyncRepo

def create_sample_files():
    """Create sample files for demonstration"""
    print("📁 Creating sample files...")
    
    # Create sample Python file
    with open("sample_model.py", "w") as f:
        f.write("""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model accuracy: {accuracy:.4f}")
    return model, accuracy

if __name__ == "__main__":
    # Sample data
    X = np.random.rand(1000, 10)
    y = np.random.randint(0, 2, 1000)
    
    model, accuracy = train_model(X, y)
    print(f"Final accuracy: {accuracy:.4f}")
""")
    
    # Create sample config file
    with open("config.json", "w") as f:
        f.write("""
{
  "model": {
    "type": "RandomForest",
    "n_estimators": 100,
    "random_state": 42
  },
  "data": {
    "train_size": 0.8,
    "test_size": 0.2
  },
  "metrics": {
    "accuracy": 0.9234,
    "precision": 0.9156,
    "recall": 0.9289
  }
}
""")
    
    # Create sample dataset
    with open("dataset.csv", "w") as f:
        f.write("""feature1,feature2,feature3,feature4,feature5,target
0.1,0.2,0.3,0.4,0.5,0
0.6,0.7,0.8,0.9,1.0,1
0.2,0.3,0.4,0.5,0.6,0
0.7,0.8,0.9,1.0,0.1,1
0.3,0.4,0.5,0.6,0.7,0
""")
    
    print("✅ Sample files created!")

def demonstrate_modelsync():
    """Demonstrate ModelSync functionality"""
    print("🚀 ModelSync Basic Usage Demo")
    print("=" * 50)
    
    # Initialize repository
    print("\n1️⃣ Initializing ModelSync repository...")
    repo = ModelSyncRepo()
    
    if repo.is_initialized():
        print("⚠️  Repository already initialized, continuing...")
    else:
        success = repo.init("Demo User", "demo@example.com")
        if not success:
            print("❌ Failed to initialize repository")
            return
    
    # Create sample files
    create_sample_files()
    
    # Add files to staging
    print("\n2️⃣ Adding files to staging area...")
    files_to_add = ["sample_model.py", "config.json", "dataset.csv"]
    added_files = repo.add(files_to_add)
    print(f"✅ Added {len(added_files)} files to staging")
    
    # Check status
    print("\n3️⃣ Checking repository status...")
    status = repo.status()
    print(f"📊 Branch: {status['branch']}")
    print(f"📁 Tracked files: {status['total_tracked']}")
    print(f"📋 Staged files: {status['total_staged']}")
    
    if status['staged_files']:
        print("   Staged files:")
        for file in status['staged_files']:
            print(f"   + {file}")
    
    # Create commit
    print("\n4️⃣ Creating commit...")
    commit_hash = repo.commit("Initial commit with sample ML project")
    if commit_hash:
        print(f"✅ Commit created: {commit_hash[:8]}")
    
    # Show log
    print("\n5️⃣ Showing commit history...")
    commits = repo.log()
    print(f"📜 Total commits: {len(commits)}")
    
    for i, commit in enumerate(commits[:3]):  # Show last 3 commits
        print(f"\n🔹 Commit {i+1}: {commit['hash'][:8]}")
        print(f"   Author: {commit['author']['name']} <{commit['author']['email']}>")
        print(f"   Date: {commit['author']['timestamp']}")
        print(f"   Message: {commit['message']}")
    
    # Demonstrate file modification
    print("\n6️⃣ Demonstrating file modification...")
    with open("sample_model.py", "a") as f:
        f.write("\n# Updated model with better parameters\n")
    
    # Check status after modification
    status = repo.status()
    if status['modified_files']:
        print("📝 Modified files detected:")
        for file in status['modified_files']:
            print(f"   ~ {file}")
    
    # Add and commit changes
    print("\n7️⃣ Adding and committing changes...")
    repo.add(["sample_model.py"])
    commit_hash = repo.commit("Updated model with better parameters")
    if commit_hash:
        print(f"✅ Changes committed: {commit_hash[:8]}")
    
    # Final status
    print("\n8️⃣ Final repository status...")
    status = repo.status()
    print(f"📊 Branch: {status['branch']}")
    print(f"📁 Tracked files: {status['total_tracked']}")
    print(f"📋 Staged files: {status['total_staged']}")
    print(f"📝 Modified files: {len(status['modified_files'])}")
    
    print("\n🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("- Try: python modelsync/cli/main.py status")
    print("- Try: python modelsync/cli/main.py log --oneline")
    print("- Start API: python modelsync/api/main.py")

def cleanup():
    """Clean up sample files"""
    print("\n🧹 Cleaning up sample files...")
    sample_files = ["sample_model.py", "config.json", "dataset.csv"]
    for file in sample_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed: {file}")

if __name__ == "__main__":
    try:
        demonstrate_modelsync()
    finally:
        cleanup()
