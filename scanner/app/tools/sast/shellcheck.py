import json
import subprocess
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class ShellCheckWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "shellcheck"
    
    @property
    def command(self) -> List[str]:
        """Base shellcheck command with JSON output format."""
        return ["shellcheck", "-f", "json"]

    def get_version(self) -> str:
        """Get ShellCheck version"""
        import subprocess
        try:
            result = subprocess.run(
                ["shellcheck", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # ShellCheck version output is multi-line
                for line in result.stdout.splitlines():
                    if line.startswith("version:"):
                        return line.replace("version:", "").strip()
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "not found"

    def should_run(self, languages: List[str], framework: Optional[str] = None) -> bool:
        shell_langs = ["shell", "bash", "sh"]
        return any(lang.lower() in shell_langs for lang in languages)
    
    def execute(self) -> List[FindingSchema]:
        """Execute shellcheck and return findings"""
        try:
            # Find shell files
            files = list(self.project_path.glob("**/*.sh"))
            if not files:
                return []
            
            # Convert to relative paths for cleaner output
            file_args = [str(f.relative_to(self.project_path)) for f in files]
            
            # Base execute_command returns stdout
            output = self.execute_command(self.command + file_args)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"ShellCheck execution failed: {e}")
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
