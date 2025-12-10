# Technical Recommendations: Career Path Navigator LLM Infrastructure

## 1. Cost Optimization Strategy

### Keeping Costs Under $5,000/Month

**Initial Projections** (1,000 requests/day = 30,000/month, 500 tokens avg):
- GPT-4 only: ~$675/month
- Claude only: ~$135/month  
- 50/50 split: ~$405/month

**Recommended Strategy**:

1. **Provider Mix**: Start with 70% Claude / 30% GPT-4 split → **~$270/month** (94% under budget)
   - Claude is 10x cheaper for input tokens and 4x cheaper for output
   - Use GPT-4 for premium users or when quality is critical
   - Adjust split based on A/B test results

2. **Aggressive Caching**: Target 40-50% cache hit rate
   - Exact match caching (TTL: 4h) for identical queries
   - Semantic similarity caching (TTL: 2h) using embeddings for similar profiles
   - Expected savings: ~$108/month at 40% hit rate

3. **Token Optimization**: 
   - Compress job market data to top 10-15 most relevant listings
   - Optimize prompts (target 100→50 tokens for system prompt)
   - Aim for 400 token average instead of 500 → 20% cost reduction

4. **Dynamic Routing**: 
   - Auto-route to Claude when budget >80% used
   - Prioritize GPT-4 for premium users or high-value requests
   - Implement request queuing for non-critical requests when approaching limit

5. **Hard Limits**: 
   - Stop at 98% budget to prevent overruns
   - Daily caps with rollover mechanism
   - Queue low-priority requests when approaching daily limit

**Expected Cost**: $200-300/month initially (60-70% under budget), scalable to 10K req/day within $5K budget.

### Monitoring for Cost Optimization

**Key Metrics to Track**:
- Cost per request by provider
- Cache hit rate (target >40%)
- Token usage distribution
- Cost per user segment
- Daily cost trends
- Provider cost efficiency (cost per quality score)

**Alerts**:
- Daily cost >$200 (1.2x normal)
- Cache hit rate <30%
- Average tokens >550
- Single user >5% of monthly spend

**Optimization Opportunities**:
- Identify frequently cached queries for pre-caching
- Optimize token-heavy request patterns
- Adjust A/B split based on cost/quality ratio
- Implement tiered service levels (free vs premium)

### Caching Strategy

**Multi-Tier Approach**:
- **Exact Match** (TTL: 4h): Same user profile + job market snapshot
- **Similarity Cache** (TTL: 2h): >85% profile similarity, similar market conditions (embedding-based)
- **Template Cache** (TTL: 24h): Common transitions (Engineer→Data Scientist), personalize with user details

**Invalidation**:
- When job market data updates (daily refresh)
- When user profile changes significantly
- Cache warming for common query patterns

**Storage**: Redis with LRU eviction, keys: `career_path:{user_hash}:{market_hash}:{version}`

## 2. A/B Testing Approach

### Test Structure

**Primary Experiment: Provider Comparison**
- **Variant A**: GPT-4 (30% traffic)
- **Variant B**: Claude (70% traffic)
- **Duration**: 4 weeks minimum (6-8 weeks if inconclusive)
- **Sticky Sessions**: Hash-based routing on `user_id` for consistency
- **Stratified Sampling**: Equal distribution across user segments, balanced by time of day

**Secondary Experiments**: Prompt variations within same provider for optimization without provider bias.

### Metrics to Determine Winner

**Primary Metrics** (Statistical Significance Required):
- **User Engagement**: CTR on recommendations, time spent, return rate
- **Business Outcomes**: Conversion rate (users taking action), NPS/CSAT, feature adoption
- **Quality**: Response relevance (user feedback), actionability score, completeness

**Secondary Metrics** (Supporting):
- Technical: Latency (p95 <3s), error rate (<1%), token efficiency
- Cost: Cost per engaged user, cost per conversion, ROI

**Analysis**:
- Minimum 1,000 users per variant (2,000 for 80% power, 5% significance)
- Chi-square for conversions, t-test for continuous metrics
- Account for multiple comparisons (Bonferroni correction)
- Segment-level analysis (by user type, experience level)

**Early Stopping**: Clear winner (p<0.01, >20% improvement), safety issues, budget constraints.

## 3. Failure Scenarios & Mitigations

### Failure Mode 1: Provider API Outage

**Scenario**: Extended downtime (>30 min) of one provider (e.g., OpenAI).

**Detection**:
- Circuit breaker enters fail state (5 failures or 50% error rate)
- Immediate alert to on-call engineer
- Monitor provider status pages

**Mitigation**:
1. **Bidirectional failover** → Route 100% to backup provider
2. Increase cache TTL temporarily (4h → 24h)
3. Return cached responses (even if stale) for non-critical requests
4. User communication banner if quality degrades

**Recovery**: In-progress state after 30s, test with 10% traffic, monitor error rates before full restoration.

### Failure Mode 2: Budget Exhaustion

**Scenario**: Monthly budget exhausted before month-end due to traffic spike.

**Detection**:
- Real-time alerts at 80%, 90%, 95% thresholds
- Daily spend >$200 (1.2x normal)
- Forecasted spend exceeds budget

**Mitigation**:
1. **Immediate**: Hard stop at 98%, route 100% to Claude, max cache TTL, queue non-premium requests
2. **Traffic Management**: Throttle free tier to 50%, prioritize premium users, show wait times
3. **Emergency**: Disable for new users, cache-only mode, request budget increase if critical

**Prevention**: Daily caps with alerts, rate limiting, cost forecasting, automatic provider routing.

### Failure Mode 3: Quality Degradation

**Scenario**: Provider quality drops (model update, prompt injection, etc.).

**Detection**:
- **Automated**: Response length validation, required field presence, sentiment analysis, format validation
- **User Feedback**: Spike in "not helpful", engagement drop, support ticket increase
- **Statistical**: Quality score drop >20% week-over-week, error rate >5%, latency increase

**Mitigation**:
1. **Immediate**: Route away from degraded provider, increase quality thresholds, enable human review queue
2. **Investigation**: Review prompt/config changes, check provider status, analyze error patterns
3. **Recovery**: Rollback prompt version, switch to backup, update quality checks

**Prevention**: Version all prompts, canary deployments (10% traffic), continuous quality monitoring, regular audits.

## 4. Quality Evaluation

### Measuring Output Quality

**Quantitative Metrics**:

1. **Completeness Score** (0-100): Required fields present
   - Career paths (2-3 recommended)
   - Skills required
   - Salary ranges
   - Timeline
   - Action steps
   - Weighted scoring based on importance

2. **Relevance Score** (0-100): User profile alignment
   - Match skills/experience mentioned
   - Job market alignment (realistic salaries/roles)
   - Career progression logic

3. **Actionability Score** (0-100): Specificity and clarity
   - Not vague or generic
   - Clear next steps
   - Resource links available

4. **User Engagement**: CTR on recommendations, time spent, return visits, conversion (users taking action)

**Qualitative**:
- User feedback (thumbs up/down, free-text)
- Follow-up surveys (NPS, CSAT)
- Human evaluation (weekly 50-sample review, expert evaluation)

### Automated Quality Checks

**Pre-Delivery** (Before sending to user):

1. **Format Validation**: Valid JSON/structured format, required fields present, no malformed data
2. **Content Validation**: Response length 200-2000 chars, career paths count 2-3, salary ranges $40k-$500k, skills list non-empty with relevant keywords
3. **Relevance Checks**: User skills mentioned (≥2 matches), current role referenced, recommended roles align with experience level
4. **Safety Checks**: No PII leakage, no harmful content, appropriate professional tone

**Post-Delivery Monitoring**:
- Anomaly detection (response time, token count, cost outliers)
- Trend analysis (quality scores, engagement, error rates)
- A/B test quality comparison

**Implementation**: Integrate into `monitor.py`, log scores in telemetry, alert if <70, reject and retry with backup if check fails.

**Quality Dashboard**: Real-time scores by provider, trends over time, quality by segment, failed checks and reasons, user feedback sentiment.

## Recommendations Summary

1. **Cost**: 70/30 Claude/GPT-4 split, 40%+ cache hit rate, 400 token average, dynamic routing → $200-300/month initially
2. **A/B Testing**: 4-week minimum, 1,000+ users per variant, measure engagement/business outcomes, statistical significance
3. **Failure Mitigation**: Bidirectional failover, budget hard stops at 98%, automated quality checks with provider failover
4. **Quality**: Automated checks (completeness, relevance, actionability) + user feedback + human evaluation samples

**Expected Outcomes**: $200-300/month at 1K req/day, scalable to 10K within $5K budget | 99.9% uptime | 90%+ quality issues caught automatically.
