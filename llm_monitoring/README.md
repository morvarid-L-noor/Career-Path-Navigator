# LLM Monitoring System

Python proof-of-concept demonstrating monitoring, telemetry, and failover for LLM API calls.

## Features

- Mock LLM providers (OpenAI, Anthropic) - no API keys required
- Token limiter (500 tokens average)
- Cost limiter ($5,000/month budget)
- Bidirectional failover (GPT-4 ↔ Claude)
- Structured telemetry logging (JSONL)
- Metrics tracking (latency, tokens, costs, errors)

## Quick Start

```bash
python -m llm_monitoring.demo
```

## Usage

```python
from llm_monitoring.monitor import LLMMonitor

monitor = LLMMonitor(log_file="telemetry.jsonl")

response = monitor.generate(
    user_profile="Software Engineer, 5 years, Python/Java",
    job_market_data="AI Engineer: $120k-180k",
    provider="openai",
    feature_version="1.2.3",
    prompt_version="v2.1"
)

stats = monitor.get_stats()
monitor.print_stats()
```

## Components

- **`monitor.py`**: Main wrapper with token/cost limiters, failover, caching
- **`providers.py`**: Mock LLM providers
- **`circuit_breaker.py`**: Failover logic
- **`metrics.py`**: Metrics collection
- **`cache.py`**: Response caching

## Telemetry

Each request logs structured JSON with:
- Timestamp, request ID, provider, model
- Latency, tokens (input/output/total), cost
- Success/error status, circuit breaker state
- Metadata (feature version, prompt version, experiment ID)
