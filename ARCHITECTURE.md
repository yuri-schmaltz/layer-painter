# Layer Painter – Architecture Documentation

Deep technical documentation for Layer Painter's design, patterns, and implementation.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [Entity Model](#entity-model)
4. [UID System](#uid-system)
5. [Handler & Cache Invalidation](#handler--cache-invalidation)
6. [Material Structure](#material-structure)
7. [Layer Types](#layer-types)
8. [Paint Pipeline](#paint-pipeline)
9. [Baking Architecture](#baking-architecture)
10. [Node Graph Management](#node-graph-management)
11. [Performance Patterns](#performance-patterns)
12. [Error Handling](#error-handling)
13. [Testing Strategy](#testing-strategy)

---

## Overview

**Layer Painter** brings Substance Painter-like procedural layering, masking, and filtering to Blender. The architecture separates concerns into:

- **Data Layer** (`data/`): Entity models and node management
- **Operator Layer** (`operators/`): User-triggered operations
- **UI Layer** (`ui/`): Viewport and node editor panels
- **Core** (`handlers.py`, `utils.py`, `constants.py`): Cross-cutting infrastructure

### Design Philosophy

1. **UID-based Lookup**: Use persistent UIDs instead of object references (survives undo/redo)
2. **Clear Separation**: Data models independent of operators and UI
3. **Handler Pattern**: Centralized event handling for cache invalidation
4. **Explicit Over Implicit**: Clear node creation, no hidden side effects
5. **Graceful Degradation**: Handle missing nodes/materials without crashing

---

## Core Principles

### 1. UIDs for Persistence

**Problem**: Blender object references become stale after undo/redo/file load.

**Solution**: Use 10-character hex strings as stable identifiers:

```python
# Material UID stored as property
material.lp.uid = "a1b2c3d4e5"  # Survives undo/redo

# Lookup material by UID (always works)
mat_by_uid = next((m for m in bpy.data.materials if m.lp.uid == uid), None)
```

**When UIDs Are Used**:
- Material UID: `material.lp.uid`
- Layer UID: `layer.uid` (also matches node group UID)
- Channel UID: `channel.uid`

### 2. Cache Invalidation Pattern

**Critical**: Caches MUST be cleared after events that invalidate object references:

```python
# In handlers.py
@persistent
def on_undo_redo_handler(dummy):
    """Clear all caches after undo/redo"""
    channel.clear_caches()
    layer.clear_caches()
    # ← Any new cached state must be cleared here

@persistent
def on_load_handler(dummy):
    """Clear all caches on file load"""
    channel.clear_caches()
    layer.clear_caches()
    set_material_uids()  # ← Re-initialize UIDs
```

**When to Add Cache Clearing**:
1. Cache any Blender object reference (node, material, image)
2. Add to `clear_caches()` function in that module
3. Call `clear_caches()` in `handlers.py` for relevant events

### 3. Recursive Node Cleanup

Remove a node and all upstream connections:

```python
def remove_connected_left(ntree, node):
    """Recursively remove node and upstream dependencies"""
    for inp in node.inputs:
        for link in inp.links:
            remove_connected_left(ntree, link.from_node)  # Recurse
    ntree.nodes.remove(node)
```

**Used For**:
- Removing old texture nodes before mode switch
- Cleanup after failed operations
- Channel removal

---

## Entity Model

### Material
**File**: `data/materials/material.py`

Top-level container:
```python
class Material:
    lp.uid: str              # Unique identifier
    lp.layers: list[Layer]   # All layers (bottom to top)
    lp.channels: list[Channel]  # All channels
    node_tree: ShaderNodeTree   # Shader editor nodes
```

**Key Methods**:
- `get_layer(uid)` → Layer by UID
- `add_layer(name, type)` → Create layer
- `remove_layer(uid)` → Delete layer
- `get_channel(uid)` → Channel by UID

### Layer
**File**: `data/materials/layers/layer.py`

Compositing unit:
```python
class Layer:
    uid: str                    # Unique identifier
    node: ShaderNodeGroup       # Layer node group
    mat_uid_ref: str            # Parent material UID
    channels: list[Channel]     # Layer channels
    enabled: bool               # Visibility toggle
    opacity: float              # Blending opacity
    blend_mode: str             # Blend mode (Normal, Multiply, etc.)
```

**Key Methods**:
- `get_material()` → Parent material by UID
- `get_channel(uid)` → Channel by UID
- `add_channel(name, type)` → Create channel
- `remove_channel(uid)` → Delete channel

### Channel
**File**: `data/materials/channels/channel.py`

Material output socket:
```python
class Channel:
    uid: str                    # Unique identifier
    inp: NodeSocket             # Input socket (layer → channel)
    out: NodeSocket             # Output socket (channel → above layer)
    is_data: bool               # Linear (True) or sRGB (False)
    data_type: str              # "COLOR" or "TEXTURE"
    name: str                   # Display name
```

**Key Methods**:
- `get_layer()` → Parent layer by UID
- `get_material()` → Parent material (via layer)
- `set_input_node()` → Connect input source
- `set_output_node()` → Connect output destination

---

## UID System

### UID Generation

```python
# In utils.py
def make_uid():
    """Generate 10-character random hex string"""
    return ''.join(random.choices('0123456789abcdef', k=10))
```

### UID Storage

UIDs are stored as **StringProperty** on Blender types to survive undo/redo:

```python
# On material
material.lp.uid = "a1b2c3d4e5"

# On node group (layer)
layer_node.uid = "f5e4d3c2b1"

# On channel
channel_property_group.uid = "1a2b3c4d5e"
```

### UID Lookup Pattern

```python
# Find material by UID
def get_material_by_uid(uid):
    return next((m for m in bpy.data.materials if m.lp.uid == uid), None)

# Find layer by UID (from list)
def get_layer_by_uid(layers, uid):
    return next((l for l in layers if l.uid == uid), None)

# Find channel in layer by UID
def get_channel_by_uid(layer, uid):
    return next((c for c in layer.channels if c.uid == uid), None)
```

### Why UIDs Are Critical

1. **Object References Become Invalid**:
   - After undo/redo: `bpy.data.materials[0]` may point to different memory address
   - After file load: Collection order changes
   - After deletion: Objects no longer exist

2. **UIDs Provide Stable Lookup**:
   - `uid` property survives all state changes
   - Always lookup by UID: `m for m in bpy.data.materials if m.lp.uid == "..."`
   - Never cache direct object references

---

## Handler & Cache Invalidation

### Event Handlers

**File**: `handlers.py`

Four critical event handlers:

#### 1. On Load Handler
```python
@persistent
def on_load_handler(dummy):
    """Runs when .blend file is loaded"""
    channel.clear_caches()
    layer.clear_caches()
    set_material_uids()  # Reinitialize UIDs if missing
```

**Triggers**: File load, new project, link/append

**Why Needed**: All object references become stale on file load

#### 2. On Undo/Redo Handler
```python
@persistent
def on_undo_redo_handler(dummy):
    """Clears caches after undo/redo operations"""
    channel.clear_caches()
    layer.clear_caches()
```

**Triggers**: Ctrl+Z, Ctrl+Shift+Z, Edit menu undo/redo

**Why Needed**: Undo/redo shifts object positions in collections

#### 3. Depsgraph Handler
```python
def depsgraph_handler(dummy):
    """Clears caches after topology changes"""
    if is_rendering():
        return  # Don't clear during bake
    channel.clear_caches()
    layer.clear_caches()
```

**Triggers**: Mesh topology changes, shader tree modifications

**Why Needed**: Node references may change position in graph

#### 4. Frame Change Handler
```python
@persistent
def frame_change_handler(dummy):
    """Runs on each frame (animation playback)"""
    # Update preview, check bake status, etc.
```

### Cache Patterns

#### Channel Cache Example
```python
# In data/materials/channels/channel.py
_channel_cache = {}  # Module-level cache

def get_channel_mix_node(layer, channel_uid):
    """Query with caching"""
    cache_key = (id(layer.node), channel_uid)
    if cache_key in _channel_cache:
        return _channel_cache[cache_key]  # Return cached
    
    # Lookup and cache
    mix_node = next((n for n in layer.node.node_tree.nodes
                     if hasattr(n, 'uid') and n.uid == channel_uid), None)
    if mix_node:
        _channel_cache[cache_key] = mix_node
    return mix_node

def clear_caches():
    """Called in handlers.py after undo/redo/load"""
    global _channel_cache
    _channel_cache = {}
```

---

## Material Structure

### Node Tree Layout

Layer Painter organizes shader nodes in a right-to-left hierarchy:

```
Shader Output ← Group (Layer N) ← Group (Layer N-1) ← ... ← Group (Layer 1)
                     ↓
                  Channels
                  ├─ Base Color
                  ├─ Normal
                  └─ Roughness
```

### Layer Node Group Structure

Each layer is a node group with internal structure:

```
Layer Node Group (layer.node)
├─ Inputs (one per channel)
│  ├─ Base Color (connects to upper layer output)
│  ├─ Normal
│  └─ Roughness
├─ Internal Nodes
│  ├─ Reroute nodes (organize layout)
│  ├─ Mix nodes (blend channels)
│  └─ Texture nodes (paint/fill data)
└─ Outputs (one per channel)
   ├─ Base Color (connects to lower layer input)
   ├─ Normal
   └─ Roughness
```

### Channel Endpoint Pattern

Each channel gets two endpoints in the layer group:

```python
# Input: Receives data from upper layer or material input
inp, group_inp = utils_groups.add_input(layer.node, SOCKETS["COLOR"], "BaseColor")
group_inp.uid = channel.uid  # Store UID for identification

# Output: Sends data to lower layer or shader output
out, group_out = utils_groups.add_output(layer.node, SOCKETS["COLOR"], "BaseColor")
group_out.uid = channel.uid  # Must match input UID
```

---

## Layer Types

### FILL Layer
**File**: `data/materials/layers/layer_types/layer_fill.py`

Procedurally generated content:

```python
def setup_channel_nodes(layer, channel, endpoints):
    """
    Create RGB node for solid color or ramp for gradient
    
    Node graph:
    RGB/Ramp → Mix Node → Layer Output
    """
```

**Features**:
- Solid color fills
- Color ramp gradients (future)
- Lightweight (no image memory)

### PAINT Layer
**File**: `data/materials/layers/layer_types/layer_paint.py`

Texture-based content:

```python
def setup_channel_nodes(layer, channel, endpoints):
    """
    Create texture pipeline with optional color node
    
    Texture Mode:
    Coordinates → Mapping → Texture → Mix Node → Layer Output
    
    Color Mode:
    RGB Node → Mix Node → Layer Output
    """
```

**Features**:
- Image texture painting
- Texture mode (with UV mapping)
- Color mode (solid RGB)
- Mode cycling

---

## Paint Pipeline

### Paint Operator Flow
**File**: `operators/paint.py` → `LP_OT_PaintChannel`

```python
def invoke(self, context, event):
    # 1. Validate setup, prompt for resolution if needed
    if resolution not set:
        return context.window_manager.invoke_props_dialog(self)
    return self.execute(context)

def execute(self, context):
    # 2. Create/reuse texture image
    tex_node = get_texture_node(layer, channel)
    img = create_image("BaseName", resolution, default_color, is_data=False)
    tex_node.image = img
    
    # 3. Save all unsaved images to disk
    save_all_unsaved()
    
    # 4. Switch to texture paint mode
    paint_image(img)
    
    # 5. Mark bake not active
    return {"FINISHED"}
```

### Image Management
**File**: `operators/utils_paint.py`

#### Image Creation
```python
def create_image(name, resolution, color, is_data=False):
    """Create new image with color space"""
    img = bpy.data.images.new(
        name, resolution, resolution,
        alpha=True,
        is_data=is_data  # Linear color space
    )
    pixels = np.zeros((resolution * resolution, 4), dtype=np.float32)
    pixels[:] = color  # Set initial color
    img.pixels = pixels.flatten()
    return img
```

#### Texture Persistence
```python
# Unsaved images in memory (persist in .blend)
# ↓ When paint stops or mode switches
# Saved to disk: <blend_dir>/layer_painter_textures/<Material>_<Channel>.png
```

---

## Baking Architecture

### Bake Setup/Cleanup Pattern
**File**: `operators/baking.py`

```python
def bake_setup(ntree, channel):
    """
    1. Create emission node
    2. Connect channel output → emission input
    3. Create output node
    4. Connect emission → output
    5. Set as active output
    """
    # Result: Shader can now be baked to texture

def bake_cleanup(ntree, channel):
    """
    1. Save baked image to disk
    2. Remove emission node
    3. Remove output node
    4. Material returns to previous state
    """
```

### Macro Chaining
```python
# Multiple bake operations chained via macro
# Execution: Setup1 → Render1 → Cleanup1 → Setup2 → Render2 → Cleanup2
# Sequential processing prevents concurrency issues
```

### Bake Status Tracking
```python
# In handlers.py
IS_BAKING = False  # Global flag

def frame_change_handler(dummy):
    """Check render completion"""
    if IS_BAKING and render_complete():
        trigger_next_bake()
```

---

## Node Graph Management

### Node Organization
**File**: `data/utils_nodes.py`

#### Organize Tree Layout
```python
def organize_tree_layout(ntree, start_node, spacing=400):
    """
    Right-to-left layout with columns:
    
    1. Get node list from output backwards
    2. Group into horizontal distance columns
    3. Position each column with spacing
    """
```

#### Recursive Node Cleanup
```python
def remove_connected_left(ntree, node):
    """Remove node and all upstream dependencies"""
    for inp in node.inputs:
        for link in inp.links:
            remove_connected_left(ntree, link.from_node)  # Recurse
    ntree.nodes.remove(node)
```

### Node Group Operations
**File**: `data/utils_groups.py`

#### Add Group Input/Output
```python
def add_input(node_group, socket_type, name):
    """
    Create input on node group with UID socket
    
    Returns: (input_socket, group_input_socket)
    """
    inp = node_group.inputs.new(socket_type, name)
    return inp, node_group.inputs[-1]  # Socket with UID

def add_output(node_group, socket_type, name):
    """Similar to add_input but for outputs"""
```

---

## Performance Patterns

### Caching Strategy

1. **Cache Expensive Lookups**:
   - Node tree traversals
   - UID-based lookups
   - Complex queries

2. **Clear on Events**:
   - File load → clear all caches
   - Undo/redo → clear all caches
   - Topology change → clear caches

3. **Module-Level Caches**:
   ```python
   # At module top
   _cache = {}  # All caches global to module
   
   def clear_caches():
       global _cache
       _cache = {}  # Called in handlers.py
   ```

### Optimization Techniques

1. **Batch Node Operations**:
   - Collect all changes
   - Execute in single update cycle
   - Reduces depsgraph recalculations

2. **Lazy Evaluation**:
   - Don't compute until needed
   - Cache computed values
   - Invalidate on relevant events

3. **GPU Baking**:
   - Use CUDA for 10-50x speedup
   - Automatic detection in Blender
   - Fallback to CPU if unavailable

---

## Error Handling

### Error Recovery Pattern

```python
def safe_operation(layer_uid):
    """Never crash, always inform user"""
    try:
        layer = get_layer_by_uid(layer_uid)
        if not layer:
            raise ValueError(f"Layer {layer_uid} not found")
        # ... operation ...
    except RuntimeError as e:
        logger.error(f"Operation failed: {e}")
        # Show user-friendly message
        return {"FINISHED"}  # Or {"CANCELLED"}
```

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `RuntimeError: Couldn't find layer node` | Layer node was deleted | Delete layer, recreate |
| `ValueError: Material not found` | Material UID invalid | Reinitialize material |
| `AttributeError: 'NoneType' has no attribute 'uid'` | Stale cache | Run handlers.clear_caches() |

---

## Testing Strategy

### Unit Tests
- **Data Models**: Test UID generation, property setting
- **Node Operations**: Test node creation, removal, cleanup
- **Cache Invalidation**: Test clear_caches() clears all state

### Integration Tests
- **Paint Workflow**: Create layer → paint → stop painting
- **Bake Workflow**: Setup → render → cleanup
- **Undo/Redo**: Verify caches clear correctly

### System Tests
- **File Load/Save**: UIDs persist across save/load
- **Multiple Materials**: Independent material operations
- **Complex Layers**: 10+ layers with multiple channels

---

## Development Guidelines

### Before Adding Features

1. **Check for UID Usage**: Does new code store object references?
   - If yes, use UIDs instead
   - Add cache clearing in handlers.py

2. **Validate Error Handling**: Will operation fail gracefully?
   - Test with missing nodes
   - Test with invalid UIDs
   - Test with stale references

3. **Verify Cache Clearing**: After undo/redo, does operation work?
   - Test with Ctrl+Z
   - Test with Ctrl+Shift+Z
   - Test with file load

### Code Review Checklist

- [ ] No direct object references stored (use UIDs)
- [ ] All error cases handled
- [ ] Cache clearing added to handlers.py
- [ ] Comprehensive docstrings
- [ ] Tests added (unit + integration)
- [ ] No circular imports
- [ ] Follows existing patterns

---

## Glossary

| Term | Definition |
|------|-----------|
| **UID** | 10-char hex string for persistent object lookup |
| **Handler** | Blender event handler (load, undo, depsgraph) |
| **Cache Invalidation** | Clearing cached references after state change |
| **Node Group** | Shader node subgraph (layer or channel) |
| **Endpoint** | Group input/output socket pair |
| **Bake** | Convert shader nodes to texture images |

---

**Version**: 1.0  
**Updated**: Phase 3 Implementation  
**Blender Version**: 4.0+
