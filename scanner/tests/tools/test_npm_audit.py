import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.tools.npm_audit import NpmAuditWrapper
from app.schemas import FindingSchema

@pytest.fixture
def npm_audit_wrapper():
    return NpmAuditWrapper(project_path=Path("/tmp/test"))

def test_npm_audit_name(npm_audit_wrapper):
    assert npm_audit_wrapper.name == "npm-audit"

def test_npm_audit_command(npm_audit_wrapper):
    cmd = npm_audit_wrapper.command
    assert "npm" in cmd
    assert "audit" in cmd
    assert "--json" in cmd

def test_should_run(npm_audit_wrapper):
    # Test with JS project
    assert npm_audit_wrapper.should_run(["JavaScript"], None) == True
    
    # Test without JS
    assert npm_audit_wrapper.should_run(["Python"], None) == False
    
    # Mock package.json existence
    with patch("pathlib.Path.exists", return_value=True):
        assert npm_audit_wrapper.should_run(["JavaScript"], None) == True

def test_parse_output(npm_audit_wrapper):
    mock_output = json.dumps({
        "vulnerabilities": {
            "express": {
                "via": [
                    {
                        "title": "Prototype Pollution",
                        "severity": "high",
                        "url": "https://npmjs.com/advisories/123"
                    }
                ]
            },
            "lodash": {
                "via": [
                    "lodash",
                    {
                        "title": "Command Injection CVE-2021-23337",
                        "severity": "critical",
                        "url": "https://npmjs.com/advisories/456"
                    }
                ]
            }
        }
    })
    
    findings = npm_audit_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check express finding
    assert "express" in findings[0].type
    assert findings[0].severity == "HIGH"
    assert "Prototype Pollution" in findings[0].message
    
    # Check lodash finding
    assert "lodash" in findings[1].type
    assert findings[1].severity == "CRITICAL"
    assert "CVE-2021-23337" in findings[1].type

def test_parse_output_empty(npm_audit_wrapper):
    findings = npm_audit_wrapper.parse_output("{}")
    assert len(findings) == 0

def test_parse_output_invalid_json(npm_audit_wrapper):
    findings = npm_audit_wrapper.parse_output("Invalid output")
    assert len(findings) == 0
