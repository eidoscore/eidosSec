import json
import subprocess
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class RetireJsWrapper(ToolWrapper):
    def __init__(self, project_path: str):
        super().__init__(project_path)
    
    @property
    def command(self) -> List[str]:
        """Retire.js CLI command with JSON output."""
        # Using stdout for simplicity if possible, but RetireJS prefers file output for JSON
        return [
            "retire",
            "--outputformat", "json",
            "--path", str(self.project_path)
        ]

    @property
    def name(self) -> str:
        return "retirejs"
    
    @property
    def requires_license(self) -> bool:
        return False
    
    def get_version(self) -> str:
        """Get Retire.js version"""
        import subprocess
        try:
            result = subprocess.run(
                ["retire", "--version"],
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
        js_langs = ["javascript", "typescript", "node"]
        return any(lang.lower() in js_langs for lang in languages)
    
    def execute(self) -> List[FindingSchema]:
        """Execute Retire.js and return findings"""
        try:
            # RetireJS outputs JSON to stdout by default if --outputpath is not provided
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"Retire.js execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            data = json.loads(output)
            # Structure: Array of objects with "file" and "results" (array of "vulnerabilities")
            
            for file_entry in data:
                file_path = file_entry.get("file", "unknown")
                for result in file_entry.get("results", []):
                    # version = result.get("version")
                    # component = result.get("component")
                    for vuln in result.get("vulnerabilities", []):
                        
                        severity_str = vuln.get("severity", "medium").lower()
                        severity = SeverityLevel.MEDIUM
                        if severity_str == "high": severity = SeverityLevel.HIGH
                        elif severity_str == "critical": severity = SeverityLevel.CRITICAL
                        elif severity_str == "low": severity = SeverityLevel.LOW
                        
                        identifiers = vuln.get("identifiers", {})
                        summary = identifiers.get("summary", vuln.get("info", ["Vulnerability"])[0])
                        
                        finding = FindingSchema(
                            type="Vulnerable Component",
                            severity=severity,
                            confidence=100,
                            file_path=file_path,
                            line_start=1, # Retire.js doesn't usually give line numbers for libs
                            line_end=1,
                            message=f"{result.get('component')}@{result.get('version')}: {summary}",
                            metadata={
                                "tool": "retirejs",
                                "component": result.get("component"),
                                "version": result.get("version"),
                                "cve": identifiers.get("CVE", []),
                                "info": vuln.get("info", [])
                            }
                        )
                        findings.append(finding)
        except Exception as e:
            self.logger.error(f"Failed to parse Retire.js output: {e}")
            
        return findings
