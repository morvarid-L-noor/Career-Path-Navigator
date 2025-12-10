"""
Circuit Breaker implementation for provider failover.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
import time


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, don't use
    HALF_OPEN = "half_open"  # Testing if recovered #Half-open state is used to test if the provider has recovered from the failure.


@dataclass
class CircuitBreaker:
    """Circuit breaker for provider failover."""
    
    failure_threshold: int = 5
    error_rate_threshold: float = 0.5 
    recovery_timeout_seconds: int = 30 #Auto-recovery after 30 seconds (half-open state)
    
    def __init__(self, failure_threshold: int = 5, error_rate_threshold: float = 0.5, 
                 recovery_timeout_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.error_rate_threshold = error_rate_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.total_requests = 0
        self.last_failure_time: Optional[float] = None
        self.opened_at: Optional[float] = None
    
    def record_success(self):
        """Record a successful request."""
        self.success_count += 1
        self.total_requests += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # If we get a success in half-open, close the circuit
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.opened_at = None
    
    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.total_requests += 1
        self.last_failure_time = time.time()
        
        # Check if we should open the circuit
        if self.state == CircuitState.CLOSED:
            error_rate = self.failure_count / self.total_requests if self.total_requests > 0 else 0
            
            if (self.failure_count >= self.failure_threshold or 
                error_rate >= self.error_rate_threshold):
                self.state = CircuitState.OPEN
                self.opened_at = time.time()
    
    def can_attempt(self) -> bool:
        """
        Check if we can attempt a request.
        
        Returns:
            True if we should try, False if circuit is open
        """
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.opened_at and (time.time() - self.opened_at) >= self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        # Auto-transition from OPEN to HALF_OPEN if timeout passed
        if self.state == CircuitState.OPEN and self.opened_at:
            if (time.time() - self.opened_at) >= self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
        
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

