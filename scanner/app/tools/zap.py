"""OWASP ZAP DAST tool wrapper"""
import json
import os
from pathlib import Path
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class ZapWrapper(ToolWrapper):
    """Wrapper for OWASP ZAP - Web Application Security Scanner"""
    
    @property
    def name(self) -> str:
        return "zap"
    
    @property
    def command(self) -> List[str]:
        target_url = self._get_target_url()
        if not target_url:
            return ["echo", "No target URL configured for ZAP scan"]
        
        return [
            "zap-baseline.py",
            "-t", target_url,
            "-J", "-",  # Output JSON to stdout
            "--auto"
        ]
    
    def get_version(self) -> str:
        """Get ZAP version"""
        import subprocess
        try:
            # ZAP baseline script version
            result = subprocess.run(
                ["zap-baseline.py", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "not found"
    
    def should_run(self, languages: List[str], framework: Optional[str] = None) -> bool:
        """Run ZAP only if target URL is configured"""
        return self._get_target_url() is not None

    def execute(self) -> List[FindingSchema]:
        """Execute ZAP and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"ZAP execution failed: {e}")
            return []
    
    def _get_target_url(self) -> Optional[str]:
        """Get target URL from environment or config file"""
        # Check environment variable first
        target = os.environ.get("ZAP_TARGET_URL", "")
        if target:
            return target
        
        # Check for target file in project
        target_file = self.project_path / ".zap_target"
        if target_file.exists():
            return target_file.read_text().strip()
        
        return None
    
    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse ZAP JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            
            # ZAP baseline scan JSON format
            site = data.get("site", [])
            for site_data in site:
                alerts = site_data.get("alerts", [])
                for alert in alerts:
                    finding = self._parse_alert(alert)
                    if finding:
                        findings.append(finding)
            
            return findings
            
        except json.JSONDecodeError:
            # If no valid JSON, return empty findings
            return []
    
    def _parse_alert(self, alert: dict) -> Optional[FindingSchema]:
        """Parse a single ZAP alert"""
        name = alert.get("name", "Unknown")
        risk = alert.get("riskdesc", "Informational")
        desc = alert.get("desc", "")
        solution = alert.get("solution", "")
        
        # Extract risk level (format: "High (High)")
        risk_level = risk.split()[0] if risk else "Informational"
        
        # Get first instance for location info
        instances = alert.get("instances", [])
        if instances:
            instance = instances[0]
            uri = instance.get("uri", "")
            method = instance.get("method", "")
            param = instance.get("param", "")
        else:
            uri = ""
            method = ""
            param = ""
        
        message = desc
        if solution:
            message += f" Solution: {solution}"
        
        return FindingSchema(
            type=f"DAST: {name}",
            severity=self._map_severity(risk_level),
            confidence=85,
            file_path=uri or "web-app",
            line_start=1,
            line_end=1,
            message=message,
            code_snippet=f"{method} {param}" if param else method,
            cwe_id=None,
            owasp_category=None
        )
    
    def _map_severity(self, zap_severity: str) -> SeverityLevel:
        """Map ZAP severity to standard levels"""
        mapping = {
            "High": SeverityLevel.HIGH,
            "Medium": SeverityLevel.MEDIUM,
            "Low": SeverityLevel.LOW,
            "Informational": SeverityLevel.INFO
        }
        return mapping.get(zap_severity, SeverityLevel.INFO)
