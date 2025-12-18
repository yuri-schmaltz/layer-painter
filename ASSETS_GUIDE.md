# Layer Painter Extended Asset System Guide

## Overview

The Extended Asset System provides comprehensive asset management with versioning, dependency resolution, and marketplace support. It enables professional asset distribution, version control, and dependency tracking for Layer Painter projects.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Asset Types](#asset-types)
5. [Versioning](#versioning)
6. [Dependencies](#dependencies)
7. [Import/Export](#importexport)
8. [Asset Bundles](#asset-bundles)
9. [Best Practices](#best-practices)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)

---

## Installation

The asset system is included with Layer Painter. Import the extended asset module:

```python
from layer_painter.assets_extended import (
    AssetManager, Asset, AssetBundle,
    AssetMetadata, AssetType, AssetCategory
)
```

### Setup

```python
# Initialize asset manager for your project
manager = AssetManager("/path/to/project")

# Assets will be stored in: /path/to/project/assets/
# Registry will be saved to: /path/to/project/asset_registry.json
```

---

## Quick Start

### Creating and Managing Assets

```python
from layer_painter.assets_extended import AssetManager, AssetType, AssetCategory

# Initialize manager
manager = AssetManager("/path/to/project")

# Register a new asset
wood_asset = manager.register_asset(
    name="Walnut Wood Texture",
    asset_type=AssetType.MATERIAL,
    category=AssetCategory.WOOD,
    version="1.0.0",
    description="High quality walnut wood material",
    author="Artist Name",
    tags=["wood", "pbr", "realistic"]
)

# Add tags for organization
wood_asset.add_tag("natural")
wood_asset.add_category_tag("exterior")

# Add dependencies
wood_asset.add_dependency("normal_processor", "1.0+", required=True,
                          description="For normal map processing")

# Save registry
manager.save_registry()
```

### Exporting Assets

```python
# Export individual asset
manager.export_asset(wood_asset, "walnut_wood_1.0.0.lpa")

# Create and export bundle
bundle = manager.create_bundle(
    name="Wood Textures Pack",
    assets=[wood_asset, oak_asset, pine_asset],
    version="1.0.0"
)

if bundle:
    manager.export_bundle(bundle, "wood_textures_pack_1.0.0.lpb")
```

### Importing Assets

```python
# Import asset
imported_asset = manager.import_asset("walnut_wood_1.0.0.lpa")

if imported_asset:
    print(f"Imported: {imported_asset.metadata.name}")
    print(f"Version: {imported_asset.metadata.version}")
    print(f"Author: {imported_asset.metadata.author}")
```

---

## Core Concepts

### Asset UIDs

Each asset has a unique identifier (UID) - a UUID that persists across versions:

```python
asset = manager.register_asset("My Asset", AssetType.TEXTURE)
print(asset.metadata.uid)  # e.g., "550e8400-e29b-41d4-a716-446655440000"
```

### Asset Metadata

Complete metadata tracks asset information:

- **Identification**: uid, name, description
- **Versioning**: version, created/modified dates
- **Type**: asset_type, category
- **Attribution**: author, license, copyright
- **Organization**: tags, category_tags
- **Compatibility**: dependencies, blender_version_min/max
- **Distribution**: file_size, file_hash, preview_image
- **Marketplace**: rating, download_count

### Asset States

Assets have lifecycle states:

1. **Registered** - Asset exists in manager, not yet saved
2. **Saved** - Asset registry persisted to disk
3. **Exported** - Asset packaged for distribution
4. **Imported** - Asset loaded from external package

---

## Asset Types

Layer Painter supports multiple asset types:

### Material (`MATERIAL`)
Complete material configurations with layers and channels:

```python
material_asset = manager.register_asset(
    name="Leather Material",
    asset_type=AssetType.MATERIAL,
    category=AssetCategory.ORGANIC
)
```

### Texture (`TEXTURE`)
Texture resources (images, data textures):

```python
texture_asset = manager.register_asset(
    name="Fabric Base Color",
    asset_type=AssetType.TEXTURE,
    category=AssetCategory.FABRIC
)
```

### Layer (`LAYER`)
Individual layer configurations:

```python
layer_asset = manager.register_asset(
    name="Rust Overlay",
    asset_type=AssetType.LAYER,
    category=AssetCategory.EFFECTS
)
```

### Layer Group (`LAYER_GROUP`)
Pre-organized layer stacks:

```python
group_asset = manager.register_asset(
    name="Weathering Stack",
    asset_type=AssetType.LAYER_GROUP,
    category=AssetCategory.EFFECTS
)
```

### Preset (`PRESET`)
Filter and operation presets:

```python
preset_asset = manager.register_asset(
    name="Vintage Color Grade",
    asset_type=AssetType.PRESET,
    category=AssetCategory.EFFECTS
)
```

### Filter (`FILTER`)
Custom filter configurations:

```python
filter_asset = manager.register_asset(
    name="Glass Distortion",
    asset_type=AssetType.FILTER,
    category=AssetCategory.EFFECTS
)
```

---

## Versioning

### Semantic Versioning

Layer Painter uses semantic versioning (MAJOR.MINOR.PATCH):

```python
asset.metadata.version = "2.1.3"  # Format: MAJOR.MINOR.PATCH

# Versions are comparable
version1 = SemanticVersion.parse("1.0.0")
version2 = SemanticVersion.parse("2.0.0")
print(version1 < version2)  # True
```

### Version Requirements

Assets can specify version requirements for dependencies:

```python
# Exact version
asset.add_dependency("processor", "1.2.3")

# Minimum version (patch-compatible)
asset.add_dependency("processor", "1.2+")

# Minor version compatibility
asset.add_dependency("processor", "1.x")

# Check compatibility
version = SemanticVersion.parse("1.2.5")
print(version.is_compatible_with("1.2+"))  # True
print(version.is_compatible_with("1.x"))   # True
print(version.is_compatible_with("2.0.0")) # False
```

### Version Tracking

Automatic tracking of version history:

```python
# Creation date (automatic)
print(asset.metadata.created_date)
# "2024-01-15T10:30:00.123456"

# Modification date (automatic)
print(asset.metadata.modified_date)
# "2024-01-15T14:45:00.654321"

# Update version
asset.metadata.version = "1.1.0"
asset.metadata.modified_date = datetime.now().isoformat()
```

### Compatibility Tracking

```python
# Minimum Blender version
asset.metadata.blender_version_min = "4.0.0"

# Maximum Blender version (optional)
asset.metadata.blender_version_max = "4.2.0"
```

---

## Dependencies

### Declaring Dependencies

Assets can declare dependencies on other assets:

```python
# Required dependency
wood_asset.add_dependency(
    name="PBR Normal Processor",
    version_requirement="1.0+",
    required=True,
    description="Processes normal maps"
)

# Optional dependency
wood_asset.add_dependency(
    name="Parallax Mapping",
    version_requirement="1.x",
    required=False,
    description="Enhanced depth effect (optional)"
)
```

### Dependency Resolution

Validate dependencies against available assets:

```python
available_assets = manager.find_assets(asset_type=AssetType.PRESET)

is_valid, issues = wood_asset.validate_dependencies(available_assets)

if is_valid:
    print("All dependencies satisfied!")
else:
    for issue in issues:
        print(f"Issue: {issue}")
    # Output:
    # Issue: Required asset 'PBR Normal Processor' version 1.0+ incompatible with available 0.9.0
    # Issue: Required asset 'Lighting Processor' not found
```

### Bundle Validation

Validate all dependencies within a bundle:

```python
bundle = manager.create_bundle(
    name="Complete Package",
    assets=[asset1, asset2, asset3]
)

if bundle:
    is_valid, issues = bundle.validate()
    if is_valid:
        print("Bundle is valid and complete!")
    else:
        print("Bundle has unresolved dependencies")
        for issue in issues:
            print(f"  - {issue}")
```

---

## Import/Export

### Exporting Individual Assets

Assets are exported as `.lpa` (Layer Painter Asset) files:

```python
# Export with metadata
success = manager.export_asset(
    asset=my_asset,
    export_path="my_textures/walnut_wood.lpa"
)

if success:
    print("Asset exported successfully")
    # File contains:
    # - metadata.json (complete metadata)
    # - asset.blend (Blender file with asset data)
```

### Importing Assets

Import `.lpa` files into projects:

```python
# Import asset
imported = manager.import_asset("walnut_wood.lpa")

if imported:
    print(f"Imported: {imported.metadata.name}")
    print(f"Version: {imported.metadata.version}")
    print(f"Author: {imported.metadata.author}")
    
    # Asset is now in manager
    manager.save_registry()
```

### Exporting Bundles

Bundles are exported as `.lpb` (Layer Painter Bundle) files:

```python
# Create bundle
bundle = manager.create_bundle(
    name="Complete Material Pack",
    assets=[wood_asset, metal_asset, fabric_asset],
    version="2.1.0"
)

# Export bundle
if bundle:
    success = manager.export_bundle(
        bundle=bundle,
        export_path="material_pack_2.1.0.lpb"
    )
    
    if success:
        print("Bundle exported successfully")
        # File contains:
        # - bundle.json (bundle metadata)
        # - assets/*/metadata.json (individual metadata)
        # - assets/*/asset.blend (asset files)
```

### Batch Import

Import multiple assets efficiently:

```python
import glob

# Find all .lpa files
lpa_files = glob.glob("library/**/*.lpa", recursive=True)

# Import all
for lpa_file in lpa_files:
    asset = manager.import_asset(lpa_file)
    if asset:
        print(f"✓ Imported {asset.metadata.name}")
    else:
        print(f"✗ Failed to import {lpa_file}")

# Save registry after batch import
manager.save_registry()
```

---

## Asset Bundles

### Creating Bundles

Combine multiple related assets:

```python
# Create bundle for wood textures
bundle = manager.create_bundle(
    name="Wood Textures Collection",
    assets=[walnut, oak, pine, ash],
    version="1.0.0"
)

# Add metadata
bundle.metadata['description'] = "Professional wood texture library"
bundle.metadata['author'] = "Texture Artist"
bundle.metadata['license'] = "CC-BY"
```

### Bundle Organization

Structure bundles logically:

```python
# Materials by category bundle
materials_bundle = manager.create_bundle(
    name="Materials By Category",
    assets=[]
)

# Add wood materials
for asset in manager.find_assets(category=AssetCategory.WOOD):
    materials_bundle.add_asset(asset)

# Add fabric materials
for asset in manager.find_assets(category=AssetCategory.FABRIC):
    materials_bundle.add_asset(asset)
```

### Bundle Validation

Validate bundles before distribution:

```python
bundle = manager.create_bundle(
    name="Complete Package",
    assets=[asset1, asset2, asset3]
)

if bundle:
    is_valid, issues = bundle.validate()
    
    print(f"Bundle Size: {bundle.get_size_mb():.1f} MB")
    print(f"Asset Count: {len(bundle.assets)}")
    print(f"Valid: {is_valid}")
    
    if not is_valid:
        for issue in issues:
            print(f"  ✗ {issue}")
```

---

## Best Practices

### 1. Version Management

- Use semantic versioning consistently
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

```python
# Good versioning progression
"1.0.0"  # Initial release
"1.1.0"  # Added new channels
"1.1.1"  # Fixed normal map quality
"2.0.0"  # Changed layer structure (breaking)
```

### 2. Metadata Completeness

Always provide complete metadata:

```python
asset = manager.register_asset(
    name="High Quality Wood",
    asset_type=AssetType.MATERIAL,
    category=AssetCategory.WOOD,
    version="1.0.0",
    description="Realistic walnut wood with PBR textures",
    author="John Doe"
)

# Add attribution
asset.metadata.copyright = "© 2024 John Doe"
asset.metadata.license = LicenseType.CC_BY

# Add detailed tags
asset.add_tag("wood")
asset.add_tag("pbr")
asset.add_tag("realistic")
asset.add_tag("scanned")
```

### 3. Dependency Management

Declare all dependencies clearly:

```python
# Document all dependencies
asset.add_dependency("normal_processor", "1.0+", required=True,
                    description="Required for normal map processing")

asset.add_dependency("parallax_mapping", "2.x", required=False,
                    description="Optional depth effect")

asset.add_dependency("base_material", "3.0+", required=True,
                    description="Foundation material system")
```

### 4. Asset Organization

Use categories and tags for organization:

```python
# Organize with categories
asset.metadata.category = AssetCategory.PBRMATERIAL

# Add classification tags
asset.add_tag("metal")
asset.add_tag("brushed")
asset.add_tag("industrial")

# Add location tags
asset.add_category_tag("urban")
asset.add_category_tag("exterior")
```

### 5. Testing Before Export

Validate before distribution:

```python
# Check dependencies
is_valid, issues = asset.validate_dependencies(manager.assets.values())
if not is_valid:
    print("Cannot export - missing dependencies:")
    for issue in issues:
        print(f"  - {issue}")
    return

# Check metadata
if not asset.metadata.author:
    print("Please set author before exporting")
    return

# Export
if manager.export_asset(asset, f"{asset.metadata.name}.lpa"):
    print("Asset exported successfully")
```

---

## API Reference

### AssetManager

#### Methods

**`register_asset(name, asset_type, category, version, description, author, tags)`**

Register new asset. Returns Asset object.

```python
asset = manager.register_asset(
    name="My Asset",
    asset_type=AssetType.TEXTURE,
    category=AssetCategory.METAL,
    version="1.0.0"
)
```

**`get_asset(uid)`**

Get asset by UID. Returns Asset or None.

```python
asset = manager.get_asset("550e8400-e29b-41d4-a716-446655440000")
```

**`find_assets(name, asset_type, category, tag, author)`**

Find assets by criteria. Returns list of Assets.

```python
textures = manager.find_assets(asset_type=AssetType.TEXTURE)
metal_materials = manager.find_assets(category=AssetCategory.METAL)
```

**`export_asset(asset, export_path)`**

Export asset to file. Returns True/False.

```python
success = manager.export_asset(asset, "export.lpa")
```

**`import_asset(import_path)`**

Import asset from file. Returns Asset or None.

```python
asset = manager.import_asset("export.lpa")
```

**`create_bundle(name, assets, version)`**

Create bundle. Returns AssetBundle or None.

```python
bundle = manager.create_bundle("Bundle", [asset1, asset2])
```

**`export_bundle(bundle, export_path)`**

Export bundle to file. Returns True/False.

```python
success = manager.export_bundle(bundle, "bundle.lpb")
```

**`get_statistics()`**

Get collection statistics. Returns dict.

```python
stats = manager.get_statistics()
print(f"Total assets: {stats['total_assets']}")
```

### Asset

#### Methods

**`add_dependency(name, version_requirement, required, description)`**

Add dependency.

```python
asset.add_dependency("processor", "1.0+", required=True)
```

**`add_tag(tag)`**

Add classification tag.

```python
asset.add_tag("pbr")
```

**`validate_dependencies(available_assets)`**

Validate dependencies. Returns (bool, list).

```python
is_valid, issues = asset.validate_dependencies(manager.assets.values())
```

---

## Troubleshooting

### Import Fails

**Problem**: Asset import fails with no error message

**Solution**:
1. Verify file is valid `.lpa` (ZIP format)
2. Check metadata.json is present
3. Verify directory permissions
4. Check Blender file format

```python
# Debug import
try:
    asset = manager.import_asset("file.lpa")
    if not asset:
        print("Import returned None")
except Exception as e:
    print(f"Import error: {e}")
```

### Dependency Not Found

**Problem**: "Required asset 'X' not found"

**Solution**:
1. Import required asset first
2. Check spelling of dependency name
3. Verify version compatibility
4. Save registry after adding assets

```python
# Make sure dependencies are imported
required_asset = manager.import_asset("required.lpa")

# Then import dependent asset
dependent_asset = manager.import_asset("dependent.lpa")

# Validate
is_valid, issues = dependent_asset.validate_dependencies(
    manager.assets.values()
)
```

### Bundle Validation Fails

**Problem**: "Bundle has no assets" or dependency issues

**Solution**:
1. Add assets before creating bundle
2. Import dependencies first
3. Check asset count

```python
# Verify assets before bundling
print(f"Available assets: {len(manager.assets)}")

# Import dependencies
for dep_file in ["dep1.lpa", "dep2.lpa"]:
    manager.import_asset(dep_file)

# Then create bundle
bundle = manager.create_bundle("Bundle", manager.assets.values())
```

### Large Bundle Export

**Problem**: Bundle export is slow or memory-intensive

**Solution**:
1. Use smaller bundles
2. Export assets individually
3. Compress before distribution
4. Split by category

```python
# Export by category
for category in AssetCategory:
    assets = manager.find_assets(category=category)
    if assets:
        bundle = manager.create_bundle(
            f"{category.value} Pack",
            assets
        )
        if bundle:
            manager.export_bundle(
                bundle,
                f"pack_{category.value}.lpb"
            )
```

---

## Summary

The Extended Asset System provides professional asset management capabilities:

- **Versioning**: Semantic versioning with compatibility checking
- **Dependencies**: Declare and validate asset dependencies
- **Distribution**: Package assets for sharing
- **Organization**: Categorize and tag assets
- **Validation**: Ensure integrity before export

For more information, see `ASSETS_EXAMPLES.md` for practical examples and integration patterns.
