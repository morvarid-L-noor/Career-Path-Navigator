# LLMOps Engineer Take-Home Assessment

This repository contains the deliverables for the Career Path Navigator LLM infrastructure assessment.

## Deliverables

### Part 1: System Design

- **`architecture_design.md`**: Architecture documentation with Mermaid diagram
- **`diagram.png`**: Visual architecture diagram

### Part 2: Configuration & Versioning Strategy

- **`config/features/career_path_navigator.json`**: Main feature configuration with prompt versioning
- **`config/prompt_versioning_strategy.md`**: Brief explanation (300-500 words) of how Rails consumes configs, versioning strategy, and rollback process
- **`config/schema/feature_config_schema.json`**: JSON schema for validation
- **`prompts/`**: Versioned prompt files

### Part 3: Monitoring Implementation

- **`llm_monitoring/`**: Python proof-of-concept demonstrating:
  - Mock LLM API calls (OpenAI, Anthropic)
  - Structured telemetry logging (JSONL)
  - Provider failover with circuit breaker
  - Metrics tracking (latency, tokens, costs, errors)

### Part 4: Technical Recommendations

- **`TECHNICAL_RECOMMENDATIONS.md`**: Technical memo covering cost optimization, A/B testing, failure scenarios, and quality evaluation

## How to Run

### Python Monitoring POC

```bash
# Install dependencies (none required - uses standard library)
cd llm_monitoring

# Run the demo
python -m llm_monitoring.demo

# This will:
# - Make mock API calls with monitoring
# - Test circuit breaker failover
# - Display statistics
# - Generate telemetry logs (llm_telemetry.jsonl)
```

## Assumptions Made

1. **Infrastructure**: Assumed cloud-based deployment (AWS/GCP) with managed services for Redis, monitoring
2. **Rails Integration**: `PromptConfigService` is a conceptual design - not implemented in this assessment
3. **Metrics Storage**: POC uses in-memory storage; production would use MongoDB/PostgreSQL
4. **Caching**: Redis-based caching assumed but not implemented in POC
5. **Monitoring**: Telemetry logs to JSONL files; production would use ELK/CloudWatch
6. **A/B Testing**: Analysis and decision-making left to data team (not implemented)

## What I'd Do Differently With More Time

1. **Real API Integration**: Replace mock providers with actual OpenAI/Anthropic SDKs
2. **Database Persistence**: Add MongoDB/PostgreSQL for metrics storage and analysis
3. **Prometheus Integration**: Export metrics to Prometheus for Grafana dashboards
4. **Rate Limiting**: Implement token-based rate limiting in the gateway
5. **Caching Implementation**: Build Redis-based response caching
6. **A/B Test Analysis**: Add statistical analysis tools for experiment evaluation
7. **Alerting System**: Integrate with PagerDuty/Slack for budget and error alerts
8. **Load Testing**: Add load testing scripts to validate 10k requests/day capacity
