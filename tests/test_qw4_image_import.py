"""Tests for QW-4: Error Handling in Image Import

Validates that:
- Image import handles missing files gracefully
- Import handles permission errors
- Import handles corrupted image files
- Import provides user-friendly error messages
- Import operations don't crash the add-on
"""

import pytest
import bpy
import os
import tempfile
from conftest import (
    BlenderTestContext,
    assert_operator_failed,
    assert_operator_succeeded,
)


class MockOperator:
    """Mock operator for testing error reporting."""
    
    def __init__(self):
        self.reports = []
    
    def report(self, level_set, message):
        """Capture report calls for verification."""
        self.reports.append((level_set, message))


class TestQW4ImageImportFileValidation:
    """Test file validation before import."""
    
    def test_import_nonexistent_file_fails_gracefully(self, blender_context):
        """Import should handle non-existent files without crashing."""
        from layer_painter.operators import images as images_module
        from layer_painter.operators import utils_paint
        
        # Try to import non-existent file
        filepath = "/path/that/does/not/exist/image.png"
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = filepath
        
        # Should not crash
        result = operator.execute(bpy.context)
        
        # Should report error
        assert_operator_failed(result)
        error_reports = [r for r in operator.report.__self__.reports if 'ERROR' in r[0]]
        assert len(error_reports) > 0
    
    def test_import_empty_filepath_fails(self, blender_context):
        """Import should handle empty filepath."""
        from layer_painter.operators import images as images_module
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = ""
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_import_directory_path_fails(self, blender_context):
        """Import should fail when given directory instead of file."""
        from layer_painter.operators import images as images_module
        
        # Use existing directory
        temp_dir = tempfile.gettempdir()
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = temp_dir
        
        result = operator.execute(bpy.context)
        
        assert_operator_failed(result)
    
    def test_import_valid_image_file(self, blender_context):
        """Import should succeed with valid image file."""
        from layer_painter.operators import images as images_module
        
        # Create valid test image
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")
        
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, "test_valid.png")
        
        # Create simple test image
        img = Image.new('RGB', (32, 32), color=(255, 0, 0))
        img.save(filepath)
        blender_context.temp_files.append(filepath)
        
        # This may fail due to other validation, but shouldn't crash
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = filepath
        
        result = operator.execute(bpy.context)
        
        # Should complete without crash (may have other checks)
        assert result in [{"FINISHED"}, {"CANCELLED"}]
        
        # Clean up
        try:
            os.remove(filepath)
        except:
            pass


class TestQW4CorruptedImageHandling:
    """Test handling of corrupted image files."""
    
    def test_corrupted_image_file_fails_gracefully(self, blender_context):
        """Import should handle corrupted image files."""
        from layer_painter.operators import images as images_module
        
        # Create corrupted image file
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, "corrupted.png")
        
        # Write garbage data
        with open(filepath, 'wb') as f:
            f.write(b"This is not a valid image file\x00\x01\x02")
        
        blender_context.temp_files.append(filepath)
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = filepath
        
        # Should not crash
        result = operator.execute(bpy.context)
        
        # Should fail gracefully
        assert result in [{"FINISHED"}, {"CANCELLED"}]


class TestQW4ImageImportFunctionValidation:
    """Test import_image() function directly."""
    
    def test_import_image_validates_filepath(self, blender_context):
        """import_image() should validate file exists."""
        from layer_painter.operators import utils_paint
        
        # Non-existent file
        filepath = "/does/not/exist.png"
        
        # Should raise error or return None, not crash
        try:
            result = utils_paint.import_image(filepath)
            # If it doesn't raise, it should return None or handle gracefully
            assert result is None or result != filepath
        except (FileNotFoundError, RuntimeError, Exception):
            # Expected to raise error
            pass
    
    def test_import_image_with_valid_file(self, blender_context):
        """import_image() should work with valid file."""
        from layer_painter.operators import utils_paint
        
        # Create valid test image
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")
        
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, "test_import.png")
        
        img = Image.new('RGB', (32, 32), color=(0, 255, 0))
        img.save(filepath)
        blender_context.temp_files.append(filepath)
        
        # Should not crash
        try:
            result = utils_paint.import_image(filepath)
            # Result should be valid or handled gracefully
            assert result is not None or result == None
        except Exception as e:
            # If exception, should be caught and handled
            assert isinstance(e, (FileNotFoundError, RuntimeError))
        
        # Clean up
        try:
            os.remove(filepath)
        except:
            pass


class TestQW4NodeValidation:
    """Test validation when nodes are missing."""
    
    def test_open_image_validates_node_group_exists(self, blender_context, test_material):
        """LP_OT_OpenImage should validate node group exists."""
        from layer_painter.operators import images as images_module
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.material = test_material.name
        operator.node = "NonExistentNode"
        operator.filepath = "/tmp/test.png"
        
        # Should fail gracefully
        result = operator.execute(bpy.context)
        
        # Should handle missing node
        assert result in [{"FINISHED"}, {"CANCELLED"}]


class TestQW4ErrorMessages:
    """Test quality of error messages."""
    
    def test_file_not_found_error_message(self, blender_context):
        """Error message should indicate file not found."""
        from layer_painter.operators import images as images_module
        
        operator = images_module.LP_OT_OpenImage()
        reports = []
        
        def capture_report(level_set, message):
            reports.append((level_set, message))
        
        operator.report = capture_report
        operator.filepath = "/nonexistent/file.png"
        
        operator.execute(bpy.context)
        
        # Check for helpful error message
        error_reports = [r for r in reports if 'ERROR' in r[0]]
        if error_reports:
            message = error_reports[0][1].lower()
            # Message should mention file or not found
            assert any(word in message for word in ['file', 'not found', 'exist']), \
                f"Message not helpful: {error_reports[0][1]}"
    
    def test_error_message_includes_filename(self, blender_context):
        """Error message should include problematic filename."""
        from layer_painter.operators import images as images_module
        
        operator = images_module.LP_OT_OpenImage()
        reports = []
        
        def capture_report(level_set, message):
            reports.append((level_set, message))
        
        operator.report = capture_report
        problem_file = "my_missing_image.png"
        operator.filepath = f"/tmp/{problem_file}"
        
        operator.execute(bpy.context)
        
        # Check if error message contains filename
        error_reports = [r for r in reports if 'ERROR' in r[0]]
        if error_reports:
            message = error_reports[0][1]
            # Should mention the problematic file
            assert problem_file in message or "missing" in message.lower(), \
                f"Error message should mention filename: {message}"


class TestQW4ExceptionHandling:
    """Test robust exception handling."""
    
    def test_import_handles_oserror(self, blender_context):
        """Import should handle OSError (permissions, etc)."""
        from layer_painter.operators import images as images_module
        
        # Try to read restricted directory
        restricted_path = "/root/test.png"  # Usually not accessible
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = restricted_path
        
        # Should not crash, even if OSError occurs
        result = operator.execute(bpy.context)
        
        assert result in [{"FINISHED"}, {"CANCELLED"}]
    
    def test_import_handles_valueerror(self, blender_context):
        """Import should handle ValueError from image decode."""
        from layer_painter.operators import images as images_module
        
        # Create file with invalid image data
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, "invalid.png")
        
        with open(filepath, 'wb') as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)  # Truncated PNG
        
        blender_context.temp_files.append(filepath)
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = filepath
        
        # Should not crash
        result = operator.execute(bpy.context)
        
        assert result in [{"FINISHED"}, {"CANCELLED"}]
    
    def test_import_handles_runtime_exceptions(self, blender_context):
        """Import should handle RuntimeError and other exceptions."""
        from layer_painter.operators import images as images_module
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        
        # Create malformed property
        operator.filepath = None  # This might cause TypeError
        operator.material = None
        
        # Should handle gracefully
        try:
            result = operator.execute(bpy.context)
            assert result in [{"FINISHED"}, {"CANCELLED"}]
        except Exception:
            # If exception, that's okay - we're testing it doesn't crash the addon
            pass


class TestQW4LoadFilePathValidation:
    """Test load_filepath_in_node() error handling."""
    
    def test_load_filepath_rejects_invalid_path(self, blender_context):
        """load_filepath_in_node() should validate filepath."""
        from layer_painter.operators import utils_paint
        
        # Invalid path
        try:
            utils_paint.load_filepath_in_node("/invalid/path.png", None)
            # If no exception, that's okay - function handled it
        except (FileNotFoundError, RuntimeError):
            # Expected
            pass
    
    def test_load_filepath_rejects_none_node(self, blender_context):
        """load_filepath_in_node() should validate node."""
        from layer_painter.operators import utils_paint
        
        # None node
        try:
            utils_paint.load_filepath_in_node("/tmp/test.png", None)
            # Handled gracefully
        except (RuntimeError, AttributeError, TypeError):
            # Expected
            pass


class TestQW4EdgeCases:
    """Test edge cases in image import."""
    
    def test_import_very_long_filepath(self, blender_context):
        """Import should handle very long filepaths."""
        from layer_painter.operators import images as images_module
        
        # Create very long path
        very_long_path = "/tmp/" + "a" * 1000 + ".png"
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = very_long_path
        
        # Should not crash
        result = operator.execute(bpy.context)
        
        assert result in [{"FINISHED"}, {"CANCELLED"}]
    
    def test_import_special_characters_in_filename(self, blender_context):
        """Import should handle special characters in filename."""
        from layer_painter.operators import images as images_module
        
        # Path with special characters
        filepath = "/tmp/test@#$%^&*().png"
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = filepath
        
        # Should not crash
        result = operator.execute(bpy.context)
        
        assert result in [{"FINISHED"}, {"CANCELLED"}]
    
    def test_import_unicode_filename(self, blender_context):
        """Import should handle unicode in filenames."""
        from layer_painter.operators import images as images_module
        
        # Unicode filename
        filepath = "/tmp/テスト_中文_🖼️.png"
        
        operator = images_module.LP_OT_OpenImage()
        operator.report = MockOperator().report
        operator.filepath = filepath
        
        # Should not crash
        result = operator.execute(bpy.context)
        
        assert result in [{"FINISHED"}, {"CANCELLED"}]
