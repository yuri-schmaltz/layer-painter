import bpy

from .. import utils
from ..operators import utils_operator


class LP_OT_MakeChannel(bpy.types.Operator):
    bl_idname = "lp.make_channel"
    bl_label = "Make Channel"
    bl_description = "Turns this input into a layer painter channel"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    node: bpy.props.StringProperty(name="Node",
                                    description="Name of the node to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    input: bpy.props.StringProperty(name="Input",
                                    description="Name of the input to use",
                                    options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def execute(self, context):
        inp = utils_operator.get_input(self.material, self.node, self.input)
        if not inp:
            self.report({'ERROR'}, f"Input '{self.input}' not found in node '{self.node}'.")
            return {"CANCELLED"}
        
        mat = bpy.data.materials.get(self.material)
        if not mat:
            self.report({'ERROR'}, f"Material '{self.material}' not found.")
            return {"CANCELLED"}
        
        try:
            mat.lp.add_channel(inp)
            utils.redraw()
            return {"FINISHED"}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add channel: {str(e)}")
            return {"CANCELLED"}


class LP_OT_RemoveChannel(bpy.types.Operator):
    bl_idname = "lp.remove_channel"
    bl_label = "Remove Channel"
    bl_description = "Removes this input as a Layer Painter channel"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    node: bpy.props.StringProperty(name="Node",
                                    description="Name of the node to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    input: bpy.props.StringProperty(name="Input",
                                    description="Name of the input to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    overwrite_uid: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def execute(self, context):
        mat = bpy.data.materials.get(self.material)
        if not mat:
            self.report({'ERROR'}, f"Material '{self.material}' not found.")
            return {"CANCELLED"}
        
        try:
            if self.overwrite_uid:
                channel = mat.lp.channel_by_uid(self.overwrite_uid)
                if not channel:
                    self.report({'ERROR'}, f"Channel not found. It may have been deleted.")
                    return {"CANCELLED"}
                mat.lp.remove_channel(channel)
            else:
                inp = utils_operator.get_input(self.material, self.node, self.input)
                if not inp:
                    self.report({'ERROR'}, f"Input '{self.input}' not found.")
                    return {"CANCELLED"}
                mat.lp.remove_channel(mat.lp.channel_by_inp(inp))
            
            utils.redraw()
            return {"FINISHED"}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to remove channel: {str(e)}")
            return {"CANCELLED"}


class LP_OT_MoveChannelUp(bpy.types.Operator):
    bl_idname = "lp.move_channel_up"
    bl_label = "Move Channel Up"
    bl_description = "Moves this channel up"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    channel_uid: bpy.props.StringProperty(name="Channel UID",
                                    description="UID of this channel",
                                    options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def execute(self, context):
        mat = bpy.data.materials.get(self.material)
        if not mat:
            self.report({'ERROR'}, f"Material '{self.material}' not found.")
            return {"CANCELLED"}
        
        try:
            mat.lp.move_channel_up(self.channel_uid)
            utils.redraw()
            return {"FINISHED"}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to move channel: {str(e)}")
            return {"CANCELLED"}


class LP_OT_MoveChannelDown(bpy.types.Operator):
    bl_idname = "lp.move_channel_down"
    bl_label = "Move Channel Down"
    bl_description = "Moves this channel down"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    material: bpy.props.StringProperty(name="Material",
                                    description="Name of the material to use",
                                    options={"HIDDEN", "SKIP_SAVE"})
    
    channel_uid: bpy.props.StringProperty(name="Channel UID",
                                    description="UID of this channel",
                                    options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def execute(self, context):
        mat = bpy.data.materials.get(self.material)
        if not mat:
            self.report({'ERROR'}, f"Material '{self.material}' not found.")
            return {"CANCELLED"}
        
        try:
            mat.lp.move_channel_down(self.channel_uid)
            utils.redraw()
            return {"FINISHED"}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to move channel: {str(e)}")
            return {"CANCELLED"}
