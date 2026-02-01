import json
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityStr

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
                    severity = SeverityStr.LOW
                    title = "PHPStan Static Analysis Issue"
                    
                    if "security" in message.lower() or "unsafe" in message.lower() or "vulnerability" in message.lower():
                        severity = SeverityStr.HIGH
                        title = "PHPStan Security Warning"
                    elif "error" in message.lower() or "fail" in message.lower():
                        severity = SeverityStr.MEDIUM
                        title = "PHPStan Error"

                    finding = FindingSchema(
                        tool="phpstan",
                        title=f"{title}: {message[:100]}",
                        description=message,
                        severity=severity,
                        file_path=file_path,
                        line=line,
                        column=0, # PHPStan JSON often doesn't give column
                        rule_id="phpstan-finding"
                    )
                    findings.append(finding)
                    
        except json.JSONDecodeError:
            pass
            
        return findings
