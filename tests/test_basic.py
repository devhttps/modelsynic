"""
Basic tests for ModelSync
"""

import pytest
import tempfile
import os
from pathlib import Path
from modelsync.core.versioning import ModelSyncRepo

class TestModelSyncRepo:
    """Test cases for ModelSyncRepo"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = ModelSyncRepo(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init_repository(self):
        """Test repository initialization"""
        # Should not be initialized initially
        assert not self.repo.is_initialized()
        
        # Initialize repository
        result = self.repo.init("Test User", "test@example.com")
        assert result is True
        assert self.repo.is_initialized()
        
        # Check if directories were created
        assert (Path(self.temp_dir) / ".modelsync").exists()
        assert (Path(self.temp_dir) / ".modelsync" / "objects").exists()
        assert (Path(self.temp_dir) / ".modelsync" / "refs").exists()
        assert (Path(self.temp_dir) / ".modelsync" / "refs" / "heads").exists()
    
    def test_add_files(self):
        """Test adding files to staging area"""
        # Initialize repository first
        self.repo.init("Test User", "test@example.com")
        
        # Create test files
        test_file1 = Path(self.temp_dir) / "test1.py"
        test_file2 = Path(self.temp_dir) / "test2.json"
        
        test_file1.write_text("print('hello world')")
        test_file2.write_text('{"test": "data"}')
        
        # Add files
        added_files = self.repo.add(["test1.py", "test2.json"])
        
        assert len(added_files) == 2
        assert "test1.py" in added_files
        assert "test2.json" in added_files
    
    def test_commit(self):
        """Test creating commits"""
        # Initialize repository
        self.repo.init("Test User", "test@example.com")
        
        # Create and add test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello world')")
        
        self.repo.add(["test.py"])
        
        # Create commit
        commit_hash = self.repo.commit("Test commit")
        
        assert commit_hash is not None
        assert len(commit_hash) == 64  # SHA-256 hash length
    
    def test_status(self):
        """Test repository status"""
        # Initialize repository
        self.repo.init("Test User", "test@example.com")
        
        # Create test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello world')")
        
        # Check status before adding
        status = self.repo.status()
        assert status["total_tracked"] >= 1
        assert status["total_staged"] == 0
        
        # Add file and check status
        self.repo.add(["test.py"])
        status = self.repo.status()
        assert status["total_staged"] == 1
        assert "test.py" in status["staged_files"]
    
    def test_log(self):
        """Test commit log"""
        # Initialize repository
        self.repo.init("Test User", "test@example.com")
        
        # Create and commit test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello world')")
        
        self.repo.add(["test.py"])
        commit_hash = self.repo.commit("Test commit")
        
        # Check log
        commits = self.repo.log()
        assert len(commits) >= 1  # At least initial commit + our commit
        
        # Find our commit
        our_commit = next((c for c in commits if c["message"] == "Test commit"), None)
        assert our_commit is not None
        assert our_commit["hash"] == commit_hash

if __name__ == "__main__":
    pytest.main([__file__])