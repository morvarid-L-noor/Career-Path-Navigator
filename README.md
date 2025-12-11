# LLMOps Engineer Assessment

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

- **`MEMO.md`**: Technical memo covering answers to cost optimization, A/B testing, failure scenarios, and quality evaluation questions

## How to Run

### Python Monitoring POC

```bash
# Install dependencies (none required - uses standard library)
cd llm_monitoring

# Run the demo
python demo.py

# This will:
# - Make mock API calls with monitoring
# - Test circuit breaker failover
# - Display statistics
# - Generate telemetry logs (llm_telemetry.jsonl)
```

## Assumptions Made

1. **Infrastructure**: Assumed cloud-based deployment (AWS) with managed services for Redis, monitoring
2. **Rails Integration**: `PromptConfigService` is a conceptual design - not implemented in this assessment
3. **Metrics Storage**: POC uses in-memory storage; production would use MongoDB/PostgreSQL/S3
4. **Caching**: Redis-based caching assumed but not implemented in POC
5. **Monitoring**: Telemetry logs to JSONL files; production would use ELK/CloudWatch
6. **A/B Testing**: Analysis and decision-making left to data team (not implemented)

## What I'd Do Differently With More Time

### Infrastructure Enhancements

1. **AWS Gateway Integration**: Implement load balancer, SSL termination, and API rate limiting at the gateway level
2. **Redis Cache Implementation**: Build Redis-based response caching with category-based cache keys (sector, degree, profile type)
3. **Database Persistence**: Add MongoDB/PostgreSQL for metrics storage and analysis (currently in-memory in POC)
4. **Storage Strategy**: Implement storage (MongoDB for structured data, S3 for telemetry logs and archival)

### Service Architecture

5. **Analyze Service**: Build dedicated service for:
   - A/B test statistical analysis (determine winners, calculate significance)
   - Cost analysis and optimization recommendations
   - Latency analysis and bottleneck identification
6. **Monitoring Service**: Create separate service for:
   - Cost alerts (budget thresholds: 80%, 90%, 95%, 100%)
   - Token limit alerts
   - Logs & audits aggregation
   - User feedback collection and analysis

### Optimization Features

7. **Categorization System**:
   - Categorize jobs by sector (tech, finance, healthcare, etc.)
   - Categorize user profiles by degree, experience level, skills
   - Store common requests per category for faster retrieval
   - Analyze which model (GPT-4 vs Claude) performs better for specific categories
8. **Smart Caching**:
   - Cache similar queries using fuzzy matching
   - Implement cache warming for common category queries
   - Cache partitioning by user segment for better performance

### Integration & Tooling

9. **Real API Integration**: Replace mock providers with actual OpenAI/Anthropic SDKs
10. **Prometheus Integration**: Export metrics to Prometheus for Grafana dashboards
11. **Rate Limiting**: Implement token-based rate limiting in the gateway
12. **Alerting System**: Integrate with PagerDuty/Slack for budget and error alerts
13. **Load Testing**: Add load testing scripts to validate 10k requests/day capacity
14. **A/B Test Analysis Tools**: Add statistical analysis tools for experiment evaluation with automated winner determination
