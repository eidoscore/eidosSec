import pytest
import json
from pathlib import Path
from app.tools.phpstan import PhpstanWrapper
from app.schemas import SeverityStr

@pytest.fixture
def phpstan_wrapper():
    return PhpstanWrapper(project_path=Path("/tmp/test"))

def test_phpstan_name(phpstan_wrapper):
    assert phpstan_wrapper.name == "phpstan"

def test_phpstan_command(phpstan_wrapper):
    cmd = phpstan_wrapper.command
    assert "phpstan" in cmd
    assert "analyse" in cmd
    assert "--error-format=json" in cmd

def test_should_run(phpstan_wrapper):
    assert phpstan_wrapper.should_run(["PHP"], None) == True
    assert phpstan_wrapper.should_run(["Python"], None) == False

def test_parse_output(phpstan_wrapper):
    mock_output = json.dumps({
        "files": {
            "/tmp/test/src/index.php": {
                "messages": [
                    {
                        "message": "Call to unsafe function eval() detected",
                        "line": 15,
                        "ignorable": True
                    },
                    {
                        "message": "Undefined variable $foo",
                        "line": 20,
                        "ignorable": True
                    }
                ]
            }
        },
        "errors": []
    })
    
    findings = phpstan_wrapper.parse_output(mock_output)
    
    assert len(findings) == 2
    
    # Check security finding (HIGH)
    assert findings[0].tool == "phpstan"
    assert findings[0].severity == SeverityStr.HIGH
    assert "Security Warning" in findings[0].title
    assert findings[0].line == 15
    assert "src/index.php" in findings[0].file_path
    
    # Check normal error (MEDIUM)
    assert findings[1].severity == SeverityStr.MEDIUM
    assert "Undefined variable" in findings[1].description

def test_parse_output_empty(phpstan_wrapper):
    findings = phpstan_wrapper.parse_output("{}")
    assert len(findings) == 0

def test_parse_output_invalid_json(phpstan_wrapper):
    findings = phpstan_wrapper.parse_output("Invalid output")
    assert len(findings) == 0
