"""Unit tests for tool wrappers"""
import pytest
from pathlib import Path
from app.tools.semgrep import SemgrepWrapper
from app.tools.bandit import BanditWrapper
from app.tools.trufflehog import TruffleHogWrapper
from app.tools.gitleaks import GitleaksWrapper
from app.tools.trivy import TrivyWrapper


class TestToolWrappers:
    """Test individual tool wrappers"""
    
    @pytest.fixture
    def test_project_path(self, tmp_path):
        """Create a temporary test project"""
        # Create a simple Python file with a vulnerability
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os

# Vulnerable code for testing
password = "hardcoded_secret_123"
os.system("ls")  # Shell injection risk
eval("print('test')")  # Use of eval
""")
        return tmp_path
    
    def test_semgrep_wrapper(self, test_project_path):
        """Test Semgrep wrapper can execute"""
        tool = SemgrepWrapper(test_project_path)
        assert tool.name == "semgrep"
        assert isinstance(tool.command, list)
        assert "semgrep" in tool.command
    
    def test_bandit_wrapper(self, test_project_path):
        """Test Bandit wrapper can execute"""
        tool = BanditWrapper(test_project_path)
        assert tool.name == "bandit"
        assert isinstance(tool.command, list)
        assert "bandit" in tool.command
    
    def test_trufflehog_wrapper(self, test_project_path):
        """Test TruffleHog wrapper can execute"""
        tool = TruffleHogWrapper(test_project_path)
        assert tool.name == "trufflehog"
        assert isinstance(tool.command, list)
        assert "trufflehog" in tool.command
    
    def test_gitleaks_wrapper(self, test_project_path):
        """Test Gitleaks wrapper can execute"""
        tool = GitleaksWrapper(test_project_path)
        assert tool.name == "gitleaks"
        assert isinstance(tool.command, list)
        assert "gitleaks" in tool.command
    
    def test_trivy_wrapper(self, test_project_path):
        """Test Trivy wrapper can execute"""
        tool = TrivyWrapper(test_project_path)
        assert tool.name == "trivy"
        assert isinstance(tool.command, list)
        assert "trivy" in tool.command
    
    def test_bandit_should_run_with_python(self, test_project_path):
        """Test Bandit only runs for Python projects"""
        tool = BanditWrapper(test_project_path)
        assert tool.should_run(["Python"], None) is True
        assert tool.should_run(["JavaScript"], None) is False
