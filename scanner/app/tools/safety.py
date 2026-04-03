import json
from typing import List, Optional, Dict, Any
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class SafetyWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "safety"

    @property
    def command(self) -> List[str]:
        # Running safety via pipx as configured in Dockerfile
        # Using --json for machine readable output
        # --full-report might give more details, but check implies basic check
        return ["pipx", "run", "safety", "check", "--json"]

    def get_version(self) -> str:
        """Get Safety version"""
        import subprocess
        try:
            # Try safety --version
            result = subprocess.run(
                ["pipx", "run", "safety", "--version"],
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
        """Run if Python is detected or requirements.txt exists"""
        if any(lang.lower() == "python" for lang in languages):
            return True
        
        req_file = self.project_path / "requirements.txt"
        return req_file.exists()

    def execute(self) -> List[FindingSchema]:
        """Execute Safety and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            self.logger.error(f"Safety execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            # Safety JSON output structure:
            # ... (comments)
            
            data = json.loads(output)
            
            # Key might be 'vulnerabilities' or direct list
            vulnerabilities = data.get("vulnerabilities", [])
            
            if not vulnerabilities and isinstance(data, list):
                vulnerabilities = data

            for vuln in vulnerabilities:
                if vuln.get("ignored", False):
                    continue

                pkg_name = vuln.get("package_name", "unknown-package")
                vuln_id = vuln.get("vulnerability_id", "unknown-id")
                advisory = vuln.get("advisory", "")
                
                # Try to determine severity from CVSS
                cvss_score = 0.0
                severity_obj = vuln.get("severity")
                if isinstance(severity_obj, dict):
                     # Try cvssv3 first, then v2
                     cvss_data = severity_obj.get("cvssv3", {}) or severity_obj.get("cvssv2", {})
                     cvss_score = cvss_data.get("base_score", 0.0)
                
                severity = SeverityLevel.LOW
                if cvss_score >= 9.0:
                    severity = SeverityLevel.CRITICAL
                elif cvss_score >= 7.0:
                    severity = SeverityLevel.HIGH
                elif cvss_score >= 4.0:
                    severity = SeverityLevel.MEDIUM
                
                # Fallback if no CVSS but "severity" text field exists
                if cvss_score == 0.0 and isinstance(severity_obj, str):
                    if "critical" in severity_obj.lower():
                        severity = SeverityLevel.CRITICAL
                    elif "high" in severity_obj.lower():
                        severity = SeverityLevel.HIGH
                    elif "medium" in severity_obj.lower():
                        severity = SeverityLevel.MEDIUM

                finding = FindingSchema(
                    type=f"Vulnerable Dependency: {pkg_name}",
                    severity=severity,
                    confidence=100, # Safety is usually definitive if ID matches
                    file_path="requirements.txt", # Logic assumes requirements.txt context
                    line_start=1, 
                    line_end=1,
                    message=f"{pkg_name} ({vuln_id}): {advisory[:200]}...",
                    code_snippet=f"{pkg_name} {vuln.get('analyzed_version', '')}",
                    rule_id=vuln_id,
                    metadata={
                        "package": pkg_name,
                        "installed_version": vuln.get("analyzed_version"),
                        "vulnerable_spec": vuln.get("vulnerable_spec")
                    }
                )
                findings.append(finding)
                    
        except json.JSONDecodeError:
            pass
        except Exception as e:
            # Catch parsing errors to prevent crash
            pass
            
        return findings
