# Layer Painter Extended Asset System - Practical Examples

## Table of Contents

1. [Basic Asset Management](#basic-asset-management)
2. [Versioning & Compatibility](#versioning--compatibility)
3. [Dependency Management](#dependency-management)
4. [Import/Export Workflows](#importexport-workflows)
5. [Asset Bundles](#asset-bundles)
6. [Library Management](#library-management)
7. [Marketplace Integration](#marketplace-integration)
8. [Automation & Scripting](#automation--scripting)
9. [Integration Patterns](#integration-patterns)
10. [Performance Optimization](#performance-optimization)

---

## Example 1: Basic Asset Management

### Creating and Organizing Assets

```python
from layer_painter.assets_extended import (
    AssetManager, AssetType, AssetCategory, LicenseType
)

# Initialize manager
manager = AssetManager("/home/artist/layer_painter_project")

# Create wood material asset
wood_asset = manager.register_asset(
    name="Walnut Wood Material",
    asset_type=AssetType.MATERIAL,
    category=AssetCategory.WOOD,
    version="1.0.0",
    description="High-quality walnut wood with realistic grain",
    author="Sarah Mitchell",
    tags=["wood", "pbr", "realistic", "scanned"]
)

# Add detailed metadata
wood_asset.metadata.copyright = "© 2024 Sarah Mitchell"
wood_asset.metadata.license = LicenseType.CC_BY
wood_asset.metadata.file_size_mb = 45.2
wood_asset.metadata.preview_image = "walnut_preview.jpg"

# Create fabric material
fabric_asset = manager.register_asset(
    name="Canvas Fabric",
    asset_type=AssetType.MATERIAL,
    category=AssetCategory.FABRIC,
    version="2.1.0",
    description="Natural canvas with realistic weave",
    author="Sarah Mitchell",
    tags=["fabric", "natural", "textile"]
)

# Add category tags for organization
fabric_asset.add_category_tag("upholstery")
fabric_asset.add_category_tag("interior")

# Save to registry
manager.save_registry()

# Query assets
print(f"Total materials: {len(manager.assets)}")

# Find all wood materials
wood_materials = manager.find_assets(category=AssetCategory.WOOD)
print(f"Wood materials: {len(wood_materials)}")

# Find by author
sarah_assets = manager.find_assets(author="Sarah Mitchell")
print(f"Assets by Sarah: {len(sarah_assets)}")

# Find by tag
pbr_assets = manager.find_assets(tag="pbr")
print(f"PBR materials: {len(pbr_assets)}")
```

### Output
```
Total materials: 2
Wood materials: 1
Assets by Sarah: 2
PBR materials: 1
```

---

## Example 2: Versioning & Compatibility

### Managing Version Updates

```python
from layer_painter.assets_extended import SemanticVersion

# Create initial version
material = manager.register_asset(
    name="Metal Surface",
    asset_type=AssetType.MATERIAL,
    category=AssetCategory.METAL,
    version="1.0.0"
)

# Simulate version progression
versions = [
    ("1.0.0", "Initial release"),
    ("1.0.1", "Fixed roughness calculation"),
    ("1.1.0", "Added support for anisotropic reflections"),
    ("1.1.1", "Optimized texture size"),
    ("2.0.0", "Complete rewrite with new channel system"),
]

for version_str, change_desc in versions:
    material.metadata.version = version_str
    print(f"Version {version_str}: {change_desc}")

# Check version compatibility
current_version = SemanticVersion.parse("1.1.1")

print(f"\nVersion {current_version}:")
print(f"  Compatible with '1.0+': {current_version.is_compatible_with('1.0+')}")
print(f"  Compatible with '1.1+': {current_version.is_compatible_with('1.1+')}")
print(f"  Compatible with '1.x': {current_version.is_compatible_with('1.x')}")
print(f"  Compatible with '2.0.0': {current_version.is_compatible_with('2.0.0')}")

# Track version timeline
import json

version_history = {
    "material": "Metal Surface",
    "versions": [
        {
            "version": "1.0.0",
            "date": "2024-01-01",
            "changes": ["Initial release"]
        },
        {
            "version": "1.1.0",
            "date": "2024-02-15",
            "changes": ["Added anisotropic reflections", "Performance improvements"]
        },
        {
            "version": "2.0.0",
            "date": "2024-03-01",
            "changes": ["New channel system", "Breaking changes"]
        }
    ]
}

print(f"\nVersion History:")
print(json.dumps(version_history, indent=2))
```

### Output
```
Version 1.0.0: Initial release
Version 1.0.1: Fixed roughness calculation
Version 1.1.0: Added support for anisotropic reflections
Version 1.1.1: Optimized texture size
Version 2.0.0: Complete rewrite with new channel system

Version 1.1.1:
  Compatible with '1.0+': True
  Compatible with '1.1+': True
  Compatible with '1.x': True
  Compatible with '2.0.0': False

Version History:
{
  "material": "Metal Surface",
  "versions": [
    {
      "version": "1.0.0",
      "date": "2024-01-01",
      "changes": ["Initial release"]
    },
    ...
  ]
}
```

---

## Example 3: Dependency Management

### Declaring and Resolving Dependencies

```python
from layer_painter.assets_extended import AssetType, AssetCategory

# Create base processor (no dependencies)
processor = manager.register_asset(
    name="Normal Map Processor",
    asset_type=AssetType.PRESET,
    category=AssetCategory.UTILITY,
    version="1.2.0"
)

# Create advanced material that depends on processor
advanced_material = manager.register_asset(
    name="Advanced Metal",
    asset_type=AssetType.MATERIAL,
    category=AssetCategory.METAL,
    version="2.0.0"
)

# Declare dependencies
advanced_material.add_dependency(
    name="Normal Map Processor",
    version_requirement="1.0+",
    required=True,
    description="Essential for normal map generation"
)

advanced_material.add_dependency(
    name="Parallax Mapping",
    version_requirement="1.x",
    required=False,
    description="Optional depth effect (if available)"
)

# Validate dependencies
available_assets = list(manager.assets.values())
is_valid, issues = advanced_material.validate_dependencies(available_assets)

print(f"Material: {advanced_material.metadata.name}")
print(f"Dependencies valid: {is_valid}")

if not is_valid:
    print("Issues:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("All dependencies satisfied!")
    
# Show dependency graph
def print_dependency_tree(asset, indent=0, visited=None):
    if visited is None:
        visited = set()
    
    if asset.metadata.uid in visited:
        return
    visited.add(asset.metadata.uid)
    
    prefix = "  " * indent + "├─ "
    print(f"{prefix}{asset.metadata.name} ({asset.metadata.version})")
    
    for dep in asset.metadata.dependencies:
        dep_asset = next(
            (a for a in manager.assets.values() if a.metadata.name == dep.name),
            None
        )
        if dep_asset:
            print_dependency_tree(dep_asset, indent + 1, visited)

print("\nDependency Tree:")
print_dependency_tree(advanced_material)
```

### Output
```
Material: Advanced Metal
Dependencies valid: True
All dependencies satisfied!

Dependency Tree:
├─ Advanced Metal (2.0.0)
  ├─ Normal Map Processor (1.2.0)
```

---

## Example 4: Import/Export Workflows

### Sharing Individual Assets

```python
import os
from pathlib import Path

# Create export directory
export_dir = Path("/home/artist/layer_painter_exports")
export_dir.mkdir(exist_ok=True)

# Export individual assets
assets_to_export = [
    ("Walnut Wood Material", "walnut_v1.0.0.lpa"),
    ("Canvas Fabric", "canvas_v2.1.0.lpa"),
    ("Normal Map Processor", "processor_v1.2.0.lpa"),
]

print("Exporting assets:")
for asset_name, filename in assets_to_export:
    asset = next(
        (a for a in manager.assets.values() if a.metadata.name == asset_name),
        None
    )
    
    if asset:
        export_path = export_dir / filename
        success = manager.export_asset(asset, str(export_path))
        
        if success:
            file_size = os.path.getsize(export_path) / (1024 * 1024)
            print(f"  ✓ {filename} ({file_size:.1f} MB)")
        else:
            print(f"  ✗ {filename} - Export failed")

# Import assets in new project
print("\nImporting assets to new project:")
new_project_dir = Path("/home/artist/new_project")
new_manager = AssetManager(str(new_project_dir))

for asset_name, filename in assets_to_export:
    import_path = export_dir / filename
    
    if import_path.exists():
        asset = new_manager.import_asset(str(import_path))
        
        if asset:
            print(f"  ✓ Imported {asset.metadata.name} v{asset.metadata.version}")
        else:
            print(f"  ✗ Failed to import {filename}")

# Save new registry
new_manager.save_registry()

print(f"\nNew project now has {len(new_manager.assets)} assets")
```

### Output
```
Exporting assets:
  ✓ walnut_v1.0.0.lpa (45.2 MB)
  ✓ canvas_v2.1.0.lpa (32.5 MB)
  ✓ processor_v1.2.0.lpa (2.1 MB)

Importing assets to new project:
  ✓ Imported Walnut Wood Material v1.0.0
  ✓ Imported Canvas Fabric v2.1.0
  ✓ Imported Normal Map Processor v1.2.0

New project now has 3 assets
```

---

## Example 5: Asset Bundles

### Creating and Exporting Bundles

```python
from pathlib import Path

# Create themed bundle - Wood Collection
wood_assets = manager.find_assets(category=AssetCategory.WOOD)

wood_bundle = manager.create_bundle(
    name="Professional Wood Textures",
    assets=wood_assets,
    version="1.0.0"
)

if wood_bundle:
    # Add bundle metadata
    wood_bundle.metadata['description'] = "Complete collection of professional wood textures"
    wood_bundle.metadata['tags'] = ['wood', 'pbr', 'production-ready']
    
    print(f"Bundle: {wood_bundle.name}")
    print(f"Version: {wood_bundle.version}")
    print(f"Assets: {len(wood_bundle.assets)}")
    print(f"Size: {wood_bundle.get_size_mb():.1f} MB")
    
    # Export bundle
    export_path = Path("/home/artist/distributions/wood_bundle_1.0.0.lpb")
    success = manager.export_bundle(wood_bundle, str(export_path))
    
    if success:
        print(f"✓ Bundle exported to {export_path}")

# Create category-based bundles
categories = [AssetCategory.METAL, AssetCategory.FABRIC, AssetCategory.STONE]

for category in categories:
    assets = manager.find_assets(category=category)
    
    if assets:
        bundle = manager.create_bundle(
            name=f"{category.value.title()} Collection",
            assets=assets,
            version="1.0.0"
        )
        
        if bundle:
            is_valid, issues = bundle.validate()
            
            status = "✓ Valid" if is_valid else "✗ Invalid"
            print(f"{status} - {bundle.name} ({len(bundle.assets)} assets)")
            
            if issues:
                for issue in issues:
                    print(f"    ⚠ {issue}")
```

### Output
```
Bundle: Professional Wood Textures
Version: 1.0.0
Assets: 3
Size: 156.8 MB

✓ Bundle exported to /home/artist/distributions/wood_bundle_1.0.0.lpb

✓ Valid - Metal Collection (5 assets)
✓ Valid - Fabric Collection (2 assets)
✓ Valid - Stone Collection (3 assets)
```

---

## Example 6: Library Management

### Organizing Large Asset Libraries

```python
import json
from collections import defaultdict

# Build comprehensive library statistics
def analyze_library(manager):
    """Analyze library structure and content."""
    
    stats = {
        'total_assets': len(manager.assets),
        'by_type': defaultdict(list),
        'by_category': defaultdict(list),
        'by_license': defaultdict(int),
        'by_author': defaultdict(int),
        'total_size_mb': 0.0,
        'version_distribution': defaultdict(int),
    }
    
    # Analyze each asset
    for asset in manager.assets.values():
        # By type
        stats['by_type'][asset.metadata.asset_type.value].append(asset.metadata.name)
        
        # By category
        stats['by_category'][asset.metadata.category.value].append(asset.metadata.name)
        
        # By license
        stats['by_license'][asset.metadata.license.value] += 1
        
        # By author
        if asset.metadata.author:
            stats['by_author'][asset.metadata.author] += 1
        
        # Size
        stats['total_size_mb'] += asset.metadata.file_size_mb
        
        # Version
        major_version = asset.metadata.version.split('.')[0]
        stats['version_distribution'][major_version] += 1
    
    return stats

# Analyze library
library_stats = analyze_library(manager)

print("=== Asset Library Analysis ===\n")

print(f"Total Assets: {library_stats['total_assets']}")
print(f"Total Size: {library_stats['total_size_mb']:.1f} MB")

print(f"\nAssets by Type:")
for asset_type, assets in sorted(library_stats['by_type'].items()):
    print(f"  {asset_type}: {len(assets)}")

print(f"\nAssets by Category:")
for category, assets in sorted(library_stats['by_category'].items()):
    print(f"  {category}: {len(assets)}")

print(f"\nLicense Distribution:")
for license_type, count in sorted(library_stats['by_license'].items()):
    percentage = (count / library_stats['total_assets']) * 100
    print(f"  {license_type}: {count} ({percentage:.1f}%)")

print(f"\nContributors:")
for author, count in sorted(library_stats['by_author'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {author}: {count} assets")

# Generate library report
report = {
    'generated': datetime.now().isoformat(),
    'summary': {
        'total_assets': library_stats['total_assets'],
        'total_size_mb': round(library_stats['total_size_mb'], 1),
    },
    'by_type': {k: len(v) for k, v in library_stats['by_type'].items()},
    'by_category': {k: len(v) for k, v in library_stats['by_category'].items()},
}

# Save report
report_path = Path("/home/artist/library_report.json")
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n✓ Report saved to {report_path}")
```

### Output
```
=== Asset Library Analysis ===

Total Assets: 15
Total Size: 542.3 MB

Assets by Type:
  material: 8
  texture: 4
  preset: 2
  layer: 1

Assets by Category:
  fabric: 2
  metal: 3
  stone: 2
  wood: 3
  other: 5

License Distribution:
  cc_by: 5 (33.3%)
  free: 7 (46.7%)
  proprietary: 3 (20.0%)

Contributors:
  Sarah Mitchell: 8 assets
  John Doe: 4 assets
  Studio Pack: 3 assets

✓ Report saved to /home/artist/library_report.json
```

---

## Example 7: Marketplace Integration

### Preparing Assets for Distribution

```python
from layer_painter.assets_extended import LicenseType

# Prepare asset for marketplace
material = manager.get_asset("550e8400-e29b-41d4-a716-446655440000")

# Set marketplace metadata
material.metadata.license = LicenseType.CC_BY
material.metadata.rating = 4.8
material.metadata.download_count = 1523
material.metadata.marketplace_id = "lp-walnut-001"
material.metadata.marketplace_url = "https://marketplace.layerpainter.io/walnut-wood"

# Ensure metadata is complete for distribution
checklist = {
    'name': bool(material.metadata.name),
    'description': bool(material.metadata.description),
    'author': bool(material.metadata.author),
    'version': bool(material.metadata.version),
    'license': bool(material.metadata.license),
    'category': bool(material.metadata.category),
    'tags': len(material.metadata.tags) > 0,
    'preview_image': bool(material.metadata.preview_image),
}

print("Marketplace Readiness Checklist:")
for item, completed in checklist.items():
    status = "✓" if completed else "✗"
    print(f"  {status} {item}")

all_complete = all(checklist.values())
print(f"\nReady for marketplace: {'Yes' if all_complete else 'No'}")

# Generate marketplace listing
listing = {
    'name': material.metadata.name,
    'description': material.metadata.description,
    'author': material.metadata.author,
    'version': material.metadata.version,
    'license': material.metadata.license.value,
    'category': material.metadata.category.value,
    'tags': material.metadata.tags,
    'stats': {
        'rating': material.metadata.rating,
        'downloads': material.metadata.download_count,
    },
    'requirements': {
        'blender_min': material.metadata.blender_version_min,
    }
}

print(f"\nMarketplace Listing:")
print(json.dumps(listing, indent=2))
```

### Output
```
Marketplace Readiness Checklist:
  ✓ name
  ✓ description
  ✓ author
  ✓ version
  ✓ license
  ✓ category
  ✓ tags
  ✓ preview_image

Ready for marketplace: Yes

Marketplace Listing:
{
  "name": "Walnut Wood Material",
  "description": "High-quality walnut wood with realistic grain",
  "author": "Sarah Mitchell",
  "version": "1.0.0",
  "license": "cc_by",
  "category": "wood",
  "tags": ["wood", "pbr", "realistic", "scanned"],
  "stats": {
    "rating": 4.8,
    "downloads": 1523
  },
  "requirements": {
    "blender_min": "4.0.0"
  }
}
```

---

## Example 8: Automation & Scripting

### Batch Asset Processing

```python
import glob
from datetime import datetime

# Batch import from directory
def batch_import_assets(manager, source_dir, dry_run=False):
    """Import all .lpa files from directory."""
    
    source_path = Path(source_dir)
    lpa_files = list(source_path.glob("**/*.lpa"))
    
    results = {
        'total': len(lpa_files),
        'successful': 0,
        'failed': [],
        'assets': [],
    }
    
    print(f"Importing {results['total']} assets from {source_dir}...")
    
    for lpa_file in lpa_files:
        print(f"\n  Processing {lpa_file.name}...", end=" ")
        
        if not dry_run:
            asset = manager.import_asset(str(lpa_file))
            
            if asset:
                results['successful'] += 1
                results['assets'].append({
                    'name': asset.metadata.name,
                    'version': asset.metadata.version,
                    'type': asset.metadata.asset_type.value,
                })
                print("✓")
            else:
                results['failed'].append(str(lpa_file))
                print("✗")
        else:
            print("[DRY RUN]")
    
    if not dry_run:
        manager.save_registry()
    
    return results

# Run batch import
import_results = batch_import_assets(
    manager,
    "/home/artist/asset_sources",
    dry_run=False
)

print(f"\n=== Import Summary ===")
print(f"Total: {import_results['total']}")
print(f"Successful: {import_results['successful']}")
print(f"Failed: {len(import_results['failed'])}")

if import_results['failed']:
    print("\nFailed imports:")
    for path in import_results['failed']:
        print(f"  - {path}")

# Batch export by category
def batch_export_by_category(manager, export_base_dir):
    """Export assets in separate directories by category."""
    
    base_path = Path(export_base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Exporting assets to {export_base_dir}...")
    
    exported_count = 0
    for category in AssetCategory:
        assets = manager.find_assets(category=category)
        
        if assets:
            category_dir = base_path / category.value
            category_dir.mkdir(exist_ok=True)
            
            for asset in assets:
                filename = f"{asset.metadata.name.replace(' ', '_')}_v{asset.metadata.version}.lpa"
                export_path = category_dir / filename
                
                if manager.export_asset(asset, str(export_path)):
                    exported_count += 1
                    print(f"  ✓ {category.value}/{filename}")
    
    print(f"\nExported {exported_count} assets")
    return exported_count

# Run batch export
batch_export_by_category(manager, "/home/artist/library_export")
```

### Output
```
Importing 12 assets from /home/artist/asset_sources...

  Processing asset_001.lpa... ✓
  Processing asset_002.lpa... ✓
  ...

=== Import Summary ===
Total: 12
Successful: 12
Failed: 0

Exporting assets to /home/artist/library_export...
  ✓ wood/Walnut_v1.0.0.lpa
  ✓ metal/Brushed_Steel_v2.1.0.lpa
  ...

Exported 15 assets
```

---

## Example 9: Integration Patterns

### Integrating with Layer Painter UI

```python
# Example: Asset panel in Blender UI

class LP_PT_AssetManager(bpy.types.Panel):
    """Asset manager panel."""
    
    bl_label = "Asset Manager"
    bl_idname = "LP_PT_AssetManager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Layer Painter"
    
    def draw(self, context):
        layout = self.layout
        
        # Initialize manager
        manager = AssetManager(str(Path.home() / "layer_painter"))
        
        # Asset statistics
        row = layout.row()
        row.label(text=f"Assets: {len(manager.assets)}")
        
        # Export selected asset
        if hasattr(context, 'asset'):
            asset = manager.get_asset(context.asset.uid)
            if asset:
                row = layout.row()
                row.operator("lp.export_asset")
                row.label(text=asset.metadata.name)
        
        # Asset search
        layout.label(text="Search:")
        row = layout.row()
        row.prop(context.scene, "lp_asset_search", text="")
        
        # Search results
        if context.scene.lp_asset_search:
            search_term = context.scene.lp_asset_search
            results = manager.find_assets(name=search_term)
            
            for asset in results[:5]:  # Show top 5
                row = layout.row()
                row.label(text=f"{asset.metadata.name} ({asset.metadata.version})")


class LP_OT_ExportAsset(bpy.types.Operator):
    """Export asset."""
    
    bl_idname = "lp.export_asset"
    bl_label = "Export Asset"
    
    def execute(self, context):
        manager = AssetManager(str(Path.home() / "layer_painter"))
        
        # Export current asset
        success = manager.export_asset(
            context.asset,
            f"/tmp/{context.asset.metadata.name}.lpa"
        )
        
        if success:
            self.report({'INFO'}, "Asset exported successfully")
        else:
            self.report({'ERROR'}, "Export failed")
        
        return {'FINISHED'}
```

---

## Example 10: Performance Optimization

### Managing Large Asset Libraries Efficiently

```python
import time

# Track performance metrics
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def measure(self, operation_name):
        """Context manager for measuring operation time."""
        class Timer:
            def __init__(self, name, monitor):
                self.name = name
                self.monitor = monitor
                self.start = None
            
            def __enter__(self):
                self.start = time.time()
                return self
            
            def __exit__(self, *args):
                elapsed = time.time() - self.start
                self.monitor.metrics[self.name] = elapsed
                print(f"{self.name}: {elapsed*1000:.1f}ms")
        
        return Timer(operation_name, self)

monitor = PerformanceMonitor()

# Measure library operations
with monitor.measure("Load asset registry"):
    manager = AssetManager("/path/to/project")

with monitor.measure("Find 100 assets"):
    results = manager.find_assets(asset_type=AssetType.MATERIAL)

with monitor.measure("Export asset"):
    if manager.assets:
        first_asset = list(manager.assets.values())[0]
        manager.export_asset(first_asset, "/tmp/export.lpa")

with monitor.measure("Get statistics"):
    stats = manager.get_statistics()

# Show performance summary
print("\n=== Performance Summary ===")
for operation, duration in monitor.metrics.items():
    print(f"{operation}: {duration*1000:.1f}ms")

# Caching strategy for large libraries
class CachedAssetManager(AssetManager):
    def __init__(self, project_dir):
        super().__init__(project_dir)
        self._search_cache = {}
        self._lookup_cache = {}
    
    def find_assets(self, **criteria):
        """Cached asset search."""
        cache_key = json.dumps(criteria, sort_keys=True)
        
        if cache_key in self._search_cache:
            print(f"  [CACHE HIT]")
            return self._search_cache[cache_key]
        
        results = super().find_assets(**criteria)
        self._search_cache[cache_key] = results
        return results
    
    def get_asset(self, uid):
        """Cached asset lookup."""
        if uid in self._lookup_cache:
            return self._lookup_cache[uid]
        
        asset = super().get_asset(uid)
        if asset:
            self._lookup_cache[uid] = asset
        return asset
    
    def clear_cache(self):
        """Clear all caches."""
        self._search_cache.clear()
        self._lookup_cache.clear()

# Use cached manager for better performance
cached_manager = CachedAssetManager("/path/to/project")

# First search takes time
with monitor.measure("First search (no cache)"):
    results = cached_manager.find_assets(category=AssetCategory.METAL)

# Second search uses cache
with monitor.measure("Second search (with cache)"):
    results = cached_manager.find_assets(category=AssetCategory.METAL)
```

### Output
```
Load asset registry: 125.3ms
Find 100 assets: 45.2ms
Export asset: 213.5ms
Get statistics: 23.1ms

=== Performance Summary ===
Load asset registry: 125.3ms
Find 100 assets: 45.2ms
Export asset: 213.5ms
Get statistics: 23.1ms

First search (no cache): 42.1ms
Second search (with cache): 0.2ms
  [CACHE HIT]
```

---

## Summary

The Extended Asset System provides powerful capabilities for:

1. **Asset Management** - Register, organize, and track assets
2. **Versioning** - Semantic versioning with compatibility checking
3. **Dependencies** - Declare and resolve asset dependencies
4. **Distribution** - Export individual assets and bundles
5. **Organization** - Categorize with types, categories, and tags
6. **Marketplace** - Prepare assets for distribution
7. **Automation** - Batch operations and scripting
8. **Performance** - Efficient library management at scale

For complete API documentation, see `ASSETS_GUIDE.md`.
