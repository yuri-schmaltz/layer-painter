# Layer Painter – User Guide

A comprehensive guide to using Layer Painter, the Substance Painter-like texture painting workflow in Blender.

---

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Core Concepts](#core-concepts)
4. [Working with Materials](#working-with-materials)
5. [Layer Management](#layer-management)
6. [Paint Workflow](#paint-workflow)
7. [Fill Layers](#fill-layers)
8. [Channels & Outputs](#channels--outputs)
9. [Baking System](#baking-system)
10. [Masking & Filters](#masking--filters)
11. [Exporting Textures](#exporting-textures)
12. [Tips & Tricks](#tips--tricks)
13. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites
- **Blender 4.0+** (Layer Painter requires Blender 4.0 or later)
- **GPU with CUDA support** (recommended for faster baking)

### Installation Steps

1. **Download Layer Painter**
   - Clone the repository or download the ZIP file

2. **Install in Blender**
   - Open Blender
   - Go to Edit → Preferences → Add-ons
   - Click "Install..." and select the `layer-painter` folder
   - Search for "Layer Painter" and enable it

3. **Verify Installation**
   - Create a new material on an object
   - You should see a "Layer Painter" panel in the shader editor

---

## Getting Started

### First Time Setup

1. **Create a Test Object**
   - Add a default cube to your scene
   - Assign a new material to it

2. **Initialize Layer Painter**
   - Select the object and material
   - In the Shader Editor, look for the "Layer Painter" panel
   - Click "New Material" to initialize Layer Painter for this material

3. **Create Your First Layer**
   - Click "New Layer" in the Layers panel
   - Select "FILL" or "PAINT" layer type
   - Set the layer name

4. **Start Painting**
   - Click the layer to activate it
   - For PAINT layers: Click "Paint Channel" to start texture painting
   - For FILL layers: Adjust settings in the Layer Settings panel

### Basic Workflow

```
1. Create Material → 2. Add Layer → 3. Add Channel → 4. Paint/Configure → 5. Bake or Export
```

---

## Core Concepts

### Materials
A **Material** is the top-level container for all texture layers. Each material has:
- Multiple layers (organized in a stack)
- Multiple channels (Base Color, Normal, Roughness, etc.)
- Export settings and presets

**Key Points:**
- Each object can have multiple materials
- Materials are independent; changes don't affect other materials
- Layer Painter enhances standard Blender materials

### Layers
A **Layer** is a unit of texture composition. Types:
- **FILL**: Procedurally generated (solid colors, patterns)
- **PAINT**: Texture-based (hand-painted images)

**Layer Properties:**
- Name, enabled/disabled state, opacity
- Blend mode (Normal, Multiply, Screen, Overlay, etc.)
- Each layer can have multiple channels

### Channels
A **Channel** is a material output (e.g., Base Color, Normal, Roughness). Each channel stores:
- Input node (connected to layer output)
- Output socket (connects to shader output)
- Data type (COLOR for Base Color, TEXTURE for Normal)

---

## Working with Materials

### Creating a New Material

1. In the Shader Editor, switch to **Layer Painter** panel
2. Click **"New Material"**
3. Select the object and material to initialize
4. The material is now ready for Layer Painter

### Viewing Material Structure

- **Viewport Panel**: Shows material tree and properties
- **Node Editor**: Shows Shader Editor with material nodes
- **Layer Stack**: Shows all layers for the material

### Material Settings

- **Output Channels**: Select which channels to bake/export
- **Export Path**: Set where textures are saved
- **Resolution**: Default texture resolution for new paint layers
- **Color Space**: Linear (data) or sRGB (color)

---

## Layer Management

### Creating Layers

1. **New Layer**
   - Right-click in the Layers panel → "New Layer"
   - Choose layer type: FILL or PAINT

2. **Duplicate Layer**
   - Right-click layer → "Duplicate Layer"
   - Creates a copy with all channels and settings

3. **Delete Layer**
   - Right-click layer → "Delete Layer"
   - Confirmation dialog prevents accidental deletion

### Organizing Layers

- **Move Layers**: Drag to reorder in the stack
- **Rename**: Double-click layer name to edit
- **Enable/Disable**: Click eye icon to toggle visibility
- **Lock Layers**: Click lock icon to prevent accidental edits

### Layer Settings Panel

Each layer has a settings panel showing:
- Layer name, type, and opacity
- Blend mode
- Channel configuration
- Current data type (TEX or COL)

---

## Paint Workflow

### Starting a Paint Session

1. **Select a PAINT Layer**
   - Click the layer name in the Layers panel

2. **Choose a Channel**
   - In the Layer Settings panel, select a channel (Base Color, Normal, etc.)

3. **Start Painting**
   - Click **"Paint Channel"** button
   - Blender switches to Texture Paint mode
   - A blank texture is created (or existing texture is loaded)

### Texture Paint Controls

- **Brush Selection**: Press F to select brush, Shift+F for brush size
- **Color Picker**: Hold Ctrl and click to sample color
- **Undo/Redo**: Ctrl+Z / Ctrl+Shift+Z
- **Switch Texture**: Paint different channels by switching layers

### Saving Painted Textures

Textures are automatically saved when you:
1. Stop the paint session (click "Stop Painting")
2. Exit Texture Paint mode
3. Switch to a different image

**Saved Location**: `<blend_file_dir>/layer_painter_textures/`

### Paint Layer Modes

#### Texture Mode (Default)
- Paint on UV-mapped textures
- Supports image import and export
- Full texture resolution control

#### Color Mode
- Use solid RGB colors instead of textures
- Useful for base colors and procedural adjustments
- Lightweight (no image memory)

**Toggle Mode**: Click **"Cycle Data Type"** in Layer Settings

---

## Fill Layers

### Creating Solid Color Fills

1. **Create a FILL Layer**
   - Right-click in Layers panel → "New Layer"
   - Select "FILL" type

2. **Configure Fill Properties**
   - In Layer Settings panel, set channel values
   - Adjusts base color or other properties

3. **Adjust Opacity**
   - Use layer opacity slider to blend with layers below

### Procedural Fill Operations

- **Solid Color Fill**: Set RGB values for uniform color
- **Color Ramp**: Use gradient editor for color transitions
- **Procedural Textures**: Connect procedural nodes (coming in P3-3)

---

## Channels & Outputs

### Understanding Channels

Each layer can output to multiple channels:
- **Base Color**: Albedo/diffuse color
- **Normal**: Surface normal map (blue-purple)
- **Roughness**: Specular response (0 = mirror, 1 = matte)
- **Metallic**: Metallicness factor
- **Emission**: Self-illumination

### Adding Channels

1. **In Layer Settings panel, click "+ Add Channel"**
2. **Select channel type** (Base Color, Normal, etc.)
3. **Choose default data type** (COLOR or TEXTURE)
4. Channel is added to the layer

### Configuring Channel Output

- **Input Socket**: Where layer data comes in
- **Output Socket**: Connects to next layer or material output
- **Data Type**: COLOR (RGB) or TEXTURE (image)
- **Blend Mode**: How to combine with layer below

---

## Baking System

### What is Baking?

Baking converts shader node outputs to texture images. Use baking to:
- Create final texture maps from procedural nodes
- Prepare textures for game engine export
- Optimize material complexity

### Baking Workflow

1. **Select Material**
   - In viewport, select object with Layer Painter material

2. **Configure Bake Settings**
   - Choose channels to bake (Base Color, Normal, etc.)
   - Set output resolution
   - Select output location

3. **Start Bake**
   - Click **"Bake All Channels"** button
   - Material switches to Cycles render engine temporarily
   - Progress bar shows bake status

4. **Bake Completes**
   - Textures are automatically saved to disk
   - Material returns to previous render engine
   - Baked images appear in viewport

### Baking Best Practices

- **Resolution**: Match texture resolution to mesh density
- **Sample Count**: Higher samples = better quality but slower bake
- **GPU vs CPU**: GPU baking (CUDA) is 10-50x faster
- **Margin**: Expand sample area to prevent edge artifacts

---

## Masking & Filters

### Creating Masks

1. **Layer Mask**
   - Right-click layer → "Add Mask"
   - Mask is black-to-white gradient (black = transparent, white = opaque)

2. **Mask Painting**
   - Click "Paint Mask" to enter mask painting mode
   - Paint in black to hide layer areas
   - Paint in white to reveal layer areas

### Advanced Filtering

- **Blur**: Gaussian blur on layer (P4 feature)
- **Sharpen**: Increase detail (P4 feature)
- **Levels**: Adjust brightness/contrast (P4 feature)
- **Curves**: Advanced tone mapping (P4 feature)

---

## Exporting Textures

### Export Formats

- **PNG**: Lossless, supports transparency (recommended)
- **EXR**: High dynamic range, 32-bit float
- **TGA**: Uncompressed, compatibility

### Export Workflow

1. **Select Export Settings**
   - In Export panel, choose channels to export
   - Set resolution and format
   - Choose output folder

2. **Export**
   - Click **"Export All Channels"**
   - Textures are saved as individual files

3. **Organize Files**
   - All textures saved to: `<output_folder>/<material_name>_<channel>.png`

### Export Presets

- **Game Engine**: Optimized for real-time (PNG, 2K)
- **Substance Painter**: High fidelity exchange format
- **Marmoset Toolbag**: Production-quality textures
- **Custom**: User-defined export configuration

---

## Tips & Tricks

### Performance Optimization

1. **Lower Texture Resolution**
   - Start with 2K (2048×2048), upscale if needed
   - Reduces memory usage and paint lag

2. **Disable Viewport Preview**
   - In preferences, toggle "Real-time Preview"
   - Improves performance on slower systems

3. **Use Fill Layers for Base Colors**
   - Solid colors use no memory
   - Paint only when detail is needed

### Workflow Acceleration

1. **Keyboard Shortcuts** (customize in Preferences)
   - Alt+P: Start/stop painting
   - Alt+B: Bake all channels
   - Alt+E: Export textures

2. **Layer Duplication**
   - Duplicate complex layers instead of recreating
   - Adjustments faster than building from scratch

3. **Batch Operations**
   - Use layer groups (coming P4) to organize and operate on multiple layers

### Creative Techniques

1. **Layered Detail**
   - Base color fill → Normal map overlay → Roughness layer
   - Build complexity through layer stacking

2. **Mask Blending**
   - Use layer masks to selectively reveal paint details
   - Combine multiple paint layers with masks for non-destructive editing

3. **Procedural Blending**
   - Use noise patterns and procedural generators
   - Combine with painted layers for organic textures

---

## Troubleshooting

### Common Issues

#### "Material not initialized with Layer Painter"
**Solution**: Click "New Material" in the Layer Painter panel for the selected material.

#### Paint texture not appearing
**Solution**: 
1. Verify object has UV map
2. Check texture coordinates in material editor
3. Ensure paint mode is active (Texture Paint mode in top-left)

#### Bake is very slow
**Solution**:
1. Check GPU is active (Render > Compute Device > CUDA)
2. Lower sample count (Settings > Bake > Samples)
3. Reduce texture resolution temporarily

#### Layer disappeared after undo
**Solution**: This is a known Blender limitation. Use File > Recover Auto Save if critical.

#### Export path not working
**Solution**:
1. Verify folder exists and is writable
2. Use full absolute path (e.g., `C:/textures/`)
3. Check file permissions

#### Normal map appears inverted
**Solution**: 
1. In Export settings, toggle "Flip Green Channel"
2. Or in shader editor, add ColorRamp and invert

### Getting Help

- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- **Troubleshooting Guide**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Issue Tracker**: GitHub Issues for bug reports
- **Community**: Blender artists forum for sharing techniques

---

## Glossary

| Term | Definition |
|------|-----------|
| **Bake** | Convert shader nodes to texture images |
| **Channel** | Material output (Base Color, Normal, etc.) |
| **Fill Layer** | Procedurally generated layer (solid color) |
| **Layer** | Compositing unit (FILL or PAINT type) |
| **Material** | Top-level container for texture layers |
| **Mask** | Black-to-white layer for selective opacity |
| **Paint Layer** | Texture-based layer (hand-painted images) |
| **UID** | Unique identifier for persistent object lookup |

---

**Version**: 1.0  
**Updated**: Phase 3 Implementation  
**Blender Version**: 4.0+
