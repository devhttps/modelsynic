"""
ModelSync API - REST API for ModelSync
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from modelsync.core.versioning import ModelSyncRepo
import os

app = FastAPI(
    title="ModelSync API",
    description="REST API for ModelSync - Version control for AI projects",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CommitRequest(BaseModel):
    message: str
    author_name: Optional[str] = None
    author_email: Optional[str] = None

class AddFilesRequest(BaseModel):
    files: List[str]

class InitRequest(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None

class StatusResponse(BaseModel):
    branch: str
    staged_files: List[str]
    modified_files: List[str]
    total_tracked: int
    total_staged: int

class CommitResponse(BaseModel):
    commit_hash: str
    message: str
    author: str
    timestamp: str

# Dependency to get repository
def get_repo() -> ModelSyncRepo:
    return ModelSyncRepo()

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "ModelSync API",
        "version": "0.1.0",
        "description": "Version control for AI projects",
        "endpoints": {
            "health": "/health",
            "init": "/init",
            "status": "/status",
            "add": "/add",
            "commit": "/commit",
            "log": "/log"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "ModelSync API"}

@app.post("/init")
def init_repository(request: InitRequest, repo: ModelSyncRepo = Depends(get_repo)):
    """Initialize a new ModelSync repository"""
    try:
        success = repo.init(request.user_name or "", request.user_email or "")
        if success:
            return {"message": "Repository initialized successfully", "status": "success"}
        else:
            return {"message": "Repository already initialized", "status": "info"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status(repo: ModelSyncRepo = Depends(get_repo)):
    """Get repository status"""
    if not repo.is_initialized():
        raise HTTPException(status_code=400, detail="Not a ModelSync repository")
    
    status_info = repo.status()
    return StatusResponse(**status_info)

@app.post("/add")
def add_files(request: AddFilesRequest, repo: ModelSyncRepo = Depends(get_repo)):
    """Add files to staging area"""
    if not repo.is_initialized():
        raise HTTPException(status_code=400, detail="Not a ModelSync repository")
    
    if not request.files:
        raise HTTPException(status_code=400, detail="No files specified")
    
    added_files = repo.add(request.files)
    return {
        "message": f"Added {len(added_files)} files to staging area",
        "added_files": list(added_files.keys()),
        "status": "success"
    }

@app.post("/commit")
def create_commit(request: CommitRequest, repo: ModelSyncRepo = Depends(get_repo)):
    """Create a new commit"""
    if not repo.is_initialized():
        raise HTTPException(status_code=400, detail="Not a ModelSync repository")
    
    commit_hash = repo.commit(
        request.message,
        request.author_name or "",
        request.author_email or ""
    )
    
    if not commit_hash:
        raise HTTPException(status_code=400, detail="Failed to create commit")
    
    return {
        "message": "Commit created successfully",
        "commit_hash": commit_hash,
        "status": "success"
    }

@app.get("/log")
def get_log(oneline: bool = False, repo: ModelSyncRepo = Depends(get_repo)):
    """Get commit history"""
    if not repo.is_initialized():
        raise HTTPException(status_code=400, detail="Not a ModelSync repository")
    
    commits = repo.log(oneline)
    return {
        "commits": commits,
        "total_commits": len(commits),
        "oneline": oneline
    }

@app.get("/branches")
def list_branches(repo: ModelSyncRepo = Depends(get_repo)):
    """List all branches"""
    if not repo.is_initialized():
        raise HTTPException(status_code=400, detail="Not a ModelSync repository")
    
    # TODO: Implement branch listing
    return {"message": "Branch listing not yet implemented", "branches": []}

@app.get("/diff")
def get_diff(repo: ModelSyncRepo = Depends(get_repo)):
    """Get file differences"""
    if not repo.is_initialized():
        raise HTTPException(status_code=400, detail="Not a ModelSync repository")
    
    status_info = repo.status()
    return {
        "modified_files": status_info.get('modified_files', []),
        "staged_files": status_info.get('staged_files', [])
    }

@app.get("/config")
def get_config(repo: ModelSyncRepo = Depends(get_repo)):
    """Get repository configuration"""
    if not repo.is_initialized():
        raise HTTPException(status_code=400, detail="Not a ModelSync repository")
    
    # TODO: Implement config reading
    return {"message": "Configuration reading not yet implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)