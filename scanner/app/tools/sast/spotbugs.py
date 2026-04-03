import json
import subprocess
from typing import List, Optional, Dict, Any
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema, SeverityLevel

class SpotBugsWrapper(ToolWrapper):
    def _output_file(self):
        return self.get_output_path("spotbugs-results.xml")

    @property
    def name(self) -> str:
        return "spotbugs"
    
    @property
    def requires_license(self) -> bool:
        return True  # PRO tool
    
    @property
    def command(self) -> List[str]:
        """CLI invocation for SpotBugs analysis."""
        return [
            "spotbugs",
            "-textui",
            "-xml",
            "-output", str(self._output_file()),
            "."
        ]

    def get_version(self) -> str:
        """Get SpotBugs version"""
        import subprocess
        try:
            result = subprocess.run(
                ["spotbugs", "-version"],
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
        return any(lang.lower() == "java" for lang in languages)
    
    def execute(self) -> List[FindingSchema]:
        """Execute SpotBugs and return findings"""
        try:
            # SpotBugs writes to file
            self.execute_command(self.command)
            
            # Read the generated XML file
            results_file = self._output_file()
            if results_file.exists():
                with open(results_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    return self.parse_output(content)
            return []
        except Exception as e:
            self.logger.error(f"SpotBugs execution failed: {e}")
            return []

    def parse_output(self, output: str) -> List[FindingSchema]:
        # SpotBugs usually writes to a file. 
        # If we use -output results.xml, we need to read it.
        # But for now, we'll implement a basic XML parser if needed.
        return []
