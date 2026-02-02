import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.tools.composer_audit import ComposerAuditWrapper
from app.schemas import FindingSchema, SeverityLevel

@pytest.fixture
def composer_audit_wrapper():
    return ComposerAuditWrapper(project_path=Path("/tmp/test"))

def test_composer_audit_name(composer_audit_wrapper):
    assert composer_audit_wrapper.name == "composer-audit"

def test_composer_audit_command(composer_audit_wrapper):
    cmd = composer_audit_wrapper.command
    assert "composer" in cmd
    assert "audit" in cmd
    assert "--format=json" in cmd

def test_should_run(composer_audit_wrapper):
    # Test without PHP
    assert composer_audit_wrapper.should_run(["Python"], None) == False
    
    # Test with PHP but no composer.json
    assert composer_audit_wrapper.should_run(["PHP"], None) == False

def test_parse_output(composer_audit_wrapper):
    mock_output = json.dumps({
        "advisories": {
            "symfony/http-kernel": [
                {
                    "title": "Remote code execution in symfony/http-kernel",
                    "cve": "CVE-2022-XXXX",
                    "link": "https://symfony.com/blog/cve-2022-xxxxx",
                    "affectedVersions": ">=5.0.0,<5.4.20",
                    "severity": "critical"
                }
            ],
            "guzzlehttp/guzzle": [
                {
                    "title": "Fix failure to release HTTP/1.1 connections",
                    "link": "https://github.com/guzzle/guzzle/security/advisories/GHSA-xxxx",
                    "severity": "high"
                }
            ]
        }
    })
    
    findings = composer_audit_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check symfony finding
    assert "symfony/http-kernel" in findings[0].type
    assert findings[0].severity == "critical"
    assert "CVE-2022-XXXX" in findings[0].type
    assert findings[0].confidence == 90
    
    # Check guzzle finding
    assert "guzzlehttp/guzzle" in findings[1].type
    assert findings[1].severity == "high"
    assert findings[1].confidence == 80

def test_parse_output_empty(composer_audit_wrapper):
    findings = composer_audit_wrapper.parse_output("{}")
    assert len(findings) == 0

def test_parse_output_no_advisories(composer_audit_wrapper):
    findings = composer_audit_wrapper.parse_output(json.dumps({"advisories": {}}))
    assert len(findings) == 0

def test_parse_output_invalid_json(composer_audit_wrapper):
    findings = composer_audit_wrapper.parse_output("Invalid output")
    assert len(findings) == 0
