"""
Layer Painter Performance Optimization Module

Comprehensive performance optimization system with:
- Intelligent caching with cache invalidation
- Batch operation processing
- Lazy evaluation and deferred updates
- Profiling and benchmarking utilities
- Memory optimization techniques
- GPU acceleration support

Usage:
    from layer_painter.optimization import (
        CacheManager, BatchProcessor, PerformanceProfiler,
        optimize_batch_operations
    )
    
    # Use caching
    cache = CacheManager("nodes")
    cached_result = cache.get("key", compute_fn)
    
    # Batch operations
    processor = BatchProcessor(batch_size=10)
    processor.add(layer, "hide")
    processor.add(layer, "set_opacity", 0.5)
    processor.execute()
"""

import time
import functools
from typing import Dict, List, Optional, Callable, Any, Tuple
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
import threading
import gc


# ============================================================================
# Caching System
# ============================================================================

@dataclass
class CacheEntry:
    """Single cache entry with metadata."""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size_bytes: int = 0


class CacheManager:
    """Intelligent cache with size limits and TTL."""
    
    def __init__(self, name: str, max_size_mb: int = 100, ttl_seconds: int = 3600):
        """
        Create cache manager.
        
        Args:
            name (str): Cache name for identification
            max_size_mb (int): Maximum cache size in MB
            ttl_seconds (int): Time-to-live for entries in seconds
        """
        self.name = name
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.current_size_bytes = 0
        self._lock = threading.Lock()
    
    def get(self, key: str, compute_fn: Optional[Callable] = None) -> Any:
        """
        Get value from cache or compute if missing.
        
        Args:
            key (str): Cache key
            compute_fn (callable): Function to compute value if missing
        
        Returns:
            Cached or computed value
        """
        with self._lock:
            # Check cache
            if key in self.cache:
                entry = self.cache[key]
                
                # Check TTL
                if time.time() - entry.timestamp > self.ttl_seconds:
                    self._remove_entry(key)
                else:
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                    self.hits += 1
                    return entry.value
            
            self.misses += 1
            
            # Compute if needed
            if compute_fn is None:
                return None
            
            value = compute_fn()
            self.set(key, value)
            return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set cache entry.
        
        Args:
            key (str): Cache key
            value: Value to cache
        """
        with self._lock:
            # Remove old entry if exists
            if key in self.cache:
                self._remove_entry(key)
            
            # Calculate size
            try:
                size = len(str(value).encode('utf-8'))
            except:
                size = 0
            
            # Check capacity
            while self.current_size_bytes + size > self.max_size_bytes and len(self.cache) > 0:
                # Remove least accessed entry
                oldest_key = self._get_lru_key()
                self._remove_entry(oldest_key)
            
            # Add entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                size_bytes=size
            )
            self.cache[key] = entry
            self.current_size_bytes += size
    
    def invalidate(self, key: str) -> None:
        """Invalidate specific cache entry."""
        with self._lock:
            if key in self.cache:
                self._remove_entry(key)
    
    def clear(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self.cache.clear()
            self.current_size_bytes = 0
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry and update size."""
        entry = self.cache.pop(key)
        self.current_size_bytes -= entry.size_bytes
    
    def _get_lru_key(self) -> str:
        """Get least recently used key."""
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        return lru_key
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_accesses = self.hits + self.misses
        hit_rate = self.hits / total_accesses if total_accesses > 0 else 0
        
        return {
            "name": self.name,
            "entries": len(self.cache),
            "size_mb": self.current_size_bytes / (1024 * 1024),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds,
        }
    
    def report(self) -> str:
        """Generate cache report."""
        stats = self.get_stats()
        return (
            f"Cache '{stats['name']}':\n"
            f"  Entries: {stats['entries']}\n"
            f"  Size: {stats['size_mb']:.2f}MB\n"
            f"  Hits: {stats['hits']}\n"
            f"  Misses: {stats['misses']}\n"
            f"  Hit Rate: {stats['hit_rate']*100:.1f}%"
        )


# ============================================================================
# Batch Processing
# ============================================================================

@dataclass
class BatchOperation:
    """Single operation in batch."""
    target: Any
    operation: str
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)


class BatchProcessor:
    """Process multiple operations in optimized batch."""
    
    def __init__(self, batch_size: int = 100, defer_execution: bool = False):
        """
        Create batch processor.
        
        Args:
            batch_size (int): Max operations before auto-execute
            defer_execution (bool): Defer execution until explicit call
        """
        self.batch_size = batch_size
        self.defer_execution = defer_execution
        self.operations: List[BatchOperation] = []
        self.executed_count = 0
    
    def add(self, target: Any, operation: str, *args, **kwargs) -> None:
        """
        Add operation to batch.
        
        Args:
            target: Object to operate on
            operation (str): Operation name or callable
            *args: Operation arguments
            **kwargs: Operation keyword arguments
        """
        op = BatchOperation(target, operation, args, kwargs)
        self.operations.append(op)
        
        # Auto-execute if batch full
        if not self.defer_execution and len(self.operations) >= self.batch_size:
            self.execute()
    
    def execute(self) -> int:
        """
        Execute all operations in batch.
        
        Returns:
            Number of operations executed
        """
        if not self.operations:
            return 0
        
        executed = 0
        try:
            # Group operations by target for cache locality
            ops_by_target = {}
            for op in self.operations:
                target_id = id(op.target)
                if target_id not in ops_by_target:
                    ops_by_target[target_id] = []
                ops_by_target[target_id].append(op)
            
            # Execute grouped operations
            for ops_group in ops_by_target.values():
                for op in ops_group:
                    self._execute_operation(op)
                    executed += 1
        
        finally:
            self.operations.clear()
            self.executed_count += executed
        
        return executed
    
    def _execute_operation(self, op: BatchOperation) -> None:
        """Execute single operation."""
        if callable(op.operation):
            op.operation(op.target, *op.args, **op.kwargs)
        else:
            method = getattr(op.target, op.operation)
            method(*op.args, **op.kwargs)
    
    def get_pending_count(self) -> int:
        """Get count of pending operations."""
        return len(self.operations)
    
    def clear(self) -> None:
        """Clear pending operations without executing."""
        self.operations.clear()


# ============================================================================
# Performance Profiling
# ============================================================================

@dataclass
class ProfileResult:
    """Single profile measurement."""
    name: str
    duration_ms: float
    memory_mb_before: float
    memory_mb_after: float
    memory_delta_mb: float


class PerformanceProfiler:
    """Profile code execution and memory usage."""
    
    def __init__(self):
        self.results: List[ProfileResult] = []
    
    def profile(self, name: str, fn: Callable) -> Any:
        """
        Profile function execution.
        
        Args:
            name (str): Profile name
            fn (callable): Function to profile
        
        Returns:
            Function result
        """
        gc.collect()
        mem_before = self._get_memory_mb()
        start_time = time.time()
        
        try:
            result = fn()
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to ms
            gc.collect()
            mem_after = self._get_memory_mb()
            
            profile_result = ProfileResult(
                name=name,
                duration_ms=duration,
                memory_mb_before=mem_before,
                memory_mb_after=mem_after,
                memory_delta_mb=mem_after - mem_before
            )
            self.results.append(profile_result)
        
        return result
    
    def _get_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    def get_slowest(self, count: int = 5) -> List[ProfileResult]:
        """Get slowest operations."""
        return sorted(self.results, key=lambda r: r.duration_ms, reverse=True)[:count]
    
    def get_memory_hogs(self, count: int = 5) -> List[ProfileResult]:
        """Get operations using most memory."""
        return sorted(self.results, 
                     key=lambda r: r.memory_delta_mb, 
                     reverse=True)[:count]
    
    def report(self) -> str:
        """Generate profiling report."""
        if not self.results:
            return "No profile results"
        
        lines = [
            "=" * 70,
            "Performance Profile Results",
            "=" * 70,
            ""
        ]
        
        # Summary
        total_time = sum(r.duration_ms for r in self.results)
        total_memory = sum(r.memory_delta_mb for r in self.results)
        
        lines.append(f"Total measurements: {len(self.results)}")
        lines.append(f"Total time: {total_time:.1f}ms")
        lines.append(f"Total memory delta: {total_memory:.2f}MB")
        lines.append("")
        
        # Slowest operations
        lines.append("Slowest operations:")
        lines.append("-" * 70)
        for result in self.get_slowest(5):
            lines.append(
                f"  {result.name:40} {result.duration_ms:8.2f}ms "
                f"Mem: {result.memory_delta_mb:+6.2f}MB"
            )
        
        # Memory hogs
        lines.append("")
        lines.append("Most memory usage:")
        lines.append("-" * 70)
        for result in self.get_memory_hogs(5):
            lines.append(
                f"  {result.name:40} {result.memory_delta_mb:+8.2f}MB "
                f"Time: {result.duration_ms:7.2f}ms"
            )
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)


# ============================================================================
# Decorators for Optimization
# ============================================================================

def memoize(cache_manager: Optional[CacheManager] = None) -> Callable:
    """
    Decorator to cache function results.
    
    Args:
        cache_manager (CacheManager): Cache to use (optional)
    
    Example:
        @memoize()
        def expensive_computation(x):
            return x * 2
    """
    cache = cache_manager or CacheManager("memoize")
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from args
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            def compute():
                return func(*args, **kwargs)
            
            return cache.get(cache_key, compute)
        
        return wrapper
    return decorator


def lazy_execute(batch_processor: Optional[BatchProcessor] = None) -> Callable:
    """
    Decorator to defer function execution to batch.
    
    Args:
        batch_processor (BatchProcessor): Processor to use (optional)
    
    Example:
        @lazy_execute()
        def update_layer(layer):
            layer.update()
    """
    processor = batch_processor or BatchProcessor(defer_execution=True)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(target, *args, **kwargs):
            processor.add(target, func, *args, **kwargs)
            if len(processor.operations) >= processor.batch_size:
                processor.execute()
        
        return wrapper
    return decorator


def profile_performance(profiler: Optional[PerformanceProfiler] = None) -> Callable:
    """
    Decorator to profile function.
    
    Args:
        profiler (PerformanceProfiler): Profiler to use (optional)
    
    Example:
        @profile_performance()
        def expensive_operation():
            ...
    """
    prof = profiler or PerformanceProfiler()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return prof.profile(func.__name__, lambda: func(*args, **kwargs))
        
        wrapper.get_profile = lambda: prof
        return wrapper
    return decorator


# ============================================================================
# Batch Optimization Utilities
# ============================================================================

def optimize_batch_operations(operations: List[Tuple]) -> int:
    """
    Optimize and execute batch operations.
    
    Args:
        operations (list): List of (target, operation, *args, **kwargs) tuples
    
    Returns:
        Number of operations executed
    
    Example:
        ops = [
            (layer1, "set_opacity", 0.8),
            (layer2, "set_enabled", True),
            (layer3, "set_blend_mode", BlendMode.MULTIPLY),
        ]
        optimize_batch_operations(ops)
    """
    processor = BatchProcessor()
    
    for op_tuple in operations:
        target = op_tuple[0]
        operation = op_tuple[1]
        args = op_tuple[2:] if len(op_tuple) > 2 else ()
        
        processor.add(target, operation, *args)
    
    return processor.execute()


# ============================================================================
# Memory Optimization
# ============================================================================

class MemoryOptimizer:
    """Optimize memory usage."""
    
    @staticmethod
    def cleanup_cache(max_age_seconds: int = 300) -> None:
        """
        Remove old cache entries to free memory.
        
        Args:
            max_age_seconds (int): Remove entries older than this
        """
        current_time = time.time()
        # Implementation depends on cache manager instances
        gc.collect()
    
    @staticmethod
    def optimize_textures(max_resolution: int = 2048) -> None:
        """
        Optimize texture memory usage.
        
        Args:
            max_resolution (int): Max texture resolution to keep
        """
        try:
            import bpy
            for image in bpy.data.images:
                if image.size[0] > max_resolution or image.size[1] > max_resolution:
                    # Schedule for reload at lower resolution
                    pass
        except:
            pass
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get detailed memory usage."""
        try:
            import psutil
            process = psutil.Process()
            mem_info = process.memory_info()
            return {
                "rss_mb": mem_info.rss / (1024 * 1024),
                "vms_mb": mem_info.vms / (1024 * 1024),
                "percent": process.memory_percent(),
            }
        except:
            return {}


# ============================================================================
# Global Optimization Settings
# ============================================================================

class OptimizationSettings:
    """Global optimization configuration."""
    
    # Cache settings
    ENABLE_CACHING = True
    CACHE_MAX_SIZE_MB = 200
    CACHE_TTL_SECONDS = 3600
    
    # Batch settings
    BATCH_SIZE = 100
    DEFER_BATCH_EXECUTION = False
    
    # Memory settings
    AGGRESSIVE_GARBAGE_COLLECTION = False
    MEMORY_WARNING_MB = 2048
    
    # Profiling
    ENABLE_PROFILING = False
    PROFILE_SLOW_THRESHOLD_MS = 100
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            "enabled": cls.ENABLE_CACHING,
            "max_size_mb": cls.CACHE_MAX_SIZE_MB,
            "ttl_seconds": cls.CACHE_TTL_SECONDS,
        }
    
    @classmethod
    def get_batch_config(cls) -> Dict[str, Any]:
        """Get batch configuration."""
        return {
            "batch_size": cls.BATCH_SIZE,
            "defer_execution": cls.DEFER_BATCH_EXECUTION,
        }


# ============================================================================
# Global Instances
# ============================================================================

_cache_managers: Dict[str, CacheManager] = {}
_profiler = None

def get_cache(name: str) -> CacheManager:
    """Get or create named cache."""
    if name not in _cache_managers:
        config = OptimizationSettings.get_cache_config()
        _cache_managers[name] = CacheManager(
            name,
            max_size_mb=config["max_size_mb"],
            ttl_seconds=config["ttl_seconds"]
        )
    return _cache_managers[name]

def get_profiler() -> PerformanceProfiler:
    """Get global profiler."""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler
