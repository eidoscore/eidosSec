"""Gitleaks git secrets detection tool wrapper"""
from pathlib import Path
from typing import List, Optional
import json
import logging

from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel
from app.utils import extract_relative_path, sanitize_finding_message

logger = logging.getLogger(__name__)


class GitleaksWrapper(ToolWrapper):
    """Wrapper for Gitleaks - git secrets scanner"""
    
    @property
    def name(self) -> str:
        return "gitleaks"
    
    @property
    def command(self) -> List[str]:
        return [
            "gitleaks",
            "detect",
            "--source", ".",
            "--report-format", "json",
            "--report-path", "/dev/stdout",
            "--no-banner",
            "--exit-code", "0"  # Don't fail on findings
        ]
    
    def get_version(self) -> str:
        """Get Gitleaks version"""
        import subprocess
        try:
            result = subprocess.run(
                ["gitleaks", "version"],
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
        """Gitleaks should always run to check for secrets"""
        return True

    def execute(self) -> List[FindingSchema]:
        """Execute Gitleaks and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            logger.error(f"Gitleaks execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse Gitleaks JSON output to findings"""
        findings = []
        
        try:
            # Gitleaks outputs an array of findings
            if not output.strip():
                return []
            
            data = json.loads(output)
            
            # Handle both array and object formats
            if isinstance(data, dict):
                results = data.get("findings", [])
            elif isinstance(data, list):
                results = data
            else:
                logger.warning("Unexpected Gitleaks output format")
                return []
            
            for result in results:
                try:
                    finding = self._parse_gitleaks_result(result)
                    if finding:
                        findings.append(finding)
                except Exception as e:
                    logger.warning(f"Failed to parse Gitleaks result: {str(e)}")
                    continue
            
            return findings
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gitleaks JSON output: {str(e)}")
            return []
    
    def _parse_gitleaks_result(self, result: dict) -> Optional[FindingSchema]:
        """Parse a single Gitleaks result"""
        
        # Extract fields
        rule_id = result.get("RuleID", "unknown")
        description = result.get("Description", "Secret detected")
        file_path = result.get("File", "")
        start_line = result.get("StartLine", 0)
        end_line = result.get("EndLine", 0)
        commit = result.get("Commit", "")
        
        # Get secret (redacted)
        secret = result.get("Secret", "")
        match_text = result.get("Match", "")
        
        # Redact actual secret for security
        redacted_secret = secret[:10] + "..." if len(secret) > 10 else "***"
        
        # Entropy score (if available)
        entropy = result.get("Entropy", 0)
        
        # Calculate confidence based on entropy and rule match
        confidence = self._calculate_confidence(entropy, rule_id)
        
        # Determine severity based on rule
        severity = self._determine_severity(rule_id, file_path)
        
        # Make file path relative
        rel_path = extract_relative_path(file_path, self.project_path)
        
        # Create message
        message = f"{description} (Rule: {rule_id})"
        if commit:
            message += f" - Found in commit {commit[:8]}"
        
        return FindingSchema(
            type=f"Secret: {rule_id}",
            severity=severity,
            confidence=confidence,
            file_path=rel_path,
            line_start=max(1, start_line),
            line_end=max(start_line, end_line),
            message=sanitize_finding_message(message),
            code_snippet=redacted_secret,
            cwe_id="CWE-798",  # Use of Hard-coded Credentials
            owasp_category="A07:2021-Identification and Authentication Failures"
        )
    
    def _calculate_confidence(self, entropy: float, rule_id: str) -> int:
        """Calculate confidence score based on entropy and rule match"""
        
        # Base confidence
        confidence = 70
        
        # High entropy increases confidence
        if entropy > 4.0:
            confidence += 15
        elif entropy > 3.0:
            confidence += 10
        
        # Known secret patterns have higher confidence
        high_confidence_rules = [
            "aws-access-token",
            "github-pat",
            "github-oauth",
            "private-key",
            "slack-webhook",
            "stripe-key"
        ]
        
        if any(pattern in rule_id.lower() for pattern in high_confidence_rules):
            confidence += 10
        
        return min(100, confidence)
    
    def _determine_severity(self, rule_id: str, file_path: str) -> SeverityLevel:
        """Determine severity based on secret type and location"""
        
        rule_lower = rule_id.lower()
        
        # Critical secrets
        critical_patterns = [
            "private-key",
            "aws-access",
            "github-pat",
            "stripe-key",
            "paypal"
        ]
        
        if any(pattern in rule_lower for pattern in critical_patterns):
            return SeverityLevel.CRITICAL
        
        # High severity secrets
        high_patterns = [
            "api-key",
            "password",
            "token",
            "secret",
            "credential"
        ]
        
        if any(pattern in rule_lower for pattern in high_patterns):
            return SeverityLevel.HIGH
        
        # Secrets in config files are more severe
        if any(ext in file_path.lower() for ext in [".env", ".config", ".yml", ".yaml"]):
            return SeverityLevel.HIGH
        
        # Default to medium
        return SeverityLevel.MEDIUM
