## 1. Cost Optimization Strategy

### Detailed Budget Calculations: 1k to 10k Requests/Day

#### Provider Cost Structure

**GPT-4 Pricing:**

- Input tokens: $0.03 per 1,000 tokens
- Output tokens: $0.06 per 1,000 tokens
- Average cost (assuming 50/50 input/output split): $0.045 per 1,000 tokens = $0.000045 per token

**Claude-3.5-Sonnet Pricing:**

- Input tokens: $0.003 per 1,000 tokens
- Output tokens: $0.015 per 1,000 tokens
- Average cost (assuming 50/50 input/output split): $0.009 per 1,000 tokens = $0.000009 per token

**Weighted Average (50/50 A/B Test Split):**

- Combined average: ($0.045 + $0.009) / 2 = $0.027 per 1,000 tokens = $0.000027 per token

#### Scenario Analysis: No Caching

**1,000 Requests/Day:**

- Tokens: 500 tokens/request × 1,000 requests = 500,000 tokens/day
- Daily cost: 500,000 × $0.000027 = $13.50/day
- Monthly cost: $13.50 × 30 = $405/month
- **Budget utilization: 8.1%** ✅ Well under budget

**5,000 Requests/Day:**

- Tokens: 500 tokens/request × 5,000 requests = 2,500,000 tokens/day
- Daily cost: 2,500,000 × $0.000027 = $67.50/day
- Monthly cost: $67.50 × 30 = $2,025/month
- **Budget utilization: 40.5%** ✅ Under budget

**10,000 Requests/Day:**

- Tokens: 500 tokens/request × 10,000 requests = 5,000,000 tokens/day
- Daily cost: 5,000,000 × $0.000027 = $135.00/day
- Monthly cost: $135.00 × 30 = $4,050/month
- **Budget utilization: 81%** ✅ Under budget with margin

#### Scenario Analysis: With 30% Cache Hit Rate

**Assumptions:**

- 30% of requests served from cache (no API cost)
- 70% of requests hit LLM APIs
- Cache TTL: 1 hour

**1,000 Requests/Day:**

- API requests: 1,000 × 0.70 = 700 requests/day
- Tokens: 500 × 700 = 350,000 tokens/day
- Daily cost: 350,000 × $0.000027 = $9.45/day
- Monthly cost: $9.45 × 30 = $283.50/month
- **Savings: $121.50/month (30% reduction)**

**5,000 Requests/Day:**

- API requests: 5,000 × 0.70 = 3,500 requests/day
- Tokens: 500 × 3,500 = 1,750,000 tokens/day
- Daily cost: 1,750,000 × $0.000027 = $47.25/day
- Monthly cost: $47.25 × 30 = $1,417.50/month
- **Savings: $607.50/month (30% reduction)**

**10,000 Requests/Day:**

- API requests: 10,000 × 0.70 = 7,000 requests/day
- Tokens: 500 × 7,000 = 3,500,000 tokens/day
- Daily cost: 3,500,000 × $0.000027 = $94.50/day
- Monthly cost: $94.50 × 30 = $2,835/month
- **Savings: $1,215/month (30% reduction)**

#### Provider-Specific Cost Breakdown (10k req/day, 70% API calls)

**GPT-4 Only (50% of API calls):**

- Requests: 7,000 × 0.50 = 3,500 requests/day
- Tokens: 500 × 3,500 = 1,750,000 tokens/day
- Daily cost: 1,750,000 × $0.000045 = $78.75/day
- Monthly cost: $78.75 × 30 = $2,362.50/month

**Claude Only (50% of API calls):**

- Requests: 7,000 × 0.50 = 3,500 requests/day
- Tokens: 500 × 3,500 = 1,750,000 tokens/day
- Daily cost: 1,750,000 × $0.000009 = $15.75/day
- Monthly cost: $15.75 × 30 = $472.50/month

**Combined (A/B Test):**

- Monthly cost: $2,362.50 + $472.50 = $2,835/month
- **Claude is 5x cheaper than GPT-4**

#### Cost Optimization Strategies by Scale

**1,000 Requests/Day:**

- Strategy: Basic caching (30% hit rate) sufficient
- Budget headroom: $4,595/month available
- Focus: Quality optimization over cost

**5,000 Requests/Day:**

- Strategy: Aggressive caching (target 40% hit rate)
- Additional: Optimize prompts to reduce token usage
- Budget headroom: $2,975/month available
- Focus: Balance quality and cost

**10,000 Requests/Day:**

- Strategy: Maximum caching (target 50% hit rate) + provider optimization
- Additional: Route more traffic to Claude if quality acceptable
- Additional: Implement token limits and prompt optimization
- Budget headroom: $2,165/month available
- Focus: Cost efficiency critical

#### Scaling Beyond 10k Requests/Day

**15,000 Requests/Day (with 50% cache hit rate):**

- API requests: 15,000 × 0.50 = 7,500 requests/day
- Tokens: 500 × 7,500 = 3,750,000 tokens/day
- Daily cost: 3,750,000 × $0.000027 = $101.25/day
- Monthly cost: $101.25 × 30 = $3,037.50/month
- **Budget utilization: 60.8%** ✅ Still under budget

**20,000 Requests/Day (with 50% cache hit rate):**

- API requests: 20,000 × 0.50 = 10,000 requests/day
- Tokens: 500 × 10,000 = 5,000,000 tokens/day
- Daily cost: 5,000,000 × $0.000027 = $135.00/day
- Monthly cost: $135.00 × 30 = $4,050/month
- **Budget utilization: 81%** ✅ At budget limit

**Cost Controls Required:**

1. **Token Limiting**: Enforce 500 token average via prompt optimization and max_tokens caps
2. **Caching**: Cache responses for identical/similar queries (Redis, 1-hour TTL) - target 50%+ hit rate
3. **Provider Selection**: Route more traffic to Claude when quality is acceptable (5x cheaper than GPT-4)
4. **Budget Alerts**: Monitor at 80%, 90%, 95% thresholds with automatic throttling
5. **Traffic Shaping**: At 95% budget, throttle non-critical requests by 50%

**Monitoring for Cost Optimization:**

- Track cost per request by provider
- Identify high-cost queries (long prompts/responses)
- Monitor cache hit rates (target >30% for 1k-5k, >50% for 10k+)
- Track token efficiency (tokens per useful output)
- Daily cost tracking with alerts at thresholds

### Caching Strategy

**Cache Key**: Hash of (user_profile_hash + job_market_data_hash + prompt_version)
**TTL**: 1 hour (job market data changes slowly)
**Storage**: Redis with fallback to in-memory cache
**Invalidation**: On prompt version updates or manual cache clear

## 2. A/B Testing Approach

### Test Structure

**Provider Comparison Test:**

- Split: 50/50 between GPT-4 and Claude
- Duration: 4-6 weeks minimum
- Sample Size: 1,000+ users per variant (2,000+ total)
- Routing: Hash-based on user_id for consistency

**Metrics to Determine Winner:**

1. **Primary**: User engagement (CTR, time spent, return rate)
2. **Secondary**: Response quality (user feedback scores, completeness)
3. **Tertiary**: Technical metrics (latency, error rate, cost efficiency)

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

- At 95%: Throttle non-critical requests (50% reduction)
- At 100%: Block new requests, serve cached responses only
- Emergency: Switch to cheaper provider (Claude) or reduce max_tokens

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
