import subprocess
import json
import xml.etree.ElementTree as ET
from typing import List
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class PmdWrapper(ToolWrapper):
    def __init__(self, project_path: str):
        super().__init__(project_path)
    
    @property
    def command(self) -> List[str]:
        output_file = self.results_dir / "pmd.xml"
        return [
            "pmd", "check",
            "-d", str(self.project_path),
            "-R", "rulesets/java/quickstart.xml",
            "-f", "xml",
            "-r", str(output_file)
        ]

    @property
    def name(self) -> str:
        return "pmd"
    
    @property
    def requires_license(self) -> bool:
        return False # Free tool
    
    def should_run(self, languages: List[str], framework: str) -> bool:
        return "java" in languages
    
    def run(self) -> List[FindingSchema]:
        output_file = self.results_dir / "pmd.xml"
        
        try:
            subprocess.run(self.command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if output_file.exists():
                 return self.parse_output(output_file)
            return []
        except Exception as e:
            self.logger.error(f"PMD failed: {e}")
            return []

    def parse_output(self, output_file) -> List[FindingSchema]:
        findings = []
        try:
            tree = ET.parse(output_file)
            root = tree.getroot()
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
