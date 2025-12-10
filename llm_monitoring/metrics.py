"""
Metrics collection and aggregation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
from collections import defaultdict


@dataclass
class RequestMetrics:
    request_id: str
    provider: str
    model: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    success: bool
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    feature_version: Optional[str] = None
    prompt_version: Optional[str] = None
    experiment_id: Optional[str] = None
    variant_id: Optional[str] = None


class MetricsCollector:
    """Collects and aggregates metrics."""
    
    def __init__(self):
        self.metrics: List[RequestMetrics] = []
        self.provider_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "latencies": []
        })
    
    def record(self, metrics: RequestMetrics):
        """Record metrics for a request."""
        self.metrics.append(metrics)
        
        stats = self.provider_stats[metrics.provider]
        stats["total_requests"] += 1
        stats["total_tokens"] += metrics.total_tokens
        stats["total_cost"] += metrics.cost_usd
        stats["latencies"].append(metrics.latency_ms)
        
        if metrics.success:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
    
    def get_provider_stats(self, provider: str) -> Dict:
        """Get aggregated statistics for a provider."""
        if provider not in self.provider_stats:
            return {}
        
        stats = self.provider_stats[provider]
        latencies = stats["latencies"]
        
        if not latencies:
            return stats
        
        latencies_sorted = sorted(latencies)
        n = len(latencies_sorted)
        
        return {
            **stats,
            "latency_p50": latencies_sorted[n // 2] if n > 0 else 0,
            "latency_p95": latencies_sorted[int(n * 0.95)] if n > 1 else latencies_sorted[0],
            "latency_p99": latencies_sorted[int(n * 0.99)] if n > 1 else latencies_sorted[0],
            "error_rate": stats["failed_requests"] / stats["total_requests"] if stats["total_requests"] > 0 else 0,
            "avg_latency": sum(latencies) / len(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies)
        }
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all providers."""
        return {
            provider: self.get_provider_stats(provider)
            for provider in self.provider_stats.keys()
        }
    
    def get_total_cost(self) -> float:
        """Get total cost across all providers."""
        return sum(stats["total_cost"] for stats in self.provider_stats.values())
    
    def get_total_requests(self) -> int:
        """Get total number of requests."""
        return len(self.metrics)
    
    def clear(self):
        """Clear all metrics (useful for testing)."""
        self.metrics.clear()
        self.provider_stats.clear()

