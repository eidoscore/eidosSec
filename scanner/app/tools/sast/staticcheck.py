import json
import subprocess
from typing import List
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class StaticcheckWrapper(ToolWrapper):
    def __init__(self, project_path: str):
        super().__init__(project_path)
        
    @property
    def command(self) -> List[str]:
        """CLI invocation for running staticcheck."""
        return ["staticcheck", "-f", "json", "./..."]

    @property
    def name(self) -> str:
        return "staticcheck"
        
    @property
    def requires_license(self) -> bool:
        return False # Free tool commonly
        
    def should_run(self, languages: List[str], framework: str) -> bool:
        return "go" in languages
        
    def run(self) -> List[FindingSchema]:
        try:
            # Run in project dir
            result = subprocess.run(
                self.command,
                cwd=self.project_path, 
                capture_output=True, 
                text=True, 
                check=False 
            )
            return self.parse_output(result.stdout)
        except Exception as e:
            self.logger.error(f"Staticcheck failed: {e}")
            return []
            
    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        for line in output.splitlines():
            try:
                data = json.loads(line)
                # Parse JSON line from staticcheck
                # {"code":"S1000","location":{"file":"main.go","line":10,"column":1},"end":{"file":"main.go","line":10,"column":1},"severity":"warning","message":"should use ..."}
                
                finding = FindingSchema(
                    type=data.get("code", "staticcheck"),
                    severity=SeverityLevel.MEDIUM, # Default
                    confidence=100,
                    file_path=data.get("location", {}).get("file", "unknown"),
                    line_start=data.get("location", {}).get("line", 1),
                    line_end=data.get("end", {}).get("line", 1),
                    message=data.get("message", ""),
                    metadata={"tool": "staticcheck", "raw": data}
                )
                findings.append(finding)
            except:
                continue
        return findings
