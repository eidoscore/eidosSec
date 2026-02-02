import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.tools.safety import SafetyWrapper
from app.schemas import FindingSchema, SeverityLevel

@pytest.fixture
def safety_wrapper():
    return SafetyWrapper(project_path=Path("/tmp/test"))

def test_safety_name(safety_wrapper):
    assert safety_wrapper.name == "safety"

def test_safety_command(safety_wrapper):
    cmd = safety_wrapper.command
    assert "safety" in cmd
    assert "check" in cmd
    assert "--json" in cmd

def test_should_run(safety_wrapper):
    # Test without Python
    assert safety_wrapper.should_run(["JavaScript"], None) == False
    
    # Test with Python but no dependency files
    assert safety_wrapper.should_run(["Python"], None) == False

def test_parse_output(safety_wrapper):
    mock_output = json.dumps([
        {
            "package_name": "django",
            "installed_version": "1.11.29",
            "vulnerable_spec": "<2.0.0",
            "advisory": "Cross-site scripting (XSS) vulnerability",
            "severity": "high",
            "cve": "CVE-2020-9404"
        },
        {
            "package_name": "requests",
            "installed_version": "2.22.0",
            "vulnerable_spec": "<2.28.0",
            "advisory": "Information disclosure",
            "severity": "medium"
        }
    ])
    
    findings = safety_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check high severity finding with CVE
    assert findings[0].severity == "high"
    assert "django" in findings[0].type
    assert "CVE-2020-9404" in findings[0].type
    assert findings[0].confidence == 85
    
    # Check medium severity finding without CVE
    assert findings[1].severity == "medium"
    assert "requests" in findings[1].type
    assert findings[1].confidence == 75

def test_parse_output_empty(safety_wrapper):
    findings = safety_wrapper.parse_output("[]")
    assert len(findings) == 0

def test_parse_output_invalid_json(safety_wrapper):
    findings = safety_wrapper.parse_output("Invalid output")
    assert len(findings) == 0
