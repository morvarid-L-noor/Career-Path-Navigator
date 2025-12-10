"""
Main monitoring wrapper for LLM API calls.
Implements: Token Limiter → Cost Limiter → A/B Router → Cache → Provider
"""

import json
import time
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from .providers import MockLLMProvider, MockOpenAIProvider, MockAnthropicProvider, LLMResponse
from .circuit_breaker import CircuitBreaker
from .metrics import MetricsCollector, RequestMetrics
from .cache import ResponseCache


class LLMMonitor:
    """
    Monitoring wrapper for LLM API calls.
    Flow: Token Limiter (500 tokens avg) → Cost Limiter ($5000/month) → Cache → Provider
    """
    
    def __init__(self, log_file: Optional[str] = None):
        self.providers: Dict[str, MockLLMProvider] = {
            "openai": MockOpenAIProvider(),
            "anthropic": MockAnthropicProvider()
        }
        self.circuit_breakers: Dict[str, CircuitBreaker] = {
            pid: CircuitBreaker() for pid in self.providers.keys()
        }
        self.cache = ResponseCache(ttl_seconds=3600)
        self.metrics = MetricsCollector()
        self.log_file = log_file
        self.log_buffer: list = []
        
        # Token limiter state
        self.max_tokens_average = 500
        self.total_requests = 0
        self.total_tokens = 0
        
        # Cost limiter state
        self.monthly_budget_usd = 5000.0
        self.monthly_spending = 0.0
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens: ~1 token per 4 characters."""
        return len(text) // 4
    
    def _validate_tokens(self, user_profile: str, job_market_data: str, 
                         system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Validate request stays within 500 tokens average."""
        input_text = (system_prompt or "") + user_profile + job_market_data
        input_tokens = self._estimate_tokens(input_text)
        max_output = max(0, self.max_tokens_average - input_tokens)
        
        if input_tokens > self.max_tokens_average:
            return {"valid": False, "input_tokens": input_tokens, "max_output": 0,
                    "message": f"Input tokens ({input_tokens}) exceed limit ({self.max_tokens_average})"}
        return {"valid": True, "input_tokens": input_tokens, "max_output": max_output,
                "message": "Request within token limits"}
    
    def _check_budget(self, estimated_cost: float) -> Dict[str, Any]:
        """Check if request fits within $5000/month budget."""
        now = datetime.now()
        if now.month != self.current_month or now.year != self.current_year:
            self.monthly_spending = 0.0
            self.current_month = now.month
            self.current_year = now.year
        
        remaining = self.monthly_budget_usd - self.monthly_spending
        usage_pct = (self.monthly_spending / self.monthly_budget_usd) * 100
        
        if self.monthly_spending + estimated_cost > self.monthly_budget_usd:
            return {"allowed": False, "reason": "Monthly budget exceeded",
                    "remaining": remaining, "usage_pct": usage_pct}
        return {"allowed": True, "reason": "Within budget", "remaining": remaining, "usage_pct": usage_pct}
    
    def _calculate_cost(self, provider_id: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on provider pricing."""
        provider = self.providers[provider_id]
        if hasattr(provider, 'cost_per_1k_input') and hasattr(provider, 'cost_per_1k_output'):
            return (input_tokens / 1000) * provider.cost_per_1k_input + (output_tokens / 1000) * provider.cost_per_1k_output
        return 0.0
    
    def _select_provider(self, preferred: Optional[str] = None) -> str:
        """Select provider, considering circuit breakers."""
        if preferred and preferred in self.providers:
            if self.circuit_breakers[preferred].can_attempt():
                return preferred
        
        for provider_id, cb in self.circuit_breakers.items():
            if cb.can_attempt():
                return provider_id
        
        return preferred or list(self.providers.keys())[0]
    
    def _get_failover_provider(self, current_provider: str) -> Optional[str]:
        """Get failover provider if current one is down."""
        for provider_id, cb in self.circuit_breakers.items():
            if provider_id != current_provider and cb.can_attempt():
                return provider_id
        return None
    
    def generate(
        self,
        user_profile: str,
        job_market_data: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        feature_version: Optional[str] = None,
        prompt_version: Optional[str] = None,
        experiment_id: Optional[str] = None,
        variant_id: Optional[str] = None
    ) -> LLMResponse:
        """Generate response following architecture flow."""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Step 1: Token validation
        token_check = self._validate_tokens(user_profile, job_market_data, system_prompt)
        if not token_check["valid"]:
            raise ValueError(f"Token limit exceeded: {token_check['message']}")
        
        # Step 2: Budget check
        estimated_input = token_check["input_tokens"]
        estimated_output = token_check["max_output"]
        avg_input_cost = 0.0165
        avg_output_cost = 0.0375
        estimated_cost = (estimated_input / 1000) * avg_input_cost + (estimated_output / 1000) * avg_output_cost
        
        budget_check = self._check_budget(estimated_cost)
        if not budget_check["allowed"]:
            raise ValueError(f"Budget limit exceeded: {budget_check['reason']}")
        
        # Step 3: Provider selection with failover
        selected_provider = self._select_provider(provider)
        provider_instance = self.providers[selected_provider]
        circuit_breaker = self.circuit_breakers[selected_provider]
        
        if not circuit_breaker.can_attempt():
            failover = self._get_failover_provider(selected_provider)
            if failover:
                selected_provider = failover
                provider_instance = self.providers[selected_provider]
                circuit_breaker = self.circuit_breakers[selected_provider]
            else:
                raise Exception("All providers unavailable")
        
        # Step 4: Check cache
        cached_response = self.cache.get(user_profile, job_market_data, system_prompt)
        if cached_response:
            response = LLMResponse(
                content=cached_response["content"],
                input_tokens=cached_response["input_tokens"],
                output_tokens=cached_response["output_tokens"],
                model=cached_response["model"],
                provider=cached_response["provider"],
                latency_ms=10.0
            )
            success = True
            error = None
        else:
            # Step 5: Make API call
            combined_prompt = f"User Profile: {user_profile}\n\nJob Market Data: {job_market_data}"
            error = None
            response = None
            success = False
            
            try:
                response = provider_instance.generate(combined_prompt, system_prompt)
                success = True
                circuit_breaker.record_success()
                
                self.cache.set(user_profile, job_market_data, {
                    "content": response.content,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "model": response.model,
                    "provider": response.provider
                }, system_prompt)
            except Exception as e:
                error = str(e)
                circuit_breaker.record_failure()
                raise
        
        # Update token tracking
        total_tokens = response.input_tokens + response.output_tokens
        self.total_requests += 1
        self.total_tokens += total_tokens
        
        # Calculate cost and record
        cost = self._calculate_cost(selected_provider, response.input_tokens, response.output_tokens)
        self.monthly_spending += cost
        
        # Create metrics
        latency_ms = (time.time() - start_time) * 1000
        metrics = RequestMetrics(
            request_id=request_id,
            provider=response.provider,
            model=response.model,
            latency_ms=latency_ms,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            success=success,
            error=error,
            feature_version=feature_version,
            prompt_version=prompt_version,
            experiment_id=experiment_id,
            variant_id=variant_id
        )
        
        self.metrics.record(metrics)
        self._log_telemetry(metrics, user_profile, job_market_data, system_prompt, response, cached_response is not None)
        
        return response
    
    def _log_telemetry(self, metrics: RequestMetrics, user_profile: str, 
                      job_market_data: str, system_prompt: Optional[str], 
                      response: Optional[LLMResponse], cache_hit: bool):
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
            "cache_hit": cache_hit,
            "circuit_breaker_state": self.circuit_breakers[metrics.provider].get_state().value,
            "metadata": {
                "feature_version": metrics.feature_version,
                "prompt_version": metrics.prompt_version,
                "experiment_id": metrics.experiment_id,
                "variant_id": metrics.variant_id
            }
        }
        
        self.log_buffer.append(log_entry)
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        token_avg = self.total_tokens / self.total_requests if self.total_requests > 0 else 0
        cost_usage_pct = (self.monthly_spending / self.monthly_budget_usd) * 100
        
        return {
            "providers": self.metrics.get_all_stats(),
            "total_requests": self.metrics.get_total_requests(),
            "total_cost_usd": round(self.metrics.get_total_cost(), 4),
            "token_limiter": {
                "max_tokens_average": self.max_tokens_average,
                "current_average": round(token_avg, 2),
                "within_limit": token_avg <= self.max_tokens_average
            },
            "cost_limiter": {
                "monthly_budget_usd": self.monthly_budget_usd,
                "monthly_spending_usd": round(self.monthly_spending, 2),
                "monthly_usage_percent": round(cost_usage_pct, 2),
                "within_budget": self.monthly_spending < self.monthly_budget_usd
            },
            "cache": self.cache.get_stats(),
            "circuit_breakers": {
                pid: cb.get_stats() for pid, cb in self.circuit_breakers.items()
            }
        }
    
    def print_stats(self):
        """Print statistics in readable format."""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("LLM MONITORING STATISTICS")
        print("="*60)
        print(f"\nTotal Requests: {stats['total_requests']}")
        print(f"Total Cost: ${stats['total_cost_usd']:.4f}")
        print("\nToken Limiter:")
        token_stats = stats['token_limiter']
        print(f"  Max Average: {token_stats['max_tokens_average']} tokens")
        print(f"  Current Average: {token_stats['current_average']:.1f} tokens")
        print(f"  Within Limit: {'Yes' if token_stats['within_limit'] else 'No'}")
        print("\nCost Limiter:")
        cost_stats = stats['cost_limiter']
        print(f"  Monthly Budget: ${cost_stats['monthly_budget_usd']:.2f}")
        print(f"  Monthly Spending: ${cost_stats['monthly_spending_usd']:.2f}")
        print(f"  Monthly Usage: {cost_stats['monthly_usage_percent']:.1f}%")
        print(f"  Within Budget: {'Yes' if cost_stats['within_budget'] else 'No'}")
        print("\nCache:")
        cache_stats = stats['cache']
        print(f"  Cached Entries: {cache_stats['total_entries']}")
        print("\nProvider Statistics:")
        for provider_id, provider_stats in stats['providers'].items():
            print(f"\n  {provider_id.upper()}:")
            print(f"    Requests: {provider_stats['total_requests']}")
            print(f"    Success Rate: {(1 - provider_stats['error_rate']) * 100:.1f}%")
            print(f"    Total Tokens: {provider_stats['total_tokens']:,}")
            print(f"    Total Cost: ${provider_stats['total_cost']:.4f}")
            if provider_stats['total_requests'] > 0:
                print(f"    Latency - P50: {provider_stats['latency_p50']:.0f}ms, "
                      f"P95: {provider_stats['latency_p95']:.0f}ms")
        print("\nCircuit Breaker States:")
        for provider_id, cb_stats in stats['circuit_breakers'].items():
            state_icon = "[OK]" if cb_stats['state'] == 'success' else "[DOWN]"
            print(f"  {provider_id}: {state_icon} {cb_stats['state']} "
                  f"(Failures: {cb_stats['failure_count']}, Error Rate: {cb_stats['error_rate']*100:.1f}%)")
        print("="*60 + "\n")
