import bpy
from bpy.app.handlers import persistent
import atexit

from .utils import make_uid
from .data.materials.channels import channel
from .data.materials.layers import layer
from .operators.assets import load_assets

# Import logging
try:
    from .logging import get_logger, LogContext, log_cache_clear
    logger = get_logger("handlers")
    logging_available = True
except ImportError:
    logging_available = False
    logger = None


def _detect_and_fix_duplicates():
    """Detects and fixes material UID duplicates caused by material duplication.
    When a material is duplicated in Blender, the new material inherits no properties.
    This function identifies duplicates by name similarity and syncs UIDs.
    """
    if logger:
        logger.debug("Checking for material UID duplicates")
    
    duplicate_count = 0
    new_uid_count = 0
    
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
                        if logger:
                            logger.debug(f"Assigned UID {mat.lp.uid} to duplicate material '{mat.name}'")
                        duplicate_count += 1
                        break
            
            # If still no UID, generate new one
            if not mat.lp.uid:
                mat.lp.uid = make_uid()
                if logger:
                    logger.debug(f"Generated new UID {mat.lp.uid} for material '{mat.name}'")
                new_uid_count += 1
    
    if logger and (duplicate_count > 0 or new_uid_count > 0):
        logger.info(f"UID initialization: {duplicate_count} duplicates synced, {new_uid_count} new UIDs generated")


def set_material_uids():
    """Assigns UIDs to materials without them. Fixed to handle duplicates."""
    _detect_and_fix_duplicates()


@persistent
def on_load_handler(dummy):
    """Runs when a blender file is loaded"""
    if logger:
        logger.info("=" * 60)
        logger.info("File loaded: clearing all caches and initializing UIDs")
        logger.debug(f"Materials in file: {len(bpy.data.materials)}")
    
    # Clear caches
    channel.clear_caches()
    if logger:
        log_cache_clear("channel")
    
    layer.clear_caches()
    if logger:
        log_cache_clear("layer")
    
    # Initialize UIDs
    set_material_uids()
    
    # Load assets
    try:
        load_assets(bpy.context)
        if logger:
            logger.debug("Assets loaded successfully")
    except Exception as e:
        if logger:
            logger.error(f"Failed to load assets: {e}")
    
    if logger:
        logger.info("=" * 60)


@persistent
def pre_save_handler(dummy):
    """Runs before a blender file is saved"""
    if logger:
        logger.debug(f"Saving file: {len(bpy.data.materials)} materials in scene")


@persistent
def depsgraph_handler(dummy):
    """Runs after the depsgraph is updated.
    NOTE: Disabled high-frequency UID sync to prevent performance issues (was causing 60+x/sec calls).
    UID assignment now handled in on_load_handler() and on_undo_redo_handler().
    """
    pass  # Previously called set_material_uids() causing lag


def on_exit_handler():
    """Runs before blender is closed"""
    if logger:
        logger.info("Closing Blender: finalizing Layer Painter")


@persistent
def on_undo_redo_handler(dummy):
    """Clears caches after undo/redo operations to prevent inconsistent state"""
    if logger:
        logger.debug("Undo/Redo detected: clearing all caches")
    
    channel.clear_caches()
    if logger:
        log_cache_clear("channel")
    
    layer.clear_caches()
    if logger:
        log_cache_clear("layer")
    
    # Re-initialize UIDs after undo/redo
    set_material_uids()


def register():
    """Register all event handlers"""
    if logger:
        logger.info("Registering Layer Painter event handlers")
    
    bpy.app.handlers.load_post.append(on_load_handler)
    bpy.app.handlers.save_pre.append(pre_save_handler)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)
    bpy.app.handlers.undo_post.append(on_undo_redo_handler)
    bpy.app.handlers.redo_post.append(on_undo_redo_handler)
    atexit.register(on_exit_handler)


def unregister():
    """Unregister all event handlers"""
    if logger:
        logger.info("Unregistering Layer Painter event handlers")
    
    bpy.app.handlers.undo_post.remove(on_undo_redo_handler)
    bpy.app.handlers.redo_post.remove(on_undo_redo_handler)
    if depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)
    bpy.app.handlers.load_post.remove(on_load_handler)
    bpy.app.handlers.save_pre.remove(pre_save_handler)
    atexit.unregister(on_exit_handler)
