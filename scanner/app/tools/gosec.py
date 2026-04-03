from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema
from app.parsers.sarif import SarifParser

class GosecWrapper(ToolWrapper):
    def _output_file(self):
        return self.get_output_path("gosec-results.sarif")

    @property
    def name(self) -> str:
        return "gosec"
    
    @property
    def requires_license(self) -> bool:
        return True

    @property
    def command(self) -> List[str]:
        return ["gosec", "-fmt=sarif", f"-out={self._output_file()}", "./..."]

    def get_version(self) -> str:
        """Get Gosec version"""
        import subprocess
        try:
            result = subprocess.run(
                ["gosec", "-version"],
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
        return any(lang.lower() == "go" for lang in languages)

    def execute(self) -> List[FindingSchema]:
        """Execute gosec and return findings"""
        try:
            # Base execute_command returns stdout, but gosec writes to results.sarif
            self.execute_command(self.command)
            return self.parse_output("")
        except Exception as e:
            # We don't have logger here, but ToolWrapper has it if we use self.logger
            import logging
            logging.getLogger(__name__).error(f"Gosec execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        # Gosec usually writes to file with -out
        try:
            with open(self._output_file(), "r", encoding="utf-8") as f:
                content = f.read()
                return SarifParser.parse(content, self.name)
        except FileNotFoundError:
            # Maybe it output to stdout?
            return SarifParser.parse(output, self.name)
