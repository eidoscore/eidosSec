import subprocess
import json
import xml.etree.ElementTree as ET
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class PmdWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "pmd"
    
    @property
    def command(self) -> List[str]:
        return [
            "pmd", "check",
            "-d", ".",
            "-R", "rulesets/java/quickstart.xml",
            "-f", "xml"
        ]

    def get_version(self) -> str:
        """Get PMD version"""
        import subprocess
        try:
            result = subprocess.run(
                ["pmd", "--version"],
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
        return any(lang.lower() == "java" for lang in languages)
    
    def execute(self) -> List[FindingSchema]:
        """Execute PMD and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"PMD execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(output)
            # <pmd> <file name="..."> <violation ...> ... </violation> </file> </pmd>
            
            for file_elem in root.findall("file"):
                file_path = file_elem.get("name", "unknown")
                for violation in file_elem.findall("violation"):
                    # Map PMD priority 1-5 to Severity
                    # 1 = High, 5 = Low
                    priority = int(violation.get("priority", 3))
                    severity = SeverityLevel.MEDIUM
                    if priority <= 2:
                        severity = SeverityLevel.HIGH
                    elif priority == 1:
                        severity = SeverityLevel.CRITICAL
                    elif priority >= 4:
                        severity = SeverityLevel.LOW
                        
                    finding = FindingSchema(
                        type=violation.get("rule", "PMD Rule"),
                        severity=severity,
                        confidence=100,
                        file_path=file_path,
                        line_start=int(violation.get("beginline", 1)),
                        line_end=int(violation.get("endline", 1)),
                        message=violation.text.strip() if violation.text else "PMD Violation",
                        metadata={
                            "tool": "pmd",
                            "ruleset": violation.get("ruleset"),
                            "externalInfoUrl": violation.get("externalInfoUrl")
                        }
                    )
                    findings.append(finding)
        except Exception as e:
            self.logger.error(f"Failed to parse PMD output: {e}")
            
        return findings
