"""Bandit Python SAST tool wrapper"""
from pathlib import Path
from typing import List, Optional
import json
import logging

from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel
from app.utils import extract_relative_path, sanitize_finding_message

logger = logging.getLogger(__name__)


class BanditWrapper(ToolWrapper):
    """Wrapper for Bandit - Python security linter"""
    
    @property
    def name(self) -> str:
        return "bandit"
    
    @property
    def command(self) -> List[str]:
        return [
            "bandit",
            "-r",  # Recursive
            ".",
            "-f", "json",  # JSON format
            "--quiet"
        ]
    
    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Only run Bandit if Python is detected"""
        return "Python" in languages
    
    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse Bandit JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            results = data.get("results", [])
            
            for result in results:
                try:
                    finding = self._parse_bandit_result(result)
                    if finding:
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Failed to parse Bandit result: {str(e)}")
                    continue
            
            return findings
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bandit JSON output: {str(e)}")
            return []
    
    def _parse_bandit_result(self, result: dict) -> Optional[FindingSchema]:
        """Parse a single Bandit result"""
        
        # Extract fields
        test_id = result.get("test_id", "unknown")
        test_name = result.get("test_name", "")
        file_path = result.get("filename", "")
        line_number = result.get("line_number", 0)
        code_snippet = result.get("code", "")
        issue_text = result.get("issue_text", "No description")
        
        # Severity and confidence from Bandit
        severity_str = result.get("issue_severity", "LOW")
        confidence_str = result.get("issue_confidence", "LOW")
        
        # Map severity
        severity = self._map_severity(severity_str)
        
        # Map confidence to numeric
        confidence = self._map_confidence(confidence_str, severity)
        
        # Extract CWE if available
        cwe_id = self._extract_cwe(result)
        
        # Make file path relative
        rel_path = extract_relative_path(file_path, self.project_path)
        
        # Create finding
        finding_type = f"{test_id}: {test_name}" if test_name else test_id
        
        return FindingSchema(
            type=finding_type,
            severity=severity,
            confidence=confidence,
            file_path=rel_path,
            line_start=max(1, line_number),
            line_end=max(1, line_number),
            message=sanitize_finding_message(issue_text),
            code_snippet=code_snippet.strip() if code_snippet else None,
            cwe_id=cwe_id,
            owasp_category=None
        )
    
    def _map_severity(self, bandit_severity: str) -> SeverityLevel:
        """Map Bandit severity to standard levels"""
        mapping = {
            "HIGH": SeverityLevel.HIGH,
            "MEDIUM": SeverityLevel.MEDIUM,
            "LOW": SeverityLevel.LOW
        }
        return mapping.get(bandit_severity.upper(), SeverityLevel.INFO)
    
    def _map_confidence(self, confidence_str: str, severity: SeverityLevel) -> int:
        """Map Bandit confidence to numeric score"""
        base_confidence = {
            "HIGH": 90,
            "MEDIUM": 75,
            "LOW": 60
        }
        
        confidence = base_confidence.get(confidence_str.upper(), 70)
        
        # Adjust based on severity
        if severity == SeverityLevel.HIGH:
            confidence += 5
        elif severity == SeverityLevel.LOW:
            confidence -= 5
        
        return max(0, min(100, confidence))
    
    def _extract_cwe(self, result: dict) -> Optional[str]:
        """Extract CWE from Bandit result if available"""
        # Bandit doesn't always provide CWE, but some tests map to common CWEs
        test_id = result.get("test_id", "")
        
        # Common Bandit test ID to CWE mappings
        cwe_mapping = {
            "B201": "CWE-78",   # Flask debug mode
            "B301": "CWE-502",  # Pickle
            "B302": "CWE-327",  # Bad crypto
            "B303": "CWE-327",  # MD5/SHA1
            "B304": "CWE-327",  # Insecure cipher
            "B305": "CWE-327",  # Insecure cipher mode
            "B306": "CWE-377",  # mktemp
            "B307": "CWE-20",   # eval
            "B308": "CWE-22",   # Path traversal
            "B501": "CWE-295",  # SSL verify disabled
            "B502": "CWE-295",  # SSL bad version
            "B503": "CWE-295",  # SSL bad ciphers
            "B506": "CWE-20",   # YAML load
            "B601": "CWE-78",   # Shell injection
            "B602": "CWE-78",   # Shell with shell=True
            "B603": "CWE-78",   # Subprocess without shell
            "B605": "CWE-78",   # Shell command
            "B607": "CWE-78",   # Partial path subprocess
        }
        
        return cwe_mapping.get(test_id)
