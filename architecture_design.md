# Career Path Navigator - System Architecture

## What This System Does

This document explains how Thrive's Career Path Navigator feature works behind the scenes. The system is designed to:

- Handle 1,000 user requests per day initially, growing to 10,000 per day
- Respond to most requests in under 3 seconds
- Stay within a $5,000 monthly budget for AI services
- Test two different AI providers (GPT-4 and Claude) to see which works better

## Architecture Diagram

```mermaid
graph TB
    subgraph "Rails Application Layer"
        RAILS[Rails App<br/>Career Path Navigator]
        CONFIG_LOADER[Config Loader<br/>JSON Parser]
    end

    subgraph "LLM Gateway Service"
        GATEWAY[LLM Gateway<br/>Python FastAPI]
        ROUTER[Request Router<br/>A/B Testing Logic]
        CACHE[Response Cache<br/>Redis]
        RATE_LIMITER[Rate Limiter<br/>Token-based]
    end

    subgraph "Provider Abstraction Layer"
        PROVIDER_MGR[Provider Manager]
        GPT4_ADAPTER[GPT-4 Adapter]
        CLAUDE_ADAPTER[Claude-3.5 Adapter]
        FAILOVER[Failover Handler<br/>Circuit Breaker]
    end

    subgraph "External LLM Providers"
        OPENAI[OpenAI API<br/>GPT-4]
        ANTHROPIC[Anthropic API<br/>Claude-3.5-Sonnet]
    end

    subgraph "Observability Layer"
        METRICS[Metrics Collector<br/>Prometheus]
        LOGS[Log Aggregator<br/>ELK/CloudWatch]
        TRACES[Distributed Tracing<br/>OpenTelemetry]
        ALERTS[Alert Manager]
    end

    subgraph "Configuration Management"
        CONFIG_STORE[Config Store<br/>S3/GitHub]
        CONFIG_SYNC[Config Sync Service]
        JSON_CONFIG[JSON Config Files<br/>- provider_settings.json<br/>- ab_test_config.json<br/>- rate_limits.json]
    end

    subgraph "Data Pipeline"
        DATABRICKS[Databricks<br/>ML Pipeline]
        JOB_DATA[Job Market Data]
    end

    RAILS --> CONFIG_LOADER
    CONFIG_LOADER --> JSON_CONFIG
    RAILS --> GATEWAY
    GATEWAY --> ROUTER
    GATEWAY --> CACHE
    GATEWAY --> RATE_LIMITER
    ROUTER --> PROVIDER_MGR
    PROVIDER_MGR --> GPT4_ADAPTER
    PROVIDER_MGR --> CLAUDE_ADAPTER
    PROVIDER_MGR --> FAILOVER
    GPT4_ADAPTER --> OPENAI
    CLAUDE_ADAPTER --> ANTHROPIC
    FAILOVER -.->|Fallback| OPENAI
    FAILOVER -.->|Fallback| ANTHROPIC

    GATEWAY --> METRICS
    GATEWAY --> LOGS
    GATEWAY --> TRACES
    PROVIDER_MGR --> METRICS
    PROVIDER_MGR --> LOGS
    METRICS --> ALERTS

    CONFIG_SYNC --> CONFIG_STORE
    CONFIG_SYNC --> JSON_CONFIG
    CONFIG_SYNC --> GATEWAY

    DATABRICKS --> JOB_DATA
    DATABRICKS -.->|Enrichment| GATEWAY
    ```

## How the System Works - Component by Component

### 1. The Main Application (Rails App)

**What it does:**
Think of this as the front desk of a hotel - it's what users interact with directly.

- Receives requests when users ask for career path recommendations
- Sends those requests to our AI service (like placing an order)
- Makes sure users are logged in and authorized
- Formats the AI's response nicely before showing it to the user

**Configuration Reader:**

- Reads settings from simple text files (like reading a recipe)
- Makes those settings available to the main app
- Can update settings without restarting the entire system

### 2. The AI Gateway Service

**What it does:**
This is like a smart receptionist that manages all communication with AI services. It sits between our app and the AI providers.

**Key Jobs:**

- **Quality Check**: Makes sure requests are valid and safe before sending them
- **Budget Tracker**: Counts how much we're spending in real-time (like a fuel gauge)
- **Smart Memory**: Remembers answers to similar questions so we don't have to ask the AI again (saves time and money)
- **Traffic Controller**: Limits how many requests each user can make (prevents abuse)
- **Test Coordinator**: Decides which AI provider to use for A/B testing (like flipping a coin, but smarter)
- **Problem Solver**: If something goes wrong, it tries again automatically

### 3. The AI Provider Manager

**What it does:**
This is like a universal translator and traffic director for different AI services.

**Provider Manager:**

- Manages connections to both GPT-4 and Claude AI services
- Runs our A/B test by sending 50% of requests to each AI (we can change this ratio)
- Keeps track of which AI is faster, cheaper, and more reliable
- Chooses which AI to use based on our settings

**AI Adapters (GPT-4 & Claude):**

- Each AI service speaks a slightly different "language" - these adapters translate
- They handle the specific way each AI company wants to receive requests
- They convert all responses into the same format so the rest of our system doesn't care which AI answered
- They optimize requests for each AI's preferences

**Backup System (Failover Handler):**

- Like a circuit breaker in your house - if one AI service breaks, it automatically switches to the backup
- If GPT-4 goes down, it automatically uses Claude instead
- Checks if services are healthy and working properly
- Tries to reconnect to failed services after a short wait

### 4. Settings and Configuration

**What it does:**
All our system settings are stored in simple text files that anyone can read and update. Think of them like recipe cards that tell the system how to behave.

**Settings File 1: AI Provider Settings** (`provider_settings.json`)
This file contains:

- Which AI services we're using (GPT-4 and Claude)
- How much we're willing to spend per request
- How long to wait for a response before giving up
- Which AI to use by default, and which to use as backup

**Settings File 2: A/B Testing Settings** (`ab_test_config.json`)
This file controls our experiment:

- Whether A/B testing is turned on or off
- What percentage of users get GPT-4 vs Claude (currently 50/50)
- Whether the same user always gets the same AI (for consistency)

**Settings File 3: Usage Limits** (`rate_limits.json`)
This file sets boundaries to protect our budget:

- Maximum requests per minute across the whole system
- Maximum requests per hour for each individual user
- Daily spending limits

**Settings Update Service:**

- Watches for when we change these settings files
- Makes sure the settings are valid (like spell-checking)
- Updates the system with new settings automatically
- Keeps a history of all changes (so we can undo mistakes)

### 5. Monitoring and Alerts

**What it does:**
This is like a dashboard in a car - it shows us how the system is performing and warns us if something goes wrong.

**Performance Dashboard:**
Tracks important numbers like:

- How many requests we're handling per second
- How fast responses are (most should be under 3 seconds)
- How much we're spending per hour and per day
- How often each AI service makes mistakes
- How often we can reuse cached answers (saves money!)
- Whether our backup systems are working

**Activity Logs:**
Keeps a record of:

- What requests came in and what responses went out (with sensitive data removed)
- When errors occur and what caused them
- What the AI services are doing
- When we change settings

**Request Tracking:**
Follows each user request from start to finish:

- How long each step takes
- Where time is being spent (waiting for AI, checking cache, etc.)
- Helps us find bottlenecks and speed things up

**Alert System:**
Sends notifications when:

- Responses are taking too long (over 3 seconds)
- Too many errors are happening (more than 5% of requests)
- We're getting close to our budget (at 80%, 90%, and 100%)
- One of the AI services goes down
- The backup system kicks in

### 6. How a Request Flows Through the System

Here's what happens when a user asks for a career path recommendation:

1. **User asks a question** → Our main app receives the request
2. **Check settings** → App looks up current configuration (which AI to use, spending limits, etc.)
3. **Send to gateway** → App forwards the request to our AI gateway service
4. **Check memory** → Gateway looks in its memory to see if we've answered a similar question before (saves time and money!)
5. **Check limits** → Gateway verifies the user hasn't exceeded their request limit
6. **Choose AI** → Gateway flips a coin (or uses a smarter method) to decide: GPT-4 or Claude?
7. **Ask the AI** → Gateway sends the question to the chosen AI service
8. **Get answer** → Gateway receives the AI's response, formats it nicely, and saves it to memory for future similar questions
9. **Record everything** → Every step is logged so we can monitor performance and debug issues
10. **Send to user** → The formatted answer is sent back through the app to the user

### 7. What Happens When Things Go Wrong

**Automatic Backup System:**

Like a circuit breaker in your house that trips when there's a problem:

- If an AI service fails 5 times in a row, or has errors on 50% of requests, we stop using it temporarily
- After 30 seconds, we try it again to see if it's fixed
- If the primary AI is down, we automatically switch to the backup AI

**Backup Plan (in order):**

1. **Try the chosen AI** → Based on our A/B test, try GPT-4 or Claude
2. **Switch to backup** → If the first AI is down, automatically use the other one
3. **Use saved answer** → If both AIs are down, use a previously saved answer (even if it's a bit old)
4. **Partial response** → As a last resort, return whatever information we have, even if incomplete

### 8. Budget Management

**Spending Tracking:**

- Counts every word we send to and receive from AI services in real-time
- Calculates costs based on each AI's pricing:
  - **GPT-4**: About 3 cents per 1,000 words sent, 6 cents per 1,000 words received
  - **Claude**: About 0.3 cents per 1,000 words sent, 1.5 cents per 1,000 words received
- Sends alerts when we hit 80%, 90%, and 100% of our daily or monthly budget
- Automatically slows down requests if we're getting close to the limit

**Ways We Save Money**:

- **Remember answers** → If someone asks a similar question, we reuse the answer instead of asking the AI again
- **Group requests** → When possible, combine multiple questions into one request
- **Optimize questions** → Write questions more efficiently to use fewer words (and cost less)
- **Choose wisely** → Use the AI that gives the best balance of quality and cost

### 9. Growing the System

**Starting Small (1,000 requests per day):**

- One gateway server is enough
- Direct connections to AI services
- Simple memory-based caching

**Scaling Up (10,000 requests per day):**

- Add more gateway servers and spread the load (like adding more cashiers at a busy store)
- Use a shared memory system so all servers can access the same cached answers
- Reuse connections to AI services (more efficient)
- Process multiple requests at the same time
- Queue requests during busy periods so nothing gets lost

### 10. Where Everything Lives

**Infrastructure (Where We Run Things):**

- **Gateway Service**: Runs in containers (like shipping containers for code) on cloud servers
- **Memory/Cache**: Uses a managed caching service (like a shared filing cabinet)
- **Settings Files**: Stored in cloud storage (like Google Drive) or code repository (like GitHub)
- **Monitoring Tools**: Uses cloud monitoring services to track performance
- **Logs**: Stored in cloud log services for easy searching

**Updating Settings:**

- Settings files are stored in a code repository (like GitHub) so we can track all changes
- When we update settings, the system automatically checks they're valid
- New settings are applied without stopping the service (users don't notice)
- The gateway checks for updates regularly or gets notified immediately when settings change

## Why We Designed It This Way

1. **Separate Gateway Service**: Keeps our main app separate from AI services, so we can update or change AI providers without touching the main app code. Also lets us scale the AI service independently.

2. **Provider Abstraction**: Makes it easy to add new AI providers in the future. We just add a new adapter - no need to rewrite the main app.

3. **Simple Text File Settings**: Easy for anyone to read and update. Can track all changes in version control. Works well with our Rails app.

4. **Automatic Backup System**: If one AI service fails, we don't lose all requests. The system automatically switches to backup, preventing total outages.

5. **Smart Memory**: Saves answers to common questions so we don't have to ask the AI again. This saves money and makes responses faster.

6. **Comprehensive Monitoring**: We can see exactly what's happening at all times. This helps us fix problems quickly and make the system better.

7. **Budget Tracking**: We always know how much we're spending. Alerts prevent surprise bills, and we can make decisions based on real cost data.

## What We Need to Build Next

1. **Build the Gateway Service** → Create the Python service that manages all AI requests
2. **Connect to AI Services** → Build the adapters that talk to GPT-4 and Claude
3. **Set Up Settings Management** → Create the system that reads and updates configuration files
4. **Deploy Monitoring Tools** → Set up dashboards and alerts so we can see what's happening
5. **Build the Memory System** → Implement caching so we can reuse answers
6. **Automate Settings Updates** → Set up automatic deployment of configuration changes
7. **Test Under Load** → Simulate heavy traffic to make sure everything works at scale
8. **Create Budget Dashboard** → Build a visual dashboard showing spending in real-time
