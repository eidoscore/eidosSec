"""cfn-nag IaC tool wrapper for CloudFormation"""
import json
from pathlib import Path
from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class CfnNagWrapper(ToolWrapper):
    """Wrapper for cfn-nag - CloudFormation security scanner"""
    
    @property
    def name(self) -> str:
        return "cfn-nag"
    
    @property
    def command(self) -> List[str]:
        return [
            "cfn-nag",
            "scan",
            "--input-path", ".",
            "--output-format", "json"
        ]
    
    def get_version(self) -> str:
        """Get cfn-nag version"""
        import subprocess
        try:
            result = subprocess.run(
                ["cfn-nag", "--version"],
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
        """Run if CloudFormation templates are detected"""
        # Check for CloudFormation files
        cfn_patterns = ["*.yaml", "*.yml", "*.json"]
        cfn_indicators = ["Resources", "AWSTemplateFormatVersion"]
        
        for pattern in cfn_patterns:
            for file_path in self.project_path.rglob(pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        if any(indicator in content for indicator in cfn_indicators):
                            return True
                    except:
                        continue
        
        return False
    
    def execute(self) -> List[FindingSchema]:
        """Execute cfn-nag and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"cfn-nag execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse cfn-nag JSON output to findings"""
        findings = []
        
        try:
            data = json.loads(output)
            
            # cfn-nag returns a list of file results
            for file_result in data:
                filename = file_result.get("filename", "")
                file_findings = file_result.get("file_results", {}).get("violations", [])
                
                for violation in file_findings:
                    finding = self._parse_violation(filename, violation)
                    if finding:
                        findings.append(finding)
            
            return findings
            
        except json.JSONDecodeError:
            return []
    
    def _parse_violation(self, filename: str, violation: dict) -> Optional[FindingSchema]:
        """Parse a single cfn-nag violation"""
        
        rule_id = violation.get("id", "")
        message = violation.get("message", "")
        logical_resource_ids = violation.get("logical_resource_ids", [])
        line_number = violation.get("line_number", 0)
        
        # Determine severity based on rule pattern
        severity = self._determine_severity(rule_id, message)
        
        resource_info = ", ".join(logical_resource_ids) if logical_resource_ids else ""
        
        return FindingSchema(
            type=f"IaC: {rule_id}",
            severity=severity,
            confidence=90,
            file_path=filename,
            line_start=line_number if line_number else 1,
            line_end=line_number if line_number else 1,
            message=message,
            code_snippet=resource_info,
            cwe_id=None,
            owasp_category=None
        )
    
    def _determine_severity(self, rule_id: str, message: str) -> SeverityLevel:
        """Determine severity based on rule ID and message"""
        message_lower = message.lower()
        rule_lower = rule_id.lower()
        
        # High severity patterns
        high_patterns = ["security", "password", "secret", "encryption", "ingress", "0.0.0.0"]
        if any(pattern in message_lower for pattern in high_patterns):
            return SeverityLevel.HIGH
        
        # Medium severity patterns
        medium_patterns = ["warning", "should", "recommend"]
        if any(pattern in message_lower for pattern in medium_patterns):
            return SeverityLevel.MEDIUM
        
        return SeverityLevel.LOW
