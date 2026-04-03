"""TruffleHog secrets detection tool wrapper"""
from pathlib import Path
from typing import List, Optional
import json
import logging
import subprocess

from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel
from app.utils import extract_relative_path, sanitize_finding_message

logger = logging.getLogger(__name__)


class TruffleHogWrapper(ToolWrapper):
    """Wrapper for TruffleHog - secrets detection tool"""
    
    @property
    def name(self) -> str:
        return "trufflehog"
    
    @property
    def command(self) -> List[str]:
        return [
            "trufflehog",
            "filesystem",
            ".",
            "--json",
            "--no-update"
        ]
    
    def get_version(self) -> str:
        """Override to handle trufflehog version output format"""
        try:
            result = subprocess.run(
                ["trufflehog", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # TruffleHog version is usually just the string
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "not found"
    
    def should_run(self, languages: List[str], framework: Optional[str] = None) -> bool:
        """TruffleHog should always run to check for secrets"""
        return True

    def execute(self) -> List[FindingSchema]:
        """Execute TruffleHog and return findings"""
        try:
            output = self.execute_command(self.command)
            return self.parse_output(output)
        except Exception as e:
            logger.error(f"TruffleHog execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse TruffleHog JSON output to findings"""
        findings = []
        
        # TruffleHog outputs one JSON object per line
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            
            try:
                result = json.loads(line)
                finding = self._parse_trufflehog_result(result)
                if finding:
                    findings.append(finding)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse TruffleHog line: {line[:100]}")
                continue
            except Exception as e:
                logger.warning(f"Failed to process TruffleHog result: {str(e)}")
                continue
        
        return findings
    
    def _parse_trufflehog_result(self, result: dict) -> Optional[FindingSchema]:
        """Parse a single TruffleHog result"""
        
        # Extract source metadata
        source_metadata = result.get("SourceMetadata", {})
        data = source_metadata.get("Data", {})
        filesystem = data.get("Filesystem", {})
        
        file_path = filesystem.get("file", "unknown")
        line_number = filesystem.get("line", 0)
        
        # Extract detector info
        detector_name = result.get("DetectorName", "unknown")
        detector_type = result.get("DetectorType", "")
        
        # Get the actual secret (truncated for security)
        raw_secret = result.get("Raw", "")
        redacted_secret = result.get("Redacted", "")
        
        # Verified secrets are higher confidence
        verified = result.get("Verified", False)
        
        # Calculate confidence based on verification
        confidence = 90 if verified else 70
        
        # Severity based on detector type
        severity = self._determine_severity(detector_name, verified)
        
        # Create message
        if verified:
            message = f"Verified {detector_name} secret found"
        else:
            message = f"Potential {detector_name} secret detected (unverified)"
        
        # Make file path relative
        rel_path = extract_relative_path(file_path, self.project_path)
        
        # Code snippet (show redacted version)
        code_snippet = redacted_secret if redacted_secret else raw_secret[:50] + "..."
        
        return FindingSchema(
            type=f"Secret: {detector_name}",
            severity=severity,
            confidence=confidence,
            file_path=rel_path,
            line_start=max(1, line_number),
            line_end=max(1, line_number),
            message=sanitize_finding_message(message),
            code_snippet=code_snippet,
            cwe_id="CWE-798",  # Use of Hard-coded Credentials
            owasp_category="A07:2021-Identification and Authentication Failures"
        )
    
    def _determine_severity(self, detector_name: str, verified: bool) -> SeverityLevel:
        """Determine severity based on secret type and verification"""
        
        # High-value secrets
        high_value_secrets = [
            "aws",
            "github",
            "gitlab",
            "google",
            "azure",
            "slack",
            "stripe",
            "paypal",
            "privatekey",
            "ssh"
        ]
        
        detector_lower = detector_name.lower()
        
        # Verified high-value secrets are critical
        if verified and any(hv in detector_lower for hv in high_value_secrets):
            return SeverityLevel.CRITICAL
        
        # Verified secrets are high
        if verified:
            return SeverityLevel.HIGH
        
        # Unverified high-value secrets are medium
        if any(hv in detector_lower for hv in high_value_secrets):
            return SeverityLevel.MEDIUM
        
        # Generic unverified secrets are low
        return SeverityLevel.LOW
