"""Checkov IaC tool wrapper"""
import json
from pathlib import Path
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class CheckovWrapper(ToolWrapper):
    """Wrapper for Checkov - Multi-platform IaC security scanner"""
    
    @property
    def name(self) -> str:
        return "checkov"
    
    @property
    def command(self) -> List[str]:
        return [
            "checkov",
            "-d", ".",
            "--output", "json",
            "--quiet",  # Suppress progress output
            "--compact"
        ]
    
    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Run if IaC files are detected"""
        # Check for common IaC file patterns
        iac_patterns = [
            "*.tf",           # Terraform
            "*.tfvars",
            "*.json",         # CloudFormation/ARM
            "*.yaml",
            "*.yml",
            "Dockerfile",     # Docker
            "*.dockerfile",
            "kubernetes/*.yaml",  # K8s
            "k8s/*.yaml",
            "helm/**/values.yaml",  # Helm
        ]
        
        # Check if any IaC files exist
        for pattern in iac_patterns:
            if list(self.project_path.rglob(pattern)):
                return True
        
        # Check for specific directories
        iac_dirs = ["terraform", "infrastructure", "k8s", "kubernetes", "helm", "docker"]
        for dir_name in iac_dirs:
            if (self.project_path / dir_name).is_dir():
                return True
        
        return False
    
    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse Checkov JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            
            # Checkov returns results by framework
            if isinstance(data, dict):
                for framework, results in data.items():
                    if isinstance(results, list):
                        for result in results:
                            finding = self._parse_result(result, framework)
                            if finding:
                                findings.append(finding)
                    elif isinstance(results, dict) and "results" in results:
                        for result in results["results"]:
                            finding = self._parse_result(result, framework)
                            if finding:
                                findings.append(finding)
            
            return findings
            
        except json.JSONDecodeError:
            return []
    
    def _parse_result(self, result: dict, framework: str) -> Optional[FindingSchema]:
        """Parse a single Checkov result"""
        
        check_id = result.get("check_id", "")
        check_name = result.get("check_name", "")
        file_path = result.get("file_path", "")
        resource = result.get("resource", "")
        severity = result.get("severity", "MEDIUM")
        guideline = result.get("guideline", "")
        
        # Get line numbers
        start_line = result.get("file_line_range", [0, 0])[0]
        end_line = result.get("file_line_range", [0, 0])[1]
        
        # Build message
        message = check_name
        if guideline:
            message += f" - {guideline}"
        
        return FindingSchema(
            type=f"IaC ({framework}): {check_id}",
            severity=self._map_severity(severity),
            confidence=90,
            file_path=file_path or "infrastructure",
            line_start=start_line if start_line else 1,
            line_end=end_line if end_line else 1,
            message=message,
            code_snippet=resource,
            cwe_id=None,
            owasp_category=None
        )
    
    def _map_severity(self, checkov_severity: str) -> SeverityLevel:
        """Map Checkov severity to standard levels"""
        if not checkov_severity:
            return SeverityLevel.MEDIUM
        
        mapping = {
            "CRITICAL": SeverityLevel.CRITICAL,
            "HIGH": SeverityLevel.HIGH,
            "MEDIUM": SeverityLevel.MEDIUM,
            "LOW": SeverityLevel.LOW,
            "INFO": SeverityLevel.INFO
        }
        return mapping.get(checkov_severity.upper(), SeverityLevel.MEDIUM)
