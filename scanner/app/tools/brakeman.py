import json
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class BrakemanWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "brakeman"

    @property
    def command(self) -> List[str]:
        # Run brakeman on current directory
        # Output format json
        # --quiet to reduce noise
        return ["brakeman", ".", "--format", "json", "--quiet", "--no-exit-on-warn", "--no-exit-on-error"]

    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Run if Ruby is detected or Rails framework is identified"""
        if "Ruby" in languages:
            return True
        if framework and "Rails" in framework:
            return True
        
        # Check for Gemfile or Rails structure if framework detection missed it
        gemfile = self.project_path / "Gemfile"
        return gemfile.exists()

    def _map_severity(self, brakeman_severity: str) -> SeverityLevel:
        if brakeman_severity == "High":
            return SeverityLevel.HIGH
        elif brakeman_severity == "Weak":
            return SeverityLevel.LOW
        else:
            return SeverityLevel.MEDIUM

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            data = json.loads(output)
            # Brakeman JSON format:
            # { "warnings": [ { "warning_type": "...", "message": "...", "file": "...", "line": 10, "confidence": "High" } ] }
            
            warnings = data.get("warnings", [])
            for warning in warnings:
                warning_type = warning.get("warning_type", "Unknown")
                message = warning.get("message", "")
                file_path = warning.get("file", "")
                line = warning.get("line", 0)
                confidence = warning.get("confidence", "Medium") # High, Medium, Weak
                
                severity = self._map_severity(confidence)
                
                # Normalize path relative to project root (usually Brakeman returns relative paths already)
                if str(self.project_path) in file_path:
                    file_path = file_path.replace(str(self.project_path), "").lstrip("/\\")

                finding = FindingSchema(
                    type=f"brakeman:{warning_type}",
                    severity=severity,
                    confidence=90 if confidence == "High" else (70 if confidence == "Medium" else 50),
                    file_path=file_path,
                    line_start=line if line > 0 else 1,
                    line_end=line if line > 0 else 1,
                    message=message,
                    cwe_id=None,
                    owasp_category="A01:2021 - Broken Access Control" if "Access" in warning_type else None
                )
                findings.append(finding)
                    
        except json.JSONDecodeError:
            pass
            
        return findings
