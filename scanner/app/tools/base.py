"""Base class for security tool wrappers"""
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, List, Optional
import hashlib
import logging
import os
import subprocess
import tempfile

from app.schemas import FindingSchema, ToolResultSchema, ToolStatus

logger = logging.getLogger(__name__)


class ToolWrapper(ABC):
    """
    Abstract base class for security tool wrappers.

    All security tools must inherit from this class and implement:
    - name property: tool name
    - command property: command to execute
    - parse_output method: parse tool output to findings
    """

    def __init_subclass__(cls, **kwargs):
        """
        Normalize custom execute() implementations to ToolResultSchema.

        Many legacy wrappers still return List[FindingSchema]. This hook keeps
        those wrappers integratable without deleting them while enforcing one
        outward execution contract for orchestrator flow.
        """
        super().__init_subclass__(**kwargs)

        custom_execute = cls.__dict__.get("execute")
        if custom_execute is None or custom_execute is ToolWrapper.execute:
            return

        if getattr(custom_execute, "_eidos_contract_wrapped", False):
            return

        @wraps(custom_execute)
        def wrapped_execute(self, *args, **kwargs):
            start_time = datetime.now()

            try:
                raw_result = custom_execute(self, *args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                return self._normalize_execution_result(raw_result, execution_time)
            except subprocess.TimeoutExpired:
                execution_time = (datetime.now() - start_time).total_seconds()
                self.logger.error("[%s] Timed out after %ss", self.name, self.timeout)
                return ToolResultSchema(
                    tool_name=self.name,
                    status=ToolStatus.TIMEOUT,
                    findings=[],
                    execution_time=execution_time,
                    error_message=f"Tool execution timed out after {self.timeout}s",
                )
            except FileNotFoundError:
                execution_time = (datetime.now() - start_time).total_seconds()
                self.logger.error("[%s] Tool not found - is it installed?", self.name)
                return ToolResultSchema(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    findings=[],
                    execution_time=execution_time,
                    error_message=f"Tool binary not found. Please ensure {self.name} is installed.",
                )
            except Exception as exc:
                execution_time = (datetime.now() - start_time).total_seconds()
                self.logger.error("[%s] Unexpected error: %s", self.name, exc)
                return ToolResultSchema(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    findings=[],
                    execution_time=execution_time,
                    error_message=f"Unexpected error: {exc}",
                )

        wrapped_execute._eidos_contract_wrapped = True
        setattr(cls, "execute", wrapped_execute)

    def __init__(self, project_path: Path):
        """Initialize tool wrapper."""
        self.project_path = project_path
        self.timeout = 300  # 5 minutes default per tool
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._last_command_returncode: Optional[int] = None
        self._last_command_stderr: str = ""
        default_results_dir = Path(tempfile.gettempdir()) / "eidossec-scan-results"
        self.scan_results_dir = Path(os.getenv("SCAN_RESULTS_DIR", str(default_results_dir)))

    @property
    def requires_license(self) -> bool:
        """
        Whether this tool requires a PRO license.
        Override in PRO tools to return True.
        """
        return False

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (e.g., 'semgrep', 'bandit')."""

    @property
    @abstractmethod
    def command(self) -> List[str]:
        """Command arguments used to execute the tool."""

    @abstractmethod
    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse tool output into findings."""

    def is_available(self) -> bool:
        """
        Check if the tool binary is available in the system PATH.
        Can be overridden to check specific versions.
        """
        import shutil

        binary = self.command[0]
        if shutil.which(binary) is None:
            return False

        version = self.get_version()
        if version == "not found" or version == "unknown":
            self.logger.warning("Tool %s binary found but version detection failed", self.name)
        else:
            self.logger.info("Tool %s available (Version: %s)", self.name, version)

        return True

    def get_version(self) -> str:
        """Get the version of the tool."""
        try:
            binary = self.command[0]
            result = subprocess.run(
                [binary, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "not found"

    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        """Determine if tool should run based on project detection."""
        return True

    def execute_command(
        self,
        command: List[str],
        timeout: Optional[int] = None,
        include_stderr: bool = False,
    ) -> str:
        """
        Execute a command from a wrapper and return stdout.

        This method intentionally does not fail on non-zero exit code because
        many security tools use non-zero for "findings detected".
        """
        result = subprocess.run(
            command,
            cwd=self.project_path,
            capture_output=True,
            text=True,
            timeout=timeout or self.timeout,
            check=False,
        )

        self._last_command_returncode = result.returncode
        self._last_command_stderr = result.stderr or ""

        if include_stderr:
            if result.stdout and result.stderr:
                return f"{result.stdout}\n{result.stderr}"
            return result.stdout or result.stderr or ""

        return result.stdout or ""

    def get_output_path(self, filename: str) -> Path:
        """
        Return a writable output file path for tool artifacts.

        This avoids writing into project source mounts that may be read-only.
        """
        project_hash = hashlib.sha1(str(self.project_path).encode("utf-8")).hexdigest()[:12]
        output_dir = self.scan_results_dir / project_hash / self.name
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / filename

    def _normalize_execution_result(self, raw_result: Any, execution_time: float) -> ToolResultSchema:
        """Coerce legacy wrapper results into ToolResultSchema."""
        if isinstance(raw_result, ToolResultSchema):
            if raw_result.execution_time <= 0:
                return raw_result.model_copy(update={"execution_time": execution_time})
            return raw_result

        if raw_result is None:
            findings: List[FindingSchema] = []
        elif isinstance(raw_result, list):
            findings = raw_result
        else:
            self.logger.error("[%s] Unexpected execute() return type: %s", self.name, type(raw_result).__name__)
            return ToolResultSchema(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                findings=[],
                execution_time=execution_time,
                error_message=f"Unexpected execute() return type: {type(raw_result).__name__}",
            )

        return ToolResultSchema(
            tool_name=self.name,
            status=ToolStatus.SUCCESS,
            findings=findings,
            execution_time=execution_time,
            raw_output=self._last_command_stderr[:1000] if self._last_command_stderr else None,
        )

    def execute(self) -> ToolResultSchema:
        """Execute tool and return normalized results."""
        start_time = datetime.now()

        try:
            self.logger.info("[%s] Executing on %s", self.name, self.project_path)
            self.logger.debug("[%s] Command: %s", self.name, " ".join(self.command))

            output = self.execute_command(self.command)
            execution_time = (datetime.now() - start_time).total_seconds()

            try:
                findings = self.parse_output(output)
                self.logger.info("[%s] Found %s findings in %.2fs", self.name, len(findings), execution_time)
                return ToolResultSchema(
                    tool_name=self.name,
                    status=ToolStatus.SUCCESS,
                    findings=findings,
                    execution_time=execution_time,
                    raw_output=output[:10000],
                )
            except Exception as parse_error:
                self.logger.error("[%s] Failed to parse output: %s", self.name, parse_error)
                return ToolResultSchema(
                    tool_name=self.name,
                    status=ToolStatus.FAILED,
                    findings=[],
                    execution_time=execution_time,
                    error_message=f"Output parsing failed: {parse_error}",
                    raw_output=output[:1000],
                )

        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error("[%s] Timed out after %ss", self.name, self.timeout)
            return ToolResultSchema(
                tool_name=self.name,
                status=ToolStatus.TIMEOUT,
                findings=[],
                execution_time=execution_time,
                error_message=f"Tool execution timed out after {self.timeout}s",
            )

        except FileNotFoundError:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error("[%s] Tool not found - is it installed?", self.name)
            return ToolResultSchema(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                findings=[],
                execution_time=execution_time,
                error_message=f"Tool binary not found. Please ensure {self.name} is installed.",
            )

        except Exception as exc:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error("[%s] Unexpected error: %s", self.name, exc)
            return ToolResultSchema(
                tool_name=self.name,
                status=ToolStatus.FAILED,
                findings=[],
                execution_time=execution_time,
                error_message=f"Unexpected error: {exc}",
            )
