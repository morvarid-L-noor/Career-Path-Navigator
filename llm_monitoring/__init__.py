"""
LLM Monitoring System - Proof of Concept

A monitoring wrapper for LLM API calls with:
- Structured telemetry logging
- Provider failover with circuit breakers
- Metrics collection (latency, tokens, costs, errors)
"""

from .monitor import LLMMonitor
from .providers import MockLLMProvider, MockOpenAIProvider, MockAnthropicProvider
from .metrics import MetricsCollector, RequestMetrics
from .circuit_breaker import CircuitBreaker, CircuitState

__all__ = [
    'LLMMonitor',
    'MockLLMProvider',
    'MockOpenAIProvider',
    'MockAnthropicProvider',
    'MetricsCollector',
    'RequestMetrics',
    'CircuitBreaker',
    'CircuitState'
]

