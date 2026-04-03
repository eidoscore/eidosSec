import json
from typing import List, Optional, Dict, Any
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class EslintWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "eslint"

    @property
    def command(self) -> List[str]:
        # Using the base configured .eslintrc or allowing eslint to find one
        # Running on current directory "."
        # Output format json
        return ["eslint", ".", "--format", "json", "--no-error-on-unmatched-pattern"]

    def get_version(self) -> str:
        """Get ESLint version"""
        import subprocess
        try:
            result = subprocess.run(
                ["eslint", "--version"],
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
        """Run only if JavaScript or TypeScript is detected"""
        target_langs = {"javascript", "typescript", "babel", "jsx", "tsx", "node"}
        return any(lang.lower() in target_langs for lang in languages)

    def execute(self) -> List[FindingSchema]:
        """Execute ESLint and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"ESLint execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            data = json.loads(output)
            # ESLint returns a list of file objects
            # [ { "filePath": "...", "messages": [ { "ruleId": "...", "severity": 2, "message": "...", ... } ] } ]
            
            for file_result in data:
                file_path = file_result.get("filePath", "")
                
                # Make path relative to project root if possible
                if str(self.project_path) in file_path:
                    file_path = file_path.replace(str(self.project_path), "").lstrip("/\\")

                for msg in file_result.get("messages", []):
                    rule_id = msg.get("ruleId")
                    if not rule_id:
                        continue  # Skip parsing errors without rule IDs
                        
                    severity = self._map_severity(msg.get("severity", 1))
                    line = msg.get("line", 0)
                    column = msg.get("column", 0)
                    message = msg.get("message", "")
                    
                    finding = FindingSchema(
                        type=f"eslint:{rule_id}",
                        severity=severity,
                        confidence=85 if severity == SeverityLevel.HIGH else (60 if severity == SeverityLevel.MEDIUM else 40),
                        file_path=file_path,
                        line_start=line if line > 0 else 1,
                        line_end=line if line > 0 else 1,
                        message=message,
                        cwe_id=None,
                        owasp_category=None
                    )
                    findings.append(finding)
                    
        except json.JSONDecodeError:
            # Fallback or empty if valid JSON isn't returned (e.g. empty string)
            pass
            
        return findings

    def _map_severity(self, eslint_severity: int) -> SeverityLevel:
        # ESLint: 1 = Warning, 2 = Error
        if eslint_severity == 2:
            return SeverityLevel.HIGH
        elif eslint_severity == 1:
            return SeverityLevel.MEDIUM
        return SeverityLevel.LOW
