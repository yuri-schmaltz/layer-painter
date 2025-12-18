import bpy

from .. import utils
from ..operators import utils_operator, utils_paint
from ..data.materials.layers.layer_types import layer_fill
from ..data import utils_nodes


class LP_OT_PaintChannel(bpy.types.Operator):
    bl_idname = "lp.paint_channel"
    bl_label = "Paint"
    bl_description = "Start painting on this channel"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    channel: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"}, default="")

    node_group: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"}, default="")
    node_name: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"}, default="")

    resolution: bpy.props.IntProperty(options={"HIDDEN"},
                                        default=2048,
                                        min=2,
                                        max=16384,
                                        name="Resolution",
                                        description="Resolution of the created image (max 16384 to prevent OOM)")
    color: bpy.props.FloatVectorProperty(options={"HIDDEN"},
                                        default=(1,1,1,0),
                                        size=4,
                                        min=0,
                                        max=1,
                                        subtype="COLOR",
                                        name="Color",
                                        description="Fill color for the created image")

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        mat = utils.active_material(context)
        if not mat:
            self.report({'ERROR'}, "No active material.")
            return {"CANCELLED"}
        
        try:
            channel = mat.lp.channel_by_uid(self.channel)
            if not channel:
                self.report({'ERROR'}, "Channel not found.")
                return {"CANCELLED"}
            
            # find tex node
            if self.channel:
                layer = mat.lp.selected
                if not layer:
                    self.report({'ERROR'}, "No layer selected.")
                    return {"CANCELLED"}
                tex, _, _ = layer_fill.get_channel_texture_nodes(layer, self.channel)
            else:
                ngroup = bpy.data.node_groups.get(self.node_group)
                if not ngroup:
                    self.report({'ERROR'}, f"Node group '{self.node_group}' not found.")
                    return {"CANCELLED"}
                node = ngroup.nodes.get(self.node_name)
                if not node:
                    self.report({'ERROR'}, f"Node '{self.node_name}' not found.")
                    return {"CANCELLED"}
                tex = node

            # create or get image
            if not tex.image:
                if self.channel:
                    img = utils_paint.create_image("image", self.resolution, self.color, channel.is_data)
                    tex.image = img
                else:
                    img = utils_paint.create_image("image", self.resolution, (0,0,0,1), False)
                    tex.image = img
            else:
                img = tex.image

            utils_paint.save_all_unsaved()
            utils_paint.paint_image(img)
            return {"FINISHED"}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start painting: {str(e)}")
            return {"CANCELLED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "resolution")
        if self.channel:
            layout.prop(self, "color")

    def invoke(self, context, event):
        # find tex node
        if self.channel:
            layer = utils.active_material(context).lp.selected
            # set up texture channel
            if layer.layer_type == "FILL":
                layer_fill.set_channel_data_type(layer, self.channel, "TEX")
                tex, _, _ = layer_fill.get_channel_texture_nodes(layer, self.channel)
            elif layer.layer_type == "PAINT":
                pass # TODO for fill layer
        else:
            ngroup = bpy.data.node_groups[self.node_group]
            tex = ngroup.nodes[self.node_name]
        
        # skip add image popup
        if tex.image:
            return self.execute(context)
        
        # add image popup
        return context.window_manager.invoke_props_dialog(self, width=300)


class LP_OT_StopPainting(bpy.types.Operator):
    bl_idname = "lp.stop_painting"
    bl_label = "Finish"
    bl_description = "Finish painting the current image"
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        utils_paint.save_all_unsaved()
        return {"FINISHED"}


class LP_OT_ToggleTexture(bpy.types.Operator):
    bl_idname = "lp.toggle_texture"
    bl_label = "Toggle Texture"
    bl_description = "Converts this input to an image input or back to color"
    bl_options = {"REGISTER", "INTERNAL"}

    node_group: bpy.props.StringProperty(options={"HIDDEN"})
    node_name: bpy.props.StringProperty(options={"HIDDEN"})
    input_index: bpy.props.IntProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        try:
            ntree = bpy.data.node_groups.get(self.node_group)
            if not ntree:
                self.report({'ERROR'}, f"Node group '{self.node_group}' not found.")
                return {"CANCELLED"}
            
            node = ntree.nodes.get(self.node_name)
            if not node:
                self.report({'ERROR'}, f"Node '{self.node_name}' not found.")
                return {"CANCELLED"}
            
            if self.input_index >= len(node.inputs):
                self.report({'ERROR'}, f"Input index out of range.")
                return {"CANCELLED"}

            if len(node.inputs[self.input_index].links) == 0:
                mat = utils.active_material(context)
                if not mat or not mat.lp.selected:
                    self.report({'ERROR'}, "No active layer selected.")
                    return {"CANCELLED"}
                tex = mat.lp.selected.texture_setup(ntree)
                ntree.links.new(tex.outputs[0], node.inputs[self.input_index])
            else:
                utils_nodes.remove_connected_left(ntree, node.inputs[self.input_index].links[0].from_node)
            
            return {"FINISHED"}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to toggle texture: {str(e)}")
            return {"CANCELLED"}
