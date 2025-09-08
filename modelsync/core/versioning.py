"""
Core versioning functionality for ModelSync
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from modelsync.config import *
from modelsync.utils.helpers import *

class ModelSyncRepo:
    """Main repository class for ModelSync"""
    
    def __init__(self, path: str = "."):
        self.path = Path(path).resolve()
        self.modelsync_dir = self.path / MODELSYNC_DIR
        
    def is_initialized(self) -> bool:
        """Check if repository is initialized"""
        return self.modelsync_dir.exists() and (self.modelsync_dir / "config").exists()
    
    def init(self, user_name: str = "", user_email: str = "") -> bool:
        """Initialize a new ModelSync repository"""
        if self.is_initialized():
            print("ModelSync repository already initialized.")
            return False
        
        try:
            # Create directory structure
            for dir_path in [OBJECTS_DIR, REFS_DIR, HEADS_DIR, METADATA_DIR, LOGS_DIR]:
                ensure_directory(str(self.path / dir_path))
            
            # Create initial files
            self._create_initial_files(user_name, user_email)
            
            # Create initial commit
            self._create_initial_commit()
            
            print("✅ ModelSync repository initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing repository: {e}")
            return False
    
    def _create_initial_files(self, user_name: str, user_email: str) -> None:
        """Create initial repository files"""
        config = DEFAULT_CONFIG.copy()
        if user_name:
            config["user"]["name"] = user_name
        if user_email:
            config["user"]["email"] = user_email
        
        write_json_file(str(self.path / CONFIG_FILE), config)
        
        # Create HEAD file pointing to main branch
        with open(self.path / HEAD_FILE, 'w') as f:
            f.write("ref: refs/heads/main")
        
        # Create empty index
        write_json_file(str(self.path / INDEX_FILE), {"files": {}})
        
        # Create logs directory and initial log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "init",
            "message": "Repository initialized",
            "user": user_name or "Unknown"
        }
        self._write_log_entry(log_entry)
    
    def _create_initial_commit(self) -> None:
        """Create initial empty commit"""
        commit_data = {
            "tree": "",
            "parent": None,
            "author": {
                "name": "ModelSync",
                "email": "modelsync@local",
                "timestamp": datetime.now().isoformat()
            },
            "committer": {
                "name": "ModelSync", 
                "email": "modelsync@local",
                "timestamp": datetime.now().isoformat()
            },
            "message": "Initial commit",
            "hash": ""
        }
        
        commit_hash = calculate_content_hash(json.dumps(commit_data, sort_keys=True).encode())
        commit_data["hash"] = commit_hash
        
        # Save commit object
        commit_path = self.path / OBJECTS_DIR / commit_hash[:2] / commit_hash[2:]
        ensure_directory(str(commit_path.parent))
        write_json_file(str(commit_path), commit_data)
        
        # Update HEAD to point to this commit
        with open(self.path / HEADS_DIR / "main", 'w') as f:
            f.write(commit_hash)
    
    def add(self, file_paths: List[str]) -> Dict[str, Any]:
        """Add files to staging area"""
        if not self.is_initialized():
            print("❌ Not a ModelSync repository. Run 'modelsync init' first.")
            return {}
        
        index = read_json_file(str(self.path / INDEX_FILE))
        added_files = {}
        
        for file_path in file_paths:
            full_path = self.path / file_path
            if not full_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue
            
            file_info = get_file_info(str(full_path))
            if file_info:
                index["files"][file_path] = file_info
                added_files[file_path] = file_info
                print(f"✅ Added: {file_path}")
        
        write_json_file(str(self.path / INDEX_FILE), index)
        return added_files
    
    def commit(self, message: str, author_name: str = "", author_email: str = "") -> Optional[str]:
        """Create a new commit"""
        if not self.is_initialized():
            print("❌ Not a ModelSync repository. Run 'modelsync init' first.")
            return None
        
        # Get current branch
        current_branch = self._get_current_branch()
        if not current_branch:
            print("❌ No current branch found.")
            return None
        
        # Get staged files
        index = read_json_file(str(self.path / INDEX_FILE))
        if not index.get("files"):
            print("❌ No files staged for commit. Use 'modelsync add' first.")
            return None
        
        # Create tree object
        tree_hash = self._create_tree_object(index["files"])
        
        # Get parent commit
        parent_hash = self._get_branch_head(current_branch)
        
        # Create commit
        config = get_config()
        commit_data = {
            "tree": tree_hash,
            "parent": parent_hash,
            "author": {
                "name": author_name or config["user"]["name"] or "Unknown",
                "email": author_email or config["user"]["email"] or "unknown@local",
                "timestamp": datetime.now().isoformat()
            },
            "committer": {
                "name": author_name or config["user"]["name"] or "Unknown",
                "email": author_email or config["user"]["email"] or "unknown@local", 
                "timestamp": datetime.now().isoformat()
            },
            "message": message,
            "hash": ""
        }
        
        commit_hash = calculate_content_hash(json.dumps(commit_data, sort_keys=True).encode())
        commit_data["hash"] = commit_hash
        
        # Save commit object
        commit_path = self.path / OBJECTS_DIR / commit_hash[:2] / commit_hash[2:]
        ensure_directory(str(commit_path.parent))
        write_json_file(str(commit_path), commit_data)
        
        # Update branch head
        with open(self.path / HEADS_DIR / current_branch, 'w') as f:
            f.write(commit_hash)
        
        # Clear staging area
        index["files"] = {}
        write_json_file(str(self.path / INDEX_FILE), index)
        
        # Log commit
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "commit",
            "message": message,
            "commit_hash": commit_hash,
            "files_count": len(index["files"]),
            "user": author_name or config["user"]["name"] or "Unknown"
        }
        self._write_log_entry(log_entry)
        
        print(f"✅ Commit created: {commit_hash[:8]}")
        print(f"📝 Message: {message}")
        return commit_hash
    
    def status(self) -> Dict[str, Any]:
        """Show repository status"""
        if not self.is_initialized():
            return {"error": "Not a ModelSync repository"}
        
        # Get tracked files
        tracked_files = get_tracked_files(str(self.path))
        
        # Get staged files
        index = read_json_file(str(self.path / INDEX_FILE))
        staged_files = index.get("files", {})
        
        # Find modified files
        modified_files = []
        for file_path in tracked_files:
            file_info = get_file_info(file_path)
            if file_path in staged_files:
                if file_info["hash"] != staged_files[file_path]["hash"]:
                    modified_files.append(file_path)
            else:
                modified_files.append(file_path)
        
        return {
            "branch": self._get_current_branch(),
            "staged_files": list(staged_files.keys()),
            "modified_files": modified_files,
            "total_tracked": len(tracked_files),
            "total_staged": len(staged_files)
        }
    
    def log(self, oneline: bool = False) -> List[Dict[str, Any]]:
        """Show commit history"""
        if not self.is_initialized():
            return []
        
        current_branch = self._get_current_branch()
        if not current_branch:
            return []
        
        commits = []
        commit_hash = self._get_branch_head(current_branch)
        
        while commit_hash:
            commit_path = self.path / OBJECTS_DIR / commit_hash[:2] / commit_hash[2:]
            if commit_path.exists():
                commit_data = read_json_file(str(commit_path))
                commits.append(commit_data)
                commit_hash = commit_data.get("parent")
            else:
                break
        
        return commits
    
    def _create_tree_object(self, files: Dict[str, Any]) -> str:
        """Create tree object from files"""
        tree_data = {"files": files}
        tree_content = json.dumps(tree_data, sort_keys=True)
        tree_hash = calculate_content_hash(tree_content.encode())
        
        tree_path = self.path / OBJECTS_DIR / tree_hash[:2] / tree_hash[2:]
        ensure_directory(str(tree_path.parent))
        write_json_file(str(tree_path), tree_data)
        
        return tree_hash
    
    def _get_current_branch(self) -> Optional[str]:
        """Get current branch name"""
        try:
            with open(self.path / HEAD_FILE, 'r') as f:
                head_content = f.read().strip()
                if head_content.startswith("ref: refs/heads/"):
                    return head_content.split("/")[-1]
        except FileNotFoundError:
            pass
        return None
    
    def _get_branch_head(self, branch: str) -> Optional[str]:
        """Get commit hash for branch head"""
        try:
            with open(self.path / HEADS_DIR / branch, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def _write_log_entry(self, entry: Dict[str, Any]) -> None:
        """Write entry to history log"""
        log_path = self.path / HISTORY_FILE
        ensure_directory(str(log_path.parent))
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")

# Convenience functions for CLI
def init_repo(user_name: str = "", user_email: str = ""):
    """Initialize repository - CLI wrapper"""
    repo = ModelSyncRepo()
    repo.init(user_name, user_email)

def commit_changes(message: str, author_name: str = "", author_email: str = ""):
    """Commit changes - CLI wrapper"""
    repo = ModelSyncRepo()
    repo.commit(message, author_name, author_email)