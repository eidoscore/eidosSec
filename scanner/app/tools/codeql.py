from typing import List
from app.tools.base import ToolWrapper
from app.schemas import FindingSchema
from app.parsers.sarif import SarifParser

class CodeQLWrapper(ToolWrapper):
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
        return ["codeql", "database", "analyze", "--format=sarif-latest", "--output=codeql-results.sarif", "."]

    def parse_output(self, output: str) -> List[FindingSchema]:
        # CodeQL writes to a file, but for the base class execute() pattern we might need to read that file.
        # However, Base ToolWrapper captures STDOUT.
        # We'll assume for now we might read the file if generated, or just parse if it was cat'd to stdout.
        # Since standard CodeQL output is to file, we'd normally override execute().
        # But let's assume we can read the file content here or the command cats it.
        
        # NOTE: In a real implementation, we would override execute() to read the file.
        # For now, let's use the SarifParser on the 'output' assuming the runner managed to capture it
        # or we read it from the file system.
        
        # Let's try to read the file if it exists, otherwise fall back to provided output
        try:
            with open(self.project_path / "codeql-results.sarif", "r") as f:
                content = f.read()
                return SarifParser.parse(content, self.name)
        except FileNotFoundError:
            return SarifParser.parse(output, self.name)
