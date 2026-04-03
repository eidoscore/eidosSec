import json
import subprocess
from typing import List, Optional
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
        
    def get_version(self) -> str:
        """Get Staticcheck version"""
        import subprocess
        try:
            result = subprocess.run(
                ["staticcheck", "-version"],
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
        return any(lang.lower() == "go" for lang in languages)
        
    def execute(self) -> List[FindingSchema]:
        """Execute staticcheck and return findings"""
        try:
            # Base execute captures stdout
            output = super().execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"Staticcheck execution failed: {e}")
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
