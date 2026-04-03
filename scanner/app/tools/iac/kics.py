import json
import subprocess
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class KicsWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "kics"
    
    @property
    def requires_license(self) -> bool:
        return True # PRO Tool? Let's say yes for business model alignment (Infra Scanning)
    
    @property
    def command(self) -> List[str]:
        """KICS CLI command with JSON output."""
        # Using stdout for JSON report to avoid file management complexity
        return [
            "kics", "scan",
            "-p", ".",
            "--report-formats", "json",
            "--output-path", "/dev/stdout",
            "--no-progress",
            "--ignore-on-exit"
        ]

    def get_version(self) -> str:
        """Get KICS version"""
        import subprocess
        try:
            result = subprocess.run(
                ["kics", "version"],
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
        # KICS scans many things (dockerfile, k8s, terraform)
        return True 
    
    def execute(self) -> List[FindingSchema]:
        """Execute KICS and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"KICS execution failed: {e}")
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
