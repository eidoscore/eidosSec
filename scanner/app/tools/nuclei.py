"""Nuclei DAST tool wrapper"""
import json
import os
from pathlib import Path
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class NucleiWrapper(ToolWrapper):
    """Wrapper for Nuclei - Fast and customizable vulnerability scanner"""
    
    @property
    def name(self) -> str:
        return "nuclei"
    
    @property
    def command(self) -> List[str]:
        target_url = self._get_target_url()
        if not target_url:
            return ["echo", "No target URL configured for Nuclei scan"]
        
        return [
            "nuclei",
            "-u", target_url,
            "-json",
            "-silent",
            "-rate-limit", "100"
        ]
    
    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Run Nuclei only if target URL is configured"""
        return self._get_target_url() is not None
    
    def _get_target_url(self) -> Optional[str]:
        """Get target URL from environment or config file"""
        # Check environment variable first
        target = os.environ.get("NUCLEI_TARGET_URL", "")
        if target:
            return target
        
        # Check for target file in project
        target_file = self.project_path / ".nuclei_target"
        if target_file.exists():
            return target_file.read_text().strip()
        
        return None
    
    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse Nuclei JSON output (newline-delimited) to findings"""
        findings = []
        
        # Nuclei outputs JSON lines (one JSON object per line)
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            try:
                data = json.loads(line)
                finding = self._parse_finding(data)
                if finding:
                    findings.append(finding)
            except json.JSONDecodeError:
                continue
        
        return findings
    
    def _parse_finding(self, data: dict) -> Optional[FindingSchema]:
        """Parse a single Nuclei finding"""
        template_id = data.get("template-id", "unknown")
        info = data.get("info", {})
        name = info.get("name", template_id)
        severity = info.get("severity", "info")
        description = info.get("description", "")
        
        host = data.get("host", "")
        matched = data.get("matched-at", "")
        
        # Extract matcher name if available
        matcher = data.get("matcher-name", "")
        
        message = description or f"Vulnerability detected: {name}"
        if matcher:
            message += f" (Matcher: {matcher})"
        
        return FindingSchema(
            type=f"DAST: {name}",
            severity=self._map_severity(severity),
            confidence=90,
            file_path=host or "web-app",
            line_start=1,
            line_end=1,
            message=message,
            code_snippet=matched,
            cwe_id=None,
            owasp_category=None
        )
    
    def _map_severity(self, nuclei_severity: str) -> SeverityLevel:
        """Map Nuclei severity to standard levels"""
        mapping = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.HIGH,
            "medium": SeverityLevel.MEDIUM,
            "low": SeverityLevel.LOW,
            "info": SeverityLevel.INFO
        }
        return mapping.get(nuclei_severity.lower(), SeverityLevel.INFO)
