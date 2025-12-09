# Career Path Navigator - System Design

## What This Is

This repository contains the design for how Thrive's Career Path Navigator feature works behind the scenes. The system:
- Tests two different AI services (GPT-4 and Claude) to see which works better
- Handles 1,000 user requests per day initially, growing to 10,000 per day
- Responds to most requests in under 3 seconds
- Stays within a $5,000 monthly budget

## Files

### Architecture Documents
- **`architecture_design.md`**: Comprehensive architecture documentation with Mermaid diagram
- **`architecture_diagram_ascii.txt`**: ASCII art diagram for easy viewing in any text editor

### Configuration Files
- **`config/provider_settings.json`**: LLM provider configuration (API keys, models, costs)
- **`config/ab_test_config.json`**: A/B testing configuration and routing strategy
- **`config/rate_limits.json`**: Rate limiting and budget constraints


## How It Works - Main Parts

1. **Main Application (Rails)**: The part users interact with - receives requests and shows responses
2. **AI Gateway Service**: The smart middleman that manages all communication with AI services
3. **AI Provider Manager**: Handles connections to different AI services (GPT-4 and Claude)
4. **Settings Management**: Simple text files that control how the system behaves
5. **Monitoring System**: Tracks performance, spending, and errors - sends alerts when needed
6. **Backup System**: Automatically switches to a backup AI if the primary one fails

### Why We Built It This Way

- **Separate Gateway**: Keeps the main app independent from AI services - easier to update and scale
- **Provider Abstraction**: Easy to add new AI services in the future without rewriting code
- **Simple Text File Settings**: Anyone can read and update - stored in version control
- **Automatic Backup**: If one AI fails, we automatically use another - prevents total outages
- **Smart Memory**: Remembers answers to save money and speed up responses
- **Comprehensive Monitoring**: Always know what's happening - helps fix problems quickly

## Settings Files

All system settings are stored in simple text files in the `config/` directory:

- **`provider_settings.json`**: Which AI services to use, how much they cost, and backup settings
- **`ab_test_config.json`**: How to split requests between GPT-4 and Claude for testing
- **`rate_limits.json`**: Limits on how many requests users can make and monthly budget

These files:
- Are stored in Git (so we can track all changes)
- Can be stored in cloud storage (like S3) or GitHub
- Are read by both the main app and the gateway service
- Can be updated without restarting the system

## How a Request Works

1. User asks for a career path recommendation
2. Main app reads current settings from text files
3. Main app sends request to the AI gateway
4. Gateway checks its memory for similar questions (saves time and money!)
5. Gateway checks if user has exceeded their request limit
6. Gateway decides which AI to use (GPT-4 or Claude) based on A/B test
7. Gateway sends question to the chosen AI service
8. Gateway receives answer, saves it to memory, and formats it
9. Everything is logged so we can monitor performance
10. Formatted answer is sent back to the user

## What Happens When Things Go Wrong

The system has multiple backup plans:

1. **Try the chosen AI**: Based on A/B test, try GPT-4 or Claude
2. **Switch to backup**: If the first AI is down, automatically use the other one
3. **Use saved answer**: If both AIs are down, use a previously saved answer (even if it's a bit old)
4. **Partial response**: As a last resort, return whatever information we have

The backup system automatically kicks in if an AI fails 5 times in a row or has errors on 50% of requests. It tries again after 30 seconds to see if the AI is working again.

## Budget Management

- Tracks spending in real-time (counts every word sent to and received from AI)
- Sends alerts when we hit 80%, 90%, 95%, and 100% of daily or monthly budget
- Automatically slows down requests if we're getting close to the limit
- Saves money by:
  - Remembering answers to common questions
  - Grouping requests when possible
  - Writing questions more efficiently
  - Choosing the AI that gives best value

## Growing the System

**Starting Small (1,000 requests per day)**:
- One gateway server is enough
- Direct connections to AI services
- Simple memory-based caching

**Scaling Up (10,000 requests per day)**:
- Add more gateway servers and spread the load
- Use shared memory so all servers can access cached answers
- Reuse connections to AI services (more efficient)
- Process multiple requests at the same time
- Queue requests during busy periods

## What We Need to Build Next

1. **Build the Gateway Service**: Create the Python service that manages all AI requests
2. **Connect to AI Services**: Build the adapters that talk to GPT-4 and Claude
3. **Set Up Settings Management**: Create the system that reads and updates configuration files
4. **Deploy Monitoring Tools**: Set up dashboards and alerts so we can see what's happening
5. **Build the Memory System**: Implement caching so we can reuse answers
6. **Automate Settings Updates**: Set up automatic deployment of configuration changes
7. **Test Under Load**: Simulate heavy traffic to make sure everything works at scale
8. **Create Budget Dashboard**: Build a visual dashboard showing spending in real-time

## Questions or Feedback

This is a foundational design that can be iterated upon based on:
- Specific infrastructure preferences
- Existing tooling and services
- Team expertise and preferences
- Budget and timeline constraints

