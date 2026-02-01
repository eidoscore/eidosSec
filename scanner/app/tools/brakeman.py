import json
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityStr

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
                
                # Default severity mapping
                severity = SeverityStr.MEDIUM
                if confidence == "High":
                    severity = SeverityStr.HIGH
                elif confidence == "Weak":
                    severity = SeverityStr.LOW
                
                # Normalize path relative to project root (usually Brakeman returns relative paths already)
                if str(self.project_path) in file_path:
                    file_path = file_path.replace(str(self.project_path), "").lstrip("/\\")

                finding = FindingSchema(
                    tool="brakeman",
                    title=f"{warning_type}: {message[:100]}",
                    description=message,
                    severity=severity,
                    file_path=file_path,
                    line=line,
                    column=0,
                    rule_id=warning.get("check_name", warning_type)
                )
                findings.append(finding)
                    
        except json.JSONDecodeError:
            pass
            
        return findings
