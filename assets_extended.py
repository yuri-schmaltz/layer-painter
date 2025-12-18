"""
Layer Painter Extended Asset System

Advanced asset management system with:
- Asset versioning and compatibility tracking
- Dependency resolution and validation
- Import/export with metadata preservation
- Asset tagging and categorization
- Asset marketplace integration support
- Bundle creation and distribution

Usage:
    from layer_painter.assets_extended import (
        AssetManager, AssetVersion, AssetBundle,
        AssetMetadata, AssetDependency
    )
    
    # Create asset manager
    manager = AssetManager("my_project")
    
    # Register asset
    asset = manager.register_asset(
        name="Wood Texture",
        asset_type="texture",
        version="1.0.0"
    )
    
    # Add dependencies
    asset.add_dependency("normal_processor", "1.0+")
    
    # Export asset
    manager.export_asset(asset, "wood_texture.lpa")
"""

import json
import os
import shutil
import hashlib
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import zipfile


# ============================================================================
# Asset Types & Categories
# ============================================================================

class AssetType(Enum):
    """Asset type enumeration."""
    MATERIAL = "material"
    TEXTURE = "texture"
    LAYER = "layer"
    LAYER_GROUP = "layer_group"
    PRESET = "preset"
    FILTER = "filter"
    BLEND_MODE = "blend_mode"
    BRUSH = "brush"
    OTHER = "other"


class AssetCategory(Enum):
    """Asset category enumeration."""
    PBRMATERIAL = "pbr_material"
    FABRIC = "fabric"
    METAL = "metal"
    WOOD = "wood"
    STONE = "stone"
    ORGANIC = "organic"
    PROCEDURAL = "procedural"
    EFFECTS = "effects"
    UTILITY = "utility"
    OTHER = "other"


class LicenseType(Enum):
    """Asset license enumeration."""
    CC0 = "cc0"  # Public domain
    CC_BY = "cc_by"  # Attribution required
    CC_BY_SA = "cc_by_sa"  # Share-alike required
    PROPRIETARY = "proprietary"
    FREE = "free"


# ============================================================================
# Version Management
# ============================================================================

@dataclass
class SemanticVersion:
    """Semantic versioning (major.minor.patch)."""
    major: int
    minor: int = 0
    patch: int = 0
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @staticmethod
    def parse(version_str: str) -> 'SemanticVersion':
        """Parse version string."""
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return SemanticVersion(major, minor, patch)
    
    def is_compatible_with(self, required: str) -> bool:
        """Check if version matches requirement (e.g., '1.0+', '1.x', '1.2.3')."""
        if required.endswith('+'):
            req_version = SemanticVersion.parse(required[:-1])
            return self.major == req_version.major and self >= req_version
        elif 'x' in required:
            parts = required.split('.')
            req_major = int(parts[0]) if parts[0] != 'x' else -1
            req_minor = int(parts[1]) if len(parts) > 1 and parts[1] != 'x' else -1
            
            if req_major >= 0 and self.major != req_major:
                return False
            if req_minor >= 0 and self.minor != req_minor:
                return False
            return True
        else:
            req_version = SemanticVersion.parse(required)
            return self == req_version
    
    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __le__(self, other):
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)
    
    def __gt__(self, other):
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)
    
    def __ge__(self, other):
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)
    
    def __eq__(self, other):
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)


# ============================================================================
# Asset Metadata
# ============================================================================

@dataclass
class AssetDependency:
    """Asset dependency specification."""
    name: str
    version_requirement: str  # e.g., "1.0+", "2.x", "1.2.3"
    required: bool = True
    description: str = ""


@dataclass
class AssetMetadata:
    """Complete asset metadata."""
    uid: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    asset_type: AssetType = AssetType.OTHER
    category: AssetCategory = AssetCategory.OTHER
    
    # Attribution
    author: str = ""
    license: LicenseType = LicenseType.PROPRIETARY
    copyright: str = ""
    
    # Tracking
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    blender_version_min: str = "4.0.0"
    blender_version_max: str = ""
    
    # Organization
    tags: List[str] = field(default_factory=list)
    category_tags: List[str] = field(default_factory=list)
    
    # Dependencies
    dependencies: List[AssetDependency] = field(default_factory=list)
    
    # Content
    file_size_mb: float = 0.0
    file_hash: str = ""
    preview_image: Optional[str] = None
    
    # Marketplace
    marketplace_id: Optional[str] = None
    marketplace_url: Optional[str] = None
    rating: float = 0.0
    download_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['asset_type'] = self.asset_type.value
        data['category'] = self.category.value
        data['license'] = self.license.value
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AssetMetadata':
        """Create from dictionary."""
        data = dict(data)
        data['asset_type'] = AssetType(data.get('asset_type', 'other'))
        data['category'] = AssetCategory(data.get('category', 'other'))
        data['license'] = LicenseType(data.get('license', 'proprietary'))
        return AssetMetadata(**data)


# ============================================================================
# Asset Management
# ============================================================================

class Asset:
    """Represents a Layer Painter asset."""
    
    def __init__(self, metadata: AssetMetadata, file_path: Optional[str] = None):
        self.metadata = metadata
        self.file_path = file_path
        self.data = None  # Loaded asset data
    
    def add_dependency(self, name: str, version_requirement: str = "1.0+", 
                      required: bool = True, description: str = ""):
        """Add dependency."""
        dep = AssetDependency(name, version_requirement, required, description)
        self.metadata.dependencies.append(dep)
    
    def add_tag(self, tag: str):
        """Add classification tag."""
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
    
    def add_category_tag(self, tag: str):
        """Add category tag."""
        if tag not in self.metadata.category_tags:
            self.metadata.category_tags.append(tag)
    
    def get_version(self) -> SemanticVersion:
        """Get parsed version."""
        return SemanticVersion.parse(self.metadata.version)
    
    def is_compatible(self, version_requirement: str) -> bool:
        """Check if asset meets version requirement."""
        return self.get_version().is_compatible_with(version_requirement)
    
    def validate_dependencies(self, available_assets: List['Asset']) -> Tuple[bool, List[str]]:
        """
        Validate that all dependencies are available.
        
        Returns:
            (is_valid, list of missing/incompatible dependencies)
        """
        issues = []
        
        for dep in self.metadata.dependencies:
            found = False
            for asset in available_assets:
                if asset.metadata.name == dep.name:
                    if asset.is_compatible(dep.version_requirement):
                        found = True
                        break
                    else:
                        issues.append(
                            f"Asset '{dep.name}' version {asset.metadata.version} "
                            f"incompatible with requirement {dep.version_requirement}"
                        )
            
            if not found and dep.required:
                issues.append(f"Required asset '{dep.name}' not found")
        
        return len(issues) == 0, issues


class AssetBundle:
    """Bundle multiple assets for distribution."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.uid = str(uuid.uuid4())
        self.name = name
        self.version = version
        self.created_date = datetime.now().isoformat()
        self.assets: List[Asset] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_asset(self, asset: Asset):
        """Add asset to bundle."""
        if asset not in self.assets:
            self.assets.append(asset)
    
    def remove_asset(self, asset: Asset):
        """Remove asset from bundle."""
        if asset in self.assets:
            self.assets.remove(asset)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate bundle integrity."""
        issues = []
        
        if not self.name:
            issues.append("Bundle name is empty")
        
        if not self.assets:
            issues.append("Bundle has no assets")
        
        # Check dependencies between assets
        for asset in self.assets:
            valid, deps_issues = asset.validate_dependencies(self.assets)
            if not valid:
                issues.extend(deps_issues)
        
        return len(issues) == 0, issues
    
    def get_size_mb(self) -> float:
        """Get total bundle size."""
        return sum(asset.metadata.file_size_mb for asset in self.assets)


class AssetManager:
    """Manage Layer Painter assets and versioning."""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.assets_dir = self.project_dir / "assets"
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        self.assets: Dict[str, Asset] = {}
        self.bundles: Dict[str, AssetBundle] = {}
        
        self._load_registry()
    
    def register_asset(self, 
                      name: str,
                      asset_type: AssetType,
                      category: AssetCategory = AssetCategory.OTHER,
                      version: str = "1.0.0",
                      description: str = "",
                      author: str = "",
                      tags: List[str] = None) -> Asset:
        """
        Register new asset.
        
        Args:
            name (str): Asset name
            asset_type (AssetType): Type of asset
            category (AssetCategory): Category
            version (str): Initial version
            description (str): Asset description
            author (str): Author name
            tags (list): Classification tags
        
        Returns:
            Newly created Asset
        """
        metadata = AssetMetadata(
            name=name,
            asset_type=asset_type,
            category=category,
            version=version,
            description=description,
            author=author,
            tags=tags or []
        )
        
        asset = Asset(metadata)
        self.assets[metadata.uid] = asset
        
        return asset
    
    def get_asset(self, uid: str) -> Optional[Asset]:
        """Get asset by UID."""
        return self.assets.get(uid)
    
    def find_assets(self, 
                   name: Optional[str] = None,
                   asset_type: Optional[AssetType] = None,
                   category: Optional[AssetCategory] = None,
                   tag: Optional[str] = None,
                   author: Optional[str] = None) -> List[Asset]:
        """
        Find assets by criteria.
        
        Args:
            name (str): Asset name (substring match)
            asset_type (AssetType): Filter by type
            category (AssetCategory): Filter by category
            tag (str): Filter by tag
            author (str): Filter by author
        
        Returns:
            List of matching assets
        """
        results = list(self.assets.values())
        
        if name:
            results = [a for a in results if name.lower() in a.metadata.name.lower()]
        
        if asset_type:
            results = [a for a in results if a.metadata.asset_type == asset_type]
        
        if category:
            results = [a for a in results if a.metadata.category == category]
        
        if tag:
            results = [a for a in results if tag in a.metadata.tags]
        
        if author:
            results = [a for a in results if author.lower() in a.metadata.author.lower()]
        
        return results
    
    def export_asset(self, asset: Asset, export_path: str) -> bool:
        """
        Export asset to file.
        
        Args:
            asset (Asset): Asset to export
            export_path (str): Where to save asset
        
        Returns:
            True if successful
        """
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create asset package (ZIP)
            with zipfile.ZipFile(export_path, 'w') as zf:
                # Write metadata
                metadata_json = json.dumps(asset.metadata.to_dict(), indent=2)
                zf.writestr("metadata.json", metadata_json)
                
                # Write asset file if exists
                if asset.file_path and Path(asset.file_path).exists():
                    zf.write(asset.file_path, "asset.blend")
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def import_asset(self, import_path: str) -> Optional[Asset]:
        """
        Import asset from file.
        
        Args:
            import_path (str): Asset file path
        
        Returns:
            Imported Asset or None if failed
        """
        try:
            import_path = Path(import_path)
            
            # Extract package
            with zipfile.ZipFile(import_path, 'r') as zf:
                # Load metadata
                metadata_json = zf.read("metadata.json").decode('utf-8')
                metadata_dict = json.loads(metadata_json)
                metadata = AssetMetadata.from_dict(metadata_dict)
                
                # Extract asset file
                asset_path = self.assets_dir / f"{metadata.uid}.blend"
                if "asset.blend" in zf.namelist():
                    with zf.open("asset.blend") as src:
                        with open(asset_path, 'wb') as dst:
                            dst.write(src.read())
            
            # Create asset object
            asset = Asset(metadata, str(asset_path))
            self.assets[metadata.uid] = asset
            
            return asset
        except Exception as e:
            print(f"Import failed: {e}")
            return None
    
    def create_bundle(self, name: str, assets: List[Asset], 
                     version: str = "1.0.0") -> Optional[AssetBundle]:
        """
        Create asset bundle.
        
        Args:
            name (str): Bundle name
            assets (list): Assets to include
            version (str): Bundle version
        
        Returns:
            AssetBundle or None if validation fails
        """
        bundle = AssetBundle(name, version)
        
        for asset in assets:
            bundle.add_asset(asset)
        
        # Validate
        is_valid, issues = bundle.validate()
        if not is_valid:
            print(f"Bundle validation failed: {issues}")
            return None
        
        self.bundles[bundle.uid] = bundle
        return bundle
    
    def export_bundle(self, bundle: AssetBundle, export_path: str) -> bool:
        """
        Export asset bundle.
        
        Args:
            bundle (AssetBundle): Bundle to export
            export_path (str): Where to save
        
        Returns:
            True if successful
        """
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create bundle package
            with zipfile.ZipFile(export_path, 'w') as zf:
                # Write bundle metadata
                bundle_meta = {
                    'uid': bundle.uid,
                    'name': bundle.name,
                    'version': bundle.version,
                    'created_date': bundle.created_date,
                    'asset_count': len(bundle.assets),
                }
                zf.writestr("bundle.json", json.dumps(bundle_meta, indent=2))
                
                # Write each asset
                for i, asset in enumerate(bundle.assets):
                    asset_meta = json.dumps(asset.metadata.to_dict(), indent=2)
                    zf.writestr(f"assets/{i:03d}/metadata.json", asset_meta)
                    
                    if asset.file_path and Path(asset.file_path).exists():
                        zf.write(asset.file_path, f"assets/{i:03d}/asset.blend")
            
            return True
        except Exception as e:
            print(f"Bundle export failed: {e}")
            return False
    
    def _load_registry(self):
        """Load asset registry from disk."""
        registry_file = self.project_dir / "asset_registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
                    for uid, asset_data in registry.items():
                        metadata = AssetMetadata.from_dict(asset_data)
                        asset = Asset(metadata)
                        self.assets[uid] = asset
            except Exception as e:
                print(f"Failed to load registry: {e}")
    
    def save_registry(self):
        """Save asset registry to disk."""
        registry_file = self.project_dir / "asset_registry.json"
        registry = {uid: asset.metadata.to_dict() for uid, asset in self.assets.items()}
        
        try:
            with open(registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            print(f"Failed to save registry: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get asset collection statistics."""
        return {
            'total_assets': len(self.assets),
            'total_bundles': len(self.bundles),
            'total_size_mb': sum(a.metadata.file_size_mb for a in self.assets.values()),
            'by_type': self._count_by_type(),
            'by_category': self._count_by_category(),
            'by_license': self._count_by_license(),
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count assets by type."""
        counts = {}
        for asset in self.assets.values():
            asset_type = asset.metadata.asset_type.value
            counts[asset_type] = counts.get(asset_type, 0) + 1
        return counts
    
    def _count_by_category(self) -> Dict[str, int]:
        """Count assets by category."""
        counts = {}
        for asset in self.assets.values():
            category = asset.metadata.category.value
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _count_by_license(self) -> Dict[str, int]:
        """Count assets by license."""
        counts = {}
        for asset in self.assets.values():
            license_type = asset.metadata.license.value
            counts[license_type] = counts.get(license_type, 0) + 1
        return counts
