"""
Mock LLM Provider implementations for demonstration.
These simulate real API calls without requiring actual API keys.
"""

import time
import random
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Structured response from an LLM provider."""
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str
    latency_ms: float


class MockLLMProvider:
    """Base class for mock LLM providers."""
    
    def __init__(self, provider_id: str, model: str, base_latency_ms: float = 1000):
        self.provider_id = provider_id
        self.model = model
        self.base_latency_ms = base_latency_ms
        self.failure_rate = 0.0  # Can be set to simulate failures
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """
        Generate a mock response.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLMResponse with mock data
        """
        # Simulate network latency (base + random variation)
        latency = self.base_latency_ms + random.uniform(-200, 500)
        time.sleep(latency / 1000)  # Convert to seconds
        
        # Simulate occasional failures
        if random.random() < self.failure_rate:
            raise Exception(f"{self.provider_id} API error: Service unavailable")
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        input_text = (system_prompt or "") + prompt
        input_tokens = len(input_text) // 4
        
        # Generate mock response
        response_text = f"Mock response from {self.provider_id} ({self.model}) for: {prompt[:50]}..."
        output_tokens = len(response_text) // 4
        
        return LLMResponse(
            content=response_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=self.model,
            provider=self.provider_id,
            latency_ms=latency
        )


class MockOpenAIProvider(MockLLMProvider):
    def __init__(self):
        super().__init__(
            provider_id="openai",
            model="gpt-4",
            base_latency_ms=1200  # Slightly slower
        )
        self.cost_per_1k_input = 0.03
        self.cost_per_1k_output = 0.06


class MockAnthropicProvider(MockLLMProvider):
    def __init__(self):
        super().__init__(
            provider_id="anthropic",
            model="claude-3-5-sonnet-20241022",
            base_latency_ms=800  # Faster
        )
        self.cost_per_1k_input = 0.003
        self.cost_per_1k_output = 0.015

