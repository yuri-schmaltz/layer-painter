"""Shared test fixtures and utilities for Blender add-on testing.

Provides:
- Blender context management (scene, materials, objects)
- UID generation for testing
- Assertion helpers
"""

import bpy
import pytest
import os
import tempfile
from typing import Optional


class BlenderTestContext:
    """Helper class to manage Blender test state."""
    
    def __init__(self):
        """Initialize test context with clean Blender scene."""
        self.materials_created = []
        self.objects_created = []
        self.temp_files = []
    
    def create_material(self, name: str = "TestMaterial") -> bpy.types.Material:
        """Create a test material and track it for cleanup."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        self.materials_created.append(mat)
        return mat
    
    def create_mesh_object(self, name: str = "TestObject") -> bpy.types.Object:
        """Create a test mesh object and track it for cleanup."""
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        self.objects_created.append(obj)
        return obj
    
    def create_temp_image_file(self, name: str = "test.png", color=(1, 1, 1, 1)) -> str:
        """Create a temporary test image file."""
        try:
            import numpy as np
            from PIL import Image
        except ImportError:
            pytest.skip("PIL/numpy not available for image creation")
        
        # Create simple test image
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, name)
        
        # Create RGB image (3 channels)
        if len(color) == 4:
            color_rgb = tuple(int(c * 255) for c in color[:3])
        else:
            color_rgb = tuple(int(c * 255) for c in color)
        
        img = Image.new('RGB', (32, 32), color_rgb)
        img.save(filepath)
        
        self.temp_files.append(filepath)
        return filepath
    
    def create_duplicate_material(self, original: bpy.types.Material) -> bpy.types.Material:
        """Duplicate a material for testing UID sync."""
        # Use Blender's built-in duplication
        duplicate = original.copy()
        self.materials_created.append(duplicate)
        return duplicate
    
    def add_layer_to_material(self, mat: bpy.types.Material) -> 'Layer':
        """Add a test layer to material (if lp property exists)."""
        if hasattr(mat, 'lp') and hasattr(mat.lp, 'add_layer'):
            # This would be tested via actual operators
            pass
        return mat
    
    def cleanup(self):
        """Clean up all created test resources."""
        # Remove objects
        for obj in self.objects_created:
            if obj and obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        
        # Remove materials
        for mat in self.materials_created:
            if mat and mat.name in bpy.data.materials:
                bpy.data.materials.remove(mat, do_unlink=True)
        
        # Clean up temp files
        for filepath in self.temp_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except OSError:
                pass


@pytest.fixture
def blender_context():
    """Fixture providing clean Blender test context."""
    ctx = BlenderTestContext()
    yield ctx
    ctx.cleanup()


@pytest.fixture
def test_material(blender_context):
    """Fixture providing a test material with nodes enabled."""
    return blender_context.create_material("LP_TestMaterial")


@pytest.fixture
def test_mesh_object(blender_context, test_material):
    """Fixture providing a test mesh object with material."""
    obj = blender_context.create_mesh_object("LP_TestObject")
    if len(obj.data.materials) == 0:
        obj.data.materials.append(test_material)
    return obj


@pytest.fixture
def active_blender_context(test_mesh_object):
    """Fixture ensuring test object is active."""
    bpy.context.view_layer.objects.active = test_mesh_object
    test_mesh_object.select_set(True)
    return test_mesh_object


def assert_material_has_uid(material: bpy.types.Material) -> bool:
    """Assert that material has valid LP UID."""
    assert hasattr(material, 'lp'), f"Material {material.name} missing lp property"
    assert hasattr(material.lp, 'uid'), f"Material {material.name} lp missing uid"
    assert material.lp.uid, f"Material {material.name} uid is empty"
    assert len(material.lp.uid) == 10, f"Material {material.name} uid invalid length: {len(material.lp.uid)}"
    return True


def assert_materials_share_uid(mat1: bpy.types.Material, mat2: bpy.types.Material):
    """Assert that duplicate materials have synced UIDs."""
    assert mat1.lp.uid == mat2.lp.uid, \
        f"Materials {mat1.name} and {mat2.name} UIDs don't match: {mat1.lp.uid} vs {mat2.lp.uid}"


def assert_operator_failed(result: dict):
    """Assert operator returned CANCELLED."""
    assert result == {"CANCELLED"}, f"Expected CANCELLED, got {result}"


def assert_operator_succeeded(result: dict):
    """Assert operator returned FINISHED."""
    assert result == {"FINISHED"}, f"Expected FINISHED, got {result}"
