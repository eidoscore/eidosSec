import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.tools.nuclei import NucleiWrapper
from app.schemas import FindingSchema

@pytest.fixture
def nuclei_wrapper():
    return NucleiWrapper(project_path=Path("/tmp/test"))

def test_nuclei_name(nuclei_wrapper):
    assert nuclei_wrapper.name == "nuclei"

def test_nuclei_no_target(nuclei_wrapper):
    """Test that Nuclei returns no-op command when no target is set"""
    with patch.dict("os.environ", {}, clear=True):
        cmd = nuclei_wrapper.command
        assert "echo" in cmd

def test_nuclei_with_env_target(nuclei_wrapper):
    """Test that Nuclei uses environment variable target"""
    with patch.dict("os.environ", {"NUCLEI_TARGET_URL": "http://example.com"}):
        cmd = nuclei_wrapper.command
        assert "nuclei" in cmd
        assert "http://example.com" in cmd

def test_should_run_with_target(nuclei_wrapper):
    with patch.dict("os.environ", {"NUCLEI_TARGET_URL": "http://example.com"}):
        assert nuclei_wrapper.should_run(["JavaScript"], None) == True

def test_should_run_without_target(nuclei_wrapper):
    with patch.dict("os.environ", {}, clear=True):
        with patch("pathlib.Path.exists", return_value=False):
            assert nuclei_wrapper.should_run(["JavaScript"], None) == False

def test_parse_output(nuclei_wrapper):
    # Nuclei outputs JSON lines (NDJSON format)
    mock_output = json.dumps({
        "template-id": "cve-2021-44228",
        "info": {
            "name": "Log4j RCE",
            "severity": "critical",
            "description": "Apache Log4j2 remote code execution"
        },
        "host": "http://example.com",
        "matched-at": "http://example.com/api/login",
        "matcher-name": "log4j-jndi"
    }) + "\n" + json.dumps({
        "template-id": "xss-reflected",
        "info": {
            "name": "Reflected XSS",
            "severity": "high",
            "description": "Cross-site scripting vulnerability"
        },
        "host": "http://example.com",
        "matched-at": "http://example.com/search?q=test"
    })
    
    findings = nuclei_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check Log4j finding
    assert findings[0].severity == "CRITICAL"
    assert "Log4j RCE" in findings[0].type
    assert "http://example.com" in findings[0].file_path
    
    # Check XSS finding
    assert findings[1].severity == "HIGH"
    assert "Reflected XSS" in findings[1].type

def test_parse_output_empty(nuclei_wrapper):
    findings = nuclei_wrapper.parse_output("")
    assert len(findings) == 0

def test_parse_output_invalid_json(nuclei_wrapper):
    findings = nuclei_wrapper.parse_output("Invalid output\nMore invalid")
    assert len(findings) == 0

def test_parse_output_partial_invalid(nuclei_wrapper):
    """Test parsing when some lines are invalid JSON"""
    mock_output = json.dumps({
        "template-id": "test",
        "info": {"name": "Test", "severity": "low"},
        "host": "http://test.com"
    }) + "\nInvalid line\n" + json.dumps({
        "template-id": "test2",
        "info": {"name": "Test2", "severity": "medium"},
        "host": "http://test2.com"
    })
    
    findings = nuclei_wrapper.parse_output(mock_output)
    assert len(findings) == 2
