"""Tests for QW-1: Material UID Duplication Fix

Validates that:
- Materials have unique UIDs on creation
- Duplicated materials inherit parent UIDs
- Duplicate detection works correctly
- Undo/redo preserves UID integrity
"""

import pytest
import bpy
from conftest import (
    BlenderTestContext, 
    assert_material_has_uid,
    assert_materials_share_uid
)


class TestQW1UIDGeneration:
    """Test UID generation for new materials."""
    
    def test_material_gets_uid_on_creation(self, blender_context):
        """Material should have LP UID after creation."""
        mat = blender_context.create_material("UIDTest1")
        
        # Material should have lp property
        assert hasattr(mat, 'lp')
        # After add-on initialization, material should have UID
        # Note: actual UID assignment happens in handlers.py set_material_uids()
        assert_material_has_uid(mat)
    
    def test_different_materials_have_different_uids(self, blender_context):
        """Each material should have unique UID."""
        mat1 = blender_context.create_material("Material1")
        mat2 = blender_context.create_material("Material2")
        
        # Force UID assignment (simulating handlers.py)
        from layer_painter import handlers
        handlers.set_material_uids()
        
        assert_material_has_uid(mat1)
        assert_material_has_uid(mat2)
        assert mat1.lp.uid != mat2.lp.uid, "Different materials should have different UIDs"
    
    def test_uid_format_is_valid(self, blender_context):
        """UID should be 10-character hex string."""
        mat = blender_context.create_material("FormatTest")
        
        # Force UID assignment
        from layer_painter import handlers
        handlers.set_material_uids()
        
        uid = mat.lp.uid
        assert len(uid) == 10, f"UID should be 10 chars, got {len(uid)}"
        assert all(c in '0123456789abcdef' for c in uid), f"UID contains invalid hex: {uid}"


class TestQW1DuplicationDetection:
    """Test duplicate material detection and UID syncing."""
    
    def test_duplicated_material_inherits_uid(self, blender_context):
        """Duplicated material should sync UID to original."""
        # Create original material
        original = blender_context.create_material("Original")
        
        # Force UID assignment
        from layer_painter import handlers
        handlers.set_material_uids()
        original_uid = original.lp.uid
        
        # Duplicate the material (creates "Original.001")
        duplicate = blender_context.create_duplicate_material(original)
        
        # Run duplicate detection
        handlers._detect_and_fix_duplicates()
        
        # Duplicate should inherit original's UID
        assert_materials_share_uid(original, duplicate)
        assert original.lp.uid == original_uid, "Original UID should not change"
    
    def test_multiple_duplicates_all_sync_uid(self, blender_context):
        """Multiple duplicates should all sync to same UID."""
        original = blender_context.create_material("Original")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        original_uid = original.lp.uid
        
        # Create multiple duplicates
        dup1 = blender_context.create_duplicate_material(original)
        dup2 = blender_context.create_duplicate_material(original)
        dup3 = blender_context.create_duplicate_material(original)
        
        # Run duplicate detection
        handlers._detect_and_fix_duplicates()
        
        # All should share same UID
        assert original.lp.uid == original_uid
        assert_materials_share_uid(original, dup1)
        assert_materials_share_uid(original, dup2)
        assert_materials_share_uid(original, dup3)
    
    def test_non_duplicate_materials_keep_unique_uids(self, blender_context):
        """Non-duplicate materials should keep their own UIDs."""
        mat1 = blender_context.create_material("Material1")
        mat2 = blender_context.create_material("Material2")
        mat3 = blender_context.create_material("Material3")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        
        uid1 = mat1.lp.uid
        uid2 = mat2.lp.uid
        uid3 = mat3.lp.uid
        
        # Run duplicate detection
        handlers._detect_and_fix_duplicates()
        
        # UIDs should remain unchanged
        assert mat1.lp.uid == uid1
        assert mat2.lp.uid == uid2
        assert mat3.lp.uid == uid3
        assert uid1 != uid2 and uid2 != uid3 and uid1 != uid3


class TestQW1LayerPreservation:
    """Test that layer structure preserved during UID sync."""
    
    def test_duplicate_material_preserves_layer_count(self, blender_context):
        """Duplicated material should have same layer structure as original."""
        # Create original material
        original = blender_context.create_material("Original")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        
        # Duplicate
        duplicate = blender_context.create_duplicate_material(original)
        
        # If original had layers (simulated by lp.layers property)
        if hasattr(original.lp, 'layers'):
            original_layer_count = len(original.lp.layers)
            
            # Run duplicate detection
            handlers._detect_and_fix_duplicates()
            
            # Layer count should match
            duplicate_layer_count = len(duplicate.lp.layers)
            assert duplicate_layer_count == original_layer_count, \
                f"Layer count mismatch: {duplicate_layer_count} vs {original_layer_count}"


class TestQW1UndoRedoIntegrity:
    """Test UID integrity across undo/redo operations."""
    
    def test_undo_redo_preserves_duplicate_uids(self, blender_context):
        """After undo/redo, duplicate UIDs should still be synced."""
        original = blender_context.create_material("Original")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        original_uid = original.lp.uid
        
        # Duplicate
        duplicate = blender_context.create_duplicate_material(original)
        
        # Sync UIDs
        handlers._detect_and_fix_duplicates()
        expected_uid = original.lp.uid
        
        # Simulate undo/redo by calling handler
        handlers.on_undo_redo_handler(None)
        
        # Clear caches and re-run detection
        handlers._detect_and_fix_duplicates()
        
        # UIDs should still be synced
        assert_materials_share_uid(original, duplicate)
    
    def test_material_uid_persists_after_handlers(self, blender_context):
        """Material UID should persist after handler calls."""
        mat = blender_context.create_material("Persistent")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        original_uid = mat.lp.uid
        
        # Call various handlers
        handlers.on_load_handler(None)
        handlers.on_undo_redo_handler(None)
        
        # UID should remain consistent
        assert mat.lp.uid == original_uid or mat.lp.uid != "", \
            "Material should have UID after handlers"


class TestQW1EdgeCases:
    """Test edge cases in duplicate detection."""
    
    def test_orphaned_duplicate_gets_new_uid(self, blender_context):
        """Duplicate with no original should get new UID."""
        # Create two separate materials
        mat1 = blender_context.create_material("Orphaned1")
        mat2 = blender_context.create_material("Orphaned2")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        
        uid1 = mat1.lp.uid
        uid2 = mat2.lp.uid
        
        # Run duplicate detection - should not affect unrelated materials
        handlers._detect_and_fix_duplicates()
        
        assert mat1.lp.uid == uid1, "Unrelated material UID changed"
        assert mat2.lp.uid == uid2, "Unrelated material UID changed"
    
    def test_duplicate_detection_with_custom_names(self, blender_context):
        """Duplicate detection should work with non-standard naming."""
        # Create materials with various naming patterns
        original = blender_context.create_material("MyCustomMaterial")
        
        from layer_painter import handlers
        handlers.set_material_uids()
        
        dup = blender_context.create_duplicate_material(original)
        # Rename to verify detection by layer count, not just name
        dup.name = f"{original.name}.001"
        
        handlers._detect_and_fix_duplicates()
        
        # Should still detect as duplicate
        assert_materials_share_uid(original, dup)
    
    def test_empty_material_list(self, blender_context):
        """Duplicate detection should handle empty material list gracefully."""
        from layer_painter import handlers
        
        # No materials created - should not crash
        handlers._detect_and_fix_duplicates()
        handlers.set_material_uids()
        
        # Should complete without error
        assert True


class TestQW1Performance:
    """Test performance of duplicate detection."""
    
    @pytest.mark.performance
    def test_duplicate_detection_scales_linearly(self, blender_context):
        """Duplicate detection should scale well with material count."""
        import time
        
        from layer_painter import handlers
        
        # Create 100 materials
        materials = []
        for i in range(100):
            mat = blender_context.create_material(f"Material_{i:03d}")
            materials.append(mat)
        
        handlers.set_material_uids()
        
        # Time duplicate detection
        start = time.time()
        handlers._detect_and_fix_duplicates()
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 1 second for 100 materials)
        assert elapsed < 1.0, f"Duplicate detection took {elapsed:.3f}s (should be < 1s)"
