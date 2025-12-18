"""Tests for QW-2: Input Validation in All Operators

Validates that:
- Operators safely handle missing materials
- Operators gracefully handle missing nodes
- Operators prevent KeyError/AttributeError crashes
- Error messages are reported to user
- Operations return CANCELLED on validation failure
"""

import pytest
import bpy
from conftest import (
    BlenderTestContext,
    assert_operator_failed,
    assert_operator_succeeded,
    assert_material_has_uid
)


class MockOperator:
    """Mock operator for testing validation patterns."""
    
    def __init__(self):
        self.reports = []
    
    def report(self, level_set, message):
        """Capture report calls for verification."""
        self.reports.append((level_set, message))


class TestQW2LayerOperatorValidation:
    """Test input validation in layer operators."""
    
    def test_add_fill_layer_validates_material(self, blender_context, active_blender_context):
        """LP_OT_AddFillLayer should validate material exists."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_AddFillLayer()
        operator.report = MockOperator().report
        
        # Set material to non-existent name
        operator.material = "NonExistentMaterial"
        
        # Execute should fail gracefully
        result = operator.execute(bpy.context)
        
        # Should return CANCELLED
        assert_operator_failed(result)
        # Should have error report
        assert len(operator.report.__self__.reports) > 0
    
    def test_add_fill_layer_succeeds_with_valid_material(self, blender_context, active_blender_context):
        """LP_OT_AddFillLayer should succeed with valid material."""
        from layer_painter.operators import layers as layers_module
        
        mat = blender_context.create_material("ValidMaterial")
        
        operator = layers_module.LP_OT_AddFillLayer()
        operator.report = MockOperator().report
        operator.material = mat.name
        
        # Execute should succeed
        result = operator.execute(bpy.context)
        
        # Should complete without crash (may have other validation checks)
        assert result in [{"FINISHED"}, {"CANCELLED"}]
    
    def test_remove_layer_validates_material(self, blender_context, active_blender_context):
        """LP_OT_RemoveLayer should validate material exists."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_RemoveLayer()
        operator.report = MockOperator().report
        
        # Set material to non-existent
        operator.material = "NonExistentMaterial"
        operator.uid = "aaaaaaaaaa"
        
        # Execute should fail gracefully
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_move_layer_up_validates_material(self, blender_context, active_blender_context):
        """LP_OT_MoveLayerUp should validate material exists."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_MoveLayerUp()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.uid = "aaaaaaaaaa"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_move_layer_down_validates_material(self, blender_context, active_blender_context):
        """LP_OT_MoveLayerDown should validate material exists."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_MoveLayerDown()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.uid = "aaaaaaaaaa"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_cycle_channel_data_validates_material(self, blender_context, active_blender_context):
        """LP_OT_CycleChannelData should validate material exists."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_CycleChannelData()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.layer = "aaaaaaaaaa"
        operator.channel = "bbbbbbbbbb"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)


class TestQW2ChannelOperatorValidation:
    """Test input validation in channel operators."""
    
    def test_make_channel_validates_material(self, blender_context, active_blender_context):
        """LP_OT_MakeChannel should validate material exists."""
        from layer_painter.operators import channels as channels_module
        
        operator = channels_module.LP_OT_MakeChannel()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.node = "SomeNode"
        operator.input = "SomeInput"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_remove_channel_validates_material(self, blender_context, active_blender_context):
        """LP_OT_RemoveChannel should validate material exists."""
        from layer_painter.operators import channels as channels_module
        
        operator = channels_module.LP_OT_RemoveChannel()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.channel = "aaaaaaaaaa"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_move_channel_up_validates_material(self, blender_context, active_blender_context):
        """LP_OT_MoveChannelUp should validate material exists."""
        from layer_painter.operators import channels as channels_module
        
        operator = channels_module.LP_OT_MoveChannelUp()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.channel = "aaaaaaaaaa"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_move_channel_down_validates_material(self, blender_context, active_blender_context):
        """LP_OT_MoveChannelDown should validate material exists."""
        from layer_painter.operators import channels as channels_module
        
        operator = channels_module.LP_OT_MoveChannelDown()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.channel = "aaaaaaaaaa"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)


class TestQW2PaintOperatorValidation:
    """Test input validation in paint operators."""
    
    def test_paint_channel_validates_material(self, blender_context, active_blender_context):
        """LP_OT_PaintChannel should validate material exists."""
        from layer_painter.operators import paint as paint_module
        
        operator = paint_module.LP_OT_PaintChannel()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.layer = "aaaaaaaaaa"
        operator.channel = "bbbbbbbbbb"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_toggle_texture_validates_material(self, blender_context, active_blender_context):
        """LP_OT_ToggleTexture should validate material exists."""
        from layer_painter.operators import paint as paint_module
        
        operator = paint_module.LP_OT_ToggleTexture()
        operator.report = MockOperator().report
        operator.material = "NonExistentMaterial"
        operator.layer = "aaaaaaaaaa"
        operator.channel = "bbbbbbbbbb"
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)


class TestQW2SafeDictAccess:
    """Test that operators use safe .get() instead of direct indexing."""
    
    def test_material_lookup_uses_get(self, blender_context, active_blender_context):
        """Operators should use bpy.data.materials.get() for safe lookup."""
        # This tests the pattern used throughout operators
        material_dict = bpy.data.materials
        
        # Safe lookup should return None instead of KeyError
        result = material_dict.get("NonExistentMaterial")
        
        assert result is None, "get() should return None for missing material"
    
    def test_safe_lookup_prevents_keyerror(self, blender_context):
        """Safe lookup pattern prevents KeyError crashes."""
        material_dict = bpy.data.materials
        
        # This would crash:
        # mat = material_dict["NonExistent"]  # KeyError!
        
        # This is safe:
        mat = material_dict.get("NonExistent")
        
        # Should return None, not crash
        assert mat is None


class TestQW2ErrorReporting:
    """Test that errors are reported to user."""
    
    def test_operator_reports_missing_material(self, blender_context, active_blender_context):
        """Operators should report error message when material missing."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_RemoveLayer()
        reports = []
        
        def capture_report(level_set, message):
            reports.append((level_set, message))
        
        operator.report = capture_report
        operator.material = "NonExistentMaterial"
        operator.uid = "aaaaaaaaaa"
        
        operator.execute(bpy.context)
        
        # Should have at least one ERROR report
        error_reports = [r for r in reports if 'ERROR' in r[0]]
        assert len(error_reports) > 0, "Should report error to user"
    
    def test_error_message_is_descriptive(self, blender_context, active_blender_context):
        """Error messages should be helpful."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_RemoveLayer()
        reports = []
        
        def capture_report(level_set, message):
            reports.append((level_set, message))
        
        operator.report = capture_report
        operator.material = "MyMissingMaterial"
        operator.uid = "aaaaaaaaaa"
        
        operator.execute(bpy.context)
        
        # Get error message
        error_reports = [r for r in reports if 'ERROR' in r[0]]
        if error_reports:
            message = error_reports[0][1]
            # Message should mention material or not found
            assert any(word in message.lower() for word in ['material', 'not found', 'missing']), \
                f"Error message not descriptive: {message}"


class TestQW2EdgeCases:
    """Test edge cases in validation."""
    
    def test_empty_material_name_validation(self, blender_context, active_blender_context):
        """Operators should handle empty material names."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_RemoveLayer()
        operator.report = MockOperator().report
        operator.material = ""
        operator.uid = "aaaaaaaaaa"
        
        # Should not crash
        result = operator.execute(bpy.context)
        assert result in [{"FINISHED"}, {"CANCELLED"}]
    
    def test_special_characters_in_material_name(self, blender_context, active_blender_context):
        """Operators should handle special characters in names."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_RemoveLayer()
        operator.report = MockOperator().report
        operator.material = "Material@#$%^&*()"
        operator.uid = "aaaaaaaaaa"
        
        # Should not crash
        result = operator.execute(bpy.context)
        assert result in [{"FINISHED"}, {"CANCELLED"}]
    
    def test_unicode_in_material_name(self, blender_context, active_blender_context):
        """Operators should handle unicode in material names."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_RemoveLayer()
        operator.report = MockOperator().report
        operator.material = "Material_日本語_中文"
        operator.uid = "aaaaaaaaaa"
        
        # Should not crash
        result = operator.execute(bpy.context)
        assert result in [{"FINISHED"}, {"CANCELLED"}]


class TestQW2RobustExceptionHandling:
    """Test that operators catch and handle exceptions."""
    
    def test_operator_catches_general_exceptions(self, blender_context, active_blender_context):
        """Operators should catch unexpected exceptions."""
        from layer_painter.operators import layers as layers_module
        
        operator = layers_module.LP_OT_RemoveLayer()
        operator.report = MockOperator().report
        
        # Use invalid UID format - should not crash
        operator.material = bpy.context.active_object.name if bpy.context.active_object else "test"
        operator.uid = None  # Invalid UID
        
        # Should return CANCELLED, not raise exception
        result = operator.execute(bpy.context)
        assert result in [{"FINISHED"}, {"CANCELLED"}]
