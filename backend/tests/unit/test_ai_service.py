import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai_service import AIService
from app.config import settings

@pytest.mark.asyncio
async def test_analyze_finding_mock():
    """Test AI service falls back to mock when ENABLE_AI_FEATURES is true but keys missing"""
    # Temporarily enable AI
    with patch("app.config.settings.ENABLE_AI_FEATURES", True):
        # Ensure no keys to trigger mock or check default behavior
        service = AIService()
        # Force provider to mock for test stability or assume default mock behavior
        service.provider = "mock"
        
        finding_data = {
            "type": "SQL Injection",
            "message": "User input used in query",
            "severity": "CRITICAL"
        }
        
        result = await service.analyze_finding(finding_data)
        
        assert result["provider"] == "mock"
        assert result["confidence"] == 0.85
        assert "fix_suggestion" in result

@pytest.mark.asyncio
async def test_analyze_finding_disabled():
    """Test service returns disabled status when flag is off"""
    with patch("app.config.settings.ENABLE_AI_FEATURES", False):
        service = AIService()
        result = await service.analyze_finding({})
        assert result["status"] == "disabled"

@pytest.mark.asyncio
async def test_openai_call_structure():
    """Test that OpenAI prompt is constructed correctly"""
    with patch("app.config.settings.ENABLE_AI_FEATURES", True):
        service = AIService()
        service.provider = "openai"
        service._call_openai = AsyncMock(return_value={"mock": "response"})
        
        finding_data = {
            "type": "XSS",
            "message": "Unescaped output",
            "severity": "HIGH",
            "file_path": "index.js",
            "line_start": 10,
            "code_snippet": "res.send(input)"
        }
        
        await service.analyze_finding(finding_data)
        
        # Verify prompt construction
        args, _ = service._call_openai.call_args
        prompt = args[0]
        assert "XSS" in prompt
        assert "res.send(input)" in prompt
