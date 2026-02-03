import logging
import json
import httpx
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service to handle AI-powered analysis of security findings"""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.provider = "openai" if self.openai_api_key else "anthropic" if self.anthropic_api_key else "mock"
        
    async def analyze_finding(self, finding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a finding using the configured AI provider.
        
        Args:
            finding_data: Dictionary containing finding details (message, code_snippet, etc.)
            
        Returns:
            Dict containing analysis results (explanation, severity assessment, fix text)
        """
        if not settings.ENABLE_AI_FEATURES:
            return {"status": "disabled", "message": "AI features are disabled"}
            
        context = self._build_prompt(finding_data)
        
        try:
            if self.provider == "openai":
                return await self._call_openai(context)
            elif self.provider == "anthropic":
                return await self._call_anthropic(context)
            else:
                return self._mock_analysis(finding_data)
        except Exception as e:
            logger.error(f"AI Analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    def _build_prompt(self, finding: Dict[str, Any]) -> str:
        """Construct the prompt for the LLM"""
        return f"""
        You are a Senior Security Engineer. Analyze the following security finding.
        
        Finding Type: {finding.get('type')}
        Severity: {finding.get('severity')}
        File: {finding.get('file_path')}
        Line: {finding.get('line_start')}
        
        Message:
        {finding.get('message')}
        
        Code Snippet:
        ```
        {finding.get('code_snippet', 'No snippet provided')}
        ```
        
        Task:
        1. Explain the vulnerability in simple terms.
        2. Assess if this is likely a True Positive or False Positive.
        3. Provide a secure code fix if applicable.
        
        Return your response in JSON format:
        {{
            "explanation": "...",
            "assessment": "True Positive/False Positive/Unknown",
            "fix_suggestion": "...",
            "confidence": 0.0-1.0
        }}
        """

    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {"role": "system", "content": "You are a specialized security analysis AI. Output valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

    async def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic API"""
        # Placeholder for Anthropic implementation
        return {"error": "Anthropic not fully implemented yet"}

    def _mock_analysis(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Mock analysis for development/testing"""
        return {
            "explanation": "This is a simulated AI analysis. The finding appears to be a standard pattern match.",
            "assessment": "True Positive (Simulated)",
            "fix_suggestion": "# Simulated secure code fix\n# Ensure inputs are validated",
            "confidence": 0.85,
            "provider": "mock"
        }

# Global instance
ai_service = AIService()
