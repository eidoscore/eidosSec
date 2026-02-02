"""Safety Python SCA tool wrapper"""
from pathlib import Path
from typing import List, Optional
import json
import logging

from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel
from app.utils import sanitize_finding_message

logger = logging.getLogger(__name__)


class SafetyWrapper(ToolWrapper):
    """Wrapper for Safety - Python dependency vulnerability scanner"""
    
    @property
    def name(self) -> str:
        return "safety"
    
    @property
    def command(self) -> List[str]:
        return [
            "safety",
            "check",
            "--json",
            "--full-report"
        ]
    
    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Run Safety if Python is detected and requirements.txt/Pipfile exists"""
        if "Python" not in languages:
            return False
        
        # Check for Python dependency files
        has_requirements = any(self.project_path.glob("requirements*.txt"))
        has_pipfile = (self.project_path / "Pipfile").exists()
        has_setup = (self.project_path / "setup.py").exists()
        has_pyproject = (self.project_path / "pyproject.toml").exists()
        
        return has_requirements or has_pipfile or has_setup or has_pyproject
    
    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse Safety JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            
            # Safety 3.x output format
            if isinstance(data, list):
                # Direct list of vulnerabilities
                vulnerabilities = data
            elif isinstance(data, dict):
                # Check different possible formats
                vulnerabilities = data.get("vulnerabilities", [])
                if not vulnerabilities and "packages" in data:
                    # Alternative format
                    vulnerabilities = self._extract_from_packages(data.get("packages", []))
            else:
                vulnerabilities = []
            
            for vuln in vulnerabilities:
                try:
                    finding = self._parse_vulnerability(vuln)
                    if finding:
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Failed to parse Safety vulnerability: {str(e)}")
                    continue
            
            return findings
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Safety JSON output: {str(e)}")
            return []
    
    def _parse_vulnerability(self, vuln: dict) -> Optional[FindingSchema]:
        """Parse a single Safety vulnerability"""
        
        # Extract fields - Safety 3.x format
        package_name = vuln.get("package_name", "unknown")
        installed_version = vuln.get("installed_version", "unknown")
        vulnerable_spec = vuln.get("vulnerable_spec", "")
        advisory = vuln.get("advisory", "No description")
        cve = vuln.get("cve", "")
        severity = vuln.get("severity", "unknown")
        
        # Build message
        message = f"{package_name} {installed_version} - {advisory}"
        if vulnerable_spec:
            message += f" (Affected: {vulnerable_spec})"
        
        # Map severity
        severity_level = self._map_severity(severity)
        
        # Calculate confidence based on CVE presence
        confidence = 85 if cve else 75
        
        # Create finding type
        finding_type = f"Vulnerable Dependency: {package_name}"
        if cve:
            finding_type += f" ({cve})"
        
        return FindingSchema(
            type=finding_type,
            severity=severity_level,
            confidence=confidence,
            file_path="requirements.txt",  # Generic since Safety scans all deps
            line_start=1,
            line_end=1,
            message=sanitize_finding_message(message),
            code_snippet=f"{package_name}=={installed_version}",
            cwe_id=None,  # Safety doesn't provide CWE
            owasp_category="A06:2021-Vulnerable and Outdated Components"
        )
    
    def _extract_from_packages(self, packages: List[dict]) -> List[dict]:
        """Extract vulnerabilities from packages format"""
        vulnerabilities = []
        for pkg in packages:
            pkg_vulns = pkg.get("vulnerabilities", [])
            for vuln in pkg_vulns:
                vuln["package_name"] = pkg.get("name", "unknown")
                vuln["installed_version"] = pkg.get("version", "unknown")
                vulnerabilities.append(vuln)
        return vulnerabilities
    
    def _map_severity(self, safety_severity: str) -> SeverityLevel:
        """Map Safety severity to standard levels"""
        if not safety_severity:
            return SeverityLevel.MEDIUM
        
        severity_lower = safety_severity.lower()
        
        mapping = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.HIGH,
            "severe": SeverityLevel.HIGH,
            "medium": SeverityLevel.MEDIUM,
            "moderate": SeverityLevel.MEDIUM,
            "low": SeverityLevel.LOW,
            "unknown": SeverityLevel.MEDIUM
        }
        
        return mapping.get(severity_lower, SeverityLevel.MEDIUM)
