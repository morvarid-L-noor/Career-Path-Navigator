# Part 1: System Design - Architecture

## Overview

This document describes the architecture for the Career Path Navigator LLM-powered feature.

**Requirements:**

- Handle 1,000 requests/day initially, scaling to 10,000/day
- 95th percentile latency < 3 seconds
- Monthly budget: $5,000 for LLM costs
- A/B test between GPT-4 and Claude-3.5-Sonnet
- Average 500 tokens per request

## Architecture Diagram

**Visual Diagram:**

- **Image file**: `diagram.png` (included in repository)
- **Interactive diagram**: [View on Excalidraw](https://excalidraw.com/#json=VuYYrp9BB6hENvhLvkTrD,sX62UHdzA6g0XjT274j5CQ)

The diagram shows the complete system architecture including:

**Current Implementation:**

- Rails application layer with configuration loader
- LLM Gateway Service (Python FastAPI) with routing, caching, and rate limiting
- External LLM providers (OpenAI GPT-4 and Anthropic Claude-3.5-Sonnet)
- Data sources (LinkedIn/Indeed job market data via Databricks pipeline)
- Storage for telemetry, metrics, A/B test results (MongoDB/S3)

**Future Recommendations (Blue Outline):**

- AWS Gateway (load balancer, SSL termination, rate limiting)
- Redis Cache (response caching to reduce latency and costs)
- Analyze Service (A/B test analysis, cost analysis, latency analysis)
- Monitoring Service (cost alerts, token limit alerts, logs & audits, user feedback)

## Request Flow

1. **Rails App** receives user request for career path recommendation
2. **Config Loader** reads current configuration (JSON files)
3. **Rails** sends request to **LLM Gateway** (Python FastAPI service)
4. **Gateway** checks cache (Redis) for similar requests
5. **Rate Limiter** validates token limits and budget constraints
6. **Request Router** selects provider based on A/B test configuration
7. **Provider Manager** routes to selected provider (GPT-4 or Claude)
8. **Circuit Breaker** monitors provider health; fails over if needed
9. **Provider Adapter** makes API call to external LLM service
10. **Gateway** receives response, caches it, logs telemetry
11. **Metrics Collector** tracks latency, tokens, costs, errors
12. **Response** returned to Rails app and displayed to user

## Provider Failover

**Circuit Breaker Pattern:**

- Opens after 5 consecutive failures OR 50% error rate
- Automatically fails over to backup provider
- Tests recovery every 30 seconds (half-open state)
- Closes when provider recovers

**Failover Hierarchy:**

1. Primary provider (A/B test selected)
2. Backup provider (automatic failover)
3. Cached response (if both providers down)
4. Graceful degradation (partial response)

## Monitoring & Observability

**Metrics Tracked:**

- Latency: p50, p95, p99, average
- Tokens: Input, output, total per request
- Costs: Per request and aggregated (USD)
- Errors: Error rate, failure counts
- Circuit breaker states

**Telemetry Logging:**

- Structured JSONL logs for each request
- Includes: timestamp, request_id, provider, latency, tokens, cost, metadata
- Sent to ELK/CloudWatch for aggregation

**Alerting:**

- Budget thresholds: 80%, 90%, 95%, 100%
- Latency degradation: P95 > 3 seconds
- Error rate spikes: > 5% error rate
- Provider outages: Circuit breaker opens

## Configuration Management

**JSON Configuration Files:**

- `provider_settings.json`: Provider configs, costs, failover settings
- `ab_test_config.json`: A/B testing configuration
- `rate_limits.json`: Rate limits and budget constraints
- `features/career_path_navigator.json`: Feature config with prompt versioning

**Hot Reloading:**

- Config files stored in Git/S3
- Config Sync Service watches for changes
- Gateway reloads configs without restart
- Validation via JSON schema before activation


## Storage Strategy

**Current Implementation:**

- Telemetry: JSONL logs for each request (cost, model, latency)
- Metrics: In-memory storage in POC (production: MongoDB/PostgreSQL)
- A/B Test Results: Stored in MongoDB for analysis
- User Feedback: Stored for quality evaluation

**Storage Options:**

- **MongoDB**: Recommended for structured data (metrics, outputs, A/B test results, user feedback)
  - JSON-based storage
  - Embedding enabled for semantic search
  - Knowledge-based queries
- **S3**: Alternative for telemetry logs and archival data
  - Cost-effective for large volumes
  - Good for long-term retention

## Future Enhancements (Not Currently Implemented)

### AWS Gateway (Load Balancer & SSL)

- **Purpose**: Entry point for client requests
- **Features**: Load balancing, SSL termination, API rate limiting, routing
- **Benefit**: Offloads infrastructure concerns from Rails application

### Redis Cache

- **Purpose**: Response caching to reduce latency and costs
- **Strategy**: Cache common queries by category (sector, degree, profile type)
- **Impact**: 30-50% cache hit rate can reduce costs significantly

### Analyze Service

- **Purpose**: Automated analysis of system performance
- **Functions**:
  - A/B test statistical analysis
  - Cost analysis and optimization recommendations
  - Latency analysis and bottleneck identification
- **Input**: Reads from Storage (MongoDB/S3)
- **Output**: Analysis reports and recommendations

### Monitoring Service

- **Purpose**: Operational oversight and alerting
- **Functions**:
  - Cost alerts (budget thresholds)
  - Token limit alerts
  - Logs & audits
  - User feedback aggregation
- **Integration**: Reads from Storage, sends alerts to operations team

### Categorization Strategy (Future)

- **Job Categorization**: Group jobs by sector (tech, finance, healthcare, etc.)
- **Profile Categorization**: Group profiles by degree, experience level, skills
- **Cache Optimization**: Store common requests per category for faster retrieval
- **Provider Selection**: Analyze which model (GPT-4 vs Claude) works better for specific categories
- **Benefit**: Reduces latency and improves cost efficiency through targeted caching

## Key Design Decisions

1. **Separate Gateway Service**: Decouples Rails from LLM providers, enables independent scaling
2. **Provider Abstraction**: Easy to add new providers without code changes
3. **JSON Configuration**: Simple, version-controlled, hot-reloadable
4. **Circuit Breaker**: Automatic failover prevents total outages
5. **Caching**: Reduces costs and improves latency for common queries
6. **Structured Logging**: Enables analysis and debugging
7. **Microservice Architecture**: Scalable, scope-based services for future growth
