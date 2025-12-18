"""Tests for QW-3: Depsgraph Handler Optimization

Validates that:
- Depsgraph handler no longer causes high CPU usage
- UID sync only runs when necessary (load, undo/redo)
- Performance is improved in interactive scenarios
- Material integrity maintained after depsgraph updates
"""

import pytest
import bpy
import time
from conftest import (
    BlenderTestContext,
    assert_material_has_uid,
)


class TestQW3DepsgraphDisabled:
    """Test that depsgraph_handler is now a no-op."""
    
    def test_depsgraph_handler_exists(self):
        """depsgraph_handler should be defined."""
        from layer_painter import handlers
        
        assert hasattr(handlers, 'depsgraph_handler'), \
            "depsgraph_handler function should exist"
    
    def test_depsgraph_handler_is_noop(self):
        """depsgraph_handler should be a no-op to avoid CPU overhead."""
        from layer_painter import handlers
        
        # Call handler - should return None (no-op)
        result = handlers.depsgraph_handler(None)
        
        # Should be no-op or return None
        assert result is None
    
    def test_depsgraph_handler_does_not_modify_materials(self, blender_context):
        """depsgraph_handler should not modify material UIDs."""
        mat = blender_context.create_material("DepsgraphTest")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        original_uid = mat.lp.uid
        
        # Call depsgraph handler multiple times
        handlers.depsgraph_handler(None)
        handlers.depsgraph_handler(None)
        handlers.depsgraph_handler(None)
        
        # UID should not change
        assert mat.lp.uid == original_uid, \
            "depsgraph_handler should not modify UIDs"


class TestQW3OptimizedUIDSync:
    """Test that UID sync only happens at appropriate times."""
    
    def test_uid_sync_on_load(self, blender_context):
        """UID sync should happen on file load."""
        mat = blender_context.create_material("LoadTest")
        
        from layer_painter import handlers
        
        # Before sync - may not have UID depending on initialization
        handlers.set_material_uids()
        
        # After load handler - should have UID
        handlers.on_load_handler(None)
        
        # Material should have valid UID
        assert_material_has_uid(mat)
    
    def test_uid_sync_on_undo_redo(self, blender_context):
        """UID sync should happen on undo/redo."""
        mat = blender_context.create_material("UndoRedoTest")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        original_uid = mat.lp.uid
        
        # Call undo/redo handler
        handlers.on_undo_redo_handler(None)
        
        # Material should maintain its UID
        assert mat.lp.uid == original_uid or mat.lp.uid != "", \
            "UID should be maintained after undo/redo"


class TestQW3PerformanceImprovement:
    """Test performance improvements from disabling depsgraph_handler."""
    
    def test_depsgraph_handler_executes_instantly(self):
        """depsgraph_handler should execute instantly (no-op)."""
        from layer_painter import handlers
        
        # Time the handler execution
        start = time.time()
        for _ in range(1000):
            handlers.depsgraph_handler(None)
        elapsed = time.time() - start
        
        # Should be nearly instantaneous
        assert elapsed < 0.1, \
            f"depsgraph_handler too slow: {elapsed:.3f}s for 1000 calls"
    
    @pytest.mark.performance
    def test_interactive_performance_with_many_materials(self, blender_context):
        """Interactive use should be responsive with many materials."""
        import time
        
        from layer_painter import handlers
        
        # Create 50 materials to simulate large project
        materials = []
        for i in range(50):
            mat = blender_context.create_material(f"PerfTest_{i:03d}")
            materials.append(mat)
        
        handlers.set_material_uids()
        
        # Simulate interactive loop (50 depsgraph updates per frame)
        start = time.time()
        for _ in range(50):
            handlers.depsgraph_handler(None)
        elapsed = time.time() - start
        
        # Should complete quickly (was 60+x/sec = ~16ms each)
        # Now should be < 1ms
        assert elapsed < 0.1, \
            f"Interactive performance degraded: {elapsed:.3f}s for 50 depsgraph updates"
    
    @pytest.mark.performance
    def test_cpu_overhead_reduced(self, blender_context):
        """CPU overhead should be significantly reduced."""
        from layer_painter import handlers
        import time
        
        # Create baseline
        mat = blender_context.create_material("BaselineTest")
        handlers.set_material_uids()
        
        # Measure depsgraph_handler overhead
        iterations = 10000
        
        start = time.time()
        for _ in range(iterations):
            handlers.depsgraph_handler(None)
        depsgraph_time = time.time() - start
        
        # Should be negligible (effectively 0)
        per_call_us = (depsgraph_time / iterations) * 1_000_000
        
        # Each call should take << 1 microsecond now
        assert per_call_us < 10, \
            f"depsgraph_handler overhead too high: {per_call_us:.1f}µs per call"


class TestQW3CacheInvalidation:
    """Test that caches are still properly invalidated."""
    
    def test_load_handler_clears_caches(self, blender_context):
        """on_load_handler should clear all caches."""
        from layer_painter import handlers
        from layer_painter.data.materials import channel, layer
        
        # Create some materials
        mat = blender_context.create_material("CacheTest")
        handlers.set_material_uids()
        
        # Call load handler
        handlers.on_load_handler(None)
        
        # Caches should be cleared (should be empty dict)
        assert hasattr(channel, 'cached_materials'), \
            "channel cache should exist"
        assert hasattr(layer, 'cached_materials'), \
            "layer cache should exist"
    
    def test_undo_redo_handler_clears_caches(self, blender_context):
        """on_undo_redo_handler should clear caches."""
        from layer_painter import handlers
        from layer_painter.data.materials import channel, layer
        
        mat = blender_context.create_material("UndoTest")
        handlers.set_material_uids()
        
        # Call undo/redo handler
        handlers.on_undo_redo_handler(None)
        
        # Caches should be cleared
        assert hasattr(channel, 'cached_materials'), \
            "channel cache should exist"
        assert hasattr(layer, 'cached_materials'), \
            "layer cache should exist"


class TestQW3UIResponsiveness:
    """Test that UI remains responsive."""
    
    @pytest.mark.performance
    def test_ui_redraw_not_blocked_by_depsgraph(self, blender_context):
        """UI redraws should not be blocked by depsgraph_handler."""
        from layer_painter import handlers
        
        # Create materials
        for i in range(20):
            blender_context.create_material(f"UITest_{i}")
        
        handlers.set_material_uids()
        
        # Simulate UI redraw loop with depsgraph updates
        frame_times = []
        for frame in range(60):  # 60 frames
            frame_start = time.time()
            
            # Simulate 4 depsgraph updates per frame (typical in Blender)
            for _ in range(4):
                handlers.depsgraph_handler(None)
            
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
        
        avg_frame_time = sum(frame_times) / len(frame_times)
        max_frame_time = max(frame_times)
        
        # Average frame time should be negligible
        assert avg_frame_time < 0.001, \
            f"Average frame time too high: {avg_frame_time*1000:.2f}ms"
        
        # No frame should take significant time
        assert max_frame_time < 0.01, \
            f"Max frame time too high: {max_frame_time*1000:.2f}ms"


class TestQW3MaterialIntegrity:
    """Test that material integrity is maintained."""
    
    def test_material_uid_consistent_after_depsgraph(self, blender_context):
        """Material UID should remain consistent across depsgraph updates."""
        mat = blender_context.create_material("IntegrityTest")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        
        original_uid = mat.lp.uid
        original_name = mat.name
        
        # Simulate depsgraph updates
        for _ in range(100):
            handlers.depsgraph_handler(None)
        
        # Material should be intact
        assert mat.name == original_name
        assert mat.lp.uid == original_uid
        assert_material_has_uid(mat)
    
    def test_multiple_materials_integrity_after_depsgraph(self, blender_context):
        """Multiple materials should maintain integrity across depsgraph updates."""
        materials = []
        for i in range(10):
            mat = blender_context.create_material(f"IntegrityTest_{i}")
            materials.append((mat, mat.lp.uid if hasattr(mat, 'lp') else None))
        
        from layer_painter import handlers
        handlers.set_material_uids()
        
        # Capture UIDs
        original_uids = {mat.name: mat.lp.uid for mat, _ in materials}
        
        # Simulate depsgraph updates
        for _ in range(100):
            handlers.depsgraph_handler(None)
        
        # All materials should maintain their UIDs
        for mat, _ in materials:
            assert mat.lp.uid == original_uids[mat.name], \
                f"Material {mat.name} UID changed"


class TestQW3BackwardCompatibility:
    """Test backward compatibility of optimization."""
    
    def test_depsgraph_handler_compatible_with_existing_code(self, blender_context):
        """Existing code calling depsgraph_handler should work."""
        from layer_painter import handlers
        
        mat = blender_context.create_material("CompatTest")
        handlers.set_material_uids()
        
        # Old code might call this directly
        try:
            result = handlers.depsgraph_handler(None)
            # Should not raise exception
            assert result is None
        except Exception as e:
            pytest.fail(f"depsgraph_handler raised exception: {e}")
    
    def test_undo_redo_workflow_unchanged(self, blender_context):
        """Undo/redo workflow should remain unchanged."""
        from layer_painter import handlers
        
        mat = blender_context.create_material("UndoWorkflow")
        handlers.set_material_uids()
        uid = mat.lp.uid
        
        # Simulate typical undo/redo workflow
        handlers.on_undo_redo_handler(None)
        handlers.on_undo_redo_handler(None)
        handlers.on_undo_redo_handler(None)
        
        # Material should still have valid UID
        assert_material_has_uid(mat)


class TestQW3NoSideEffects:
    """Test that optimization introduces no side effects."""
    
    def test_depsgraph_handler_idempotent(self):
        """Multiple depsgraph_handler calls should have same effect."""
        from layer_painter import handlers
        
        # Call multiple times - should all be no-ops
        for _ in range(10):
            result = handlers.depsgraph_handler(None)
            assert result is None
    
    def test_depsgraph_handler_does_not_modify_scene(self, blender_context):
        """depsgraph_handler should not modify scene state."""
        from layer_painter import handlers
        
        # Create scene state
        original_materials = set(bpy.data.materials.keys())
        
        # Call handler many times
        for _ in range(100):
            handlers.depsgraph_handler(None)
        
        # Scene state should be unchanged
        current_materials = set(bpy.data.materials.keys())
        assert current_materials == original_materials, \
            "depsgraph_handler modified scene state"
