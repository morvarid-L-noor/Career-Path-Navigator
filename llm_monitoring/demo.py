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
    
    # Simulate a series of requests
    requests = [
        {
            "prompt": "What career paths are available for a software engineer with 5 years of experience?",
            "provider": "openai",
            "feature_version": "1.2.3",
            "prompt_version": "v2.1",
            "experiment_id": "provider_comparison",
            "variant_id": "variant_a"
        },
        {
            "prompt": "What skills should I develop to transition to data science?",
            "provider": "anthropic",
            "feature_version": "1.2.3",
            "prompt_version": "v2.0",
            "experiment_id": "provider_comparison",
            "variant_id": "variant_b"
        },
        {
            "prompt": "What is the average salary for a product manager?",
            "provider": None,  # Auto-select
            "feature_version": "1.2.3",
            "prompt_version": "v1.5"
        },
    ]
    
    # Make requests
    for i, req in enumerate(requests, 1):
        print(f"Request {i}: {req['prompt'][:50]}...")
        try:
            response = monitor.generate(**req)
            print(f"  [OK] Success: {response.content[:60]}...")
            print(f"  Tokens: {response.input_tokens} in, {response.output_tokens} out")
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
                prompt="Test request",
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

