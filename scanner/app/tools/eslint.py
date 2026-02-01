import json
from typing import List, Optional, Dict, Any
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityStr

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

    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Run only if JavaScript or TypeScript is detected"""
        target_langs = {"JavaScript", "TypeScript", "Babel", "JSX", "TSX"}
        return any(lang in target_langs for lang in languages)

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
                        tool="eslint",
                        title=f"{rule_id}: {message[:100]}",
                        description=message,
                        severity=severity,
                        file_path=file_path,
                        line=line,
                        column=column,
                        rule_id=rule_id,
                        # ESLint doesn't provide CWEs natively without plugins mapping
                        # We could map common security rules here if needed
                    )
                    findings.append(finding)
                    
        except json.JSONDecodeError:
            # Fallback or empty if valid JSON isn't returned (e.g. empty string)
            pass
            
        return findings

    def _map_severity(self, eslint_severity: int) -> SeverityStr:
        # ESLint: 1 = Warning, 2 = Error
        if eslint_severity == 2:
            return SeverityStr.HIGH
        elif eslint_severity == 1:
            return SeverityStr.MEDIUM
        return SeverityStr.LOW
