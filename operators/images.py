import bpy
from bpy_extras.io_utils import ImportHelper
import os

from . import utils_paint
from .. import utils, constants
from ..operators import utils_operator
from ..data.materials.layers.layer_types import layer_fill


def import_image(filepath):
    """Opens image from given path and saves it in folder next to blend file.
    
    Args:
        filepath: Path to image file to import.
    
    Returns:
        Loaded and saved image object.
    
    Raises:
        FileNotFoundError: If image file doesn't exist.
        RuntimeError: If image load or save fails.
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Image file not found: {filepath}")
        
        img = bpy.data.images.load(filepath)
        if not img:
            raise RuntimeError(f"Blender failed to load image: {filepath}")
        
        utils_paint.save_image(img)
        return img
    except Exception as e:
        raise RuntimeError(f"Error importing image '{filepath}': {str(e)}") from e


def load_filepath_in_node(node, filepath, non_color):
    """Loads given filepath into given node. Handles errors gracefully.
    
    Args:
        node: Image texture node to load into.
        filepath: Path to image file.
        non_color: Whether to use Non-Color colorspace.
    
    Raises:
        RuntimeError: If loading fails.
    """
    if not filepath:
        return
    
    if not os.path.exists(filepath):
        raise RuntimeError(f"Image file does not exist: {filepath}")
    
    if "." not in filepath:
        raise RuntimeError(f"Invalid filename (no extension): {filepath}")
    
    try:
        img = import_image(filepath)
        node.image = img
        
        if non_color:
            img.colorspace_settings.name = "Non-Color"
        else:
            img.colorspace_settings.name = "sRGB"
    except Exception as e:
        # Re-raise with context for caller to handle
        raise RuntimeError(f"Failed to load image in node: {str(e)}") from e


class LP_OT_OpenImage(bpy.types.Operator, ImportHelper):
    bl_idname = "lp.open_image"
    bl_label = "Open Image"
    bl_description = "Opens an image for this input"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    filter_glob: bpy.props.StringProperty(
        default='*.png;*.jpg;*.jpeg;*.tif;*.exr',
        options={'HIDDEN'}
    )
    
    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    node_tree: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    non_color: bpy.props.BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def execute(self, context):
        try:
            ntree = bpy.data.node_groups.get(self.node_tree)
            if not ntree:
                self.report({'ERROR'}, f"Node group '{self.node_tree}' not found. It may have been deleted.")
                return {'CANCELLED'}
            
            node = ntree.nodes.get(self.node)
            if not node:
                self.report({'ERROR'}, f"Node '{self.node}' not found in node group.")
                return {'CANCELLED'}
            
            load_filepath_in_node(node, self.filepath, self.non_color)
            return {'FINISHED'}
        except RuntimeError as e:
            self.report({'ERROR'}, f"Failed to load image: {str(e)}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error loading image: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}


class LP_OT_OpenImages(bpy.types.Operator, ImportHelper):
    bl_idname = "lp.open_images"
    bl_label = "Open Images"
    bl_description = "Opens the selected images in their respective channels"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    filter_glob: bpy.props.StringProperty(
        default='*.png;*.jpg;*.jpeg;*.tif;*.exr',
        options={'HIDDEN'}
    )
    
    files: bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def find_channel_from_name(self, context, name):
        mat = utils.active_material(context)
        for channel in constants.CHANNEL_ABBR:
            for abbr in channel["abbr"]:
                if abbr in name:
                    for channel_name in channel["names"]:
                        for channel in mat.lp.channels:
                            if channel.name == channel_name:
                                return channel
        return None

    def execute(self, context):
        mat = utils.active_material(context)
        not_found = 0
        
        for blob in self.files:
            filepath = os.path.join(os.path.dirname(self.filepath), blob.name)
            channel = self.find_channel_from_name(context, blob.name.split(".")[0].lower())

            if not channel:
                not_found += 1
                import_image(filepath)
            else:
                layer_fill.set_channel_data_type(mat.lp.selected, channel.uid, "TEX")
                layer_fill.get_channel_mix_node(mat.lp.selected, channel.uid).mute = False
                tex_node = layer_fill.get_channel_value_node(mat.lp.selected, channel.uid)
                load_filepath_in_node(tex_node, filepath, channel.is_data)
                
        if not_found:
            self.report({"WARNING"}, message=f"{not_found} images were imported but didn't match a channel!")
        return {"FINISHED"}