import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.tools.checkov import CheckovWrapper
from app.schemas import FindingSchema, SeverityLevel

@pytest.fixture
def checkov_wrapper():
    return CheckovWrapper(project_path=Path("/tmp/test"))

def test_checkov_name(checkov_wrapper):
    assert checkov_wrapper.name == "checkov"

def test_checkov_command(checkov_wrapper):
    cmd = checkov_wrapper.command
    assert "checkov" in cmd
    assert "-d" in cmd
    assert "--output" in cmd
    assert "json" in cmd

def test_should_run_with_terraform(checkov_wrapper):
    """Test detection of Terraform files"""
    with patch("pathlib.Path.rglob") as mock_rglob:
        mock_rglob.side_effect = lambda x: [Path("/tmp/test/main.tf")] if x == "*.tf" else []
        assert checkov_wrapper.should_run(["HCL"], None) == True

def test_should_run_with_kubernetes(checkov_wrapper):
    """Test detection of Kubernetes files"""
    with patch("pathlib.Path.rglob") as mock_rglob:
        mock_rglob.side_effect = lambda x: [Path("/tmp/test/k8s/deployment.yaml")] if "*.yaml" in x else []
        assert checkov_wrapper.should_run(["YAML"], "Kubernetes") == True

def test_should_run_with_docker(checkov_wrapper):
    """Test detection of Dockerfile"""
    with patch("pathlib.Path.rglob") as mock_rglob:
        mock_rglob.side_effect = lambda x: [Path("/tmp/test/Dockerfile")] if x == "Dockerfile" else []
        assert checkov_wrapper.should_run(["Dockerfile"], None) == True

def test_should_run_without_iac(checkov_wrapper):
    """Test that it doesn't run when no IaC files exist"""
    with patch("pathlib.Path.rglob", return_value=[]):
        with patch.object(Path, "is_dir", return_value=False):
            assert checkov_wrapper.should_run(["Python"], None) == False

def test_parse_output(checkov_wrapper):
    mock_output = json.dumps({
        "terraform": [
            {
                "check_id": "CKV_AWS_1",
                "check_name": "S3 bucket has Public Access Block enabled",
                "file_path": "/main.tf",
                "resource": "aws_s3_bucket.mybucket",
                "severity": "HIGH",
                "guideline": "https://docs.checkov.io/...",
                "file_line_range": [10, 20]
            },
            {
                "check_id": "CKV_AWS_2",
                "check_name": "Ensure EBS volume encryption",
                "file_path": "/ebs.tf",
                "resource": "aws_ebs_volume.data",
                "severity": "MEDIUM",
                "file_line_range": [5, 15]
            }
        ]
    })
    
    findings = checkov_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check S3 finding
    assert findings[0].severity == "high"
    assert "CKV_AWS_1" in findings[0].type
    assert findings[0].file_path == "/main.tf"
    assert findings[0].line_start == 10
    assert findings[0].line_end == 20
    
    # Check EBS finding
    assert findings[1].severity == "medium"
    assert "CKV_AWS_2" in findings[1].type

def test_parse_output_empty(checkov_wrapper):
    findings = checkov_wrapper.parse_output("{}")
    assert len(findings) == 0

def test_parse_output_invalid_json(checkov_wrapper):
    findings = checkov_wrapper.parse_output("Invalid output")
    assert len(findings) == 0

def test_map_severity(checkov_wrapper):
    """Test severity mapping"""
    assert checkov_wrapper._map_severity("CRITICAL") == SeverityLevel.CRITICAL
    assert checkov_wrapper._map_severity("HIGH") == SeverityLevel.HIGH
    assert checkov_wrapper._map_severity("MEDIUM") == SeverityLevel.MEDIUM
    assert checkov_wrapper._map_severity("LOW") == SeverityLevel.LOW
    assert checkov_wrapper._map_severity("INFO") == SeverityLevel.INFO
    assert checkov_wrapper._map_severity("UNKNOWN") == SeverityLevel.MEDIUM  # Default
    assert checkov_wrapper._map_severity("") == SeverityLevel.MEDIUM  # Default for empty
