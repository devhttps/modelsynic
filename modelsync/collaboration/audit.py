"""
Audit and collaboration features for ModelSync
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from modelsync.utils.helpers import ensure_directory, write_json_file, read_json_file

class AuditLog:
    """Audit logging for ModelSync operations"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.audit_dir = self.repo_path / ".modelsync" / "audit"
        self.audit_file = self.audit_dir / "audit_log.jsonl"
        ensure_directory(str(self.audit_dir))
    
    def log_action(
        self,
        action: str,
        user: str,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Log an action to the audit trail"""
        
        audit_entry = {
            "id": self._generate_audit_id(),
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "metadata": metadata or {},
            "ip_address": self._get_client_ip(),
            "user_agent": self._get_user_agent()
        }
        
        # Write to audit log file
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry) + '\n')
        
        print(f"📝 Audit logged: {action} by {user} on {resource_type}:{resource_id}")
        return audit_entry["id"]
    
    def get_audit_trail(
        self,
        user: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit trail with optional filters"""
        
        if not self.audit_file.exists():
            return []
        
        entries = []
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply filters
                    if user and entry.get("user") != user:
                        continue
                    if action and entry.get("action") != action:
                        continue
                    if resource_type and entry.get("resource_type") != resource_type:
                        continue
                    if start_date and entry.get("timestamp") < start_date:
                        continue
                    if end_date and entry.get("timestamp") > end_date:
                        continue
                    
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return sorted(entries, key=lambda x: x["timestamp"], reverse=True)
    
    def get_user_activity(self, user: str) -> Dict[str, Any]:
        """Get activity summary for a specific user"""
        entries = self.get_audit_trail(user=user)
        
        if not entries:
            return {"user": user, "total_actions": 0, "actions": {}}
        
        action_counts = {}
        resource_types = {}
        recent_actions = []
        
        for entry in entries:
            action = entry.get("action", "unknown")
            resource_type = entry.get("resource_type", "unknown")
            
            action_counts[action] = action_counts.get(action, 0) + 1
            resource_types[resource_type] = resource_types.get(resource_type, 0) + 1
            
            if len(recent_actions) < 10:
                recent_actions.append({
                    "action": action,
                    "resource": f"{resource_type}:{entry.get('resource_id', 'unknown')}",
                    "timestamp": entry.get("timestamp")
                })
        
        return {
            "user": user,
            "total_actions": len(entries),
            "actions": action_counts,
            "resource_types": resource_types,
            "recent_actions": recent_actions,
            "first_action": entries[-1]["timestamp"] if entries else None,
            "last_action": entries[0]["timestamp"] if entries else None
        }
    
    def get_resource_history(self, resource_type: str, resource_id: str) -> List[Dict[str, Any]]:
        """Get history of actions on a specific resource"""
        return self.get_audit_trail(resource_type=resource_type)
    
    def _generate_audit_id(self) -> str:
        """Generate unique audit ID"""
        timestamp = datetime.now().isoformat()
        random_data = f"{timestamp}_{hash(timestamp)}"
        return hashlib.sha256(random_data.encode()).hexdigest()[:16]
    
    def _get_client_ip(self) -> str:
        """Get client IP address (simplified)"""
        # In a real implementation, this would get the actual client IP
        return "127.0.0.1"
    
    def _get_user_agent(self) -> str:
        """Get user agent (simplified)"""
        # In a real implementation, this would get the actual user agent
        return "ModelSync-CLI/1.0"

class CollaborationManager:
    """Manages collaboration features"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.collab_dir = self.repo_path / ".modelsync" / "collaboration"
        self.users_file = self.collab_dir / "users.json"
        self.permissions_file = self.collab_dir / "permissions.json"
        self.audit_log = AuditLog(str(self.repo_path))
        ensure_directory(str(self.collab_dir))
        self._load_data()
    
    def _load_data(self):
        """Load collaboration data"""
        self.users = read_json_file(str(self.users_file)) or {}
        self.permissions = read_json_file(str(self.permissions_file)) or {}
    
    def _save_data(self):
        """Save collaboration data"""
        write_json_file(str(self.users_file), self.users)
        write_json_file(str(self.permissions_file), self.permissions)
    
    def add_user(
        self,
        username: str,
        email: str,
        role: str = "contributor",
        permissions: List[str] = None
    ) -> bool:
        """Add a user to the collaboration system"""
        
        if username in self.users:
            print(f"❌ User '{username}' already exists")
            return False
        
        user_data = {
            "username": username,
            "email": email,
            "role": role,
            "permissions": permissions or self._get_default_permissions(role),
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        self.users[username] = user_data
        self._save_data()
        
        # Log user addition
        self.audit_log.log_action(
            action="user_added",
            user="system",
            resource_type="user",
            resource_id=username,
            details={"email": email, "role": role}
        )
        
        print(f"✅ User added: {username} ({role})")
        return True
    
    def update_user_permissions(
        self,
        username: str,
        permissions: List[str],
        updated_by: str
    ) -> bool:
        """Update user permissions"""
        
        if username not in self.users:
            print(f"❌ User '{username}' not found")
            return False
        
        old_permissions = self.users[username]["permissions"]
        self.users[username]["permissions"] = permissions
        self.users[username]["updated_at"] = datetime.now().isoformat()
        self._save_data()
        
        # Log permission change
        self.audit_log.log_action(
            action="permissions_updated",
            user=updated_by,
            resource_type="user",
            resource_id=username,
            details={
                "old_permissions": old_permissions,
                "new_permissions": permissions
            }
        )
        
        print(f"✅ Updated permissions for user: {username}")
        return True
    
    def check_permission(
        self,
        username: str,
        action: str,
        resource_type: str,
        resource_id: str
    ) -> bool:
        """Check if user has permission for an action"""
        
        if username not in self.users:
            return False
        
        user = self.users[username]
        if not user.get("active", True):
            return False
        
        # Check role-based permissions
        role = user.get("role", "contributor")
        if self._has_role_permission(role, action, resource_type):
            return True
        
        # Check specific permissions
        user_permissions = user.get("permissions", [])
        required_permission = f"{action}_{resource_type}"
        
        return required_permission in user_permissions
    
    def get_collaborators(self) -> List[Dict[str, Any]]:
        """Get list of all collaborators"""
        return list(self.users.values())
    
    def get_user_permissions(self, username: str) -> List[str]:
        """Get permissions for a specific user"""
        if username not in self.users:
            return []
        
        return self.users[username].get("permissions", [])
    
    def _get_default_permissions(self, role: str) -> List[str]:
        """Get default permissions for a role"""
        role_permissions = {
            "admin": [
                "read_all", "write_all", "delete_all", "manage_users",
                "manage_permissions", "view_audit", "export_data"
            ],
            "contributor": [
                "read_all", "write_models", "write_datasets", "write_experiments",
                "create_branches", "merge_branches"
            ],
            "viewer": [
                "read_all", "view_models", "view_datasets", "view_experiments"
            ]
        }
        
        return role_permissions.get(role, ["read_all"])
    
    def _has_role_permission(self, role: str, action: str, resource_type: str) -> bool:
        """Check if role has permission for action"""
        # Admin has all permissions
        if role == "admin":
            return True
        
        # Contributor can write to most resources
        if role == "contributor" and action in ["read", "write", "create"]:
            return True
        
        # Viewer can only read
        if role == "viewer" and action == "read":
            return True
        
        return False
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get activity summary for all users"""
        users = list(self.users.keys())
        summary = {
            "total_users": len(users),
            "active_users": len([u for u in self.users.values() if u.get("active", True)]),
            "user_activity": {}
        }
        
        for user in users:
            summary["user_activity"][user] = self.audit_log.get_user_activity(user)
        
        return summary
