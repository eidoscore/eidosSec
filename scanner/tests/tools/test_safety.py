import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.tools.safety import SafetyWrapper
from app.schemas import SeverityLevel

@pytest.fixture
def safety_wrapper():
    return SafetyWrapper(project_path=Path("/tmp/test"))

def test_safety_name(safety_wrapper):
    assert safety_wrapper.name == "safety"

def test_safety_command(safety_wrapper):
    cmd = safety_wrapper.command
    assert "pipx" in cmd
    assert "safety" in cmd
    assert "check" in cmd
    assert "--json" in cmd

def test_should_run(safety_wrapper):
    assert safety_wrapper.should_run(["Python"], None) == True
    # Mock requirements.txt existence
    with patch("pathlib.Path.exists", return_value=True):
        assert safety_wrapper.should_run([], None) == True

def test_parse_output(safety_wrapper):
    mock_output = json.dumps({
        "vulnerabilities": [
            {
                "vulnerability_id": "CVE-2023-1234",
                "package_name": "requests",
                "analyzed_version": "2.0.0",
                "vulnerable_spec": "<2.31.0",
                "advisory": "Critical flaw in requests",
                "severity": {
                    "cvssv3": {
                        "base_score": 9.8
                    }
                }
            },
            {
                "vulnerability_id": "PYSEC-2023-5678",
                "package_name": "flask",
                "analyzed_version": "0.12",
                "advisory": "Medium issue in flask",
                "severity": {
                    "cvssv3": {
                        "base_score": 5.3
                    }
                }
            }
        ]
    })
    
    findings = safety_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check Critical finding
    assert findings[0].severity == SeverityLevel.CRITICAL
    assert "requests" in findings[0].type
    assert findings[0].metadata["package"] == "requests"
    
    # Check Medium finding
    assert findings[1].severity == SeverityLevel.MEDIUM
    assert "flask" in findings[1].type

def test_parse_output_empty(safety_wrapper):
    findings = safety_wrapper.parse_output("{}")
    assert len(findings) == 0

def test_parse_output_invalid_json(safety_wrapper):
    findings = safety_wrapper.parse_output("Invalid output")
    assert len(findings) == 0
