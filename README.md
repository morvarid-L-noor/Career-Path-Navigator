# Career Path Navigator - LLMOps Assessment

## Deliverables

### Part 1: System Architecture
- **`architecture_design.md`**: System architecture with diagram (diagram.pmg)
- Architecture supports 1,000-10,000 requests/day, <3s latency, $5,000/month budget

### Part 2: Prompt Versioning System
- **`config/features/career_path_navigator.json`**: Feature configuration with prompt versioning
- **`config/prompt_versioning_strategy.md`**: Versioning strategy and rollback process (300-500 words)
- **`config/schema/feature_config_schema.json`**: JSON schema for validation
- **`prompts/career_path_navigator/`**: Versioned prompt files

**Key Features:**
- Independent prompt versioning (v2.1, v1.5)
- Feature versioning (semantic: 1.2.3)
- A/B testing support
- Quick rollback without code deployment

### Part 3: Monitoring Implementation
- **`llm_monitoring/`**: Python proof-of-concept for monitoring
  - `monitor.py`: Main monitoring wrapper with token/cost limiters
  - `providers.py`: Mock LLM providers (OpenAI, Anthropic)
  - `circuit_breaker.py`: Failover logic
  - `metrics.py`: Metrics collection
  - `cache.py`: Response caching
  - `demo.py`: Working demonstration

**Key Features:**
- Token limiter (500 tokens average)
- Cost limiter ($5,000/month budget)
- Bidirectional failover (GPT-4 ↔ Claude)
- Structured telemetry logging (JSONL)
- Metrics tracking (latency, tokens, costs, errors)

### Part 4: Technical Recommendations
- **`TECHNICAL_RECOMMENDATIONS.md`**: Technical memo covering:
  - Cost Optimization Strategy
  - A/B Testing Approach
  - Failure Scenarios & Mitigations (3 scenarios)
  - Quality Evaluation

## How to Run

### Prerequisites
- Python 3.8+
- No external dependencies required (uses standard library only)

### Running the Monitoring Demo

```bash
# Run the monitoring demonstration
python -m llm_monitoring.demo

# This will:
# - Make several mock API calls with tracking
# - Simulate failures to test circuit breaker
# - Display comprehensive statistics
# - Generate telemetry logs (llm_telemetry.jsonl)
```

### Using the Monitoring System

```python
from llm_monitoring.monitor import LLMMonitor

# Initialize monitor with optional log file
monitor = LLMMonitor(log_file="telemetry.jsonl")

# Make a request
response = monitor.generate(
    user_profile="Software Engineer, 5 years, Python/Java, interested in AI/ML",
    job_market_data="AI Engineer: $120k-180k, ML Engineer: $130k-200k",
    provider="openai",  # or "anthropic", or None for A/B test selection
    feature_version="1.2.3",
    prompt_version="v2.1",
    experiment_id="provider_comparison",
    variant_id="variant_a"
)

# Get statistics
stats = monitor.get_stats()
monitor.print_stats()
```

## Assumptions Made

1. **Configuration Storage**: JSON files stored in version control (Git) and accessible to Rails app. In production, these could be in S3, GitHub, or a config service.

2. **Caching**: In-memory cache for POC. Production would use Redis with proper TTL and eviction policies.

3. **Monitoring**: File-based telemetry logging (JSONL). Production would integrate with ELK, CloudWatch, or similar.

4. **Provider APIs**: Mock providers simulate real API behavior. Production would use OpenAI and Anthropic SDKs.

5. **Token Estimation**: Simple character-based estimation (1 token ≈ 4 chars). Production would use tiktoken or similar libraries.

6. **Cost Calculation**: Based on published pricing. Actual costs may vary with usage tiers or discounts.

7. **A/B Testing**: Simple hash-based routing. Production would use a dedicated experimentation platform.

8. **Failover**: Bidirectional failover between GPT-4 and Claude. No tertiary fallback considered.

9. **Budget Tracking**: In-memory monthly tracking. Production would use persistent storage with proper date handling.

10. **Quality Checks**: Basic validation logic included. Production would have more sophisticated quality scoring.

## What I'd Do Differently With More Time

1. **Production-Ready Gateway**: Build a complete FastAPI service with proper error handling, retries, rate limiting, and health checks.

2. **Advanced Caching**: Implement semantic similarity caching using embeddings (e.g., OpenAI embeddings) to cache similar but not identical queries.

3. **Comprehensive Testing**: Add unit tests, integration tests, and load tests to validate behavior under various conditions.

4. **Observability Integration**: Integrate with Prometheus for metrics, OpenTelemetry for distributed tracing, and proper log aggregation.

5. **Configuration Service**: Build a proper configuration service with validation, versioning, and rollback APIs instead of file-based approach.

6. **Quality Scoring**: Implement more sophisticated quality evaluation using LLM-as-judge or fine-tuned models for relevance scoring.

7. **Cost Forecasting**: Add predictive cost modeling based on historical patterns to proactively manage budget.

8. **A/B Testing Platform**: Build a proper experimentation platform with statistical analysis, early stopping, and multi-variant support.

9. **Provider Abstraction**: Create a more robust provider abstraction layer to easily add new providers (e.g., Gemini, Cohere).

10. **Documentation**: Add API documentation, deployment guides, runbooks, and troubleshooting guides.

11. **Security**: Add request sanitization, PII detection/redaction, and proper secret management.

12. **Performance**: Optimize for sub-second latency with connection pooling, async requests, and response streaming.

## File Structure

```
.
├── README.md                              # This file
├── architecture_design.md                 # Part 1: System architecture
├── TECHNICAL_RECOMMENDATIONS.md          # Part 4: Technical recommendations
├── config/
│   ├── features/
│   │   ├── career_path_navigator.json     # Main feature configuration
│   │   └── career_path_navigator.v1.2.2.json  # Archived version
│   ├── schema/
│   │   └── feature_config_schema.json   # JSON schema for validation
│   ├── prompt_versioning_strategy.md     # Part 2: Versioning strategy
│   ├── provider_settings.json            # Provider configuration
│   ├── ab_test_config.json              # A/B testing configuration
│   └── rate_limits.json                 # Rate limits and budgets
├── prompts/
│   └── career_path_navigator/
│       ├── system/
│       │   ├── v2.1.txt                 # System prompt versions
│       │   └── v2.0.txt
│       └── user/
│           ├── v1.5.txt                 # User template versions
│           └── v1.4.txt
└── llm_monitoring/                      # Part 3: Monitoring POC
    ├── monitor.py                       # Main monitoring wrapper
    ├── providers.py                     # Mock LLM providers
    ├── circuit_breaker.py               # Failover logic
    ├── metrics.py                       # Metrics collection
    ├── cache.py                         # Response caching
    ├── demo.py                          # Demonstration script
    ├── requirements.txt                 # Dependencies (none needed)
    └── README.md                        # Monitoring system docs
```

## Configuration Files

- `config/provider_settings.json`: LLM provider settings (API keys, models, costs)
- `config/ab_test_config.json`: A/B testing configuration and routing strategy
- `config/rate_limits.json`: Rate limits and budget constraints
- `config/features/career_path_navigator.json`: Main feature configuration with prompt versioning
