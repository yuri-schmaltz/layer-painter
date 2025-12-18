# Layer Painter – Troubleshooting Guide

Quick reference for common issues and solutions.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Material & Layer Issues](#material--layer-issues)
3. [Paint Workflow Issues](#paint-workflow-issues)
4. [Baking Issues](#baking-issues)
5. [Export Issues](#export-issues)
6. [Performance Issues](#performance-issues)
7. [Undo/Redo Issues](#undoredo-issues)
8. [Node Editor Issues](#node-editor-issues)
9. [Debug Logging](#debug-logging)
10. [Getting Additional Help](#getting-additional-help)

---

## Installation Issues

### Add-on Won't Install

**Symptom**: "Failed to install add-on" when selecting folder

**Solutions**:
1. **Verify Blender Version** (requires 4.0+)
   - Help → About Blender → check version number
   - Install latest Blender from blender.org if older

2. **Check Folder Structure**
   - Ensure `__init__.py` exists in root folder
   - Correct structure:
     ```
     layer-painter/
     ├─ __init__.py
     ├─ handlers.py
     ├─ constants.py
     ├─ data/
     ├─ operators/
     └─ ui/
     ```

3. **Reinstall from Scratch**
   - Edit → Preferences → Add-ons
   - Search "Layer Painter" → Remove if present
   - Restart Blender
   - Edit → Preferences → Add-ons → Install → Select folder
   - Enable add-on

### Add-on Enabled But No UI Appears

**Symptom**: Add-on in list but no Layer Painter panel

**Solutions**:
1. **Switch to Shader Editor**
   - Layer Painter panel only appears in Shader Editor
   - Top-right: Change from "Properties" to "Shader Editor"

2. **Select Object with Material**
   - Ensure selected object has a material assigned
   - In Material Properties, confirm material exists

3. **Check Add-on Folder Permissions**
   - Windows: Add-on folder must be readable by Blender
   - Ensure no "Access Denied" errors in system
   - Move to non-protected folder if needed

---

## Material & Layer Issues

### "Material not initialized with Layer Painter"

**Symptom**: Panel shows error but no "New Material" button

**Solutions**:
1. **Click "New Material" Button**
   - This initializes the selected material
   - Should add Layer Painter properties

2. **Verify Material Selection**
   - In Material Properties, select correct material
   - In Shader Editor, ensure correct material displayed

3. **Re-initialize If Corrupted**
   - Delete all layers (use "Delete" button)
   - Delete material and recreate
   - Click "New Material" to reinitialize

### Layer Disappeared After Undo

**Symptom**: Clicked Ctrl+Z and layer vanished from list

**Solutions**:
1. **Redo the Undo** (Ctrl+Shift+Z)
   - May restore if undo was partial

2. **Check Layer Still Exists**
   - In Shader Editor, look for layer node group
   - If visible, layer data may still exist but UI didn't refresh
   - Deselect/reselect material to refresh

3. **Save Work Periodically**
   - Blender undo history is limited (default 32 steps)
   - Save with File → Save (Ctrl+S) before major operations
   - Use File → Recover Auto Save if needed

4. **Known Limitation**
   - Some Blender undo states can cause layer references to break
   - This is a Blender limitation, not Layer Painter bug
   - Workaround: Use File → Recover Auto Save

### Cannot Add New Layer

**Symptom**: "New Layer" button does nothing or shows error

**Solutions**:
1. **Verify Material Selected**
   - Select material in Material Properties first
   - Click "New Material" if not initialized

2. **Check Material Property Group**
   - Shader Editor → Material Properties → check "Layer Painter" section
   - If missing, re-run "New Material"

3. **Restart Blender**
   - Close and reopen Blender
   - Open .blend file again
   - Try creating layer

---

## Paint Workflow Issues

### Paint Texture Not Appearing on Model

**Symptom**: Paint on texture but model appears unchanged

**Solutions**:
1. **Check UV Mapping**
   - Select object
   - Switch to UV Editing workspace
   - Verify object has non-overlapping UV map
   - If missing, add UV map:
     - Object Mode → UV → Unwrap

2. **Check Texture Coordinates in Shader**
   - In Shader Editor, check layer node group
   - Texture Coordinate node should be connected
   - If missing, cycle data type to recreate:
     - Layer Settings → Cycle Data Type

3. **Check Viewport Shading**
   - Top-right: Change shading mode
   - Texture Paint preview only shows in "Material Preview" (3rd sphere icon)
   - Or "Rendered" mode (4th sphere icon)

4. **Verify Image is Saved**
   - After painting, click "Stop Painting"
   - Check `<blend_dir>/layer_painter_textures/` folder
   - Image file should exist with name like `Material.001_BaseColor.png`

### Paint Tool Not Working

**Symptom**: Brush moves but doesn't paint anything

**Solutions**:
1. **Verify Texture Paint Mode Active**
   - Top-left should show "Texture Paint"
   - If not, click to switch (or Tab key)

2. **Check Tool Settings**
   - Right panel → Tool Settings
   - Verify brush size > 0 (F key to adjust)
   - Check opacity > 0 (Shift+F to adjust)

3. **Ensure Image is Assigned**
   - Click "Paint Channel" again to verify image created
   - Check texture node has image assigned
   - Switch tabs in Texture Paint panel to refresh

### Paint Color Picker Not Working

**Symptom**: Ctrl+Click doesn't sample color

**Solutions**:
1. **Switch to Texture Paint Mode**
   - Ensure mode is "Texture Paint" (not "Weight Paint")

2. **Check Brush Settings**
   - Right panel → Tool → ensure sample location is "Image Plane"
   - Check "Sample Texture Paint Object" is enabled

3. **Verify Color Mode**
   - If layer is in color mode (not texture), picker may not work
   - Cycle to texture mode: Layer Settings → Cycle Data Type

### Image Not Saving After Paint

**Symptom**: Painted texture disappears after stopping paint mode

**Solutions**:
1. **Check File Path Permissions**
   - Verify `<blend_dir>/layer_painter_textures/` folder is writable
   - Windows: Right-click folder → Properties → Security → check permissions
   - If read-only, move .blend file to Documents or Desktop

2. **Check Disk Space**
   - Verify hard drive has enough space (>500MB recommended)
   - Check available space in Windows: File Explorer → right-click drive

3. **Verify Save in Preferences**
   - Layer Painter → Preferences → toggle "Auto Save Images"
   - Manually save: Click "Stop Painting" button

4. **Reimport Image to Scene**
   - If image file exists but not loaded in Blender:
   - Image Editor → Open Image
   - Select `.png` file from `layer_painter_textures/`

---

## Baking Issues

### Bake Produces Black Image

**Symptom**: Bake completes but result is completely black

**Solutions**:
1. **Check Material Has Actual Content**
   - Verify layers have color data (not invisible)
   - Try baking simpler material first (single fill layer)

2. **Verify Emission Node Connected**
   - In Shader Editor during bake, check nodes:
   - Should see "Emission" node connected to output
   - If missing, bake setup failed

3. **Check Render Engine**
   - Bake uses Cycles render engine
   - Render Properties → Render Engine → should show "Cycles" during bake
   - If CPU-only: Bake may be slow but should work

4. **Lower Sample Count**
   - Bake Settings → Samples → reduce to 32
   - Low samples = fast but noisy
   - Try bake to verify it works

### Bake Is Extremely Slow

**Symptom**: Bake started 10+ minutes ago and still going

**Solutions**:
1. **Enable GPU Acceleration**
   - Edit → Preferences → System → Compute Device
   - Select CUDA (NVIDIA) or HIP (AMD)
   - If no option appears, GPU not supported
   - Restart Blender after change

2. **Lower Resolution**
   - Bake Settings → Resolution → reduce from 4K to 2K or 1K
   - Lower resolution = exponentially faster
   - Can upscale later if needed

3. **Reduce Sample Count**
   - Bake Settings → Samples → reduce to 32-64
   - Sample count is multiplier on time
   - Can increase later for final quality

4. **Reduce Complexity**
   - Remove unnecessary layers
   - Simplify material graph
   - Bake individual channels instead of all at once

5. **Check System Resources**
   - Close other applications (Chrome, etc.)
   - Free up RAM: Restart Blender
   - Monitor temperature: GPU should be <80°C

### Bake Produces Artifacts

**Symptom**: Bake result has streaks, seams, or noise

**Solutions**:
1. **Increase Sample Count**
   - Bake Settings → Samples → increase to 256+
   - More samples = cleaner result but slower

2. **Adjust Margin**
   - Bake Settings → Margin → increase from 16 to 32
   - Larger margin = more expanded sampling area
   - Prevents seam artifacts

3. **Fix UV Seams**
   - UV Editor → select seams (orange edges)
   - Select → Mark Seams
   - UV → Seam Weight → increase value
   - Tells Cycles to blend across seams

4. **Use Temporal Smoothing**
   - Render Properties → Denoise → enable "Temporal"
   - Reduces noise via frame averaging
   - Works for static materials

### Bake Memory Error

**Symptom**: "Out of Memory" error during bake or display

**Solutions**:
1. **Close Other Applications**
   - Free RAM: Chrome, video editors, etc.
   - Target: 8GB+ available for Blender

2. **Reduce Texture Resolution**
   - Start with 2K (2048×2048) instead of 4K
   - Resolution impacts memory quadratically

3. **Reduce Sample Count**
   - Bake Settings → Samples → reduce to 32-64

4. **Use CPU Instead of GPU**
   - CPU uses main RAM (usually more available)
   - Edit → Preferences → System → Compute Device → CPU
   - Will be slower but might work

---

## Export Issues

### Export File Not Created

**Symptom**: Export starts but no files appear in folder

**Solutions**:
1. **Verify Export Path**
   - Export Settings → Export Path
   - Click folder icon to verify path exists
   - Use absolute path: `C:/MyTextures/` not `./textures/`

2. **Check Folder Permissions**
   - Windows: Right-click folder → Properties → Security
   - Verify Blender has Write permission
   - If not, move to Documents or Desktop

3. **Verify Export Format**
   - Export Settings → Format → PNG or EXR
   - Ensure file format is correct

4. **Check Disk Space**
   - Export Settings → Resolution → check file size estimate
   - Verify hard drive has enough space

5. **Manually Save**
   - Image Editor → open image
   - Image → Save As
   - Select location and format

### Exported Normal Map Appears Inverted

**Symptom**: Normal map lighting appears reversed (concave instead of convex)

**Solutions**:
1. **Toggle Green Channel**
   - Export Settings → Advanced → Flip Green Channel
   - This inverts the Y component of normal map

2. **Fix in Post**
   - Image Editor → open exported normal map
   - Shader Editor → add ColorRamp after image
   - Invert colors: ColorRamp → Colors → Invert

3. **Engine-Specific Adjustment**
   - Different game engines expect different normal directions
   - Check engine documentation for normal map format
   - Adjust accordingly or use converter

### Color Space Wrong (Too Bright/Dark)

**Symptom**: Exported image brightness doesn't match in-engine

**Solutions**:
1. **Check Data Type**
   - Layer Settings → check channel is marked correctly
   - Base Color: Color (sRGB)
   - Normal/Roughness: Data (Linear)

2. **Verify Export Color Space**
   - Export Settings → Color Space
   - Match destination engine (typically sRGB for color, Linear for data)

3. **Post-Process**
   - Image Editor → open image
   - Curves node to adjust brightness/contrast
   - Re-save with correct color space

---

## Performance Issues

### Blender Freezes During Interaction

**Symptom**: UI hangs for 1-5 seconds when clicking buttons

**Solutions**:
1. **Reduce Viewport Preview Quality**
   - Preferences → Layer Painter → Toggle "Real-time Preview" off
   - Disables viewport updates during operations

2. **Simplify Material**
   - Remove unnecessary layers
   - Delete unused channels
   - Reduce node complexity

3. **Lower Texture Resolution**
   - Preferences → Layer Painter → Default Resolution → 1K or 512
   - Less memory = faster operations

4. **Disable Depsgraph Listener**
   - Preferences → Layer Painter → Toggle "Auto Update" off
   - Prevents depsgraph from recalculating on every change

5. **Increase Undo Memory**
   - Edit → Preferences → System → Undo Steps → increase to 64+
   - More undo steps can slow down operations slightly

### Paint Mode Has Lag

**Symptom**: Brush strokes are delayed or jerky

**Solutions**:
1. **Lower Texture Resolution**
   - File texture being painted is too large
   - Reduce from 4K to 2K or 1K
   - Can upscale after painting

2. **Simplify Shader**
   - Too many nodes = slow evaluation
   - Bake complex nodes to texture first
   - Rebuild with fewer nodes

3. **Use Solid Brush**
   - Soft brushes with high blur = slower
   - Settings → Brush → Hardness → increase to 1.0
   - Use soft brush only for final details

4. **Close Unnecessary Panels**
   - Properties panel takes rendering time
   - Close or minimize during painting
   - Focus viewport for best performance

---

## Undo/Redo Issues

### Undo Doesn't Restore Previous State

**Symptom**: Ctrl+Z pressed but nothing changed

**Solutions**:
1. **Verify Undo History Exists**
   - Edit → Undo History → check if previous steps listed
   - If history empty, nothing to undo

2. **Check for Cache Issues**
   - Layer should be recognized after undo
   - If UI shows stale data, restart Blender

3. **Save Before Major Operations**
   - Undo history is limited (default 32 steps)
   - File → Save (Ctrl+S) before major edits
   - Undo history resets after save

### Undo Causes Errors After Undo

**Symptom**: After Ctrl+Z, "layer not found" error appears

**Solutions**:
1. **This is Known Issue**
   - Some Blender undo states corrupt Layer Painter references
   - Workaround: Use File → Recover Auto Save

2. **Increase Undo Steps**
   - Edit → Preferences → System → Undo Steps
   - Increase from 32 to 64
   - More history = better undo reliability

3. **Save Frequently**
   - File → Save (Ctrl+S) after important edits
   - Prevents loss of work due to undo issues

4. **Report Issue**
   - If undo consistently broken:
   - File → Save As (backup)
   - Report to GitHub Issues with .blend file

---

## Node Editor Issues

### Layer Node Missing from Editor

**Symptom**: Layer listed in panel but not visible in Shader Editor

**Solutions**:
1. **Verify Shader Editor Shows Material**
   - Shader Editor → material dropdown → select material

2. **Check Layer Node Exists**
   - Shader Editor → scroll nodes → look for "Group" node with layer name
   - Should say "Group" type with layer name

3. **Force Refresh**
   - Deselect material, reselect
   - Close/reopen Shader Editor
   - Restart Blender

4. **Orphaned Node**
   - If node doesn't exist, layer is corrupted
   - Delete layer in Layer Painter panel
   - Recreate layer from scratch

### Channel Nodes Disconnected

**Symptom**: Channel outputs not connected to mix/output nodes

**Solutions**:
1. **Reconnect Manually** (Temporary)
   - Shader Editor → drag channel output to mix input
   - Verify connection established

2. **Rebuild Layer** (Permanent)
   - Delete layer in Layer Painter panel
   - Create new layer
   - Re-add channels

3. **Check for Corruption**
   - Save .blend file
   - Load in new Blender session
   - If issue persists, file may be corrupted

---

## Debug Logging

### Enable Debug Output

For developers debugging issues, enable logging:

```python
# In Python console:
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('LayerPainter')
logger.setLevel(logging.DEBUG)

# Now Layer Painter will print debug info to console
```

### Common Debug Messages

| Message | Meaning | Action |
|---------|---------|--------|
| `Layer UID not found` | Layer deleted or cache stale | Restart Blender |
| `Node tree missing` | Material corrupted | Delete/recreate material |
| `Couldn't find channel endpoint` | Channel removed incorrectly | Rebuild layer |
| `Image save failed` | Permissions or disk space | Check path/permissions |

---

## Getting Additional Help

### Official Resources

- **Documentation**: [USER_GUIDE.md](USER_GUIDE.md) (User documentation)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) (Technical deep-dive)
- **GitHub**: [layer-painter repo](https://github.com/your-repo) (Issue tracker)

### Community Support

- **Blender Artists Forum**: [polycount.com](https://polycount.com) for texturing tips
- **Stack Exchange**: [blender.stackexchange.com](https://blender.stackexchange.com)
- **Blender Discord**: Official Blender community server

### Reporting Bugs

When reporting issues on GitHub:

1. **Include Reproduction Steps**
   ```
   1. Create new material
   2. Add PAINT layer
   3. Click "Paint Channel"
   4. [Issue occurs]
   ```

2. **Attach .blend File**
   - Minimal reproducible .blend file
   - Include any custom textures/images

3. **System Info**
   - Blender version (Help → About)
   - GPU model and driver version
   - OS (Windows 10/11, Mac, Linux)

4. **Error Log**
   - If error message shown, include full text
   - Help → Toggle System Console (Windows)
   - Run from terminal (Mac/Linux)

---

**Version**: 1.0  
**Updated**: Phase 3 Implementation  
**Last Reviewed**: 2024
