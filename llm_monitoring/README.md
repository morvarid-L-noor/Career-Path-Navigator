# LLM Monitoring System - Proof of Concept

A Python proof-of-concept demonstrating monitoring, telemetry, and failover for LLM API calls.

## Features

- ✅ **Mock LLM Providers**: Simulates OpenAI and Anthropic APIs without requiring real keys
- ✅ **Structured Telemetry**: Logs all requests in JSONL format with comprehensive metadata
- ✅ **Circuit Breaker Failover**: Automatically switches providers when one fails
- ✅ **Metrics Collection**: Tracks latency (p50, p95, p99), tokens, costs, and error rates
- ✅ **Request Tracking**: Captures feature versions, prompt versions, and A/B test metadata

## Quick Start

```bash
# Run the demo
python llm_monitoring/demo.py

# This will:
# - Make several mock API calls
# - Simulate failures to test circuit breaker
# - Display statistics
# - Generate telemetry logs (llm_telemetry.jsonl)
```

## Usage Example

```python
from llm_monitoring import LLMMonitor

# Initialize monitor with optional log file
monitor = LLMMonitor(log_file="telemetry.jsonl")

# Make a request with two inputs (matching architecture)
response = monitor.generate(
    user_profile="Software Engineer, 5 years, Python/Java, interested in AI/ML",
    job_market_data="AI Engineer: $120k-180k, ML Engineer: $130k-200k",
    system_prompt="You are a career advisor.",
    provider="openai",  # or "anthropic", or None for A/B test selection
    feature_version="1.2.3",
    prompt_version="v2.1",
    experiment_id="provider_comparison",
    variant_id="variant_a"
)

# Get statistics
stats = monitor.get_stats()
monitor.print_stats()  # Pretty-printed version
```

## Architecture

### Components

1. **`providers.py`**: Mock LLM provider implementations
   - `MockOpenAIProvider`: Simulates GPT-4
   - `MockAnthropicProvider`: Simulates Claude-3.5-Sonnet

2. **`monitor.py`**: Main monitoring wrapper
   - `LLMMonitor`: Handles all API calls following architecture flow
   - Implements: Token Limiter → Cost Limiter → A/B Router → Cache → Provider
   - Bidirectional failover
   - Telemetry logging
   - Metrics collection

3. **`token_limiter.py`**: Token limit enforcement
   - `TokenLimiter`: Enforces 500 tokens average (prompt + response)
   - Validates requests before sending
   - Tracks running average

4. **`cost_limiter.py`**: Budget enforcement
   - `CostLimiter`: Enforces $5000/month budget
   - Tracks monthly and daily spending
   - Sends alerts at thresholds (80%, 90%, 95%, 100%)

5. **`cache.py`**: Response caching
   - `ResponseCache`: In-memory cache (Redis in production)
   - Content-based hashing for similar queries
   - TTL-based expiration

6. **`circuit_breaker.py`**: Failover logic
   - `CircuitBreaker`: Implements circuit breaker pattern
   - States: CLOSED, OPEN, HALF_OPEN
   - Automatic recovery
   - Bidirectional failover (GPT-4 ↔ Claude)

7. **`metrics.py`**: Metrics collection
   - `MetricsCollector`: Aggregates request metrics
   - Calculates percentiles (p50, p95, p99)
   - Tracks costs, tokens, error rates

## Telemetry Data

Each request logs structured JSON with:

```json
{
  "timestamp": "2024-01-20T10:30:00.123456",
  "request_id": "uuid",
  "provider": "openai",
  "model": "gpt-4",
  "latency_ms": 1234.56,
  "tokens": {
    "input": 150,
    "output": 200,
    "total": 350
  },
  "cost_usd": 0.021,
  "success": true,
  "error": null,
  "circuit_breaker_state": "closed",
  "metadata": {
    "feature_version": "1.2.3",
    "prompt_version": "v2.1",
    "experiment_id": "provider_comparison",
    "variant_id": "variant_a"
  },
  "prompt_length": 50,
  "response_length": 100
}
```

## Metrics Tracked

### Per Provider
- Total requests (successful + failed)
- Error rate
- Total tokens (input + output)
- Total cost (USD)
- Latency: p50, p95, p99, average, min, max

### Circuit Breaker
- Current state (closed/open/half_open)
- Failure count
- Success count
- Error rate
- Time opened

### Global
- Total requests across all providers
- Total cost across all providers

## Circuit Breaker Behavior

The circuit breaker opens (stops using a provider) when:
- 5 consecutive failures, OR
- Error rate exceeds 50%

After 30 seconds, it transitions to HALF_OPEN to test recovery.
If successful, it closes again. If it fails, it reopens.

## Failover Strategy

The system implements **bidirectional failover**:

1. Try preferred provider (if specified)
2. If circuit breaker is open, try the other provider (bidirectional: GPT-4 ↔ Claude)
3. If all providers are down, raise exception

**Bidirectional Failover**: GPT-4 and Claude are each other's failover. If GPT-4 fails, the system automatically switches to Claude. If Claude fails, it automatically switches to GPT-4.

## Example Output

```
============================================================
LLM MONITORING STATISTICS
============================================================

Total Requests: 9
Total Cost: $0.0042

Provider Statistics:

  OPENAI:
    Requests: 5
    Success Rate: 20.0%
    Total Tokens: 1,750
    Total Cost: $0.0026
    Latency - P50: 1200ms, P95: 1500ms, P99: 1700ms

  ANTHROPIC:
    Requests: 4
    Success Rate: 100.0%
    Total Tokens: 1,400
    Total Cost: $0.0016
    Latency - P50: 800ms, P95: 1100ms, P99: 1300ms

Circuit Breaker States:
  openai: 🔴 open (Failures: 4, Error Rate: 80.0%)
  anthropic: 🟢 closed (Failures: 0, Error Rate: 0.0%)
============================================================
```

## Integration with Rails

This monitoring system would be integrated into the LLM Gateway Service (Python FastAPI) described in the architecture. The gateway would:

1. Load configuration from JSON files
2. Use `LLMMonitor` for all provider calls
3. Export metrics to Prometheus
4. Send logs to ELK/CloudWatch
5. Use telemetry data for A/B test analysis

## Next Steps for Production

- Replace mock providers with real API clients
- Add Prometheus metrics export
- Integrate with distributed tracing (OpenTelemetry)
- Add database persistence for metrics
- Implement rate limiting
- Add retry logic with exponential backoff
- Create Grafana dashboards
- Set up alerting based on metrics

