import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from app.tools.zap import ZapWrapper
from app.schemas import FindingSchema

@pytest.fixture
def zap_wrapper():
    return ZapWrapper(project_path=Path("/tmp/test"))

def test_zap_name(zap_wrapper):
    assert zap_wrapper.name == "zap"

def test_zap_no_target(zap_wrapper):
    """Test that ZAP returns no-op command when no target is set"""
    with patch.dict("os.environ", {}, clear=True):
        cmd = zap_wrapper.command
        assert "echo" in cmd

def test_zap_with_env_target(zap_wrapper):
    """Test that ZAP uses environment variable target"""
    with patch.dict("os.environ", {"ZAP_TARGET_URL": "http://example.com"}):
        cmd = zap_wrapper.command
        assert "zap-baseline.py" in cmd
        assert "http://example.com" in cmd

def test_zap_with_file_target(zap_wrapper):
    """Test that ZAP reads target from file"""
    with patch.dict("os.environ", {}, clear=True):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value="http://target.com"):
                cmd = zap_wrapper.command
                assert "http://target.com" in cmd

def test_should_run_with_target(zap_wrapper):
    with patch.dict("os.environ", {"ZAP_TARGET_URL": "http://example.com"}):
        assert zap_wrapper.should_run(["JavaScript"], None) == True

def test_should_run_without_target(zap_wrapper):
    with patch.dict("os.environ", {}, clear=True):
        with patch("pathlib.Path.exists", return_value=False):
            assert zap_wrapper.should_run(["JavaScript"], None) == False

def test_parse_output(zap_wrapper):
    mock_output = json.dumps({
        "site": [{
            "alerts": [
                {
                    "name": "SQL Injection",
                    "riskdesc": "High (High)",
                    "desc": "SQL injection vulnerability detected",
                    "solution": "Use parameterized queries",
                    "instances": [{
                        "uri": "http://example.com/search",
                        "method": "POST",
                        "param": "query"
                    }]
                },
                {
                    "name": "XSS",
                    "riskdesc": "Medium (Medium)",
                    "desc": "Cross-site scripting",
                    "solution": "Encode output",
                    "instances": [{
                        "uri": "http://example.com/profile",
                        "method": "GET",
                        "param": "name"
                    }]
                }
            ]
        }]
    })
    
    findings = zap_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check SQL injection finding
    assert findings[0].severity == "HIGH"
    assert "SQL Injection" in findings[0].type
    assert "http://example.com/search" in findings[0].file_path
    
    # Check XSS finding
    assert findings[1].severity == "MEDIUM"
    assert "XSS" in findings[1].type

def test_parse_output_empty(zap_wrapper):
    findings = zap_wrapper.parse_output("{}")
    assert len(findings) == 0

def test_parse_output_invalid_json(zap_wrapper):
    findings = zap_wrapper.parse_output("Invalid output")
    assert len(findings) == 0
