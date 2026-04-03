"""Semgrep SAST tool wrapper"""
from pathlib import Path
from typing import List, Optional
import json
import logging
import subprocess

from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel
from app.utils import extract_relative_path, sanitize_finding_message

logger = logging.getLogger(__name__)


class SemgrepWrapper(ToolWrapper):
    """Wrapper for Semgrep - multi-language SAST tool"""
    
    @property
    def name(self) -> str:
        return "semgrep"
    
    @property
    def command(self) -> List[str]:
        return [
            "semgrep",
            "--config=p/security-audit",
            "--config=p/owasp-top-10",
            "--json",
            "--no-git-ignore",
            "--quiet",
            "."
        ]
    
    def get_version(self) -> str:
        """Override to handle semgrep --version output format"""
        try:
            result = subprocess.run(
                ["semgrep", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Semgrep version is just the string
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "not found"
    
    def should_run(self, languages: List[str], framework: Optional[str] = None) -> bool:
        """Semgrep supports multiple languages"""
        supported = [
            "python", "javascript", "typescript", "go", "java", "ruby", 
            "php", "c", "cpp", "csharp", "ocaml", "rust", "swift"
        ]
        return any(lang.lower() in supported for lang in languages)

    def execute(self) -> List[FindingSchema]:
        """Execute Semgrep and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            logger.error(f"Semgrep execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse Semgrep JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            results = data.get("results", [])
            
            for result in results:
                try:
                    finding = self._parse_semgrep_result(result)
                    if finding:
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Failed to parse Semgrep result: {str(e)}")
                    continue
            
            return findings
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Semgrep JSON output: {str(e)}")
            return []
    
    def _parse_semgrep_result(self, result: dict) -> Optional[FindingSchema]:
        """Parse a single Semgrep result"""
        
        # Extract basic fields
        check_id = result.get("check_id", "unknown")
        file_path = result.get("path", "")
        
        # Get line numbers
        start_obj = result.get("start", {})
        end_obj = result.get("end", {})
        line_start = start_obj.get("line", 0)
        line_end = end_obj.get("line", 0)
        
        # Get extra metadata
        extra = result.get("extra", {})
        message = extra.get("message", "No description")
        severity_str = extra.get("severity", "WARNING")
        metadata = extra.get("metadata", {})
        code_snippet = extra.get("lines", "")
        
        # Map severity
        severity = self._map_severity(severity_str)
        
        # Extract CWE
        cwe_id = self._extract_cwe(metadata)
        
        # Extract OWASP category
        owasp_category = self._extract_owasp(metadata)
        
        # Make file path relative
        rel_path = extract_relative_path(file_path, self.project_path)
        
        return FindingSchema(
            type=check_id,
            severity=severity,
            confidence=85,  # Semgrep has high accuracy
            file_path=rel_path,
            line_start=max(1, line_start),
            line_end=max(line_start, line_end),
            message=sanitize_finding_message(message),
            code_snippet=code_snippet.strip() if code_snippet else None,
            cwe_id=cwe_id,
            owasp_category=owasp_category
        )
    
    def _map_severity(self, semgrep_severity: str) -> SeverityLevel:
        """Map Semgrep severity to standard levels"""
        mapping = {
            "ERROR": SeverityLevel.HIGH,
            "WARNING": SeverityLevel.MEDIUM,
            "INFO": SeverityLevel.LOW
        }
        return mapping.get(semgrep_severity.upper(), SeverityLevel.INFO)
    
    def _extract_cwe(self, metadata: dict) -> Optional[str]:
        """Extract CWE ID from metadata"""
        cwe = metadata.get("cwe", [])
        if cwe and isinstance(cwe, list) and len(cwe) > 0:
            # CWE can be string or number
            cwe_val = str(cwe[0]).replace("CWE-", "")
            return f"CWE-{cwe_val}"
        return None
    
    def _extract_owasp(self, metadata: dict) -> Optional[str]:
        """Extract OWASP category from metadata"""
        owasp = metadata.get("owasp", [])
        if owasp and isinstance(owasp, list) and len(owasp) > 0:
            return str(owasp[0])
        return None
