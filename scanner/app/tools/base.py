"""Base class for security tool wrappers"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import subprocess
import logging
from datetime import datetime

from app.schemas import ToolResultSchema, FindingSchema, ToolStatus

logger = logging.getLogger(__name__)


class ToolWrapper(ABC):
    """
    Abstract base class for security tool wrappers
    
    All security tools must inherit from this class and implement:
    - name property: tool name
    - command property: command to execute
    - parse_output method: parse tool output to findings
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize tool wrapper
        
        Args:
            project_path: Path to project directory to scan
        """
        self.project_path = project_path
        self.timeout = 300  # 5 minutes default per tool
        
    @property
    def requires_license(self) -> bool:
        """
        Whether this tool requires a PRO license
        Override in PRO tools to return True
        """
        return False

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (e.g., 'semgrep', 'bandit')"""
        pass
    
    @property
    @abstractmethod
    def command(self) -> List[str]:
        """
        Command to execute tool
        
        Returns:
            List of command arguments (e.g., ['semgrep', '--json', '.'])
        """
        pass
    
    @abstractmethod
    def parse_output(self, output: str) -> List[FindingSchema]:
        """
        Parse tool output to findings
        
        Args:
            output: Raw tool output (usually JSON)
            
        Returns:
            List of Finding objects
        """
        pass
    
    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """
        Determine if tool should run based on detected languages/frameworks
        
        Override this method if tool is language/framework-specific
        
        Args:
            languages: Detected programming languages
            framework: Detected framework (if any)
            
        Returns:
            True if tool should run, False otherwise
        """
        return True  # By default, run all tools
    
    def execute(self) -> ToolResultSchema:
        """
        Execute tool and return results
        
        Returns:
            ToolResult with findings, status, and timing
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"[{self.name}] Executing on {self.project_path}")
            logger.debug(f"[{self.name}] Command: {' '.join(self.command)}")
            
            # Execute tool
            result = subprocess.run(
                self.command,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False  # Don't raise on non-zero exit codes
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Some tools return non-zero exit codes when findings are found
            # So we don't check return code, just parse output
            
            # Parse output to findings
            try:
                findings = self.parse_output(result.stdout)
                logger.info(f"[{self.name}] Found {len(findings)} findings in {execution_time:.2f}s")
                
                return ToolResultSchema(
                    tool_name=self.name,
                    status=ToolStatus.SUCCESS,
                    findings=findings,
                    execution_time=execution_time,
                    raw_output=result.stdout[:10000]  # Limit raw output size
                )
                
            except Exception as parse_error:
                logger.error(f"[{self.name}] Failed to parse output: {str(parse_error)}")
                return ToolResultSchema(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    findings=[],
                    execution_time=execution_time,
                    error_message=f"Output parsing failed: {str(parse_error)}",
                    raw_output=result.stdout[:1000]
                )
            
        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"[{self.name}] Timed out after {self.timeout}s")
            return ToolResultSchema(
                tool_name=self.name,
                status=ToolStatus.TIMEOUT,
                findings=[],
                execution_time=execution_time,
                error_message=f"Tool execution timed out after {self.timeout}s"
            )
            
        except FileNotFoundError:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"[{self.name}] Tool not found - is it installed?")
            return ToolResultSchema(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                findings=[],
                execution_time=execution_time,
                error_message=f"Tool binary not found. Please ensure {self.name} is installed."
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"[{self.name}] Unexpected error: {str(e)}")
            return ToolResultSchema(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                findings=[],
                execution_time=execution_time,
                error_message=f"Unexpected error: {str(e)}"
            )
