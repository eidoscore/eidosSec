import pytest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from app.tools.eslint import EslintWrapper
from app.schemas import SeverityLevel

@pytest.fixture
def eslint_wrapper():
    return EslintWrapper(project_path=Path("/tmp/test"))

def test_eslint_name(eslint_wrapper):
    assert eslint_wrapper.name == "eslint"

def test_eslint_command(eslint_wrapper):
    cmd = eslint_wrapper.command
    assert "eslint" in cmd
    assert "--format" in cmd
    assert "json" in cmd

def test_should_run(eslint_wrapper):
    assert eslint_wrapper.should_run(["JavaScript"], None) == True
    assert eslint_wrapper.should_run(["TypeScript"], None) == True
    assert eslint_wrapper.should_run(["Python"], None) == False

def test_parse_output(eslint_wrapper):
    mock_output = json.dumps([
        {
            "filePath": "/tmp/test/src/index.js",
            "messages": [
                {
                    "ruleId": "security/detect-eval-with-expression",
                    "severity": 2,
                    "message": "Eval with expression is dangerous",
                    "line": 10,
                    "column": 5
                },
                {
                    "ruleId": "no-console",
                    "severity": 1,
                    "message": "Unexpected console statement",
                    "line": 15,
                    "column": 1
                }
            ]
        }
    ])
    
    findings = eslint_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check first finding (Error -> HIGH)
    assert "eslint" in findings[0].type
    assert "security/detect-eval-with-expression" in findings[0].type
    assert findings[0].severity == "high"
    assert findings[0].line_start == 10
    assert "src/index.js" in findings[0].file_path
    
    # Check second finding (Warning -> MEDIUM)
    assert findings[1].severity == "medium"
    assert "no-console" in findings[1].type

def test_parse_output_empty(eslint_wrapper):
    findings = eslint_wrapper.parse_output("[]")
    assert len(findings) == 0

def test_parse_output_invalid_json(eslint_wrapper):
    findings = eslint_wrapper.parse_output("Invalid output")
    assert len(findings) == 0
