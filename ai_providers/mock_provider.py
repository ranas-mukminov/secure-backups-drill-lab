"""Mock AI provider for testing."""

from typing import Optional

from ai_providers.base import AIProvider


class MockAIProvider(AIProvider):
    """Mock AI provider for testing (returns deterministic responses)."""

    def __init__(self, response: str = "Mock AI response") -> None:
        """Initialize mock provider.

        Args:
            response: The response to return for all requests
        """
        self.response = response

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate mock text response.

        Args:
            prompt: The text prompt (ignored)
            max_tokens: Maximum tokens (ignored)
            temperature: Temperature (ignored)
            system_prompt: System prompt (ignored)

        Returns:
            The configured mock response
        """
        return self.response

    def is_available(self) -> bool:
        """Mock provider is always available.

        Returns:
            True
        """
        return True
