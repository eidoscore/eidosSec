import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

# Import output schema from Scanner
from app.schemas import ScanResultSchema, FindingSchema, SeverityLevel, ToolStatus, ToolResultSchema
import importlib.util
import sys

# Dynamically load backend schemas to avoid 'app' package collision
# relative path from this test file: ../../../backend/app/schemas.py
backend_schemas_path = Path(__file__).parents[3] / "backend" / "app" / "schemas.py"

try:
    spec = importlib.util.spec_from_file_location("backend_schemas", str(backend_schemas_path))
    backend_schemas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend_schemas)
    FindingBase = backend_schemas.FindingBase
    BACKEND_AVAILABLE = True
except Exception as e:
    print(f"Failed to load backend schemas: {e}")
    BACKEND_AVAILABLE = False

@pytest.fixture
def mock_findings():
    return [
        FindingSchema(
            type="CVE-2023-1234",
            severity=SeverityLevel.CRITICAL,
            confidence=100,
            file_path="requirements.txt",
            line_start=1,
            line_end=1,
            message="Critical vulnerability in package X",
            metadata={
                "package": "package-x",
                "version": "1.0.0",
                "tool_specific": "some data"
            }
        )
    ]

@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend schemas not available for import")
def test_scanner_output_matches_backend_schema(mock_findings):
    """
    Verify that ScanResultSchema from Scanner can be correctly parsed 
    by Backend Pydantic models.
    """
    # Create a scanner result
    scan_result = ScanResultSchema(
        scan_id="123e4567-e89b-12d3-a456-426614174000",
        project_path="/tmp/project",
        status="completed",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        total_findings=len(mock_findings),
        findings=mock_findings,
        tools_executed=["safety"],
        tool_results=[],
        execution_time=1.5,
        metadata={"env": "test"}
    )
    
    # Serialize to dict (as if sent over HTTP)
    # Pydantic v2 use model_dump(), v1 uses dict() or json()
    # Using json() then load to ensure JSON compatibility
    json_data = scan_result.json()
    data = json.loads(json_data)
    
    # 1. Verify Findings compatibility
    # Backend FindingBase should accept the finding data
    
    for finding_data in data["findings"]:
        # backend.FindingBase has 'type', 'severity', etc.
        # It uses 'finding_metadata' instead of 'metadata'
        
        # Map metadata -> finding_metadata
        if "metadata" in finding_data:
            # Backend now expects 'metadata' directly (aliased field)
            pass
        
        # We might need to map enum values if backend expects strings
        # Scanner SeverityLevel.CRITICAL is "critical" (str enum)
        
        # validation should pass
        backend_finding = FindingBase(**finding_data)
        
        assert backend_finding.type == "CVE-2023-1234"
        assert backend_finding.metadata["package"] == "package-x"

    # 2. Verify Scan structure (if we have a matching schema)
    # Backend ScanDetailResponse likely resembles ScanResultSchema
    # but we might not have exact 1:1 mapping in this test without full backend mapping logic
    # The critical part is Findings structure consistency.

def test_deduplication_preserves_metadata(mock_findings):
    """
    Verify that deduplication logic preserves the metadata field
    which is critical for the new feature.
    """
    from app.orchestrator import ScanOrchestrator
    
    orchestrator = ScanOrchestrator(Path("/tmp"), "test", "redis://")
    
    # Duplicate findings
    f1 = mock_findings[0]
    f2 = mock_findings[0].copy()
    f2.metadata = {"package": "package-x", "version": "1.0.0", "other": "data"}
    
    # Mock deduplication (direct call to private method or wrapper)
    # Since we can't easily mock _deduplicate_findings internal logic without the full class setup,
    # we rely on the existing unit test, but this checks schema compliance essentially.
    
    merged = orchestrator._merge_findings([f1, f2])
    
    assert merged.metadata["duplicate_count"] == 2
    assert "package" in merged.metadata
