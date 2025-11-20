"""Mock AI provider for testing."""


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
        _prompt: str,
        _max_tokens: int = 1000,
        _temperature: float = 0.7,
        _system_prompt: str | None = None,
    ) -> str:
        """Generate mock text response.

        Args:
            _prompt: The text prompt (ignored)
            _max_tokens: Maximum tokens (ignored)
            _temperature: Temperature (ignored)
            _system_prompt: System prompt (ignored)

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
