"""
Time utility functions for Agent Memory OS

Provides helper functions for timestamp formatting and parsing.
"""

from datetime import datetime, timezone
from typing import Optional


def format_timestamp(dt: datetime, include_timezone: bool = True) -> str:
    """
    Format datetime to ISO string
    
    Args:
        dt: Datetime object to format
        include_timezone: Whether to include timezone info
        
    Returns:
        Formatted timestamp string
    """
    if include_timezone and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse timestamp string to datetime
    
    Args:
        timestamp_str: ISO format timestamp string
        
    Returns:
        Parsed datetime object or None if invalid
    """
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        try:
            # Try parsing without timezone info
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            return None


def get_current_timestamp() -> datetime:
    """
    Get current timestamp with UTC timezone
    
    Returns:
        Current datetime with UTC timezone
    """
    return datetime.now(timezone.utc)


def is_recent(dt: datetime, hours: int = 24) -> bool:
    """
    Check if datetime is within recent hours
    
    Args:
        dt: Datetime to check
        hours: Number of hours to consider "recent"
        
    Returns:
        True if datetime is within specified hours
    """
    now = get_current_timestamp()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    time_diff = now - dt
    return time_diff.total_seconds() < (hours * 3600) 