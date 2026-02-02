import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from app.tools.cfn_nag import CfnNagWrapper
from app.schemas import FindingSchema

@pytest.fixture
def cfn_nag_wrapper():
    return CfnNagWrapper(project_path=Path("/tmp/test"))

def test_cfn_nag_name(cfn_nag_wrapper):
    assert cfn_nag_wrapper.name == "cfn-nag"

def test_cfn_nag_command(cfn_nag_wrapper):
    cmd = cfn_nag_wrapper.command
    assert "cfn-nag" in cmd
    assert "scan" in cmd
    assert "--output-format" in cmd
    assert "json" in cmd

def test_should_run_with_cloudformation(cfn_nag_wrapper):
    """Test detection of CloudFormation files"""
    mock_content = 'AWSTemplateFormatVersion: "2010-09-09"\nResources:\n  Bucket:'
    
    with patch("pathlib.Path.rglob") as mock_rglob:
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.read_text.return_value = mock_content
        mock_rglob.return_value = [mock_file]
        
        assert cfn_nag_wrapper.should_run(["YAML"], None) == True

def test_should_run_without_cloudformation(cfn_nag_wrapper):
    """Test that it doesn't run when no CF files exist"""
    with patch("pathlib.Path.rglob", return_value=[]):
        assert cfn_nag_wrapper.should_run(["Python"], None) == False

def test_parse_output(cfn_nag_wrapper):
    mock_output = json.dumps([
        {
            "filename": "template.yaml",
            "file_results": {
                "violations": [
                    {
                        "id": "F1",
                        "message": "S3 bucket should have encryption enabled",
                        "logical_resource_ids": ["MyBucket"],
                        "line_number": 15
                    },
                    {
                        "id": "W2",
                        "message": "Security group should restrict ingress",
                        "logical_resource_ids": ["MySecurityGroup"],
                        "line_number": 25
                    }
                ]
            }
        }
    ])
    
    findings = cfn_nag_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check encryption finding
    assert findings[0].severity == "HIGH"  # Contains "encryption"
    assert "F1" in findings[0].type
    assert findings[0].file_path == "template.yaml"
    assert findings[0].line_start == 15
    
    # Check security group finding
    assert findings[1].severity == "HIGH"  # Contains "Security"
    assert "W2" in findings[1].type

def test_parse_output_empty(cfn_nag_wrapper):
    findings = cfn_nag_wrapper.parse_output("[]")
    assert len(findings) == 0

def test_parse_output_invalid_json(cfn_nag_wrapper):
    findings = cfn_nag_wrapper.parse_output("Invalid output")
    assert len(findings) == 0

def test_determine_severity(cfn_nag_wrapper):
    """Test severity determination logic"""
    # High severity patterns
    assert cfn_nag_wrapper._determine_severity("F1", "Security group open") == "HIGH"
    assert cfn_nag_wrapper._determine_severity("F2", "Password in plaintext") == "HIGH"
    assert cfn_nag_wrapper._determine_severity("F3", "No encryption") == "HIGH"
    
    # Medium severity patterns
    assert cfn_nag_wrapper._determine_severity("W1", "Warning: should use") == "MEDIUM"
    
    # Low severity (default)
    assert cfn_nag_wrapper._determine_severity("I1", "Information") == "LOW"
