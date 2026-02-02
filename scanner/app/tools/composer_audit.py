import json
from pathlib import Path
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class ComposerAuditWrapper(ToolWrapper):
    """Wrapper for Composer audit - PHP dependency vulnerability scanner"""
    
    @property
    def name(self) -> str:
        return "composer-audit"
    
    @property
    def command(self) -> List[str]:
        return [
            "composer", "audit", "--format=json"
        ]
    
    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Run if PHP detected and composer.json exists"""
        if "PHP" not in languages:
            return False
            
        return (self.project_path / "composer.json").exists()
    
    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse Composer audit JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            
            # Composer audit format: {"advisories": {"package/name": [{...}]}}
            advisories = data.get("advisories", {})
            
            for package_name, package_advisories in advisories.items():
                for advisory in package_advisories:
                    finding = self._parse_advisory(package_name, advisory)
                    if finding:
                        findings.append(finding)
            
            return findings
            
        except json.JSONDecodeError as e:
            return []
    
    def _parse_advisory(self, package_name: str, advisory: dict) -> Optional[FindingSchema]:
        """Parse a single Composer advisory"""
        
        # Extract fields
        title = advisory.get("title", "")
        cve = advisory.get("cve", "")
        link = advisory.get("link", "")
        affected_versions = advisory.get("affectedVersions", "")
        severity = advisory.get("severity", "medium")
        
        # Build message
        message = title
        if link:
            message += f" - {link}"
        
        # Map severity
        severity_level = self._map_severity(severity)
        
        # Create finding type
        finding_type = f"Vulnerable Dependency: {package_name}"
        if cve:
            finding_type += f" ({cve})"
        
        return FindingSchema(
            type=finding_type,
            severity=severity_level,
            confidence=90 if cve else 80,
            file_path="composer.json",
            line_start=1,
            line_end=1,
            message=message,
            code_snippet=f"{package_name}: {affected_versions}" if affected_versions else package_name,
            cwe_id=None,
            owasp_category="A06:2021-Vulnerable and Outdated Components"
        )
    
    def _map_severity(self, composer_severity: str) -> SeverityLevel:
        """Map Composer audit severity to standard levels"""
        mapping = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.HIGH,
            "medium": SeverityLevel.MEDIUM,
            "low": SeverityLevel.LOW
        }
        return mapping.get(composer_severity.lower(), SeverityLevel.MEDIUM)
