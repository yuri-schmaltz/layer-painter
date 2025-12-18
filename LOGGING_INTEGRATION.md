"""
Layer Painter Logging Integration Examples

This file shows how to integrate logging into operators and utility functions.
Copy patterns from here to add logging to existing code.

Key Integration Points:
1. @log_operation() decorator for operators
2. LogContext context manager for complex operations
3. Direct logger calls for specific events
4. Performance decorators for slow operations
"""

# ============================================================================
# Example 1: Operator with Logging Decorator
# ============================================================================

"""
In operators/layers.py:

from layer_painter.logging import log_operation, get_logger

logger = get_logger("layers")

class LP_OT_CreateLayer(bpy.types.Operator):
    '''Create a new layer'''
    bl_idname = 'lp.create_layer'
    bl_label = 'Create Layer'
    
    layer_type: bpy.props.EnumProperty(
        items=[('FILL', 'Fill', ''), ('PAINT', 'Paint', '')])
    
    @log_operation("create_layer")  # ← Automatic logging with metrics
    def execute(self, context):
        # Function body
        logger.info(f"Creating {self.layer_type} layer")
        # ... layer creation code ...
        return {'FINISHED'}
"""


# ============================================================================
# Example 2: Context Manager for Multi-Step Operations
# ============================================================================

"""
In operators/baking.py:

from layer_painter.logging import LogContext, get_logger

logger = get_logger("baking")

class LP_OT_BakeAllChannels(bpy.types.Operator):
    '''Bake all channels to textures'''
    bl_idname = 'lp.bake_all'
    bl_label = 'Bake All Channels'
    
    def execute(self, context):
        with LogContext("bake_all_channels", logger) as ctx:
            # Setup phase
            ctx.log("Setting up bake nodes")
            setup_bake_nodes(context)
            
            # Bake phase
            ctx.log("Starting render bake")
            bpy.ops.render.render(write_still=False)
            
            # Cleanup phase
            ctx.log("Cleaning up bake nodes and saving images")
            cleanup_bake_nodes(context)
            
            return {'FINISHED'}
        # LogContext automatically logs duration and any errors
"""


# ============================================================================
# Example 3: Direct Logger Calls
# ============================================================================

"""
In operators/paint.py:

from layer_painter.logging import get_logger

logger = get_logger("paint")

class LP_OT_PaintChannel(bpy.types.Operator):
    '''Paint on texture channel'''
    bl_idname = 'lp.paint_channel'
    bl_label = 'Paint Channel'
    
    layer_uid: bpy.props.StringProperty()
    channel_uid: bpy.props.StringProperty()
    resolution: bpy.props.IntProperty(default=2048)
    
    def invoke(self, context, event):
        logger.debug(f"Paint invoke: layer={self.layer_uid}, channel={self.channel_uid}")
        
        if self.resolution == 0:
            logger.warning("Resolution not set, showing dialog")
            return context.window_manager.invoke_props_dialog(self)
        
        return self.execute(context)
    
    def execute(self, context):
        try:
            logger.info(f"Starting paint session on channel {self.channel_uid}")
            
            # Create image
            logger.debug(f"Creating {self.resolution}x{self.resolution} image")
            img = create_image("texture", self.resolution, (1,1,1,1))
            logger.debug(f"Image created: {img.name}")
            
            # Switch to paint mode
            logger.debug("Switching to texture paint mode")
            switch_to_paint_mode(img)
            
            logger.info("Paint session started successfully")
            return {'FINISHED'}
        
        except Exception as e:
            logger.error(f"Paint failed: {e}", exc_info=True)
            return {'CANCELLED'}
"""


# ============================================================================
# Example 4: Performance Logging
# ============================================================================

"""
In data/utils_nodes.py:

from layer_painter.logging import log_performance, get_logger

logger = get_logger("nodes")

@log_performance(threshold_ms=500)  # Warn if takes > 500ms
def organize_tree_layout(ntree, start_node, spacing=400):
    '''Organize shader node layout - warns if slow'''
    logger.debug(f"Organizing {len(ntree.nodes)} nodes")
    
    # ... layout organization code ...
    
    logger.debug(f"Layout organized: {len(positioned_nodes)} nodes positioned")
"""


# ============================================================================
# Example 5: Cache Operation Logging
# ============================================================================

"""
In data/materials/layers/layer.py:

from layer_painter.logging import log_cache_operation, log_cache_clear, get_logger

logger = get_logger("layer")

_cached_nodes = {}

@log_cache_operation("layer_nodes")  # Automatic cache hit/miss logging
def get_layer_node(layer_uid):
    '''Get layer node with caching and logging'''
    # Cache lookup
    if layer_uid in _cached_nodes:
        return _cached_nodes[layer_uid]
    
    # Search and cache
    for node in bpy.data.node_groups:
        if hasattr(node, 'uid') and node.uid == layer_uid:
            _cached_nodes[layer_uid] = node
            return node
    
    return None

def clear_caches():
    '''Clear layer cache and log'''
    global _cached_nodes
    old_size = len(_cached_nodes)
    _cached_nodes.clear()
    log_cache_clear("layer_nodes", old_size)
"""


# ============================================================================
# Example 6: Detailed State Tracking
# ============================================================================

"""
In operators/paint.py:

from layer_painter.logging import get_logger, record_metric

logger = get_logger("paint")

def save_painted_texture(image, output_path):
    '''Save texture with detailed logging'''
    start_time = time.time()
    
    try:
        logger.debug(f"Saving image {image.name} to {output_path}")
        
        # Validation
        if not image.has_data:
            logger.error(f"Image {image.name} has no pixel data")
            raise ValueError("Image has no data")
        
        if len(output_path) == 0:
            logger.error("Output path is empty")
            raise ValueError("Output path required")
        
        # Save
        logger.debug(f"Writing {image.size_x}x{image.size_y} to disk")
        image.save_render(output_path)
        
        # Verify
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            duration = time.time() - start_time
            logger.info(f"Saved {image.name}: {file_size/1024:.1f}KB in {duration:.2f}s")
            record_metric("save_texture", duration, success=True)
        else:
            logger.error(f"File not created at {output_path}")
            raise IOError("File save failed")
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Save failed after {duration:.2f}s: {e}")
        record_metric("save_texture", duration, success=False, error=str(e))
        raise
"""


# ============================================================================
# Example 7: Error Context Logging
# ============================================================================

"""
In operators/utils_operator.py:

from layer_painter.logging import get_logger, get_error_log

logger = get_logger("operator")

def safe_get_material(mat_uid):
    '''Safe material lookup with error context'''
    try:
        mat = next((m for m in bpy.data.materials if m.lp.uid == mat_uid), None)
        if not mat:
            logger.error(f"Material not found: uid={mat_uid}")
            raise RuntimeError(f"Material UID {mat_uid} not found")
        return mat
    
    except Exception as e:
        # Record with context for debugging
        context_info = {
            'material_uid': mat_uid,
            'available_materials': len(bpy.data.materials),
            'initialized_materials': sum(1 for m in bpy.data.materials if m.lp.uid)
        }
        get_error_log().record_error(e, context_info)
        logger.error(f"Material lookup failed with context: {context_info}")
        raise
"""


# ============================================================================
# Example 8: Using Logging in UI Panels
# ============================================================================

"""
In ui/viewport/layers/panel_layers.py:

from layer_painter.logging import get_logger, log_ui_event

logger = get_logger("ui_layers")

class LP_PT_LayersPanel(bpy.types.Panel):
    '''Layer Painter Layers Panel'''
    bl_label = "Layers"
    bl_idname = "LP_PT_LAYERS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Layer Painter'
    
    def draw(self, context):
        layout = self.layout
        
        # Log panel draw
        log_ui_event("layers_panel_draw", {
            'materials': len(bpy.data.materials),
            'visible': True
        })
        
        # Draw buttons
        row = layout.row()
        if row.operator("lp.create_layer"):
            log_ui_event("button_create_layer_clicked")
"""


# ============================================================================
# Example 9: Metrics Integration
# ============================================================================

"""
In preferences/main.py:

from layer_painter.logging import generate_debug_report, save_debug_report

class LP_OT_ExportDebugReport(bpy.types.Operator):
    '''Export Layer Painter debug report'''
    bl_idname = 'lp.export_debug_report'
    bl_label = 'Export Debug Report'
    
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Where to save debug report",
        subtype='FILE_PATH'
    )
    
    def execute(self, context):
        try:
            save_debug_report(self.filepath)
            self.report({'INFO'}, f"Debug report saved to {self.filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export report: {e}")
            return {'CANCELLED'}
"""


# ============================================================================
# Usage Guide: Integration Checklist
# ============================================================================

"""
When adding logging to a module:

1. Import logging at top:
   from layer_painter.logging import (
       get_logger, log_operation, LogContext, 
       log_cache_clear, record_metric
   )
   
   logger = get_logger("module_name")

2. For operators, use @log_operation() decorator:
   @log_operation("operation_name")
   def execute(self, context):
       # Automatically logs start, completion, duration, and errors

3. For multi-step operations, use LogContext:
   with LogContext("operation_name") as ctx:
       ctx.log("Step 1 complete")
       # Automatically logs start, completion, duration

4. For cache operations, use log_cache_clear():
   _cache.clear()
   log_cache_clear("cache_name", len(_cache))

5. For metrics, use record_metric():
   duration = time.time() - start
   record_metric("operation", duration, success=True)

6. View logs:
   # During development: Check Blender system console
   # For reports: Export via "Export Debug Report" operator

7. Performance tuning:
   # Run generate_debug_report() to get timing statistics
   # Identify slow operations (avg_time, max_time)
   # Add @log_performance() decorator to slow functions
"""


# ============================================================================
# Accessing Logs Programmatically
# ============================================================================

"""
# Get logger for any module
logger = get_logger("module_name")

# Log at different levels
logger.debug("Detailed debug info")      # Only visible when log_level=DEBUG
logger.info("Important information")     # Always visible
logger.warning("Warning message")        # Visible at WARNING level
logger.error("Error occurred")          # Always visible

# Get metrics
from layer_painter.logging import get_metrics

metrics = get_metrics()
stats = metrics.get_all_stats()
print(stats)  # {"operation_name": {"count": 5, "avg_time": 0.123, ...}}

# Get error log
from layer_painter.logging import get_error_log

errors = get_error_log()
recent = errors.get_recent_errors(5)
summary = errors.get_error_summary()  # {"RuntimeError": 2, "ValueError": 1}

# Generate reports
from layer_painter.logging import generate_debug_report, save_debug_report

report = generate_debug_report()  # Get as string
save_debug_report("debug_report.txt")  # Save to file
"""
