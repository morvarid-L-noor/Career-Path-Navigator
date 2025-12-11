## 1. Cost Optimization Strategy

### How would you keep costs under $5,000/month initially?

**Base Calculation (1,000 requests/day, no caching):**

- Average: 500 tokens/request
- Daily tokens: 500 × 1,000 = 500,000 tokens/day
- Provider costs (50/50 A/B test): GPT-4 ($0.045/1k) + Claude ($0.009/1k) = $0.027/1k tokens average
- Daily cost: 500,000 × $0.000027 = **$13.50/day**
- Monthly cost: $13.50 × 30 = **$405/month** (8.1% of budget) ✅

**With 30% Cache Hit Rate:**

- API requests: 1,000 × 0.70 = 700 requests/day
- Monthly cost: 700 × 500 × $0.000027 × 30 = **$283.50/month** (5.7% of budget) ✅

**Cost Controls:**

1. **Token Limiting**: Enforce 500 token average via `max_tokens` caps and prompt optimization
2. **Caching**: Target 30%+ cache hit rate (saves ~30% of costs)
3. **Provider Selection**: Route to Claude when quality acceptable (5x cheaper: $0.009 vs $0.045 per 1k tokens)
4. **Budget Alerts**: Monitor at 80%, 90%, 95% thresholds with automatic throttling

### What monitoring would help identify cost optimization opportunities?

**Key Metrics to Track:**

1. **Cost per Request by Provider**: Identify if Claude can replace GPT-4 for certain use cases
2. **Token Efficiency**: Tokens per useful output - flag queries with excessive token usage
3. **Cache Hit Rate**: Target >30% for 1k req/day, >50% for 10k+ req/day
4. **High-Cost Queries**: Identify requests with unusually long prompts/responses
5. **Daily Cost Trends**: Track spending patterns to predict budget issues early
6. **Provider Cost Comparison**: Real-time cost difference between GPT-4 and Claude

**Alerting Thresholds:**

- Daily cost > $166.67 (monthly budget / 30 days)
- Cache hit rate < 20% (below target)
- Token usage > 600 tokens/request average (20% over target)
- Cost per request > $0.02 (indicates inefficient queries)

### Caching Strategy Considerations

**Cache Key Design:**

- Hash of: `user_profile_hash + job_market_data_hash + prompt_version`
- Ensures same user profile + market data + prompt version = cache hit

**TTL Strategy:**

- **1 hour TTL**: Job market data changes slowly, user profiles are relatively stable
- **Invalidation**: On prompt version updates or manual cache clear
- **Storage**: Redis with fallback to in-memory cache

**Expected Impact:**

- **30% cache hit rate**: Reduces monthly cost from $405 to $283.50 (saves $121.50/month)
- **50% cache hit rate** (at scale): Reduces 10k req/day cost from $4,050 to $2,025/month (saves $2,025/month)

**Cache Considerations:**

- Cache similar queries (fuzzy matching) for better hit rates
- Monitor cache size to prevent memory issues
- Implement cache warming for common queries
- Consider cache partitioning by user segment for better performance

## 2. A/B Testing Approach

### Test Structure

**Provider Comparison Test:**

- Split: 50/50 between GPT-4 and Claude
- Duration: 4-6 weeks minimum
- Sample Size: 1,000+ users per variant (2,000+ total)
- Routing: Hash-based on user_id for consistency

**Metrics to Determine Winner:**

1. **Primary**: Response quality (user feedback scores, completeness)
2. **Secondary**: Technical metrics (latency, error rate, cost efficiency)

**Statistical Requirements:**

- Minimum 95% confidence (p < 0.05)
- Account for multiple comparisons (Bonferroni correction)
- Monitor for early stopping if clear winner emerges

**Decision Criteria:**

- Winner: Statistically significant improvement in primary metrics
- Tie: Continue test or choose based on cost/latency
- Rollout: Gradual rollout (10% → 50% → 100%) with monitoring

## 3. Failure Scenarios & Mitigations

### Scenario 1: Provider API Outage

**Detection:**

- Circuit breaker opens after 5 consecutive failures or 50% error rate
- Alert triggered immediately

**Mitigation:**

- Automatic failover to backup provider
- If both providers down: serve cached responses
- Graceful degradation: return partial/cached data

**Recovery:**

- Circuit breaker tests recovery every 30 seconds (half-open state)
- Auto-close on successful request

### Scenario 2: Budget Exceeded

**Detection:**

- Real-time cost tracking with alerts at 80%, 90%, 95%
- Daily/monthly budget limits enforced

**Mitigation:**

- At 95%: Throttle non-critical requests (50% reduction) or Switch to cheaper provider (Claude)
- At 100%: Block new requests, serve cached responses only
- Emergency: reduce max_tokens

**Prevention:**

- Daily budget caps ($166.67/day for $5k/month)
- Token limits per request
- Aggressive caching to reduce API calls

### Scenario 3: Latency Degradation

**Detection:**

- P95 latency > 3 seconds triggers alert
- Monitor provider-specific latency trends

**Mitigation:**

- Route traffic to faster provider (Claude typically faster)
- Increase cache TTL to reduce API calls
- Implement request queuing during peak load
- Scale gateway service horizontally

**Root Cause Analysis:**

- Check provider status pages
- Analyze latency by provider, region, time of day
- Review prompt complexity (longer prompts = slower responses)

## 4. Quality Evaluation

### Measuring Output Quality

**Automated Checks:**

1. **Completeness**: Response contains required sections (next roles, skills, steps)
2. **Length**: Response within expected token range (not too short/long)
3. **Format**: Valid JSON/structure if required
4. **Safety**: Content filtering (no harmful/inappropriate content)

**User Feedback:**

- Thumbs up/down on responses
- Optional text feedback
- Track feedback rate and sentiment

**Quantitative Metrics:**

- User engagement: CTR on recommendations, time spent viewing
- Business outcomes: Users taking action on recommendations
- Return rate: Users coming back for more recommendations

**Quality Scoring:**

- Combine automated checks (30%) + user feedback (40%) + engagement (30%)
- Track quality scores by provider, prompt version, experiment variant
- Alert if quality drops >10% from baseline

### Implementation

**Automated Quality Checks:**

```python
def validate_response(response: str, expected_sections: List[str]) -> QualityScore:
    checks = {
        'has_all_sections': all(section in response for section in expected_sections),
        'appropriate_length': 100 < len(response) < 2000,
        'no_errors': 'error' not in response.lower(),
    }
    return QualityScore(checks=checks, score=sum(checks.values()) / len(checks))
```

**Feedback Collection:**

- Rails app collects user feedback via UI
- Store in database with request_id for correlation
- Aggregate weekly for analysis

**Quality Dashboard:**

- Track quality trends over time
- Compare quality by provider/prompt version
- Alert on quality degradation
