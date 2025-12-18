# Layer Painter

A professional Blender add-on that brings layer-based texture painting directly into Blender's shader editor. Create complex materials using procedural layers, painted textures, masks, and filters—all within a non-destructive workflow.

## Features

### Layer System
- **FILL Layers**: Procedurally generated content (solid colors, gradients, patterns)
- **PAINT Layers**: Texture-based painting with direct viewport integration
- **Layer Opacity**: Per-layer and per-channel opacity control
- **Layer Stacking**: Intuitive layer ordering with drag-and-drop support

### Channel Management
- **Multi-Channel Support**: Base Color, Metallic, Roughness, Normal, Emission, Alpha, and more
- **Flexible Data Types**: COLOR (solid values) or TEXTURE (image-based) per channel
- **Channel Painting**: Direct texture painting mode with automatic image creation and management
- **Channel Baking**: Export channels to optimized textures

### Masking & Filtering
- **Procedural Masks**: Layer-level masking using shader nodes
- **Advanced Filtering**: Query and filter layers by name, type, visibility, and custom properties
- **Blend Modes**: Multiple blend modes for layer compositing
- **Layer Groups**: Organize layers into hierarchical groups

### Asset Management
- **Asset Registry**: Built-in system for masks, filters, and material presets
- **Semantic Versioning**: Version-aware asset dependencies
- **Import/Export**: Bundle and share assets as `.lpa` archives
- **Dependency Validation**: Automatic checking of asset requirements

### Performance & Optimization
- **Smart Caching**: LRU+TTL cache system for materials, nodes, and channels
- **Batch Processing**: Efficient multi-layer operations
- **Performance Profiling**: Built-in metrics for operation timing and resource usage
- **Undo/Redo Safe**: Proper cache invalidation on Blender state changes

## Installation

1. Clone or download this repository
2. Copy the `layer-painter` folder to your Blender addons directory:
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\{version}\scripts\addons\`
   - **macOS**: `~/Library/Application Support/Blender/{version}/scripts/addons/`
   - **Linux**: `~/.config/blender/{version}/scripts/addons/`
3. Open Blender and navigate to Edit > Preferences > Add-ons
4. Search for "Layer Painter" and enable the checkbox
5. Access the addon from the 3D Viewport sidebar (N key) under the "Layer Painter" tab

## Quick Start

1. **Create a Material**: Select an object and add a material in the Material Properties panel
2. **Add Layers**: In the Layer Painter panel (3D Viewport > N key), click "Add Layer"
3. **Choose Layer Type**: Select FILL for procedural content or PAINT for texture painting
4. **Configure Channels**: Add channels (Base Color, Roughness, etc.) to your layer
5. **Paint or Adjust**: Use Paint mode for textures or adjust procedural values for FILL layers
6. **Stack & Mask**: Add more layers, reorder them, and apply masks for complex effects

For detailed workflows, see [USER_GUIDE.md](USER_GUIDE.md).

## Development

### Requirements
- Blender 4.0+
- Python 3.10+ (included with Blender)

### Development Setup
1. Clone the repository into your Blender addons folder
2. Enable Developer Extras: Preferences > Interface > Developer Extras
3. Enable Blender's Python Console: Window > Toggle System Console
4. Reload scripts after changes: F3 > "Reload Scripts" or restart Blender

### Code Standards
- **PEP 8**: Follow Python style conventions
- **Type Hints**: Use type annotations for function parameters and returns
- **Docstrings**: Document all public functions, classes, and methods
- **UID Pattern**: Always use UIDs for cross-reference persistence, never direct object refs
- **Cache Invalidation**: Clear caches in handlers.py for undo/redo/file load events

### Testing Protocol
Before submitting changes:
- Layer operations (create, delete, reorder, undo/redo)
- Paint workflow (enter paint mode, save textures, exit)
- Baking (single channel, multiple channels, macro chain)
- File operations (save, load, verify UID persistence)
- Cache invalidation (test after undo, redo, and file reload)

## Architecture

### Module Structure
```
layer-painter/
├── ui/              # UI panels and layout (VIEW_3D, NODE_EDITOR)
├── operators/       # User-triggered operations (commands)
├── data/            # Core business logic (layers, channels, materials)
├── assets/          # Asset management (masks, filters)
├── addon/           # Addon configuration and preferences
├── handlers.py      # Blender event handlers (load, save, undo, redo)
├── constants.py     # Global constants (node types, socket types, names)
└── utils.py         # Utility functions (UID generation, redraw, active material)
```

### Key Concepts

**Layer**: A compositing layer containing one or more channels. Types: FILL (procedural) or PAINT (texture-based).

**Channel**: A material output (e.g., Base Color, Normal, Roughness). Stores default value and data type (COLOR or TEXTURE).

**Mask**: A procedural node group that modulates layer/channel output. Stacked like Photoshop layer masks.

**Filter**: A procedural node group applied to layer output. Different from masks in application point.

**UID**: Unique identifier (10-char hex) for layers, channels, and materials. Used for persistent references.

### Data Flow
1. User creates Material > Layer > Channel
2. Layer initializes node group in material shader editor
3. Channel adds input/output sockets and nodes to layer group
4. Layer creates nodes based on channel data type (COLOR/TEXTURE)
5. Masks/Filters are chained as node groups
6. Layer opacity and channel opacity modulate final output

### Caching Strategy
- **Channel Cache**: `cached_materials`, `cached_inputs` – Material and input socket references by UID
- **Layer Cache**: `cached_materials`, `cached_nodes` – Material and node group references by UID
- **Invalidation Points**: File load, undo, redo, depsgraph updates
- **Rationale**: Blender object references become invalid after state changes; UIDs provide stable lookup

### Contributing

We welcome contributions for bug fixes, feature improvements, and asset creation (masks, filters, presets).

**Workflow:**
1. Fork the repository
2. Create a feature branch
3. Make your changes following the code standards above
4. Test thoroughly using the testing protocol
5. Submit a pull request with a clear description

**What We Need:**
- Bug fixes and stability improvements
- New layer types and blend modes
- Advanced mask and filter presets
- Performance optimizations
- Documentation improvements

## Technical Stack

- **Blender API**: `bpy` module for Blender integration
- **Shader Nodes**: Material node tree manipulation via `bpy.types.ShaderNode*`
- **Property Groups**: Custom properties using `bpy.props` for persistent data
- **Handlers**: Event-driven architecture with `bpy.app.handlers`
- **Caching**: Custom LRU+TTL cache implementation for performance
- **UID System**: 10-character hexadecimal identifiers for stable references

## Documentation

| Document | Description |
|----------|-------------|
| [USER_GUIDE.md](USER_GUIDE.md) | Complete user guide with step-by-step workflows |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, entity relationships, and implementation patterns |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues, error messages, and solutions |
| [API.md](API.md) | Full API reference with code examples |
| [ASSETS_GUIDE.md](ASSETS_GUIDE.md) | Asset system documentation (versioning, dependencies, bundles) |

## License

This project is licensed under the GPL-3.0 License. See [LICENSE](LICENSE) for details.

