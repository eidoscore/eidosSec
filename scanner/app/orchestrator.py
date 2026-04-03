"""Scan orchestrator - coordinates execution of security tools"""
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime, timezone
import redis
import json
import logging
import os

logger = logging.getLogger(__name__)

from app.tools.semgrep import SemgrepWrapper
from app.tools.bandit import BanditWrapper
from app.tools.trufflehog import TruffleHogWrapper
from app.tools.gitleaks import GitleaksWrapper
from app.tools.trivy import TrivyWrapper
from app.tools.eslint import EslintWrapper
from app.tools.phpstan import PhpstanWrapper
from app.tools.brakeman import BrakemanWrapper
from app.tools.safety import SafetyWrapper
from app.tools.npm_audit import NpmAuditWrapper
from app.tools.composer_audit import ComposerAuditWrapper
from app.tools.zap import ZapWrapper
from app.tools.nuclei import NucleiWrapper
from app.tools.cfn_nag import CfnNagWrapper
from app.tools.checkov import CheckovWrapper
from app.tools.codeql import CodeQLWrapper
from app.tools.gosec import GosecWrapper
from app.tools.sast.staticcheck import StaticcheckWrapper
from app.tools.sast.spotbugs import SpotBugsWrapper
from app.tools.sast.pmd import PmdWrapper
from app.tools.sast.shellcheck import ShellCheckWrapper
from app.tools.sca.retirejs import RetireJsWrapper
from app.tools.iac.kics import KicsWrapper
from app.schemas import ScanResultSchema, FindingSchema, ToolResultSchema
from app.services.license import LicenseVerifier

class ScanOrchestrator:
    QUICK_PROFILE_TOOLS = {
        "semgrep",
        "bandit",
        "gitleaks",
        "trufflehog",
        "trivy",
        "eslint",
        "phpstan",
        "brakeman",
        "safety",
        "npm_audit",
        "composer_audit",
    }
    DEEP_PROFILE_TOOLS = {
        "semgrep",
        "bandit",
        "trufflehog",
        "gitleaks",
        "trivy",
        "eslint",
        "phpstan",
        "brakeman",
        "safety",
        "npm_audit",
        "composer_audit",
        "zap",
        "nuclei",
        "cfn_nag",
        "checkov",
    }
    DEFAULT_STABILIZATION_TOOLS = {
        "codeql",
        "gosec",
        "staticcheck",
        "spotbugs",
        "pmd",
        "shellcheck",
        "retirejs",
        "kics",
    }

    def __init__(self, project_path: Path, scan_id: str, redis_url: str, scan_mode: str = "quick"):
        self.project_path = project_path
        self.scan_id = scan_id
        self.redis_client = redis.from_url(redis_url)
        self.license_verifier = LicenseVerifier()
        self.scan_mode = (scan_mode or "quick").lower()
        if self.scan_mode not in {"quick", "deep", "custom"}:
            logger.warning(f"[Scan {self.scan_id}] Unknown scan mode '{self.scan_mode}', fallback to quick")
            self.scan_mode = "quick"
        self.stabilization_enabled = self._is_flag_enabled(
            os.getenv("ENABLE_STABILIZATION_TOOLS", "false")
        )
        
        # Initialize detectors
        from app.detectors.language import LanguageDetector
        from app.detectors.framework import FrameworkDetector
        self.language_detector = LanguageDetector()
        self.framework_detector = FrameworkDetector()

        self.all_tools = [
            SemgrepWrapper(project_path),
            BanditWrapper(project_path),
            TruffleHogWrapper(project_path),
            GitleaksWrapper(project_path),
            TrivyWrapper(project_path),
            EslintWrapper(project_path),
            PhpstanWrapper(project_path),
            BrakemanWrapper(project_path),
            SafetyWrapper(project_path),
            NpmAuditWrapper(project_path),
            ComposerAuditWrapper(project_path),
            ZapWrapper(project_path),
            NucleiWrapper(project_path),
            CfnNagWrapper(project_path),
            CheckovWrapper(project_path),
            # PRO Tools (Month 5)
            CodeQLWrapper(project_path),
            GosecWrapper(project_path),
            StaticcheckWrapper(project_path),
            SpotBugsWrapper(project_path),
            PmdWrapper(project_path),
            ShellCheckWrapper(project_path),
            RetireJsWrapper(project_path),
            KicsWrapper(project_path),
        ]

    def _is_flag_enabled(self, value: str) -> bool:
        return str(value).strip().lower() in {"1", "true", "yes", "on"}

    def _parse_tool_name_list(self, raw: str) -> Set[str]:
        if not raw:
            return set()
        return {tool.strip() for tool in raw.split(",") if tool.strip()}

    def _get_selected_tool_names(self) -> Set[str]:
        all_tool_names = {tool.name for tool in self.all_tools}

        if self.scan_mode == "quick":
            selected = set(self.QUICK_PROFILE_TOOLS)
        elif self.scan_mode == "deep":
            selected = set(self.DEEP_PROFILE_TOOLS)
        else:  # custom
            custom_names = self._parse_tool_name_list(os.getenv("SCAN_CUSTOM_TOOLS", ""))
            if custom_names:
                selected = custom_names
            else:
                logger.warning(
                    f"[Scan {self.scan_id}] custom mode without SCAN_CUSTOM_TOOLS, fallback to deep profile"
                )
                selected = set(self.DEEP_PROFILE_TOOLS)

        if self.stabilization_enabled:
            staged_names = self._parse_tool_name_list(os.getenv("STABILIZATION_TOOL_NAMES", ""))
            if not staged_names:
                staged_names = set(self.DEFAULT_STABILIZATION_TOOLS)
            selected.update(staged_names)

        return selected.intersection(all_tool_names)
    
    # ... (run_scan, _publish_progress, etc. unchanged) ...

    def _filter_tools(self, languages: List[str], framework: str) -> List:
        """
        Filter tools based on detected languages AND license status AND availability
        """
        tools_to_run = []
        selected_tool_names = self._get_selected_tool_names()
        license_status = self.license_verifier.verify()
        is_pro = license_status.get("plan") in ["pro", "enterprise"]
        
        for tool in self.all_tools:
            # 0. Check profile selection and staged rollout controls
            if tool.name not in selected_tool_names:
                logger.debug(f"[Scan {self.scan_id}] Skipping {tool.name} (not in profile '{self.scan_mode}')")
                continue

            # 1. Check if tool is applicable for this project
            if not tool.should_run(languages, framework):
                logger.debug(f"[Scan {self.scan_id}] Skipping {tool.name} (not applicable)")
                continue

            # 2. Check if tool is installed/available
            if not tool.is_available():
                logger.warning(f"[Scan {self.scan_id}] Skipping {tool.name} (binary not found in PATH)")
                continue

            # 3. Check license requirement
            if tool.requires_license and not is_pro:
                logger.info(f"[Scan {self.scan_id}] Skipping {tool.name} (requires PRO license)")
                continue

            tools_to_run.append(tool)
        
        return tools_to_run

    def run_scan(self) -> ScanResultSchema:
        """
        Execute complete security scan
        
        Returns:
            ScanResult with all findings and metadata
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"[Scan {self.scan_id}] Starting scan on {self.project_path}")
        
        try:
            # Step 1: Detect languages and frameworks
            self._publish_progress(0, "Detecting languages and frameworks...")
            languages = self.language_detector.detect(self.project_path)
            framework = self.framework_detector.detect(self.project_path)
            
            logger.info(f"[Scan {self.scan_id}] Detected languages: {languages}")
            logger.info(f"[Scan {self.scan_id}] Detected framework: {framework}")
            
            # Step 2: Filter tools based on detected languages/frameworks
            self._publish_progress(10, "Selecting applicable tools...")
            tools_to_run = self._filter_tools(languages, framework)
            tool_names = [tool.name for tool in tools_to_run]
            logger.info(f"[Scan {self.scan_id}] Running {len(tools_to_run)} tools")
            
            # Announce the list of tools that will be run
            self._publish_progress(
                12, 
                f"Selected {len(tools_to_run)} tools: {', '.join(tool_names)}", 
                tools_total=len(tools_to_run),
                tools_list=tool_names
            )
            
            # Step 3: Execute tools sequentially
            all_findings: List[FindingSchema] = []
            tool_results: List[ToolResultSchema] = []
            tools_executed: List[str] = []
            
            for i, tool in enumerate(tools_to_run):
                # Calculate progress percentage (10% for detection, 80% for tools, 10% for finalization)
                progress = 15 + int((i / len(tools_to_run)) * 75)
                self._publish_progress(
                    progress, 
                    f"Running {tool.name}...",
                    current_tool=tool.name,
                    tool_status="running"
                )
                
                # Execute tool
                result = tool.execute()
                tool_results.append(result)
                
                if result.status == "success":
                    all_findings.extend(result.findings)
                    tools_executed.append(tool.name)
                    logger.info(
                        f"[Scan {self.scan_id}] {tool.name}: "
                        f"{len(result.findings)} findings in {result.execution_time:.2f}s"
                    )
                    # Report completion of this tool
                    self._publish_progress(
                        progress, 
                        f"Completed {tool.name}",
                        current_tool=tool.name,
                        tool_status="completed",
                        findings_count=len(result.findings)
                    )
                else:
                    logger.warning(
                        f"[Scan {self.scan_id}] {tool.name} {result.status}: "
                        f"{result.error_message}"
                    )
                    self._publish_progress(
                        progress, 
                        f"Failed {tool.name}",
                        current_tool=tool.name,
                        tool_status="failed",
                        error=result.error_message
                    )
            
            # Step 4: Deduplicate findings
            self._publish_progress(90, "Deduplicating findings...")
            deduplicated_findings = self._deduplicate_findings(all_findings)
            
            # Step 5: Finalize
            self._publish_progress(90, "Finalizing scan results...")
            
            completed_at = datetime.now(timezone.utc)
            total_time = (completed_at - start_time).total_seconds()
            
            # Create result
            result = ScanResultSchema(
                scan_id=self.scan_id,
                project_path=str(self.project_path),
                status="completed",
                started_at=start_time,
                completed_at=completed_at,
                total_findings=len(deduplicated_findings),
                findings=deduplicated_findings,
                tools_executed=tools_executed,
                tool_results=tool_results,
                execution_time=total_time,
                metadata={
                    "languages": languages,
                    "framework": framework,
                    "scan_mode": self.scan_mode,
                    "stabilization_enabled": self.stabilization_enabled,
                    "tools_total": len(self.all_tools),
                    "tools_run": len(tools_executed),
                    "original_findings_count": len(all_findings),
                    "deduplicated_findings_count": len(deduplicated_findings)
                }
            )
            
            self._publish_progress(100, "Scan complete")
            logger.info(
                f"[Scan {self.scan_id}] Completed: {len(deduplicated_findings)} findings "
                f"(deduplicated from {len(all_findings)}) "
                f"from {len(tools_executed)} tools in {total_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[Scan {self.scan_id}] Failed: {str(e)}", exc_info=True)
            
            # Create failed result
            return ScanResultSchema(
                scan_id=self.scan_id,
                project_path=str(self.project_path),
                status="failed",
                started_at=start_time,
                completed_at=datetime.now(timezone.utc),
                total_findings=0,
                findings=[],
                tools_executed=[],
                tool_results=[],
                execution_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                metadata={"error": str(e)}
            )
            
    def _deduplicate_findings(self, findings: List[FindingSchema]) -> List[FindingSchema]:
        """
        Deduplicate findings from multiple tools
        
        Strategy:
        1. Group by file_path
        2. Within file, look for findings at same/nearby lines with same type/severity
        3. Merge duplicates
        """
        if not findings:
            return []
            
        unique_findings = []
        processed_indices = set()
        
        # Sort by file path and line number for easier processing
        sorted_findings = sorted(findings, key=lambda f: (f.file_path, f.line_start))
        
        for i, f1 in enumerate(sorted_findings):
            if i in processed_indices:
                continue
                
            current_group = [f1]
            processed_indices.add(i)
            
            # Look ahead for duplicates
            for j in range(i + 1, len(sorted_findings)):
                if j in processed_indices:
                    continue
                    
                f2 = sorted_findings[j]
                
                # Different file means no more duplicates for f1 (since sorted)
                if f2.file_path != f1.file_path:
                    break
                    
                # Check for duplicate criteria
                if self._is_duplicate(f1, f2):
                    current_group.append(f2)
                    processed_indices.add(j)
            
            # Merge group into single finding
            unique_findings.append(self._merge_findings(current_group))
            
        return unique_findings
    
    def _is_duplicate(self, f1: FindingSchema, f2: FindingSchema) -> bool:
        """Check if two findings are duplicates"""
        # Must be same file (already checked in caller, but safety check)
        if f1.file_path != f2.file_path:
            return False
            
        # Check line proximity (within 2 lines)
        if abs(f1.line_start - f2.line_start) > 2:
            return False
            
        # Check type/title similarity
        # Simplistic check: if one type/title contains the other, or vice versa
        # Or if both are "sqli", "xss" etc
        if f1.type.lower() in f2.type.lower() or f2.type.lower() in f1.type.lower():
            return True
            
        return False
        
    def _merge_findings(self, group: List[FindingSchema]) -> FindingSchema:
        """Merge a group of duplicate findings into one"""
        if len(group) == 1:
            return group[0]
            
        # Base finding is the one with highest confidence
        primary = max(group, key=lambda f: f.confidence)
        
        # Merge metadata
        merged_metadata = primary.metadata.copy()
        merged_metadata["duplicate_count"] = len(group)
        merged_metadata["merged_tools"] = list(set(
            f.metadata.get("tool", "unknown") for f in group
        ))
        
        return FindingSchema(
            type=primary.type,
            severity=primary.severity,
            confidence=max(f.confidence for f in group),
            file_path=primary.file_path,
            line_start=primary.line_start,
            line_end=primary.line_end,
            message=primary.message,
            code_snippet=primary.code_snippet,
            cwe_id=primary.cwe_id,
            owasp_category=primary.owasp_category,
            metadata=merged_metadata
        )
    
    
    def _publish_progress(self, percentage: int, message: str, **kwargs):
        """
        Publish scan progress to Redis pub/sub channel
        
        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
            **kwargs: Additional data to include in payload
        """
        try:
            progress_data = {
                "scan_id": self.scan_id,
                "progress": percentage,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            # Merge extra data
            progress_data.update(kwargs)
            
            channel = f"scan:{self.scan_id}:progress"
            self.redis_client.publish(channel, json.dumps(progress_data))
            
            logger.debug(f"[Scan {self.scan_id}] Progress: {percentage}% - {message}")
            
        except Exception as e:
            # Don't fail the scan if progress publishing fails
            logger.warning(f"[Scan {self.scan_id}] Failed to publish progress: {str(e)}")
