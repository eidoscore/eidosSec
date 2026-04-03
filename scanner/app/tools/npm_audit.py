import json
from pathlib import Path
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class NpmAuditWrapper(ToolWrapper):
    """Wrapper for npm audit - Node.js dependency vulnerability scanner"""
    
    @property
    def name(self) -> str:
        return "npm-audit"
    
    @property
    def command(self) -> List[str]:
        return [
            "npm", "audit", "--json"
        ]
    
    def get_version(self) -> str:
        """Get npm version"""
        import subprocess
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return f"npm {result.stdout.strip()}"
            return "unknown"
        except Exception:
            return "not found"
    
    def should_run(self, languages: List[str], framework: Optional[str] = None) -> bool:
        """Run if JavaScript/TypeScript detected and package.json exists"""
        is_js_ts = any(lang.lower() in ["javascript", "typescript"] for lang in languages)
        if not is_js_ts:
            return False
            
        return (self.project_path / "package.json").exists()

    def execute(self) -> List[FindingSchema]:
        """Execute npm audit and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"npm audit execution failed: {e}")
            return []
    
    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse npm audit JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            
            # Handle npm audit different output formats
            vulnerabilities = data.get("vulnerabilities", {})
            
            for pkg_name, vuln_data in vulnerabilities.items():
                for advisory in vuln_data.get("via", []):
                    if isinstance(advisory, str):
                        # Indirect dependency (just package name)
                        continue
                        
                    # Extract vulnerability details
                    severity = advisory.get("severity", "moderate").lower()
                    title = advisory.get("title", "")
                    url = advisory.get("url", "")
                    
                    # Create finding
                    finding = FindingSchema(
                        type=f"Vulnerable Dependency: {pkg_name}",
                        severity=self._map_severity(severity),
                        confidence=90 if "CVE-" in title else 80,
                        file_path="package.json",
                        line_start=1,
                        line_end=1,
                        message=f"{title} - {url}" if url else title,
                        code_snippet=pkg_name,
                        cwe_id=None,
                        owasp_category="A06:2021-Vulnerable and Outdated Components"
                    )
                    findings.append(finding)
            
            return findings
            
        except json.JSONDecodeError as e:
            return []
    
    def _map_severity(self, npm_severity: str) -> SeverityLevel:
        """Map npm audit severity to standard levels"""
        mapping = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.HIGH,
            "moderate": SeverityLevel.MEDIUM,
            "low": SeverityLevel.LOW
        }
        return mapping.get(npm_severity.lower(), SeverityLevel.MEDIUM)
