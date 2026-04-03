"""Trivy SCA (Software Composition Analysis) tool wrapper"""
from pathlib import Path
from typing import List, Optional
import json
import logging

from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel
from app.utils import sanitize_finding_message

logger = logging.getLogger(__name__)


class TrivyWrapper(ToolWrapper):
    """Wrapper for Trivy - vulnerability scanner for dependencies"""
    
    @property
    def name(self) -> str:
        return "trivy"
    
    @property
    def command(self) -> List[str]:
        return [
            "trivy",
            "filesystem",
            ".",
            "--format", "json",
            "--scanners", "vuln",
            "--quiet"
        ]
    
    def get_version(self) -> str:
        """Get Trivy version"""
        import subprocess
        try:
            result = subprocess.run(
                ["trivy", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Trivy version output can be multi-line, get first line
                return result.stdout.split('\n')[0].strip()
            return "unknown"
        except Exception:
            return "not found"
    
    def should_run(self, languages: List[str], framework: Optional[str] = None) -> bool:
        """Trivy supports multiple package managers"""
        return True # Always run as it's a versatile SCA tool

    def execute(self) -> List[FindingSchema]:
        """Execute Trivy and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            logger.error(f"Trivy execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse Trivy JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            results = data.get("Results", [])
            
            for result in results:
                # Get target file (manifest file like package.json, requirements.txt)
                target = result.get("Target", "dependencies")
                vulnerabilities = result.get("Vulnerabilities", [])
                
                for vuln in vulnerabilities:
                    try:
                        finding = self._parse_trivy_vulnerability(vuln, target)
                        if finding:
                            findings.append(finding)
                    except Exception as e:
                        logger.warning(f"Failed to parse Trivy vulnerability: {str(e)}")
                        continue
            
            return findings
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Trivy JSON output: {str(e)}")
            return []
    
    def _parse_trivy_vulnerability(self, vuln: dict, target: str) -> Optional[FindingSchema]:
        """Parse a single Trivy vulnerability"""
        
        # Extract vulnerability info
        vuln_id = vuln.get("VulnerabilityID", "unknown")
        pkg_name = vuln.get("PkgName", "unknown")
        installed_version = vuln.get("InstalledVersion", "")
        fixed_version = vuln.get("FixedVersion", "")
        title = vuln.get("Title", "")
        description = vuln.get("Description", "")
        severity_str = vuln.get("Severity", "UNKNOWN")
        
        # CVSS scores
        cvss = vuln.get("CVSS", {})
        cvss_score = 0
        for vendor_data in cvss.values():
            if isinstance(vendor_data, dict):
                score = vendor_data.get("V3Score", 0)
                cvss_score = max(cvss_score, score)
        
        # References
        references = vuln.get("References", [])
        
        # Map severity
        severity = self._map_severity(severity_str, cvss_score)
        
        # Calculate confidence (CVE database is highly accurate)
        confidence = 95 if cvss_score > 0 else 85
        
        # Create message
        message = f"{vuln_id} in {pkg_name}@{installed_version}"
        if title:
            message += f": {title}"
        if fixed_version:
            message += f" (Fix available: {fixed_version})"
        
        # Code snippet shows the dependency
        code_snippet = f"{pkg_name}=={installed_version}"
        
        # Determine file path (dependency manifest)
        file_path = self._determine_manifest_file(target)
        
        return FindingSchema(
            type=f"Vulnerability: {vuln_id}",
            severity=severity,
            confidence=confidence,
            file_path=file_path,
            line_start=1,
            line_end=1,
            message=sanitize_finding_message(message),
            code_snippet=code_snippet,
            cwe_id=self._extract_cwe(vuln),
            owasp_category="A06:2021-Vulnerable and Outdated Components"
        )
    
    def _map_severity(self, trivy_severity: str, cvss_score: float) -> SeverityLevel:
        """Map Trivy severity to standard levels"""
        
        # Use CVSS score if available (more accurate)
        if cvss_score > 0:
            if cvss_score >= 9.0:
                return SeverityLevel.CRITICAL
            elif cvss_score >= 7.0:
                return SeverityLevel.HIGH
            elif cvss_score >= 4.0:
                return SeverityLevel.MEDIUM
            else:
                return SeverityLevel.LOW
        
        # Fallback to Trivy severity rating
        mapping = {
            "CRITICAL": SeverityLevel.CRITICAL,
            "HIGH": SeverityLevel.HIGH,
            "MEDIUM": SeverityLevel.MEDIUM,
            "LOW": SeverityLevel.LOW,
            "UNKNOWN": SeverityLevel.INFO
        }
        return mapping.get(trivy_severity.upper(), SeverityLevel.INFO)
    
    def _extract_cwe(self, vuln: dict) -> Optional[str]:
        """Extract CWE from vulnerability data"""
        # Trivy sometimes includes CWE in references or metadata
        cwe_ids = vuln.get("CweIDs", [])
        if cwe_ids and len(cwe_ids) > 0:
            return cwe_ids[0]
        return None
    
    def _determine_manifest_file(self, target: str) -> str:
        """Determine the manifest file name from target"""
        # Trivy target includes the manifest file path
        # Examples: "package.json", "requirements.txt", "composer.lock"
        
        if "package" in target.lower():
            return "package.json"
        elif "requirements" in target.lower():
            return "requirements.txt"
        elif "composer" in target.lower():
            return "composer.json"
        elif "gemfile" in target.lower():
            return "Gemfile.lock"
        elif "go.mod" in target.lower():
            return "go.mod"
        elif "pom.xml" in target.lower():
            return "pom.xml"
        elif "build.gradle" in target.lower():
            return "build.gradle"
        else:
            return target
