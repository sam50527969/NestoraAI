"""
Nestora Business Memory

This package exposes a single shared MemoryManager instance
used throughout the application.
"""

from .memory_manager import MemoryManager

_memory_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    """
    Return the application's shared MemoryManager.

    All AI agents, missions and services should obtain memory
    through this function instead of creating their own instance.
    """
    return _memory_manager