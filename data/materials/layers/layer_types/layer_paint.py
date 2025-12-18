"""Paint Layer Type Implementation

Paint layers use texture images as their primary input, with optional color/solid mode fallback.
Supports texture mapping, coordinate transforms, and automatic texture creation.

Node Structure:
    Texture Coordinate → Mapping → Texture Image Node → Mix Node → Opacity → Output
    or
    RGB Color Node → Mix Node → Opacity → Output (in color mode)
"""

import bpy

from ..... import constants
from .....data import utils_nodes


def setup_channel_nodes(layer, channel, endpoints):
    """Creates the nodes for the given channel in the form of a paint layer.
    
    Paint layers use texture nodes as the primary input, with optional color mix fallback.
    Node structure:
        Texture Node → Mix Node → Opacity → Channel Output
    
    Args:
        layer: Parent layer object
        channel: Channel being configured
        endpoints: Channel endpoint sockets (input/output)
    
    Raises:
        RuntimeError: If layer node or channel input not found
    """
    if not layer.node:
        raise RuntimeError(f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed.")
    if not channel.inp:
        raise RuntimeError(f"Couldn't find input for channel '{channel.name}'. Delete channel to proceed.")

    # Add channel mix node
    mix = layer.__add_channel_mix(channel)
    
    # Add opacity control
    layer.__add_channel_opacity(mix)

    # Setup texture node for paint input (default mode)
    tex = __setup_node_value(layer, channel)
    if tex:
        layer.node.node_tree.links.new(tex.outputs[0], mix.inputs[2])


def remove_channel_nodes(layer, channel_uid):
    """Removes the endpoints and channel nodes from the given layer.
    
    This function cleans up all nodes associated with a paint layer channel,
    including texture nodes, mappings, and coordinate transforms.
    
    Args:
        layer: Parent layer object
        channel_uid: UID of channel to remove
    
    Raises:
        RuntimeError: If layer node not found
    """
    if not layer.node:
        raise RuntimeError(f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed.")

    # Get the channel mix node (identified by UID)
    try:
        mix_node = layer.node.node_tree.nodes[channel_uid]
    except KeyError:
        # Channel nodes already removed or UID doesn't exist
        return

    # Remove connected nodes (texture, mapping, coordinates)
    __remove_paint_channel_nodes(layer, mix_node)

    # Remove channel endpoints
    inp_index, out_index = layer.get_channel_endpoint_indices(channel_uid)
    if inp_index is not None and inp_index < len(layer.node.node_tree.interface.inputs):
        layer.node.node_tree.interface.remove(
            layer.node.node_tree.interface.inputs[inp_index]
        )
    if out_index is not None and out_index < len(layer.node.node_tree.interface.outputs):
        layer.node.node_tree.interface.remove(
            layer.node.node_tree.interface.outputs[out_index]
        )


def get_channel_mix_node(layer, channel_uid):
    """Returns the mix node for the given layer and channel.
    
    Args:
        layer: Parent layer object
        channel_uid: UID of the channel
    
    Returns:
        ShaderNode: The mix node for the channel
    
    Raises:
        RuntimeError: If layer or mix node not found
    """
    if not layer.node:
        raise RuntimeError(f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed.")
    try:
        return layer.node.node_tree.nodes[channel_uid]
    except KeyError:
        raise RuntimeError(
            f"Couldn't find mix node for channel '{channel_uid}'. Delete channel to proceed."
        )


def get_channel_texture_node(layer, channel_uid):
    """Returns the texture image node for the given channel uid, or None if color mode.
    
    Args:
        layer: Parent layer object
        channel_uid: UID of the channel
    
    Returns:
        ShaderNode or None: The texture node if in texture mode, None if in color mode
    """
    if not layer.node:
        raise RuntimeError(f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed.")
    
    try:
        mix_node = get_channel_mix_node(layer, channel_uid)
    except RuntimeError:
        return None
    
    # Get input to mix node (should be texture or color)
    if not mix_node.inputs[2].links:
        return None
    
    input_node = mix_node.inputs[2].links[0].from_node
    
    # If it's a texture node, return it
    if input_node.bl_idname == constants.NODES["TEX"]:
        return input_node
    
    # If it's a mix/color node, return None (color mode)
    return None


def get_channel_color_node(layer, channel_uid):
    """Returns the RGB/color node for the given channel uid, or None if texture mode.
    
    Args:
        layer: Parent layer object
        channel_uid: UID of the channel
    
    Returns:
        ShaderNode or None: The color node if in color mode, None if in texture mode
    """
    if not layer.node:
        raise RuntimeError(f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed.")
    
    try:
        mix_node = get_channel_mix_node(layer, channel_uid)
    except RuntimeError:
        return None
    
    # Get input to mix node
    if not mix_node.inputs[2].links:
        return None
    
    input_node = mix_node.inputs[2].links[0].from_node
    
    # If it's a color/mix node, return it
    if input_node.bl_idname in [constants.NODES["RGB"], constants.NODES["MIX"]]:
        return input_node
    
    # If it's a texture node, return None (texture mode)
    return None


def get_channel_opacity_socket(layer, channel_uid):
    """Returns the opacity node's value socket for the given channel uid.
    
    Args:
        layer: Parent layer object
        channel_uid: UID of the channel
    
    Returns:
        NodeSocket or None: The opacity node's input socket, or None if not found
    """
    if not layer.node:
        raise RuntimeError(f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed.")
    
    try:
        mix_node = get_channel_mix_node(layer, channel_uid)
    except RuntimeError:
        return None
    
    # Get opacity node (connected to opacity socket)
    if not mix_node.inputs[0].links:
        return None
    
    opacity_node = mix_node.inputs[0].links[0].from_node
    
    # Opacity node should be a color ramp or mix node
    if opacity_node.bl_idname in [constants.NODES["RAMP"], constants.NODES["MIX"]]:
        return opacity_node.inputs[0]
    
    return None


def get_channel_data_type(layer, channel_uid):
    """Returns the type of data for this paint channel: 'TEX' (texture) or 'COL' (color).
    
    Args:
        layer: Parent layer object
        channel_uid: UID of the channel
    
    Returns:
        str: 'TEX' for texture mode, 'COL' for color mode
    """
    tex_node = get_channel_texture_node(layer, channel_uid)
    return "TEX" if tex_node else "COL"


def cycle_channel_data_type(layer, channel_uid):
    """Cycles the paint channel between texture and color mode.
    
    Args:
        layer: Parent layer object
        channel_uid: UID of the channel
    
    Raises:
        RuntimeError: If layer, channel, or mix node not found
    """
    if not layer.node:
        raise RuntimeError(f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed.")

    data_type = get_channel_data_type(layer, channel_uid)
    mix_node = get_channel_mix_node(layer, channel_uid)
    channel = layer.mat.lp.channel_by_uid(channel_uid)

    if not channel:
        raise RuntimeError(f"Channel '{channel_uid}' not found in material.")

    # Get connection point
    connect_socket = mix_node.inputs[2]

    # Remove current node and dependencies
    if connect_socket.links:
        old_node = connect_socket.links[0].from_node
        utils_nodes.remove_connected_left(layer.node.node_tree, old_node)

    # Switch to texture mode
    if data_type == "COL":
        tex_node = __setup_node_texture(layer, channel)
        if tex_node:
            layer.node.node_tree.links.new(tex_node.outputs[0], connect_socket)

    # Switch to color mode
    elif data_type == "TEX":
        color_node = __setup_node_color(layer, channel)
        if color_node:
            layer.node.node_tree.links.new(color_node.outputs[0], connect_socket)


def __setup_node_value(layer, channel):
    """Setup the value node for the paint layer.
    
    Paint layers default to texture mode for best quality. This creates
    a complete texture node setup with mapping and coordinates.
    
    Args:
        layer: Parent layer object
        channel: Channel being configured
    
    Returns:
        ShaderNode: The texture image node
    """
    return __setup_node_texture(layer, channel)


def __setup_node_texture(layer, channel):
    """Setup texture image node with mapping and coordinate transform.
    
    Creates a complete texture setup:
    - Texture Coordinate node (generates UV)
    - Mapping node (transforms UV)
    - Texture Image node (samples texture)
    
    Args:
        layer: Parent layer object
        channel: Channel being configured
    
    Returns:
        ShaderNode or None: The texture image node, or None if setup failed
    """
    if not layer.node or not layer.node.node_tree:
        return None

    ntree = layer.node.node_tree

    # Create texture node
    tex_node = ntree.nodes.new(constants.NODES["TEX"])
    tex_node.name = f"tex_{channel.name}"
    tex_node.label = f"Paint: {channel.name}"

    # Create mapping node for UV transformation
    mapp_node = ntree.nodes.new(constants.NODES["MAPP"])
    mapp_node.name = f"mapp_{channel.name}"
    mapp_node.label = "Mapping"

    # Create texture coordinate node
    coord_node = ntree.nodes.new(constants.NODES["COORD"])
    coord_node.name = f"coord_{channel.name}"
    coord_node.label = "Coordinates"

    # Connect nodes: Coordinates → Mapping → Texture
    try:
        ntree.links.new(coord_node.outputs["UV"], mapp_node.inputs["Vector"])
        ntree.links.new(mapp_node.outputs["Vector"], tex_node.inputs["Vector"])
    except (RuntimeError, KeyError):
        # Handle missing sockets in different Blender versions
        pass

    return tex_node


def __setup_node_color(layer, channel):
    """Setup RGB/color node for solid color paint mode.
    
    Used when cycling from texture mode to solid color mode.
    
    Args:
        layer: Parent layer object
        channel: Channel being configured
    
    Returns:
        ShaderNode or None: The RGB color node, or None if setup failed
    """
    if not layer.node or not layer.node.node_tree:
        return None

    ntree = layer.node.node_tree

    # Create RGB color node
    rgb_node = ntree.nodes.new(constants.NODES["RGB"])
    rgb_node.name = f"col_{channel.name}"
    rgb_node.label = f"Color: {channel.name}"

    # Set default color from channel if available
    if hasattr(channel, 'default_value') and channel.default_value:
        rgb_node.outputs[0].default_value = channel.default_value
    else:
        # Default to white for better visibility
        rgb_node.outputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

    return rgb_node


def __remove_paint_channel_nodes(layer, mix_node):
    """Remove all nodes connected to a paint channel mix node.
    
    Recursively removes texture, mapping, and coordinate nodes.
    
    Args:
        layer: Parent layer object
        mix_node: The mix node whose inputs to clean up
    """
    if not layer.node or not layer.node.node_tree:
        return

    ntree = layer.node.node_tree

    # Remove the value node (texture or color) and its dependencies
    if mix_node.inputs[2].links:
        value_node = mix_node.inputs[2].links[0].from_node
        utils_nodes.remove_connected_left(ntree, value_node)

    # Remove the opacity node and its dependencies
    if mix_node.inputs[0].links:
        opacity_node = mix_node.inputs[0].links[0].from_node
        utils_nodes.remove_connected_left(ntree, opacity_node)

    # Remove the mix node itself
    try:
        ntree.nodes.remove(mix_node)
    except RuntimeError:
        # Node already removed
        pass
