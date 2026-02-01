import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.tools.brakeman import BrakemanWrapper
from app.schemas import SeverityStr

@pytest.fixture
def brakeman_wrapper():
    return BrakemanWrapper(project_path=Path("/tmp/test"))

def test_brakeman_name(brakeman_wrapper):
    assert brakeman_wrapper.name == "brakeman"

def test_brakeman_command(brakeman_wrapper):
    cmd = brakeman_wrapper.command
    assert "brakeman" in cmd
    assert "--format" in cmd
    assert "json" in cmd

def test_should_run(brakeman_wrapper):
    assert brakeman_wrapper.should_run(["Ruby"], None) == True
    assert brakeman_wrapper.should_run([], "Rails") == True
    # Mock existence of Gemfile
    with patch("pathlib.Path.exists", return_value=True):
        assert brakeman_wrapper.should_run(["Python"], None) == True

def test_parse_output(brakeman_wrapper):
    mock_output = json.dumps({
        "warnings": [
            {
                "warning_type": "SQL Injection",
                "check_name": "SQL",
                "message": "Possible SQL injection",
                "file": "app/controllers/users_controller.rb",
                "line": 42,
                "confidence": "High"
            },
            {
                "warning_type": "Cross-Site Scripting",
                "check_name": "XSS",
                "message": "Unescaped output",
                "file": "app/views/users/show.html.erb",
                "line": 15,
                "confidence": "Medium"
            }
        ]
    })
    
    findings = brakeman_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check High confidence finding (High Severity)
    assert findings[0].tool == "brakeman"
    assert findings[0].severity == SeverityStr.HIGH
    assert "SQL Injection" in findings[0].title
    assert findings[0].line == 42
    
    # Check Medium confidence finding (Medium Severity)
    assert findings[1].severity == SeverityStr.MEDIUM
    assert "Cross-Site Scripting" in findings[1].title

def test_parse_output_empty(brakeman_wrapper):
    findings = brakeman_wrapper.parse_output("{}")
    assert len(findings) == 0

def test_parse_output_invalid_json(brakeman_wrapper):
    findings = brakeman_wrapper.parse_output("Invalid output")
    assert len(findings) == 0
