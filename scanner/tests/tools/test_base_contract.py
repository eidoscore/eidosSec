from pathlib import Path

from app.schemas import FindingSchema, SeverityLevel, ToolResultSchema
from app.tools.base import ToolWrapper


class LegacyListWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "legacy-list"

    @property
    def command(self) -> list[str]:
        return ["echo", "legacy"]

    def parse_output(self, output: str):
        return []

    def execute(self):
        # Legacy behavior used by many wrappers in this repo.
        return [
            FindingSchema(
                type="legacy-rule",
                severity=SeverityLevel.LOW,
                confidence=80,
                file_path="app.py",
                line_start=1,
                line_end=1,
                message="legacy finding",
            )
        ]


class LegacyNoneWrapper(ToolWrapper):
    @property
    def name(self) -> str:
        return "legacy-none"

    @property
    def command(self) -> list[str]:
        return ["echo", "legacy"]

    def parse_output(self, output: str):
        return []

    def execute(self):
        return None


def test_legacy_execute_is_normalized_to_tool_result(tmp_path: Path):
    wrapper = LegacyListWrapper(tmp_path)
    result = wrapper.execute()

    assert isinstance(result, ToolResultSchema)
    assert result.tool_name == "legacy-list"
    assert result.status == "success"
    assert len(result.findings) == 1


def test_legacy_none_result_is_normalized_to_empty_success(tmp_path: Path):
    wrapper = LegacyNoneWrapper(tmp_path)
    result = wrapper.execute()

    assert isinstance(result, ToolResultSchema)
    assert result.tool_name == "legacy-none"
    assert result.status == "success"
    assert result.findings == []
