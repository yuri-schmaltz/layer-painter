"""
Performance Optimization - Usage Examples

Examples of using Layer Painter's performance optimization system.
"""

from layer_painter.optimization import (
    CacheManager, BatchProcessor, PerformanceProfiler,
    memoize, lazy_execute, profile_performance,
    optimize_batch_operations, MemoryOptimizer,
    OptimizationSettings, get_cache, get_profiler
)


# ============================================================================
# Example 1: Basic Caching
# ============================================================================

def example_basic_caching():
    """Simple caching examples."""
    
    # Create cache
    cache = CacheManager("nodes", max_size_mb=50, ttl_seconds=600)
    
    # Cache a computed value
    def expensive_lookup(node_uid):
        # Simulated expensive operation
        for node in range(1000000):
            pass
        return f"Node_{node_uid}"
    
    # First call: computes
    result1 = cache.get("node_a", lambda: expensive_lookup("a"))
    print(f"First call: {result1}")
    
    # Second call: cached
    result2 = cache.get("node_a", lambda: expensive_lookup("a"))
    print(f"Second call (cached): {result2}")
    
    # Get cache statistics
    stats = cache.get_stats()
    print(f"Cache hit rate: {stats['hit_rate']*100:.1f}%")
    print(f"Cache size: {stats['size_mb']:.2f}MB")
    
    # Print report
    print(cache.report())


# ============================================================================
# Example 2: Cache Invalidation
# ============================================================================

def example_cache_invalidation():
    """Manage cache lifecycle."""
    
    cache = CacheManager("materials")
    
    # Add entries
    cache.set("mat_1", {"name": "Material 1"})
    cache.set("mat_2", {"name": "Material 2"})
    
    print(f"Cache entries: {len(cache.cache)}")
    
    # Invalidate specific entry
    cache.invalidate("mat_1")
    print(f"After invalidate: {len(cache.cache)}")
    
    # Clear entire cache
    cache.clear()
    print(f"After clear: {len(cache.cache)}")


# ============================================================================
# Example 3: Batch Operations
# ============================================================================

def example_batch_operations():
    """Optimize with batch processing."""
    
    # Create some objects
    class Layer:
        def __init__(self, name):
            self.name = name
            self.enabled = True
            self.opacity = 1.0
        
        def set_enabled(self, enabled):
            self.enabled = enabled
        
        def set_opacity(self, opacity):
            self.opacity = opacity
        
        def toggle(self):
            self.enabled = not self.enabled
    
    layers = [Layer(f"Layer_{i}") for i in range(5)]
    
    # Process in batch
    processor = BatchProcessor(batch_size=10)
    
    # Add operations
    for layer in layers:
        processor.add(layer, "set_opacity", 0.8)
        processor.add(layer, "set_enabled", True)
    
    # Execute batch
    count = processor.execute()
    print(f"Executed {count} operations")
    
    # Verify results
    for layer in layers:
        print(f"{layer.name}: enabled={layer.enabled}, opacity={layer.opacity}")


# ============================================================================
# Example 4: Deferred Batch Execution
# ============================================================================

def example_deferred_batch():
    """Defer batch execution for later."""
    
    class Layer:
        def __init__(self, name):
            self.name = name
            self.data = None
        
        def update(self):
            self.data = f"Updated_{self.name}"
    
    layers = [Layer(f"Layer_{i}") for i in range(3)]
    
    # Create deferred processor
    processor = BatchProcessor(batch_size=100, defer_execution=True)
    
    # Add many operations (won't execute immediately)
    for layer in layers:
        processor.add(layer, "update")
    
    print(f"Pending operations: {processor.get_pending_count()}")
    
    # Execute manually when ready
    processor.execute()
    
    # Verify
    for layer in layers:
        print(f"{layer.name}: {layer.data}")


# ============================================================================
# Example 5: Memoization Decorator
# ============================================================================

def example_memoization():
    """Use memoization decorator."""
    
    call_count = 0
    
    @memoize()
    def fibonacci(n):
        nonlocal call_count
        call_count += 1
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # First call: computes
    result1 = fibonacci(10)
    calls_first = call_count
    print(f"First call to fib(10): {result1}, function calls: {calls_first}")
    
    # Second call: uses cache
    call_count = 0
    result2 = fibonacci(10)
    calls_second = call_count
    print(f"Second call to fib(10): {result2}, function calls: {calls_second}")
    
    print(f"Performance improvement: {calls_first/max(calls_second,1):.1f}x faster")


# ============================================================================
# Example 6: Performance Profiling
# ============================================================================

def example_performance_profiling():
    """Profile function execution and memory."""
    
    profiler = PerformanceProfiler()
    
    def operation_1():
        """Fast operation."""
        time_data = sum(range(1000))
        return time_data
    
    def operation_2():
        """Slow operation."""
        time_data = sum(range(1000000))
        return time_data
    
    def operation_3():
        """Memory-intensive operation."""
        data = [x for x in range(100000)]
        return sum(data)
    
    # Profile operations
    profiler.profile("Fast Op", operation_1)
    profiler.profile("Slow Op", operation_2)
    profiler.profile("Memory Op", operation_3)
    
    # Get report
    print(profiler.report())
    
    # Get specific results
    slowest = profiler.get_slowest(2)
    print(f"\nSlowest operation: {slowest[0].name} ({slowest[0].duration_ms:.2f}ms)")


# ============================================================================
# Example 7: Profiling Decorator
# ============================================================================

def example_profiling_decorator():
    """Use profiling decorator."""
    
    @profile_performance()
    def compute_texture_normal():
        """Compute normal map."""
        import time
        time.sleep(0.1)  # Simulate work
        return "normal_map.png"
    
    # Call function
    result = compute_texture_normal()
    
    # Get profiler
    profiler = compute_texture_normal.get_profile()
    print(profiler.report())


# ============================================================================
# Example 8: Batch Optimization Helper
# ============================================================================

def example_batch_optimization():
    """Use batch optimization helper."""
    
    class Layer:
        def __init__(self, name):
            self.name = name
            self.opacity = 1.0
            self.blend_mode = "Normal"
            self.enabled = True
        
        def set_opacity(self, opacity):
            self.opacity = opacity
        
        def set_blend_mode(self, mode):
            self.blend_mode = mode
        
        def set_enabled(self, enabled):
            self.enabled = enabled
    
    layers = [Layer(f"Layer_{i}") for i in range(10)]
    
    # Define batch operations
    operations = []
    
    # Decrease opacity for all layers
    for layer in layers:
        operations.append((layer, "set_opacity", 0.7))
    
    # Set blend modes
    for layer in layers:
        operations.append((layer, "set_blend_mode", "Multiply"))
    
    # Enable all
    for layer in layers:
        operations.append((layer, "set_enabled", True))
    
    # Execute in optimized batch
    count = optimize_batch_operations(operations)
    print(f"Executed {count} operations in batch")
    
    # Verify
    for layer in layers:
        print(f"{layer.name}: opacity={layer.opacity}, blend={layer.blend_mode}")


# ============================================================================
# Example 9: Memory Optimization
# ============================================================================

def example_memory_optimization():
    """Memory optimization utilities."""
    
    # Get current memory usage
    mem_usage = MemoryOptimizer.get_memory_usage()
    print(f"Current memory usage: {mem_usage}")
    
    # Cleanup old cache entries
    MemoryOptimizer.cleanup_cache(max_age_seconds=300)
    print("Cleaned up old cache entries")
    
    # Optimize texture sizes
    MemoryOptimizer.optimize_textures(max_resolution=2048)
    print("Optimized texture sizes")


# ============================================================================
# Example 10: Global Cache Usage
# ============================================================================

def example_global_cache():
    """Use global cache instances."""
    
    # Get named cache
    node_cache = get_cache("nodes")
    layer_cache = get_cache("layers")
    
    # Store data
    node_cache.set("node_1", {"type": "Mix", "inputs": 2})
    layer_cache.set("layer_1", {"type": "PAINT", "opacity": 0.8})
    
    # Retrieve
    node_data = node_cache.get("node_1")
    layer_data = layer_cache.get("layer_1")
    
    print(f"Node cache: {node_cache.get_stats()['entries']} entries")
    print(f"Layer cache: {layer_cache.get_stats()['entries']} entries")


# ============================================================================
# Example 11: Custom Cache for Layer Queries
# ============================================================================

def example_custom_cache():
    """Use cache for expensive layer queries."""
    
    class Material:
        def __init__(self, name):
            self.name = name
            self.layers = []
        
        def add_layer(self, layer):
            self.layers.append(layer)
            layer_query_cache.invalidate(f"{self.name}_visible")
    
    class Layer:
        def __init__(self, name, enabled=True):
            self.name = name
            self.enabled = enabled
    
    layer_query_cache = CacheManager("layer_queries")
    
    # Create material
    mat = Material("Test Material")
    for i in range(100):
        mat.add_layer(Layer(f"Layer_{i}", enabled=(i % 2 == 0)))
    
    # Expensive query
    def get_visible_layers():
        return [l for l in mat.layers if l.enabled]
    
    # First call: computes
    visible = layer_query_cache.get(
        f"{mat.name}_visible",
        get_visible_layers
    )
    print(f"First query: {len(visible)} visible layers")
    
    # Second call: cached
    visible = layer_query_cache.get(
        f"{mat.name}_visible",
        get_visible_layers
    )
    print(f"Second query (cached): {len(visible)} visible layers")
    
    print(f"Cache efficiency: {layer_query_cache.get_stats()['hit_rate']*100:.1f}%")


# ============================================================================
# Example 12: Optimization Settings
# ============================================================================

def example_optimization_settings():
    """Configure global optimization settings."""
    
    # Get current settings
    cache_config = OptimizationSettings.get_cache_config()
    batch_config = OptimizationSettings.get_batch_config()
    
    print(f"Cache config: {cache_config}")
    print(f"Batch config: {batch_config}")
    
    # Modify settings
    OptimizationSettings.ENABLE_CACHING = True
    OptimizationSettings.CACHE_MAX_SIZE_MB = 300
    OptimizationSettings.BATCH_SIZE = 50
    OptimizationSettings.ENABLE_PROFILING = True
    
    print("Updated optimization settings")


# ============================================================================
# Example 13: Practical Workflow - Optimize Layer Operations
# ============================================================================

def example_practical_layer_workflow():
    """Practical example: optimize layer batch operations."""
    
    class Channel:
        def __init__(self, name):
            self.name = name
    
    class Layer:
        def __init__(self, name, layer_type):
            self.name = name
            self.type = layer_type
            self.opacity = 1.0
            self.enabled = True
            self.channels = [Channel("Base Color"), Channel("Normal")]
        
        def set_opacity(self, val):
            self.opacity = val
        
        def set_enabled(self, val):
            self.enabled = val
    
    class Material:
        def __init__(self, name):
            self.name = name
            self.layers = []
        
        def add_layer(self, layer):
            self.layers.append(layer)
    
    # Create material with layers
    mat = Material("PBR Material")
    for i in range(20):
        layer_type = "PAINT" if i % 2 == 0 else "FILL"
        layer = Layer(f"{layer_type}_Layer_{i}", layer_type)
        mat.add_layer(layer)
    
    # Batch operation: show all paint, hide all fill
    operations = []
    
    for layer in mat.layers:
        if layer.type == "PAINT":
            operations.append((layer, "set_enabled", True))
        else:
            operations.append((layer, "set_enabled", False))
    
    # Execute batch
    count = optimize_batch_operations(operations)
    print(f"Configured {count} layers in batch operation")
    
    # Verify
    paint_count = sum(1 for l in mat.layers if l.type == "PAINT" and l.enabled)
    fill_count = sum(1 for l in mat.layers if l.type == "FILL" and not l.enabled)
    print(f"Result: {paint_count} paint visible, {fill_count} fill hidden")


# ============================================================================
# Example 14: Cache Efficiency Monitoring
# ============================================================================

def example_cache_monitoring():
    """Monitor cache efficiency."""
    
    cache = CacheManager("test")
    
    # Simulate workload with varying cache hits
    for i in range(100):
        key = f"item_{i % 20}"  # Only 20 unique keys
        cache.get(key, lambda: f"value_{key}")
    
    stats = cache.get_stats()
    
    print("Cache Efficiency Report:")
    print(f"  Total accesses: {stats['hits'] + stats['misses']}")
    print(f"  Cache hits: {stats['hits']}")
    print(f"  Cache misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']*100:.1f}%")
    print(f"  Stored entries: {stats['entries']}")
    print(f"  Cache size: {stats['size_mb']:.2f}MB")


# ============================================================================
# Performance Tips & Best Practices
# ============================================================================

"""
Performance Optimization Best Practices:

1. **Caching**:
   - Cache expensive lookups (node searches, layer queries)
   - Use appropriate TTL for cache entries
   - Monitor cache hit rate (aim for >70%)
   - Clear cache on relevant events

2. **Batch Operations**:
   - Batch similar operations together
   - Process 50-100 ops per batch
   - Group by target for cache locality
   - Defer execution for non-critical updates

3. **Memory**:
   - Profile peak memory usage
   - Monitor texture sizes (cap at 4K)
   - Clear unused caches periodically
   - Use lazy loading for large datasets

4. **Profiling**:
   - Profile slow operations (>100ms)
   - Track memory-intensive functions
   - Identify bottlenecks early
   - Use @profile_performance() decorator

5. **Node Operations**:
   - Cache node lookups by UID
   - Batch node creation
   - Defer layout organization
   - Profile shader tree traversals

6. **Texture Operations**:
   - Batch texture creation
   - Cache image lookups
   - Defer resolution changes
   - Monitor memory usage

7. **Baking**:
   - Use GPU acceleration (CUDA/HIP)
   - Lower resolution for testing
   - Batch bake multiple channels
   - Profile bake time
"""
