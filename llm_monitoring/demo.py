"""
Demo script showing the monitoring system in action.
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_monitoring.monitor import LLMMonitor


def main():
    """Run a demonstration of the monitoring system."""
    
    print("Initializing LLM Monitor...")
    monitor = LLMMonitor(log_file="llm_telemetry.jsonl")
    
    print("\nMaking mock API calls...\n")
    
    # Simulate a series of requests with two inputs: user_profile and job_market_data
    requests = [
        {
            "user_profile": "Software Engineer, 5 years experience, Python/Java, interested in AI/ML",
            "job_market_data": "AI Engineer roles: $120k-180k, ML Engineer: $130k-200k, Data Scientist: $110k-160k",
            "provider": "openai",
            "feature_version": "1.2.3",
            "prompt_version": "v2.1",
            "experiment_id": "provider_comparison",
            "variant_id": "variant_a"
        },
        {
            "user_profile": "Data Analyst, 3 years experience, SQL/Python, wants to transition to Data Science",
            "job_market_data": "Data Scientist roles: $110k-160k, Senior Data Analyst: $95k-140k, ML Engineer: $130k-200k",
            "provider": "anthropic",
            "feature_version": "1.2.3",
            "prompt_version": "v2.0",
            "experiment_id": "provider_comparison",
            "variant_id": "variant_b"
        },
        {
            "user_profile": "Product Manager, 4 years experience, wants salary information",
            "job_market_data": "Product Manager: $120k-180k, Senior PM: $150k-220k, Director PM: $180k-280k",
            "provider": None,  # Auto-select via A/B test
            "feature_version": "1.2.3",
            "prompt_version": "v1.5"
        },
    ]
    
    # Make requests
    for i, req in enumerate(requests, 1):
        print(f"Request {i}: User Profile: {req['user_profile'][:40]}...")
        try:
            response = monitor.generate(**req)
            print(f"  [OK] Success: {response.content[:60]}...")
            print(f"  Tokens: {response.input_tokens} in, {response.output_tokens} out (Total: {response.input_tokens + response.output_tokens})")
            print(f"  Latency: {response.latency_ms:.0f}ms\n")
        except Exception as e:
            print(f"  [ERROR] Error: {e}\n")
        
        time.sleep(0.5)  # Small delay between requests
    
    # Simulate some failures to test circuit breaker
    print("Simulating failures to test circuit breaker...\n")
    monitor.providers["openai"].failure_rate = 0.8  # 80% failure rate
    
    for i in range(6):
        print(f"Request with high failure rate ({i+1}/6)...")
        try:
            response = monitor.generate(
                user_profile="Test user profile",
                job_market_data="Test job market data",
                provider="openai",
                feature_version="1.2.3"
            )
            print(f"  [OK] Success\n")
        except Exception as e:
            print(f"  [ERROR] Error: {e}\n")
        time.sleep(0.3)
    
    # Reset failure rate
    monitor.providers["openai"].failure_rate = 0.0
    
    # Print final statistics
    monitor.print_stats()
    
    # Show some log entries
    print("\nSample Telemetry Log Entries:")
    print("-" * 60)
    if monitor.log_buffer:
        import json
        for entry in monitor.log_buffer[:3]:
            print(json.dumps(entry, indent=2))
            print()


if __name__ == "__main__":
    main()

