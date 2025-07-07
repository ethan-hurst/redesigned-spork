"""
Memory optimization utilities for Microsoft Dynamics & Power Platform Architecture Builder.

This module provides utilities for optimizing memory usage when working with
large architectures and component catalogs.
"""

import gc
import logging
import weakref
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
import psutil
import os

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class MemoryMonitor:
    """
    Monitor and track memory usage during operations.
    """

    def __init__(self):
        """Initialize the memory monitor."""
        self.process = psutil.Process(os.getpid())
        self._memory_snapshots: List[Dict[str, Any]] = []

    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get current memory information.

        Returns:
            Dictionary with memory statistics
        """
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
                "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
                "percent": memory_percent,
                "available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "total_mb": psutil.virtual_memory().total / 1024 / 1024,
            }
        except Exception as e:
            logger.debug(f"Failed to get memory info: {e}")
            return {}

    def snapshot(self, label: str = "") -> Dict[str, Any]:
        """
        Take a memory snapshot.

        Args:
            label: Optional label for the snapshot

        Returns:
            Memory information at time of snapshot
        """
        snapshot = self.get_memory_info()
        snapshot["label"] = label
        snapshot["timestamp"] = __import__("time").time()
        self._memory_snapshots.append(snapshot)
        
        if snapshot:
            logger.debug(f"Memory snapshot '{label}': {snapshot['rss_mb']:.1f} MB RSS")
        
        return snapshot

    def get_memory_delta(self, start_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate memory delta from a starting snapshot.

        Args:
            start_snapshot: Starting memory snapshot

        Returns:
            Dictionary with memory delta information
        """
        current = self.get_memory_info()
        if not current or not start_snapshot:
            return {}
            
        return {
            "rss_delta_mb": current["rss_mb"] - start_snapshot.get("rss_mb", 0),
            "vms_delta_mb": current["vms_mb"] - start_snapshot.get("vms_mb", 0),
            "percent_delta": current["percent"] - start_snapshot.get("percent", 0),
        }

    def log_memory_usage(self, operation: str = "") -> None:
        """
        Log current memory usage.

        Args:
            operation: Description of the current operation
        """
        memory_info = self.get_memory_info()
        if memory_info:
            logger.info(
                f"Memory usage{' for ' + operation if operation else ''}: "
                f"{memory_info['rss_mb']:.1f} MB RSS ({memory_info['percent']:.1f}%)"
            )


def memory_profile(operation_name: str = "") -> Callable[[F], F]:
    """
    Decorator to profile memory usage of a function.

    Args:
        operation_name: Name of the operation being profiled

    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = MemoryMonitor()
            start_snapshot = monitor.snapshot(f"start_{operation_name or func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_snapshot = monitor.snapshot(f"end_{operation_name or func.__name__}")
                delta = monitor.get_memory_delta(start_snapshot)
                
                if delta:
                    logger.debug(
                        f"Memory delta for {operation_name or func.__name__}: "
                        f"{delta['rss_delta_mb']:+.1f} MB RSS"
                    )
                    
                    # Log warning if memory usage increased significantly
                    if delta.get("rss_delta_mb", 0) > 50:  # More than 50MB increase
                        logger.warning(
                            f"High memory usage in {operation_name or func.__name__}: "
                            f"{delta['rss_delta_mb']:+.1f} MB increase"
                        )
        
        return wrapper
    return decorator


class ObjectPool:
    """
    Object pool for reusing expensive-to-create objects.
    """

    def __init__(self, factory: Callable[[], Any], max_size: int = 10):
        """
        Initialize object pool.

        Args:
            factory: Function to create new objects
            max_size: Maximum number of objects to pool
        """
        self.factory = factory
        self.max_size = max_size
        self._pool: List[Any] = []
        self._in_use: weakref.WeakSet = weakref.WeakSet()

    def get(self) -> Any:
        """
        Get an object from the pool.

        Returns:
            Object from pool or newly created object
        """
        if self._pool:
            obj = self._pool.pop()
        else:
            obj = self.factory()
        
        self._in_use.add(obj)
        return obj

    def release(self, obj: Any) -> None:
        """
        Release an object back to the pool.

        Args:
            obj: Object to release
        """
        if obj in self._in_use and len(self._pool) < self.max_size:
            # Reset object if it has a reset method
            if hasattr(obj, 'reset'):
                obj.reset()
            
            self._pool.append(obj)
            self._in_use.discard(obj)

    def clear(self) -> None:
        """Clear the pool."""
        self._pool.clear()


class LazyLoader:
    """
    Lazy loader for expensive-to-load data structures.
    """

    def __init__(self, loader: Callable[[], Any]):
        """
        Initialize lazy loader.

        Args:
            loader: Function to load the data
        """
        self._loader = loader
        self._data: Optional[Any] = None
        self._loaded = False

    def get(self) -> Any:
        """
        Get the loaded data, loading it if necessary.

        Returns:
            Loaded data
        """
        if not self._loaded:
            self._data = self._loader()
            self._loaded = True
        return self._data

    def is_loaded(self) -> bool:
        """
        Check if data is loaded.

        Returns:
            True if data is loaded
        """
        return self._loaded

    def unload(self) -> None:
        """Unload the data to free memory."""
        self._data = None
        self._loaded = False


class ChunkedProcessor:
    """
    Process large datasets in chunks to reduce memory usage.
    """

    def __init__(self, chunk_size: int = 100):
        """
        Initialize chunked processor.

        Args:
            chunk_size: Size of each processing chunk
        """
        self.chunk_size = chunk_size

    def process_in_chunks(
        self, 
        data: List[Any], 
        processor: Callable[[List[Any]], List[Any]]
    ) -> List[Any]:
        """
        Process data in chunks.

        Args:
            data: Data to process
            processor: Function to process each chunk

        Returns:
            Processed results
        """
        results = []
        
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            chunk_results = processor(chunk)
            results.extend(chunk_results)
            
            # Force garbage collection after each chunk
            if i % (self.chunk_size * 5) == 0:  # Every 5 chunks
                gc.collect()
        
        return results


def optimize_for_large_architecture(architecture_size: int) -> Dict[str, Any]:
    """
    Get optimization settings based on architecture size.

    Args:
        architecture_size: Number of components in the architecture

    Returns:
        Dictionary with optimization settings
    """
    if architecture_size < 10:
        # Small architecture - no special optimizations needed
        return {
            "use_chunked_processing": False,
            "enable_caching": True,
            "gc_frequency": 0,
            "max_memory_mb": 512,
        }
    elif architecture_size < 50:
        # Medium architecture - light optimizations
        return {
            "use_chunked_processing": False,
            "enable_caching": True,
            "gc_frequency": 10,
            "max_memory_mb": 1024,
        }
    else:
        # Large architecture - aggressive optimizations
        return {
            "use_chunked_processing": True,
            "chunk_size": 20,
            "enable_caching": True,
            "gc_frequency": 5,
            "max_memory_mb": 2048,
        }


def force_garbage_collection() -> Dict[str, Any]:
    """
    Force garbage collection and return statistics.

    Returns:
        Dictionary with garbage collection statistics
    """
    monitor = MemoryMonitor()
    before = monitor.get_memory_info()
    
    # Force garbage collection
    collected = gc.collect()
    
    after = monitor.get_memory_info()
    
    stats = {
        "objects_collected": collected,
        "memory_freed_mb": before.get("rss_mb", 0) - after.get("rss_mb", 0),
        "before_mb": before.get("rss_mb", 0),
        "after_mb": after.get("rss_mb", 0),
    }
    
    if stats["memory_freed_mb"] > 1:  # Only log if significant memory was freed
        logger.info(
            f"Garbage collection freed {stats['memory_freed_mb']:.1f} MB, "
            f"collected {stats['objects_collected']} objects"
        )
    
    return stats


class MemoryEfficientArchitectureProcessor:
    """
    Memory-efficient processor for large architecture operations.
    """

    def __init__(self, max_memory_mb: int = 1024):
        """
        Initialize the processor.

        Args:
            max_memory_mb: Maximum memory usage threshold in MB
        """
        self.max_memory_mb = max_memory_mb
        self.monitor = MemoryMonitor()
        self.chunked_processor = ChunkedProcessor()

    def check_memory_usage(self) -> bool:
        """
        Check if memory usage is within limits.

        Returns:
            True if memory usage is acceptable
        """
        memory_info = self.monitor.get_memory_info()
        current_mb = memory_info.get("rss_mb", 0)
        
        if current_mb > self.max_memory_mb:
            logger.warning(
                f"Memory usage ({current_mb:.1f} MB) exceeds limit ({self.max_memory_mb} MB)"
            )
            # Try to free some memory
            force_garbage_collection()
            return False
        
        return True

    def process_components_efficiently(
        self, 
        components: List[Any], 
        processor: Callable[[Any], Any]
    ) -> List[Any]:
        """
        Process components efficiently with memory monitoring.

        Args:
            components: Components to process
            processor: Function to process each component

        Returns:
            Processed components
        """
        if len(components) < 20:
            # Process all at once for small lists
            return [processor(comp) for comp in components]
        
        # Use chunked processing for large lists
        def chunk_processor(chunk: List[Any]) -> List[Any]:
            return [processor(comp) for comp in chunk]
        
        return self.chunked_processor.process_in_chunks(components, chunk_processor)


# Global memory monitor instance
_memory_monitor: Optional[MemoryMonitor] = None


def get_memory_monitor() -> MemoryMonitor:
    """
    Get the global memory monitor instance.

    Returns:
        Global MemoryMonitor instance
    """
    global _memory_monitor
    if _memory_monitor is None:
        _memory_monitor = MemoryMonitor()
    return _memory_monitor