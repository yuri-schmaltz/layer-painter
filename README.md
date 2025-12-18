# Layer Painter

Layer Painter is a addon for blender, made to bring a workflow similar to a tool like substance painter or armor paint directly inside blender.
The goal here is to provide a workflow which makes the tools mentioned above unnecessary for a lot of projects, keeping the work fully inside of blender.

**[Discord Server](https://discord.com/invite/s9dawzV5JU)**

The discord server is used as the main place to share information and work regarding the addon. You can join it to ask questions and get more information about contributing.

## Overview
- [Addon](#addon)
- [Development](#development)
- [Architecture](#architecture)
- [Additional Assets](#additional-assets)
- [Tutorials](#tutorials)
- [Contributors](#contributors)
- [Changelog](#changelog)

## Addon
WIP (This section will contain a written description on how to use the addon)

## Development

### Setup
1. Clone the repository into your Blender addons folder: `~/.config/blender/X.Y/scripts/addons/`
2. Enable the addon in Blender preferences (Edit > Preferences > Add-ons > Layer Painter)
3. Open Blender console (Window > Toggle System Console) to see debug messages

### Code Style
- Follow PEP 8 conventions
- Use descriptive variable/function names
- Add docstrings to all functions and classes
- Include type hints where applicable (Python 3.9+)

### Testing
Before submitting PRs, test:
- Create/remove/move layers and verify no crashes
- Undo/redo operations (Ctrl+Z / Ctrl+Shift+Z)
- Paint textures and verify image creation
- Bake channels and verify progress feedback

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
- `channel.cached_materials` / `channel.cached_inputs`: Cache material/input references by UID
- `layer.cached_materials` / `layer.cached_nodes`: Cache material/node references by UID
- **Invalidation**: Cleared on file load, undo/redo, depsgraph update
- **Rationale**: Blender object references can become invalid; UIDs provide persistent lookup

## Additional Assets
- [Texture Based Grunge Maps by BongoCat - Already Included](https://drive.google.com/file/d/11sJSfT7jJohLHouMSQB5oc4GzUHtOifO/view)

## Tutorials
[Layer Painter 2, Complete Tutorial and free scene by blanchsb](https://www.youtube.com/watch?v=YDt9LFbjJU4)

[Layer Painter 2, Materials and Asset Browser Tutorial by blanchsb](https://www.youtube.com/watch?v=glMGVkGhtAg)

## Contributors
This addon is maintained by contributors. This most importantly includes contributions for code but also for assets like masks and filters and tutorials. If you're interested in contributing any of these, just open a pull request for adding them yourself or join the discord server and ask for more information.

### Code Contributions
You can fix bugs, add your own feature ideas or other people ideas. If it's something bigger ask on the discord server before you start working to know if someone else already started on it or if you should make changes to your initial idea. When you're done, submit a pull request and your code can be added.

#### Open features
- [ ] Baking different masks to images (Bevel, Pointiness, Curvature, ...)
- [ ] Baking masks / mask stacks to a single image mask
- [ ] Other layer types (for example a paint only layer or a material layer)
- [ ] PBR Texture assets
- [ ] Brush assets for texture painting
- [ ] Different channel presets for NPR, PBR, ...

## Changelog
#### v2.0.0
- Initial release

#### v2.0.1
 - Added 2, Cycles Only, Edge/Cavity Mask: 'Edge and Corner Mask - Bevel', 'Edge Mask Pointiness' 
 - Added 1, Eevee and Cycles Edge/Cavity Mask:'Cavity, Crevice, Innercorner Mask - from AO'
 - Added 10 new Procedural Grunge Masks for Eevee and Cycles "Procedural Noise Masks": 'Gneiss, Malachite, Agate', 'Rust', 'Concrete/Marble', 'Dusty, 'Dirt, 'Smuged Dirt', 'Dirt Spots', 'Distorted Spots', 'Spline Noise', 'Noisy Lines'

---

## Documentation (Phases 3 & 4)

The following documentation was added to cover advanced features, optimization, and asset management:

- [USER_GUIDE.md](USER_GUIDE.md) – Complete user guide and workflows
- [ARCHITECTURE.md](ARCHITECTURE.md) – System design, entity model, and patterns
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) – Common issues and solutions
- [API.md](API.md) – Full API reference with examples
- [LOGGING_INTEGRATION.md](LOGGING_INTEGRATION.md) – Production logging setup and examples
- [ASSETS_GUIDE.md](ASSETS_GUIDE.md) – Asset system (versioning, dependencies, import/export)
- [FILTERING_EXAMPLES.md](FILTERING_EXAMPLES.md) – Advanced filtering and layer queries
- [OPTIMIZATION_EXAMPLES.md](OPTIMIZATION_EXAMPLES.md) – Caching, batching, profiling examples
- [ASSETS_EXAMPLES.md](ASSETS_EXAMPLES.md) – Practical asset workflows and bundle creation
- [PHASES_3_4_UPDATE.md](PHASES_3_4_UPDATE.md) – Summary of new features

