import json
import subprocess
from typing import List
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class ShellCheckWrapper(ToolWrapper):
    def __init__(self, project_path: str):
        super().__init__(project_path)
    
    @property
    def command(self) -> List[str]:
        """Base shellcheck command with JSON output format."""
        return ["shellcheck", "-f", "json"]

    @property
    def name(self) -> str:
        return "shellcheck"
    
    @property
    def requires_license(self) -> bool:
        return False
    
    def should_run(self, languages: List[str], framework: str) -> bool:
        return "shell" in languages or "bash" in languages
    
    def run(self) -> List[FindingSchema]:
        # ShellCheck requires finding files first.
        # find . -name "*.sh" -exec shellcheck -f json {} +
        # But we can also use 'find' and pipe to xargs if we want, or just loop in python.
        # Simpler: use shell globbing if shell=True or find command.
        
        # Let's verify if there are shell files first? 
        # Actually 'should_run' accounts for that usually, but we need to pass filenames to shellcheck.
        
        # We'll use a find command to get shell files and pass them.
        try:
            # Safer way: find files in python
            files = list(self.project_path.glob("**/*.sh"))
            if not files:
                return []
                
            # Convert to strings
            file_args = [str(f) for f in files]
            
            command = self.command + file_args
            
            # Run command
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            
            # ShellCheck returns JSON array or empty
            return self.parse_output(result.stdout)
            
        except Exception as e:
            self.logger.error(f"ShellCheck failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            data = json.loads(output)
            # [{"file": "script.sh", "line": 1, "column": 1, "level": "error", "code": 1234, "message": "..."}]
            
            for item in data:
                level = item.get("level", "info")
                severity = SeverityLevel.LOW
                if level == "error":
                    severity = SeverityLevel.HIGH
                elif level == "warning":
                    severity = SeverityLevel.MEDIUM
                    
                finding = FindingSchema(
                    type=f"SC{item.get('code')}",
                    severity=severity,
                    confidence=100,
                    file_path=item.get("file", "unknown"),
                    line_start=item.get("line", 1),
                    line_end=item.get("endLine", item.get("line", 1)),
                    message=item.get("message", ""),
                    metadata={
                        "tool": "shellcheck",
                        "code": item.get("code")
                    }
                )
                findings.append(finding)
        except json.JSONDecodeError:
            pass # No output or invalid
        except Exception as e:
            self.logger.error(f"Failed to parse ShellCheck output: {e}")
            
        return findings
