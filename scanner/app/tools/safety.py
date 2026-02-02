import json
from typing import List, Optional, Dict, Any
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityStr

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

    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Run if Python is detected or requirements.txt exists"""
        if "Python" in languages:
            return True
        
        req_file = self.project_path / "requirements.txt"
        return req_file.exists()

    def parse_output(self, output: str) -> List[FindingSchema]:
        findings = []
        try:
            # Safety JSON output structure:
            # {
            #    "vulnerabilities": [
            #        {
            #            "vulnerability_id": "...",
            #            "package_name": "...",
            #            "ignored": false,
            #            "vulnerable_spec": "...",
            #            "advisory": "...",
            #            "severity": { "cvssv3": { "base_score": 9.8 } }
            #        }
            #    ]
            # }
            # Note: The structure might vary slightly between versions, 
            # safety 3.0 has a specific format.
            
            data = json.loads(output)
            
            # Key might be 'vulnerabilities' or direct list in older versions
            # Safety 3.x usually has top level keys
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
                
                severity = SeverityStr.LOW
                if cvss_score >= 9.0:
                    severity = SeverityStr.CRITICAL
                elif cvss_score >= 7.0:
                    severity = SeverityStr.HIGH
                elif cvss_score >= 4.0:
                    severity = SeverityStr.MEDIUM
                
                # Fallback if no CVSS but "severity" text field exists
                if cvss_score == 0.0 and isinstance(severity_obj, str):
                    if "critical" in severity_obj.lower():
                        severity = SeverityStr.CRITICAL
                    elif "high" in severity_obj.lower():
                        severity = SeverityStr.HIGH
                    elif "medium" in severity_obj.lower():
                        severity = SeverityStr.MEDIUM

                finding = FindingSchema(
                    tool="safety",
                    title=f"Vulnerable Dependency: {pkg_name} ({vuln_id})",
                    description=advisory,
                    severity=severity,
                    file_path="requirements.txt", # Logic assumes requirements.txt context
                    line=1, # Can't easily determine line number without parsing requirements.txt manually
                    column=0,
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
