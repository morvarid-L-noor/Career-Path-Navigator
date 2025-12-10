"""
Main monitoring wrapper for LLM API calls.
"""

import json
import time
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from .providers import MockLLMProvider, MockOpenAIProvider, MockAnthropicProvider, LLMResponse
from .circuit_breaker import CircuitBreaker, CircuitState
from .metrics import MetricsCollector, RequestMetrics


class LLMMonitor:
 
    
    def __init__(self, log_file: Optional[str] = None):
     
        # Initialize providers
        self.providers: Dict[str, MockLLMProvider] = {
            "openai": MockOpenAIProvider(),
            "anthropic": MockAnthropicProvider()
        }
        
        # Initialize circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            provider_id: CircuitBreaker()
            for provider_id in self.providers.keys()
        }
        
        # Metrics collector
        self.metrics = MetricsCollector()
        
        # Logging
        self.log_file = log_file
        self.log_buffer: list = []
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        feature_version: Optional[str] = None,
        prompt_version: Optional[str] = None,
        experiment_id: Optional[str] = None,
        variant_id: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate a response with full monitoring.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            provider: Preferred provider (None for auto-selection)
            feature_version: Feature version for tracking
            prompt_version: Prompt version for tracking
            experiment_id: A/B test experiment ID
            variant_id: A/B test variant ID
            
        Returns:
            LLMResponse from the provider
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Select provider (with failover)
        selected_provider_id = self._select_provider(provider)
        provider_instance = self.providers[selected_provider_id]
        circuit_breaker = self.circuit_breakers[selected_provider_id]
        
        # Check circuit breaker
        if not circuit_breaker.can_attempt():
            # Try failover
            failover_provider = self._get_failover_provider(selected_provider_id)
            if failover_provider:
                selected_provider_id = failover_provider
                provider_instance = self.providers[selected_provider_id]
                circuit_breaker = self.circuit_breakers[selected_provider_id]
            else:
                raise Exception("All providers are unavailable (circuit breakers open)")
        
        # Make the API call
        error = None
        response = None
        success = False
        
        try:
            response = provider_instance.generate(prompt, system_prompt)
            success = True
            circuit_breaker.record_success()
        except Exception as e:
            error = str(e)
            circuit_breaker.record_failure()
            raise
        
        finally:
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            
            # Calculate cost
            cost = self._calculate_cost(selected_provider_id, response.input_tokens if response else 0, 
                                       response.output_tokens if response else 0)
            
            # Create metrics
            metrics = RequestMetrics(
                request_id=request_id,
                provider=selected_provider_id,
                model=provider_instance.model,
                latency_ms=latency_ms,
                input_tokens=response.input_tokens if response else 0,
                output_tokens=response.output_tokens if response else 0,
                total_tokens=(response.input_tokens + response.output_tokens) if response else 0,
                cost_usd=cost,
                success=success,
                error=error,
                feature_version=feature_version,
                prompt_version=prompt_version,
                experiment_id=experiment_id,
                variant_id=variant_id
            )
            
            # Record metrics
            self.metrics.record(metrics)
            
            # Log structured telemetry
            self._log_telemetry(metrics, prompt, system_prompt, response)
        
        return response
    
    def _select_provider(self, preferred: Optional[str] = None) -> str:
        """Select a provider, considering circuit breakers."""
        if preferred and preferred in self.providers:
            if self.circuit_breakers[preferred].can_attempt():
                return preferred
        
        # Find first available provider
        for provider_id, cb in self.circuit_breakers.items():
            if cb.can_attempt():
                return provider_id
        
        # If all are down, return preferred or first one anyway
        return preferred or list(self.providers.keys())[0]
    
    def _get_failover_provider(self, current_provider: str) -> Optional[str]:
        """Get a failover provider if current one is down."""
        providers = list(self.providers.keys())
        providers.remove(current_provider)
        
        for provider_id in providers:
            if self.circuit_breakers[provider_id].can_attempt():
                return provider_id
        
        return None
    
    def _calculate_cost(self, provider_id: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on provider pricing."""
        provider = self.providers[provider_id]
        
        if hasattr(provider, 'cost_per_1k_input') and hasattr(provider, 'cost_per_1k_output'):
            input_cost = (input_tokens / 1000) * provider.cost_per_1k_input
            output_cost = (output_tokens / 1000) * provider.cost_per_1k_output
            return input_cost + output_cost
        
        return 0.0
    
    def _log_telemetry(self, metrics: RequestMetrics, prompt: str, 
                      system_prompt: Optional[str], response: Optional[LLMResponse]):
        """Log structured telemetry data."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": metrics.request_id,
            "provider": metrics.provider,
            "model": metrics.model,
            "latency_ms": round(metrics.latency_ms, 2),
            "tokens": {
                "input": metrics.input_tokens,
                "output": metrics.output_tokens,
                "total": metrics.total_tokens
            },
            "cost_usd": round(metrics.cost_usd, 6),
            "success": metrics.success,
            "error": metrics.error,
            "circuit_breaker_state": self.circuit_breakers[metrics.provider].get_state().value,
            "metadata": {
                "feature_version": metrics.feature_version,
                "prompt_version": metrics.prompt_version,
                "experiment_id": metrics.experiment_id,
                "variant_id": metrics.variant_id
            },
            "prompt_length": len(prompt),
            "response_length": len(response.content) if response else 0
        }
        
        # Add to buffer
        self.log_buffer.append(log_entry)
        
        # Write to file if configured
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            "providers": self.metrics.get_all_stats(),
            "total_requests": self.metrics.get_total_requests(),
            "total_cost_usd": round(self.metrics.get_total_cost(), 4),
            "circuit_breakers": {
                provider_id: cb.get_stats()
                for provider_id, cb in self.circuit_breakers.items()
            }
        }
    
    def print_stats(self):
        """Print statistics in a readable format."""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("LLM MONITORING STATISTICS")
        print("="*60)
        
        print(f"\nTotal Requests: {stats['total_requests']}")
        print(f"Total Cost: ${stats['total_cost_usd']:.4f}")
        
        print("\nProvider Statistics:")
        for provider_id, provider_stats in stats['providers'].items():
            print(f"\n  {provider_id.upper()}:")
            print(f"    Requests: {provider_stats['total_requests']}")
            print(f"    Success Rate: {(1 - provider_stats['error_rate']) * 100:.1f}%")
            print(f"    Total Tokens: {provider_stats['total_tokens']:,}")
            print(f"    Total Cost: ${provider_stats['total_cost']:.4f}")
            if provider_stats['total_requests'] > 0:
                print(f"    Latency - P50: {provider_stats['latency_p50']:.0f}ms, "
                      f"P95: {provider_stats['latency_p95']:.0f}ms, "
                      f"P99: {provider_stats['latency_p99']:.0f}ms")
        
        print("\nCircuit Breaker States:")
        for provider_id, cb_stats in stats['circuit_breakers'].items():
            state_icon = "[OK]" if cb_stats['state'] == 'closed' else "[DOWN]" if cb_stats['state'] == 'open' else "[TEST]"
            print(f"  {provider_id}: {state_icon} {cb_stats['state']} "
                  f"(Failures: {cb_stats['failure_count']}, "
                  f"Error Rate: {cb_stats['error_rate']*100:.1f}%)")
        
        print("="*60 + "\n")

