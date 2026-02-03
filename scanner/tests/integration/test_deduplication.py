import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from pathlib import Path
from app.orchestrator import ScanOrchestrator
from app.schemas import FindingSchema, SeverityLevel, ToolResultSchema, ToolStatus

@pytest.fixture
def mock_tools():
    # Helper to create a mock tool with specific findings
    def create_tool(name, findings):
        tool = MagicMock()
        tool.name = name
        tool.should_run.return_value = True
        
        result = ToolResultSchema(
            tool_name=name,
            status=ToolStatus.SUCCESS,
            findings=findings,
            execution_time=1.0
        )
        tool.execute.return_value = result
        return tool
    return create_tool

def test_deduplication_exact_match(mock_tools):
    """Test merging of exact duplicate findings from different tools"""
    
    # Finding 1 from Tool A
    f1 = FindingSchema(
        type="sqli",
        # description removed
        severity=SeverityLevel.HIGH,
        confidence=80,
        file_path="src/db.py",
        line_start=10,
        line_end=10,
        message="Possible SQL injection in query"
    )
    
    # Finding 2 from Tool B (Exact same location and type)
    f2 = FindingSchema(
        type="sqli",
        # description removed
        severity=SeverityLevel.HIGH,
        confidence=90,
        file_path="src/db.py",
        line_start=10,
        line_end=10,
        message="SQL injection vulnerability"
    )
    
    tools = [
        mock_tools("Tool A", [f1]),
        mock_tools("Tool B", [f2])
    ]
    
    with patch("app.orchestrator.ScanOrchestrator._filter_tools", return_value=tools):
        with patch("app.orchestrator.ScanOrchestrator._publish_progress"):
            orchestrator = ScanOrchestrator(Path("/tmp"), "test-scan", "redis://localhost")
            # Inject our mock tools into strict list for safety, though _filter_tools mock handles run
            orchestrator.all_tools = tools 
            
            result = orchestrator.run_scan()
            
            # Should be deduplicated to 1 finding
            assert len(result.findings) == 1
            # Confidence should increase (heuristic or max)
            assert result.findings[0].confidence >= 90
            assert "Tool A" in result.tools_executed
            assert "Tool B" in result.tools_executed

def test_deduplication_near_match(mock_tools):
    """Test merging of findings that are close in lines (e.g. +/- 2 lines)"""
    
    # Finding 1 at line 10
    f1 = FindingSchema(
        type="xss",
        # description removed
        severity=SeverityLevel.MEDIUM,
        confidence=50,
        file_path="views/index.html",
        line_start=10,
        line_end=10,
        message="XSS found"
    )
    
    # Finding 2 at line 12 (Close enough?)
    f2 = FindingSchema(
        type="xss",
        # description removed
        severity=SeverityLevel.MEDIUM,
        confidence=50,
        file_path="views/index.html",
        line_start=12,
        line_end=12,
        message="Reflected XSS"
    )
    
    tools = [
        mock_tools("Tool A", [f1]),
        mock_tools("Tool B", [f2])
    ]
    
    with patch("app.orchestrator.ScanOrchestrator._filter_tools", return_value=tools):
        with patch("app.orchestrator.ScanOrchestrator._publish_progress"):
            orchestrator = ScanOrchestrator(Path("/tmp"), "test-scan", "redis://localhost")
            result = orchestrator.run_scan()
            
            # If logic allows +/- 2 lines, this should be 1 finding
            # If not implemented yet, this test serves as TDD spec
            assert len(result.findings) == 1
