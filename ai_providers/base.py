"""Abstract AI provider interface."""

from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """Abstract base class for AI text generation providers."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            system_prompt: Optional system prompt to set context

        Returns:
            Generated text response

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available.

        Returns:
            True if provider can be used, False otherwise
        """
        pass
