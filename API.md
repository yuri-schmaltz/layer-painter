# Layer Painter – API Reference

Complete API reference for Layer Painter classes and functions.

---

## Table of Contents

1. [Material API](#material-api)
2. [Layer API](#layer-api)
3. [Channel API](#channel-api)
4. [Paint API](#paint-api)
5. [Baking API](#baking-api)
6. [Node Management API](#node-management-api)
7. [Utilities API](#utilities-api)
8. [Operator API](#operator-api)

---

## Material API

**Module**: `data.materials.material`

### Material Class

Represents a Layer Painter material.

#### Properties

```python
material.lp.uid: str
    Unique identifier (10-char hex string)
    Persists across undo/redo/file load

material.lp.layers: list[Layer]
    All layers in material (ordered bottom to top)

material.lp.channels: list[Channel]
    All channels in material

material.node_tree: ShaderNodeTree
    Blender shader node tree
```

#### Methods

```python
def get_layer(material, uid: str) -> Layer | None
    Get layer by UID
    
    Args:
        material (Material): Material object
        uid (str): Layer UID
    
    Returns:
        Layer if found, None otherwise

def add_layer(material, name: str, layer_type: str) -> Layer
    Create new layer
    
    Args:
        material (Material): Material object
        name (str): Layer name
        layer_type (str): "FILL" or "PAINT"
    
    Returns:
        Newly created Layer
    
    Raises:
        ValueError: Invalid layer type

def remove_layer(material, uid: str) -> bool
    Delete layer by UID
    
    Args:
        material (Material): Material object
        uid (str): Layer UID to delete
    
    Returns:
        True if deleted, False if not found

def get_channel(material, uid: str) -> Channel | None
    Get channel by UID
    
    Args:
        material (Material): Material object
        uid (str): Channel UID
    
    Returns:
        Channel if found, None otherwise

def add_channel(material, name: str, data_type: str) -> Channel
    Add channel to material
    
    Args:
        material (Material): Material object
        name (str): Channel name
        data_type (str): "COLOR" or "TEXTURE"
    
    Returns:
        Newly created Channel
    
    Raises:
        ValueError: Invalid data type

def duplicate_layer(material, uid: str) -> Layer
    Create copy of layer with all settings
    
    Args:
        material (Material): Material object
        uid (str): Layer to duplicate
    
    Returns:
        Duplicated Layer (new UID)
    
    Raises:
        RuntimeError: Layer not found

def set_layer_opacity(material, uid: str, opacity: float)
    Set layer blending opacity
    
    Args:
        material (Material): Material object
        uid (str): Layer UID
        opacity (float): 0.0-1.0 (0=transparent, 1=opaque)
    
    Raises:
        ValueError: Opacity out of range

def set_layer_blend_mode(material, uid: str, blend_mode: str)
    Set layer blend mode
    
    Args:
        material (Material): Material object
        uid (str): Layer UID
        blend_mode (str): "Normal", "Multiply", "Screen", "Overlay", etc.
    
    Raises:
        ValueError: Invalid blend mode
```

---

## Layer API

**Module**: `data.materials.layers.layer`

### Layer Class

Represents a compositing layer.

#### Properties

```python
layer.uid: str
    Unique identifier (matches node group UID)

layer.node: ShaderNodeGroup
    Layer node group in shader tree

layer.mat_uid_ref: str
    Parent material UID

layer.channels: list[Channel]
    Channels in this layer

layer.enabled: bool
    Layer visibility

layer.opacity: float
    Blending opacity (0.0-1.0)

layer.blend_mode: str
    Blend mode name

layer.name: str
    Display name
```

#### Methods

```python
def get_material(layer) -> Material | None
    Get parent material
    
    Returns:
        Parent Material if found, None otherwise

def get_channel(layer, uid: str) -> Channel | None
    Get channel by UID
    
    Args:
        uid (str): Channel UID
    
    Returns:
        Channel if found, None otherwise

def add_channel(layer, name: str, data_type: str) -> Channel
    Add channel to layer
    
    Args:
        name (str): Channel name (e.g., "BaseColor")
        data_type (str): "COLOR" or "TEXTURE"
    
    Returns:
        Newly created Channel
    
    Raises:
        RuntimeError: Layer node not found

def remove_channel(layer, uid: str) -> bool
    Delete channel from layer
    
    Args:
        uid (str): Channel UID to delete
    
    Returns:
        True if deleted, False if not found

def set_enabled(layer, enabled: bool)
    Toggle layer visibility
    
    Args:
        enabled (bool): True = visible, False = hidden

def set_opacity(layer, opacity: float)
    Set blending opacity
    
    Args:
        opacity (float): 0.0-1.0

def set_blend_mode(layer, blend_mode: str)
    Set blend mode
    
    Args:
        blend_mode (str): "Normal", "Multiply", "Screen", etc.

def organize_layout(layer)
    Auto-organize node layout in tree
    
    Raises:
        RuntimeError: Layer node corrupted
```

#### Layer Type Specific

**File**: `data/materials/layers/layer_types/layer_fill.py`

```python
def setup_channel_nodes(layer, channel, endpoints)
    Create RGB/procedural nodes for FILL layer
    
    Args:
        layer (Layer): FILL layer
        channel (Channel): Channel to setup
        endpoints (tuple): (input_socket, output_socket)
    
    Raises:
        RuntimeError: Node creation failed

def remove_channel_nodes(layer, channel_uid: str) -> bool
    Remove all nodes for channel
    
    Args:
        layer (Layer): FILL layer
        channel_uid (str): Channel UID to remove
    
    Returns:
        True if removed, False if not found
```

**File**: `data/materials/layers/layer_types/layer_paint.py`

```python
def setup_channel_nodes(layer, channel, endpoints)
    Create texture/color nodes for PAINT layer
    
    Args:
        layer (Layer): PAINT layer
        channel (Channel): Channel to setup
        endpoints (tuple): (input_socket, output_socket)
    
    Raises:
        RuntimeError: Node creation failed

def remove_channel_nodes(layer, channel_uid: str) -> bool
    Remove all nodes for channel
    
    Args:
        layer (Layer): PAINT layer
        channel_uid (str): Channel UID to remove
    
    Returns:
        True if removed, False if not found

def get_channel_texture_node(layer, channel_uid: str) -> ShaderNode | None
    Get texture image node (texture mode only)
    
    Args:
        layer (Layer): PAINT layer
        channel_uid (str): Channel UID
    
    Returns:
        Texture node or None

def get_channel_color_node(layer, channel_uid: str) -> ShaderNode | None
    Get RGB node (color mode only)
    
    Args:
        layer (Layer): PAINT layer
        channel_uid (str): Channel UID
    
    Returns:
        RGB node or None

def get_channel_data_type(layer, channel_uid: str) -> str
    Get current data type
    
    Args:
        layer (Layer): PAINT layer
        channel_uid (str): Channel UID
    
    Returns:
        "TEX" or "COL"

def cycle_channel_data_type(layer, channel_uid: str)
    Switch between texture and color modes
    
    Args:
        layer (Layer): PAINT layer
        channel_uid (str): Channel UID
    
    Raises:
        RuntimeError: Channel not found
```

---

## Channel API

**Module**: `data.materials.channels.channel`

### Channel Class

Represents a material output channel.

#### Properties

```python
channel.uid: str
    Unique identifier

channel.inp: NodeSocket
    Input socket (layer → channel)

channel.out: NodeSocket
    Output socket (channel → above layer)

channel.is_data: bool
    True = linear (Normal, Roughness)
    False = sRGB (Base Color)

channel.data_type: str
    "COLOR" or "TEXTURE"

channel.name: str
    Display name
```

#### Methods

```python
def get_layer(channel) -> Layer | None
    Get parent layer by UID
    
    Returns:
        Parent Layer if found, None otherwise

def get_material(channel) -> Material | None
    Get parent material (via layer)
    
    Returns:
        Parent Material if found, None otherwise

def set_input_node(channel, node: ShaderNode)
    Connect input source node
    
    Args:
        node (ShaderNode): Source node

def set_output_node(channel, node: ShaderNode)
    Connect output destination node
    
    Args:
        node (ShaderNode): Destination node

def get_input_value(channel) -> Any
    Get current input value
    
    Returns:
        Color, float, or texture depending on type

def set_input_value(channel, value: Any)
    Set input value
    
    Args:
        value (Any): Color tuple, float, or image
    
    Raises:
        TypeError: Value type mismatch
```

---

## Paint API

**Module**: `operators.paint`

### LP_OT_PaintChannel Operator

Start texture painting on channel.

```python
# Properties
resolution: int
    Texture resolution (512, 1024, 2048, 4096)

default_color: float[4]
    Initial texture color (RGBA)

layer_uid: str
    Target layer UID

channel_uid: str
    Target channel UID

# Methods
def poll(context) -> bool
    Check if paint operation can run
    
    Returns:
        True if valid context, False otherwise

def invoke(self, context, event) -> set
    Show resolution dialog if needed
    
    Returns:
        {"FINISHED"}, {"CANCELLED"}, or invoke result

def execute(self, context) -> set
    Start paint session
    
    Returns:
        {"FINISHED"} or {"CANCELLED"}
```

### LP_OT_StopPainting Operator

Stop painting and save texture.

```python
def poll(context) -> bool
    Check if painting active
    
    Returns:
        True if in paint mode, False otherwise

def execute(self, context) -> set
    Stop paint mode and save
    
    Returns:
        {"FINISHED"} or {"CANCELLED"}
```

---

## Baking API

**Module**: `operators.baking`

### Baking Operators

```python
# LP_OT_BakeSetupChannel
def poll(context) -> bool
    Check if bake can start
    
    Returns:
        True if valid material, False otherwise

def execute(self, context) -> set
    Setup emission nodes for baking
    
    Returns:
        {"FINISHED"} or {"CANCELLED"}

# LP_OT_BakeCleanupChannel
def execute(self, context) -> set
    Remove bake nodes and save image
    
    Returns:
        {"FINISHED"} or {"CANCELLED"}

# LP_OT_BakeFinish
def execute(self, context) -> set
    Complete bake process
    
    Returns:
        {"FINISHED"} or {"CANCELLED"}
```

### Baking Utilities

**Module**: `operators.utils_paint`

```python
def save_all_unsaved()
    Save all unsaved images to disk
    
    Location: <blend_dir>/layer_painter_textures/
    Format: <Material>_<Channel>.png

def paint_image(image: Image)
    Switch to texture paint mode
    
    Args:
        image (Image): Image to paint on
    
    Raises:
        RuntimeError: Paint mode failed

def create_image(name: str, resolution: int, color: tuple, is_data: bool) -> Image
    Create new image texture
    
    Args:
        name (str): Image name
        resolution (int): Width/height in pixels
        color (tuple): Default color (R, G, B, A)
        is_data (bool): True = linear, False = sRGB
    
    Returns:
        New Image object
```

---

## Node Management API

**Module**: `data.utils_nodes`

### Node Organization

```python
def organize_tree_layout(ntree: ShaderNodeTree, start_node: ShaderNode, spacing: int = 400)
    Auto-arrange nodes right-to-left
    
    Args:
        ntree (ShaderNodeTree): Shader tree
        start_node (ShaderNode): Starting node (output)
        spacing (int): Horizontal spacing between columns
    
    Raises:
        RuntimeError: Layout failed

def remove_connected_left(ntree: ShaderNodeTree, node: ShaderNode)
    Recursively remove node and upstream connections
    
    Args:
        ntree (ShaderNodeTree): Shader tree
        node (ShaderNode): Node to remove
    
    Raises:
        RuntimeError: Node not in tree

def get_node_by_uid(ntree: ShaderNodeTree, uid: str) -> ShaderNode | None
    Find node by UID
    
    Args:
        ntree (ShaderNodeTree): Shader tree
        uid (str): Node UID
    
    Returns:
        Node if found, None otherwise

def set_node_uid(node: ShaderNode, uid: str)
    Assign UID to node
    
    Args:
        node (ShaderNode): Node object
        uid (str): Unique identifier
```

### Node Group Operations

**Module**: `data.utils_groups`

```python
def add_input(node_group: ShaderNodeGroup, socket_type: str, name: str) -> tuple[NodeSocket, NodeSocket]
    Create group input socket
    
    Args:
        node_group (ShaderNodeGroup): Group node
        socket_type (str): Socket type ("NodeSocketColor", "NodeSocketFloatFactor", etc.)
        name (str): Display name
    
    Returns:
        (input_socket, group_input_socket)

def add_output(node_group: ShaderNodeGroup, socket_type: str, name: str) -> tuple[NodeSocket, NodeSocket]
    Create group output socket
    
    Args:
        node_group (ShaderNodeGroup): Group node
        socket_type (str): Socket type
        name (str): Display name
    
    Returns:
        (output_socket, group_output_socket)

def remove_input(node_group: ShaderNodeGroup, index: int)
    Remove group input by index
    
    Args:
        node_group (ShaderNodeGroup): Group node
        index (int): Input index

def remove_output(node_group: ShaderNodeGroup, index: int)
    Remove group output by index
    
    Args:
        node_group (ShaderNodeGroup): Group node
        index (int): Output index
```

---

## Utilities API

**Module**: `utils`

### General Utilities

```python
def make_uid() -> str
    Generate random 10-character hex UID
    
    Returns:
        Unique identifier string
    
    Example:
        uid = make_uid()  # "a1b2c3d4e5"

def get_active_material(context) -> Material | None
    Get currently selected material
    
    Args:
        context: Blender context
    
    Returns:
        Material if found, None otherwise

def redraw()
    Force UI refresh
    
    Updates all panels and viewports
    Useful after state changes

def set_material_uids()
    Ensure all materials have UIDs
    
    Initializes missing UIDs on file load
    Called in handlers.on_load_handler()
```

---

## Operator API

**Module**: `operators`

### Base Patterns

All Layer Painter operators follow this pattern:

```python
class LP_OT_SomeName(bpy.types.Operator):
    bl_idname = "lp.some_name"       # Unique identifier
    bl_label = "Some Name"            # Display name
    bl_description = "Does something" # Tooltip
    bl_options = {"REGISTER", "UNDO"} # Undo support
    
    # Properties passed as parameters
    layer_uid: bpy.props.StringProperty()
    channel_uid: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context) -> bool:
        """Check if operation can run"""
        return utils_operator.base_poll(context)
    
    def execute(self, context) -> set:
        """Execute operation"""
        try:
            # Do work
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
```

### Common Operators

```python
# Layer Operations
"lp.create_layer"       # Create new layer
"lp.delete_layer"       # Delete layer
"lp.duplicate_layer"    # Duplicate layer
"lp.move_layer_up"      # Move layer up in stack
"lp.move_layer_down"    # Move layer down in stack

# Channel Operations
"lp.add_channel"        # Add channel to layer
"lp.remove_channel"     # Remove channel
"lp.cycle_data_type"    # Toggle texture/color mode

# Paint Operations
"lp.paint_channel"      # Start painting
"lp.stop_painting"      # Stop painting

# Bake Operations
"lp.bake_all"           # Bake all channels
"lp.bake_setup"         # Setup bake nodes
"lp.bake_finish"        # Finalize and cleanup

# Export Operations
"lp.export_textures"    # Export to files
"lp.export_preset"      # Export with preset
```

---

## Constants

**Module**: `constants`

### Node Types

```python
NODES = {
    "TEX": "ShaderNodeTexImage",
    "GROUP": "ShaderNodeGroup",
    "RGB": "ShaderNodeRGB",
    "MIX": "ShaderNodeMix",
    "EMIT": "ShaderNodeEmission",
    "OUT": "ShaderNodeOutputMaterial",
    "REMAP": "ShaderNodeMapping",
    "COORD": "ShaderNodeTexCoord",
}
```

### Socket Types

```python
SOCKETS = {
    "COLOR": "NodeSocketColor",
    "FLOAT": "NodeSocketFloatFactor",
    "VECTOR": "NodeSocketVector",
    "RGBA": "NodeSocketColor",
}
```

### File Paths

```python
TEX_DIR_NAME = "layer_painter_textures"  # Subfolder for images
EXPORT_OUT_NAME = "LP_BakeOutput"        # Bake output node name
EXPORT_EMIT_NAME = "LP_BakeEmission"     # Bake emission node name
```

---

## Error Handling

### Common Exceptions

```python
RuntimeError
    Node not found, operation failed
    Example: "Couldn't find layer node for 'X'"

ValueError
    Invalid parameter value
    Example: "Layer type must be 'FILL' or 'PAINT'"

TypeError
    Type mismatch
    Example: "Expected Material, got NoneType"

AttributeError
    Stale reference after undo/redo
    Example: "'NoneType' has no attribute 'uid'"
```

### Error Recovery

```python
def safe_lookup(lookup_fn):
    """Never crash, always return result"""
    try:
        return lookup_fn()
    except Exception as e:
        logger.error(f"Lookup failed: {e}")
        return None
```

---

## Example Usage

### Create Material with Layer

```python
import bpy
from layer_painter.data.materials import material

# Get active material
mat = bpy.context.object.data.materials[0]

# Initialize Layer Painter
material.init_material(mat)

# Create FILL layer
layer = material.add_layer(mat, "Base Color", "FILL")

# Add channel
channel = layer.add_channel("Base Color", "COLOR")

# Set opacity
material.set_layer_opacity(mat, layer.uid, 0.8)
```

### Paint on Channel

```python
from layer_painter.operators import paint

# Trigger paint operator
bpy.ops.lp.paint_channel(
    layer_uid=layer.uid,
    channel_uid=channel.uid,
    resolution=2048,
    default_color=(1, 1, 1, 1)
)

# Stop painting
bpy.ops.lp.stop_painting()
```

### Export Textures

```python
from layer_painter.data import export

# Export all channels
export.export_material(
    material=mat,
    output_path="/path/to/textures/",
    format="PNG",
    resolution=2048
)
```

---

**Version**: 1.0  
**Updated**: Phase 3 Implementation  
**Blender Version**: 4.0+
