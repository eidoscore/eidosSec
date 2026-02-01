"""Scan orchestrator - coordinates execution of security tools"""
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import redis
import json
import logging

from app.tools.semgrep import SemgrepWrapper
from app.tools.bandit import BanditWrapper
from app.tools.eslint import EslintWrapper
from app.tools.phpstan import PhpstanWrapper
from app.tools.brakeman import BrakemanWrapper

class ScanOrchestrator:
    # ... (existing methods)

    def __init__(self, project_path: Path, scan_id: str, redis_url: str):
        # ... (existing init code)
        
        self.all_tools = [
            SemgrepWrapper(project_path),
            BanditWrapper(project_path),
            TruffleHogWrapper(project_path),
            GitleaksWrapper(project_path),
            TrivyWrapper(project_path),
            EslintWrapper(project_path),
            PhpstanWrapper(project_path),
            BrakemanWrapper(project_path),
        ]
    
    def run_scan(self) -> ScanResultSchema:
        """
        Execute complete security scan
        
        Returns:
            ScanResult with all findings and metadata
        """
        start_time = datetime.utcnow()
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
            logger.info(f"[Scan {self.scan_id}] Running {len(tools_to_run)} tools")
            
            # Step 3: Execute tools sequentially
            all_findings: List[FindingSchema] = []
            tool_results: List[ToolResultSchema] = []
            tools_executed: List[str] = []
            
            for i, tool in enumerate(tools_to_run):
                # Calculate progress percentage (10% for detection, 80% for tools, 10% for finalization)
                progress = 10 + int((i / len(tools_to_run)) * 80)
                self._publish_progress(progress, f"Running {tool.name}...")
                
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
                else:
                    logger.warning(
                        f"[Scan {self.scan_id}] {tool.name} {result.status}: "
                        f"{result.error_message}"
                    )
            
            # Step 4: Finalize
            self._publish_progress(90, "Finalizing scan results...")
            
            completed_at = datetime.utcnow()
            total_time = (completed_at - start_time).total_seconds()
            
            # Create result
            result = ScanResultSchema(
                scan_id=self.scan_id,
                project_path=str(self.project_path),
                status="completed",
                started_at=start_time,
                completed_at=completed_at,
                total_findings=len(all_findings),
                findings=all_findings,
                tools_executed=tools_executed,
                tool_results=tool_results,
                execution_time=total_time,
                metadata={
                    "languages": languages,
                    "framework": framework,
                    "tools_total": len(self.all_tools),
                    "tools_run": len(tools_executed),
                }
            )
            
            self._publish_progress(100, "Scan complete")
            logger.info(
                f"[Scan {self.scan_id}] Completed: {len(all_findings)} findings "
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
                completed_at=datetime.utcnow(),
                total_findings=0,
                findings=[],
                tools_executed=[],
                tool_results=[],
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                metadata={"error": str(e)}
            )
    
    def _filter_tools(self, languages: List[str], framework: str) -> List:
        """
        Filter tools based on detected languages and frameworks
        
        Args:
            languages: Detected programming languages
            framework: Detected framework (if any)
            
        Returns:
            List of tools to run
        """
        tools_to_run = []
        
        for tool in self.all_tools:
            if tool.should_run(languages, framework):
                tools_to_run.append(tool)
            else:
                logger.info(f"[Scan {self.scan_id}] Skipping {tool.name} (not applicable)")
        
        return tools_to_run
    
    def _publish_progress(self, percentage: int, message: str):
        """
        Publish scan progress to Redis pub/sub channel
        
        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
        """
        try:
            progress_data = {
                "scan_id": self.scan_id,
                "progress": percentage,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            channel = f"scan:{self.scan_id}:progress"
            self.redis_client.publish(channel, json.dumps(progress_data))
            
            logger.debug(f"[Scan {self.scan_id}] Progress: {percentage}% - {message}")
            
        except Exception as e:
            # Don't fail the scan if progress publishing fails
            logger.warning(f"[Scan {self.scan_id}] Failed to publish progress: {str(e)}")
