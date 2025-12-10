"""
Circuit Breaker implementation for provider failover.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
import time


class CircuitState(Enum):
    """Circuit breaker states."""
    SUCCESS = "success"  # Normal operation
    FAIL = "fail"  # Failing, don't use
    IN_PROGRESS = "in_progress"  # Testing if recovered - used to test if the provider has recovered from the failure.


@dataclass
class CircuitBreaker:
    """Circuit breaker for provider failover."""
    
    failure_threshold: int = 5
    error_rate_threshold: float = 0.5 
    recovery_timeout_seconds: int = 30 #Auto-recovery after 30 seconds (in-progress state)
    
    def __init__(self, failure_threshold: int = 5, error_rate_threshold: float = 0.5, 
                 recovery_timeout_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.error_rate_threshold = error_rate_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        
        self.state = CircuitState.SUCCESS
        self.failure_count = 0
        self.success_count = 0
        self.total_requests = 0
        self.last_failure_time: Optional[float] = None
        self.opened_at: Optional[float] = None
    
    def record_success(self):
        """Record a successful request."""
        self.success_count += 1
        self.total_requests += 1
        
        if self.state == CircuitState.IN_PROGRESS:
            # If we get a success in in-progress, mark as success
            self.state = CircuitState.SUCCESS
            self.failure_count = 0
            self.opened_at = None
    
    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.total_requests += 1
        self.last_failure_time = time.time()
        
        # Check if we should mark as failed
        if self.state == CircuitState.SUCCESS:
            error_rate = self.failure_count / self.total_requests if self.total_requests > 0 else 0
            
            if (self.failure_count >= self.failure_threshold or 
                error_rate >= self.error_rate_threshold):
                self.state = CircuitState.FAIL
                self.opened_at = time.time()
    
    def can_attempt(self) -> bool:
        """
        Check if we can attempt a request.
        
        Returns:
            True if we should try, False if circuit is in fail state
        """
        if self.state == CircuitState.SUCCESS:
            return True
        
        if self.state == CircuitState.FAIL:
            # Check if recovery timeout has passed
            if self.opened_at and (time.time() - self.opened_at) >= self.recovery_timeout_seconds:
                self.state = CircuitState.IN_PROGRESS
                return True
            return False
        
        if self.state == CircuitState.IN_PROGRESS:
            return True
        
        return False
    
    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        # Auto-transition from FAIL to IN_PROGRESS if timeout passed
        if self.state == CircuitState.FAIL and self.opened_at:
            if (time.time() - self.opened_at) >= self.recovery_timeout_seconds:
                self.state = CircuitState.IN_PROGRESS
        
        return self.state
    
    def get_stats(self) -> dict:
        error_rate = self.failure_count / self.total_requests if self.total_requests > 0 else 0
        
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_requests": self.total_requests,
            "error_rate": error_rate,
            "opened_at": self.opened_at
        }

