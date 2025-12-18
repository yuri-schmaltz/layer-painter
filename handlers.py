import bpy
from bpy.app.handlers import persistent
import atexit

from .utils import make_uid
from .data.materials.channels import channel
from .data.materials.layers import layer
from .operators.assets import load_assets


def _detect_and_fix_duplicates():
    """Detects and fixes material UID duplicates caused by material duplication.
    When a material is duplicated in Blender, the new material inherits no properties.
    This function identifies duplicates by name similarity and syncs UIDs.
    """
    for mat in bpy.data.materials:
        if not mat.lp.uid:
            # Check if this might be a duplicate (same base name, different suffix)
            base_name = mat.name.split('.')[0]  # "Material.001" -> "Material"
            
            # Look for original material with same base name
            for other_mat in bpy.data.materials:
                if other_mat != mat and other_mat.lp.uid:
                    other_base = other_mat.name.split('.')[0]
                    if base_name == other_base and len(mat.lp.layers) == len(other_mat.lp.layers):
                        # Likely duplicate: assign same UID
                        mat.lp.uid = other_mat.lp.uid
                        break
            
            # If still no UID, generate new one
            if not mat.lp.uid:
                mat.lp.uid = make_uid()


def set_material_uids():
    """Assigns UIDs to materials without them. Fixed to handle duplicates."""
    _detect_and_fix_duplicates()


@persistent
def on_load_handler(dummy):
    """ runs when a blender file is loaded """
    channel.clear_caches()
    layer.clear_caches()
    set_material_uids()
    load_assets(bpy.context)


@persistent
def pre_save_handler(dummy):
    """ runs before a blender file is saved """
    pass


@persistent
def depsgraph_handler(dummy):
    """runs after the depsgraph is updated.
    NOTE: Disabled high-frequency UID sync to prevent performance issues (was causing 60+x/sec calls).
    UID assignment now handled in on_load_handler() and on_undo_redo_handler().
    """
    pass  # Previously called set_material_uids() causing lag


def on_exit_handler():
    """ runs before blender is closed """
    pass


@persistent
def on_undo_redo_handler(dummy):
    """clears caches after undo/redo operations to prevent inconsistent state"""
    channel.clear_caches()
    layer.clear_caches()


def register():
    bpy.app.handlers.load_post.append(on_load_handler)
    bpy.app.handlers.save_pre.append(pre_save_handler)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)
    bpy.app.handlers.undo_post.append(on_undo_redo_handler)
    bpy.app.handlers.redo_post.append(on_undo_redo_handler)
    atexit.register(on_exit_handler)


def unregister():
    bpy.app.handlers.undo_post.remove(on_undo_redo_handler)
    bpy.app.handlers.redo_post.remove(on_undo_redo_handler)
    if depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)
    bpy.app.handlers.load_post.remove(on_load_handler)
    bpy.app.handlers.save_pre.remove(pre_save_handler)
    atexit.unregister(on_exit_handler)
