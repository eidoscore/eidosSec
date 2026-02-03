import json
import subprocess
from typing import List
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class KicsWrapper(ToolWrapper):
    def __init__(self, project_path: str):
        super().__init__(project_path)
    
    @property
    def command(self) -> List[str]:
        """KICS CLI command with JSON output."""
        return [
            "kics", "scan",
            "-p", str(self.project_path),
            "-o", str(self.results_dir),
            "--output-name", "kics-results.json",
            "--report-formats", "json",
            "--ignore-on-exit", "results"
        ]

    @property
    def name(self) -> str:
        return "kics"
    
    @property
    def requires_license(self) -> bool:
        return True # PRO Tool? Let's say yes for business model alignment (Infra Scanning)
    
    def should_run(self, languages: List[str], framework: str) -> bool:
        # KICS scans many things (dockerfile, k8s, terraform)
        # We can run it if we detect 'docker', 'terraform', etc OR just always run it if license allows
        # because it auto-detects files.
        return True 
    
    def run(self) -> List[FindingSchema]:
        output_file = self.results_dir / "kics-results.json"
        
        command = [
            "kics", "scan",
            "-p", str(self.project_path),
            "-o", str(self.results_dir),
            "--output-name", "kics-results.json",
            "--report-formats", "json",
            "--ignore-on-exit", "results" # Don't exit 1 on findings
        ]
        
        try:
            self.run_command(self.command)
            if output_file.exists():
                with open(output_file, 'r', encoding='utf-8') as f:
                    return self.parse_output(f.read())
            return []
        except Exception as e:
            self.logger.error(f"KICS failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            data = json.loads(output)
            # KICS JSON structure:
            # { "queries": [ { "query_name": "...", "severity": "HIGH", "files": [ {"file_name": "...", "line": 1} ] } ] }
            
            for query in data.get("queries", []):
                query_name = query.get("query_name", "Unknown Issue")
                sev_str = query.get("severity", "INFO").upper()
                count = query.get("files", [])
                
                severity = SeverityLevel.LOW
                if sev_str == "HIGH": severity = SeverityLevel.HIGH
                elif sev_str == "CRITICAL": severity = SeverityLevel.CRITICAL
                elif sev_str == "MEDIUM": severity = SeverityLevel.MEDIUM
                
                for f in query.get("files", []):
                    finding = FindingSchema(
                        type=query_name,
                        severity=severity,
                        confidence=90,
                        file_path=f.get("file_name", "unknown"),
                        line_start=f.get("line", 1),
                        line_end=f.get("line", 1),
                        message=query_name,
                        metadata={
                            "tool": "kics",
                            "category": query.get("category"),
                            "description": query.get("description"),
                            "platform": query.get("platform")
                        }
                    )
                    findings.append(finding)
                    
        except Exception as e:
            self.logger.error(f"Failed to parse KICS output: {e}")
            
        return findings
