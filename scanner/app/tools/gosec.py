from typing import List, Optional
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema
from app.parsers.sarif import SarifParser

class GosecWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "gosec"
    
    @property
    def requires_license(self) -> bool:
        return True

    @property
    def command(self) -> List[str]:
        return ["gosec", "-fmt=sarif", "-out=results.sarif", "./..."]

    def should_run(self, languages: List[str], framework: Optional[str]) -> bool:
        return "go" in languages

    def parse_output(self, output: str) -> List[FindingSchema]:
        # Gosec usually writes to file with -out
        try:
            with open(self.project_path / "results.sarif", "r") as f:
                content = f.read()
                return SarifParser.parse(content, self.name)
        except FileNotFoundError:
            # Maybe it output to stdout?
            return SarifParser.parse(output, self.name)
