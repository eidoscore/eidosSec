import json
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class PhpstanWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "phpstan"

    @property
    def command(self) -> List[str]:
        # Analyse current directory
        # Output format json
        # Level 5 is a good balance for security checks
        return ["phpstan", "analyse", ".", "--level=5", "--no-progress", "--error-format=json"]

    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Run only if PHP is detected"""
        return "PHP" in languages

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            data = json.loads(output)
            # PHPStan JSON format:
            # { "files": { "path/to/file.php": { "messages": [ { "message": "...", "line": 10, "ignorable": true } ] } } }
            
            files = data.get("files", {})
            for file_path, file_data in files.items():
                
                # Normalize path relative to project root
                if str(self.project_path) in file_path:
                    file_path = file_path.replace(str(self.project_path), "").lstrip("/\\")

                for msg in file_data.get("messages", []):
                    message = msg.get("message", "")
                    line = msg.get("line", 0)
                    
                    # Basic heuristic for severity/security relevance
                    # Since PHPStan is static analysis, not purely security
                    severity = SeverityLevel.LOW
                    title = "PHPStan Static Analysis Issue"
                    
                    if "security" in message.lower() or "unsafe" in message.lower() or "vulnerability" in message.lower():
                        severity = SeverityLevel.HIGH
                        title = "PHPStan Security Warning"
                    elif "error" in message.lower() or "fail" in message.lower():
                        severity = SeverityLevel.MEDIUM
                        title = "PHPStan Error"

                    finding = FindingSchema(
                        type=f"phpstan:{title.replace(' ', '_').lower()}",
                        severity=severity,
                        confidence=75 if severity == SeverityLevel.HIGH else (50 if severity == SeverityLevel.MEDIUM else 30),
                        file_path=file_path,
                        line_start=line if line > 0 else 1,
                        line_end=line if line > 0 else 1,
                        message=message,
                        cwe_id=None,
                        owasp_category=None
                    )
                    findings.append(finding)
                    
        except json.JSONDecodeError:
            pass
            
        return findings
