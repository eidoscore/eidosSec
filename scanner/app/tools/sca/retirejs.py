import json
import subprocess
from typing import List
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class RetireJsWrapper(ToolWrapper):
    def __init__(self, project_path: str):
        super().__init__(project_path)
    
    @property
    def name(self) -> str:
        return "retirejs"
    
    @property
    def requires_license(self) -> bool:
        return False
    
    def should_run(self, languages: List[str], framework: str) -> bool:
        return "javascript" in languages or "typescript" in languages or "node" in languages
    
    def run(self) -> List[FindingSchema]:
        output_file = self.results_dir / "retire.json"
        
        command = [
            "retire",
            "--outputformat", "json",
            "--outputpath", str(output_file),
            "--path", str(self.project_path)
        ]
        
        try:
            self.run_command(command)
            if output_file.exists():
                with open(output_file, 'r') as f:
                    return self.parse_output(f.read())
            return []
        except Exception as e:
            self.logger.error(f"Retire.js failed: {e}")
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
