"""
Response Cache - Redis-based caching for similar queries.
For POC, uses in-memory cache. In production, would use Redis.
"""

import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class ResponseCache:
    """
    Response cache for storing and retrieving similar queries.
    Uses content-based hashing to identify similar requests.
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize response cache.
        
        Args:
            ttl_seconds: Time to live for cached entries (default 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def _generate_cache_key(self, user_profile: str, job_market_data: str, 
                           system_prompt: Optional[str] = None) -> str:
        """
        Generate a cache key from request content.
        
        Args:
            user_profile: User profile data
            job_market_data: Job market data
            system_prompt: Optional system prompt
            
        Returns:
            Cache key (hash of content)
        """
        content = json.dumps({
            "user_profile": user_profile,
            "job_market_data": job_market_data,
            "system_prompt": system_prompt or ""
        }, sort_keys=True)
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, user_profile: str, job_market_data: str, 
            system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available.
        
        Args:
            user_profile: User profile data
            job_market_data: Job market data
            system_prompt: Optional system prompt
            
        Returns:
            Cached response dict or None if not found/expired
        """
        cache_key = self._generate_cache_key(user_profile, job_market_data, system_prompt)
        
        if cache_key not in self.cache:
            return None
        
        cached_entry = self.cache[cache_key]
        
        # Check if expired
        if datetime.now() > cached_entry["expires_at"]:
            del self.cache[cache_key]
            return None
        
        return cached_entry["response"]
    
    def set(self, user_profile: str, job_market_data: str, 
            response: Dict[str, Any], system_prompt: Optional[str] = None):
        """
        Store response in cache.
        
        Args:
            user_profile: User profile data
            job_market_data: Job market data
            response: Response to cache
            system_prompt: Optional system prompt
        """
        cache_key = self._generate_cache_key(user_profile, job_market_data, system_prompt)
        
        self.cache[cache_key] = {
            "response": response,
            "cached_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=self.ttl_seconds)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        # Clean expired entries
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry["expires_at"]
        ]
        for key in expired_keys:
            del self.cache[key]
        
        return {
            "total_entries": len(self.cache),
            "ttl_seconds": self.ttl_seconds
        }
    
    def clear(self):
        """Clear all cached entries."""
        self.cache.clear()

