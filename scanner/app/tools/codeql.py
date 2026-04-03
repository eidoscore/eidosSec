from typing import List, Optional
import logging

from app.tools.base import ToolWrapper
from app.schemas import FindingSchema
from app.parsers.sarif import SarifParser

logger = logging.getLogger(__name__)


class CodeQLWrapper(ToolWrapper):
    def _output_file(self):
        return self.get_output_path("codeql-results.sarif")

    @property
    def name(self) -> str:
        return "codeql"

    @property
    def requires_license(self) -> bool:
        return True

    @property
    def command(self) -> List[str]:
        # In a real scenario, this would involve complex database creation and analysis steps.
        # For this wrapper, we assume a build script or simplified command that outputs SARIF.
        return [
            "codeql",
            "database",
            "analyze",
            "--format=sarif-latest",
            f"--output={self._output_file()}",
            ".",
        ]

    def get_version(self) -> str:
        """Get CodeQL version"""
        import subprocess

        try:
            result = subprocess.run(
                ["codeql", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                # CodeQL version output is usually the first line
                return result.stdout.splitlines()[0].strip()
            return "unknown"
        except Exception:
            return "not found"

    def should_run(self, languages: List[str], framework: Optional[str] = None) -> bool:
        # CodeQL supports many languages
        supported = ["python", "javascript", "typescript", "go", "java", "cpp", "csharp", "ruby"]
        return any(lang.lower() in supported for lang in languages)

    def execute(self) -> List[FindingSchema]:
        """Execute CodeQL and return findings"""
        try:
            # CodeQL usually outputs to a file, so we override execute to handle that
            self.execute_command(self.command)

            # Read the generated SARIF file
            sarif_file = self._output_file()
            if sarif_file.exists():
                with open(sarif_file, "r", encoding="utf-8") as f:
                    return SarifParser.parse(f.read(), self.name)
            return []
        except Exception as e:
            logger.error("CodeQL execution failed: %s", e)
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        """Parse SARIF output either from stdout or the generated output file."""
        if output and output.strip():
            return SarifParser.parse(output, self.name)

        sarif_file = self._output_file()
        if not sarif_file.exists():
            return []

        try:
            with open(sarif_file, "r", encoding="utf-8") as f:
                return SarifParser.parse(f.read(), self.name)
        except Exception as exc:
            logger.error("Failed to read CodeQL SARIF file: %s", exc)
            return []
