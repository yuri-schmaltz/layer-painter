"""
Layer Painter Advanced Filtering System

Comprehensive filtering and query system for Layer Painter with:
- Layer filtering by type, name, opacity, visibility
- Advanced layer queries (chains, presets, history)
- Blend mode support and blending operations
- Layer group operations
- Filter presets and saved queries

Usage:
    from layer_painter.filtering import LayerFilter, BlendMode
    
    # Create filter
    filter = LayerFilter(layer_type="PAINT", min_opacity=0.5)
    
    # Apply filter to material
    filtered_layers = filter.apply(material)
    
    # Use presets
    visible_paint_layers = LayerFilter.preset_visible_paint_layers(material)
"""

import bpy
from enum import Enum
from typing import List, Dict, Optional, Callable, Tuple, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


# ============================================================================
# Blend Mode Definitions
# ============================================================================

class BlendMode(Enum):
    """Blend mode enumeration for layers."""
    NORMAL = "Normal"
    MULTIPLY = "Multiply"
    SCREEN = "Screen"
    OVERLAY = "Overlay"
    SOFT_LIGHT = "Soft Light"
    HARD_LIGHT = "Hard Light"
    COLOR_DODGE = "Color Dodge"
    COLOR_BURN = "Color Burn"
    DARKEN = "Darken"
    LIGHTEN = "Lighten"
    DIFFERENCE = "Difference"
    EXCLUSION = "Exclusion"
    ADD = "Add"
    SUBTRACT = "Subtract"
    LINEAR_BURN = "Linear Burn"
    LINEAR_DODGE = "Linear Dodge"


# Blend mode shader implementations
BLEND_MODE_NODES = {
    BlendMode.NORMAL: "Mix",  # Uses input opacity
    BlendMode.MULTIPLY: "Multiply",
    BlendMode.SCREEN: "Screen",
    BlendMode.OVERLAY: "Overlay",
    BlendMode.ADD: "Add",
}


# ============================================================================
# Filter Definition
# ============================================================================

@dataclass
class FilterCriteria:
    """Defines filter criteria for layer queries."""
    layer_type: Optional[str] = None  # "FILL" or "PAINT"
    min_opacity: float = 0.0
    max_opacity: float = 1.0
    enabled_only: bool = False
    name_contains: Optional[str] = None
    name_exact: Optional[str] = None
    blend_mode: Optional[BlendMode] = None
    has_channels: Optional[List[str]] = None  # Must have these channels


class LayerFilter:
    """Advanced layer filtering and query system."""
    
    def __init__(self, 
                 layer_type: Optional[str] = None,
                 min_opacity: float = 0.0,
                 max_opacity: float = 1.0,
                 enabled_only: bool = False,
                 name_contains: Optional[str] = None,
                 name_exact: Optional[str] = None,
                 blend_mode: Optional[BlendMode] = None,
                 has_channels: Optional[List[str]] = None):
        """
        Create layer filter with criteria.
        
        Args:
            layer_type (str): Filter by layer type ("FILL" or "PAINT")
            min_opacity (float): Minimum opacity (0-1)
            max_opacity (float): Maximum opacity (0-1)
            enabled_only (bool): Only include enabled layers
            name_contains (str): Filter by substring in name
            name_exact (str): Filter by exact name match
            blend_mode (BlendMode): Filter by blend mode
            has_channels (list): Filter by required channels
        """
        self.criteria = FilterCriteria(
            layer_type=layer_type,
            min_opacity=min_opacity,
            max_opacity=max_opacity,
            enabled_only=enabled_only,
            name_contains=name_contains,
            name_exact=name_exact,
            blend_mode=blend_mode,
            has_channels=has_channels or []
        )
    
    def apply(self, material) -> List:
        """
        Apply filter to material layers.
        
        Args:
            material: Material object
        
        Returns:
            List of layers matching filter criteria
        """
        filtered_layers = []
        
        for layer in material.lp.layers:
            if self._matches_criteria(layer):
                filtered_layers.append(layer)
        
        return filtered_layers
    
    def _matches_criteria(self, layer) -> bool:
        """Check if layer matches all filter criteria."""
        criteria = self.criteria
        
        # Type filter
        if criteria.layer_type and layer.type != criteria.layer_type:
            return False
        
        # Opacity filter
        if not (criteria.min_opacity <= layer.opacity <= criteria.max_opacity):
            return False
        
        # Enabled filter
        if criteria.enabled_only and not layer.enabled:
            return False
        
        # Name filters
        if criteria.name_exact and layer.name != criteria.name_exact:
            return False
        
        if criteria.name_contains and criteria.name_contains.lower() not in layer.name.lower():
            return False
        
        # Blend mode filter
        if criteria.blend_mode and layer.blend_mode != criteria.blend_mode.value:
            return False
        
        # Channel filter
        if criteria.has_channels:
            layer_channel_names = {ch.name for ch in layer.channels}
            if not all(ch in layer_channel_names for ch in criteria.has_channels):
                return False
        
        return True
    
    def count(self, material) -> int:
        """Count layers matching filter."""
        return len(self.apply(material))
    
    def first(self, material):
        """Get first layer matching filter."""
        results = self.apply(material)
        return results[0] if results else None
    
    def last(self, material):
        """Get last layer matching filter."""
        results = self.apply(material)
        return results[-1] if results else None
    
    def reverse_order(self, material) -> List:
        """Get filtered layers in reverse order."""
        return list(reversed(self.apply(material)))
    
    def by_index(self, material, index: int):
        """Get nth filtered layer."""
        results = self.apply(material)
        return results[index] if 0 <= index < len(results) else None
    
    # Preset filters
    @staticmethod
    def preset_paint_layers(material) -> List:
        """Get all PAINT layers."""
        return LayerFilter(layer_type="PAINT").apply(material)
    
    @staticmethod
    def preset_fill_layers(material) -> List:
        """Get all FILL layers."""
        return LayerFilter(layer_type="FILL").apply(material)
    
    @staticmethod
    def preset_visible_layers(material) -> List:
        """Get all visible (enabled) layers."""
        return LayerFilter(enabled_only=True).apply(material)
    
    @staticmethod
    def preset_hidden_layers(material) -> List:
        """Get all hidden (disabled) layers."""
        layers = material.lp.layers
        return [l for l in layers if not l.enabled]
    
    @staticmethod
    def preset_opaque_layers(material, threshold: float = 0.9) -> List:
        """Get layers with high opacity."""
        return LayerFilter(min_opacity=threshold).apply(material)
    
    @staticmethod
    def preset_transparent_layers(material, threshold: float = 0.1) -> List:
        """Get layers with low opacity."""
        return LayerFilter(max_opacity=threshold).apply(material)
    
    @staticmethod
    def preset_visible_paint_layers(material) -> List:
        """Get visible PAINT layers."""
        filter = LayerFilter(layer_type="PAINT", enabled_only=True)
        return filter.apply(material)
    
    @staticmethod
    def preset_visible_fill_layers(material) -> List:
        """Get visible FILL layers."""
        filter = LayerFilter(layer_type="FILL", enabled_only=True)
        return filter.apply(material)
    
    @staticmethod
    def preset_with_base_color(material) -> List:
        """Get layers with Base Color channel."""
        return LayerFilter(has_channels=["Base Color"]).apply(material)
    
    @staticmethod
    def preset_with_normal(material) -> List:
        """Get layers with Normal channel."""
        return LayerFilter(has_channels=["Normal"]).apply(material)
    
    @staticmethod
    def by_name(material, name: str) -> Optional[Any]:
        """Find layer by exact name."""
        return LayerFilter(name_exact=name).first(material)
    
    @staticmethod
    def by_name_partial(material, substring: str) -> List:
        """Find layers containing substring in name."""
        return LayerFilter(name_contains=substring).apply(material)


# ============================================================================
# Layer Grouping & Organization
# ============================================================================

@dataclass
class LayerGroup:
    """Represents a logical group of layers."""
    name: str
    layers: List = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_layer(self, layer):
        """Add layer to group."""
        if layer not in self.layers:
            self.layers.append(layer)
    
    def remove_layer(self, layer):
        """Remove layer from group."""
        if layer in self.layers:
            self.layers.remove(layer)
    
    def get_visible_layers(self) -> List:
        """Get enabled layers in group."""
        return [l for l in self.layers if l.enabled]
    
    def set_all_visible(self, visible: bool = True):
        """Show/hide all layers in group."""
        for layer in self.layers:
            layer.enabled = visible
    
    def set_all_opacity(self, opacity: float):
        """Set opacity for all layers in group."""
        for layer in self.layers:
            layer.opacity = max(0.0, min(1.0, opacity))
    
    def delete_all(self, material):
        """Delete all layers in group."""
        for layer in self.layers[:]:  # Copy list to avoid modification during iteration
            material.remove_layer(layer.uid)
        self.layers.clear()


class LayerGroupManager:
    """Manage layer groups for organization."""
    
    def __init__(self):
        self.groups: Dict[str, LayerGroup] = {}
    
    def create_group(self, name: str, description: str = "") -> LayerGroup:
        """Create new layer group."""
        group = LayerGroup(name=name, description=description)
        self.groups[name] = group
        return group
    
    def get_group(self, name: str) -> Optional[LayerGroup]:
        """Get group by name."""
        return self.groups.get(name)
    
    def delete_group(self, name: str):
        """Delete group (doesn't delete layers)."""
        if name in self.groups:
            del self.groups[name]
    
    def list_groups(self) -> List[LayerGroup]:
        """Get all groups."""
        return list(self.groups.values())
    
    def organize_by_type(self, material) -> Dict[str, LayerGroup]:
        """Create groups based on layer type."""
        groups = {}
        
        paint_group = LayerGroup(name="Paint Layers", description="All PAINT layers")
        fill_group = LayerGroup(name="Fill Layers", description="All FILL layers")
        
        for layer in material.lp.layers:
            if layer.type == "PAINT":
                paint_group.add_layer(layer)
            elif layer.type == "FILL":
                fill_group.add_layer(layer)
        
        groups["Paint"] = paint_group
        groups["Fill"] = fill_group
        
        return groups
    
    def organize_by_channel(self, material) -> Dict[str, LayerGroup]:
        """Create groups based on primary channel."""
        groups = {}
        
        for layer in material.lp.layers:
            if layer.channels:
                channel_name = layer.channels[0].name
                if channel_name not in groups:
                    groups[channel_name] = LayerGroup(name=f"{channel_name} Layers")
                groups[channel_name].add_layer(layer)
        
        return groups
    
    def organize_by_opacity(self, material) -> Dict[str, LayerGroup]:
        """Create groups based on opacity ranges."""
        groups = {
            "Opaque (0.75-1.0)": LayerGroup(name="Opaque Layers"),
            "Semi-Opaque (0.5-0.75)": LayerGroup(name="Semi-Opaque Layers"),
            "Transparent (0-0.5)": LayerGroup(name="Transparent Layers"),
        }
        
        for layer in material.lp.layers:
            if layer.opacity >= 0.75:
                groups["Opaque (0.75-1.0)"].add_layer(layer)
            elif layer.opacity >= 0.5:
                groups["Semi-Opaque (0.5-0.75)"].add_layer(layer)
            else:
                groups["Transparent (0-0.5)"].add_layer(layer)
        
        return groups


# ============================================================================
# Layer Queries & Chains
# ============================================================================

class LayerQuery:
    """Build complex layer queries using method chaining."""
    
    def __init__(self, material):
        """Create query for material."""
        self.material = material
        self.filters: List[Callable] = []
    
    def of_type(self, layer_type: str) -> 'LayerQuery':
        """Filter by layer type."""
        self.filters.append(lambda l: l.type == layer_type)
        return self
    
    def paint(self) -> 'LayerQuery':
        """Filter to PAINT layers."""
        return self.of_type("PAINT")
    
    def fill(self) -> 'LayerQuery':
        """Filter to FILL layers."""
        return self.of_type("FILL")
    
    def visible(self) -> 'LayerQuery':
        """Filter to visible layers."""
        self.filters.append(lambda l: l.enabled)
        return self
    
    def hidden(self) -> 'LayerQuery':
        """Filter to hidden layers."""
        self.filters.append(lambda l: not l.enabled)
        return self
    
    def opacity_at_least(self, threshold: float) -> 'LayerQuery':
        """Filter by minimum opacity."""
        self.filters.append(lambda l: l.opacity >= threshold)
        return self
    
    def opacity_at_most(self, threshold: float) -> 'LayerQuery':
        """Filter by maximum opacity."""
        self.filters.append(lambda l: l.opacity <= threshold)
        return self
    
    def named(self, name: str) -> 'LayerQuery':
        """Filter by exact name."""
        self.filters.append(lambda l: l.name == name)
        return self
    
    def named_like(self, substring: str) -> 'LayerQuery':
        """Filter by name substring."""
        self.filters.append(lambda l: substring.lower() in l.name.lower())
        return self
    
    def with_channel(self, channel_name: str) -> 'LayerQuery':
        """Filter by channel presence."""
        def has_channel(layer):
            return any(ch.name == channel_name for ch in layer.channels)
        self.filters.append(has_channel)
        return self
    
    def custom(self, predicate: Callable) -> 'LayerQuery':
        """Add custom filter function."""
        self.filters.append(predicate)
        return self
    
    def execute(self) -> List:
        """Execute query and get results."""
        results = list(self.material.lp.layers)
        for filter_fn in self.filters:
            results = [l for l in results if filter_fn(l)]
        return results
    
    def count(self) -> int:
        """Count matching layers."""
        return len(self.execute())
    
    def first(self):
        """Get first matching layer."""
        results = self.execute()
        return results[0] if results else None
    
    def last(self):
        """Get last matching layer."""
        results = self.execute()
        return results[-1] if results else None
    
    def any(self) -> bool:
        """Check if any layers match."""
        return len(self.execute()) > 0
    
    def all_match(self) -> bool:
        """Check if all layers match."""
        total = len(self.material.lp.layers)
        matching = len(self.execute())
        return total > 0 and total == matching


# ============================================================================
# Blend Mode Operations
# ============================================================================

class BlendModeOperations:
    """Blend mode utilities and operations."""
    
    @staticmethod
    def get_supported_modes() -> List[BlendMode]:
        """Get list of supported blend modes."""
        return list(BlendMode)
    
    @staticmethod
    def apply_blend_mode(layer, blend_mode: BlendMode):
        """Apply blend mode to layer."""
        layer.blend_mode = blend_mode.value
    
    @staticmethod
    def cycle_blend_mode(layer):
        """Cycle to next blend mode."""
        modes = [m for m in BlendMode]
        current_idx = 0
        
        for i, mode in enumerate(modes):
            if layer.blend_mode == mode.value:
                current_idx = i
                break
        
        next_idx = (current_idx + 1) % len(modes)
        layer.blend_mode = modes[next_idx].value
        return modes[next_idx]
    
    @staticmethod
    def multiply_layers(bottom_layer, top_layer, output_channel: str = "Base Color"):
        """
        Apply multiply blend between two layers.
        
        Args:
            bottom_layer: Bottom layer
            top_layer: Top layer (applies multiply)
            output_channel: Channel to apply to
        """
        top_layer.blend_mode = BlendMode.MULTIPLY.value
    
    @staticmethod
    def screen_layers(bottom_layer, top_layer, output_channel: str = "Base Color"):
        """Apply screen blend between two layers."""
        top_layer.blend_mode = BlendMode.SCREEN.value
    
    @staticmethod
    def overlay_layers(bottom_layer, top_layer, output_channel: str = "Base Color"):
        """Apply overlay blend between two layers."""
        top_layer.blend_mode = BlendMode.OVERLAY.value


# ============================================================================
# Filter Presets & History
# ============================================================================

class FilterPreset:
    """Saved filter configuration."""
    
    def __init__(self, name: str, criteria: FilterCriteria, description: str = ""):
        self.name = name
        self.criteria = criteria
        self.description = description
    
    def apply(self, material) -> List:
        """Apply preset filter to material."""
        filter = LayerFilter(
            layer_type=self.criteria.layer_type,
            min_opacity=self.criteria.min_opacity,
            max_opacity=self.criteria.max_opacity,
            enabled_only=self.criteria.enabled_only,
            name_contains=self.criteria.name_contains,
            name_exact=self.criteria.name_exact,
            blend_mode=self.criteria.blend_mode,
            has_channels=self.criteria.has_channels
        )
        return filter.apply(material)


class FilterPresetManager:
    """Manage saved filter presets."""
    
    def __init__(self):
        self.presets: Dict[str, FilterPreset] = {}
        self._init_default_presets()
    
    def _init_default_presets(self):
        """Initialize built-in presets."""
        self.presets["Visible Paint"] = FilterPreset(
            name="Visible Paint",
            criteria=FilterCriteria(layer_type="PAINT", enabled_only=True),
            description="All visible paint layers"
        )
        
        self.presets["Visible Fill"] = FilterPreset(
            name="Visible Fill",
            criteria=FilterCriteria(layer_type="FILL", enabled_only=True),
            description="All visible fill layers"
        )
        
        self.presets["Opaque"] = FilterPreset(
            name="Opaque",
            criteria=FilterCriteria(min_opacity=0.9),
            description="Layers with opacity > 0.9"
        )
        
        self.presets["Transparent"] = FilterPreset(
            name="Transparent",
            criteria=FilterCriteria(max_opacity=0.5),
            description="Layers with opacity < 0.5"
        )
    
    def create_preset(self, name: str, criteria: FilterCriteria, description: str = ""):
        """Create new preset."""
        preset = FilterPreset(name, criteria, description)
        self.presets[name] = preset
        return preset
    
    def get_preset(self, name: str) -> Optional[FilterPreset]:
        """Get preset by name."""
        return self.presets.get(name)
    
    def list_presets(self) -> List[str]:
        """Get all preset names."""
        return list(self.presets.keys())
    
    def delete_preset(self, name: str):
        """Delete preset."""
        if name in self.presets:
            del self.presets[name]
    
    def apply_preset(self, name: str, material) -> List:
        """Apply preset to material."""
        preset = self.get_preset(name)
        if preset:
            return preset.apply(material)
        return []


# ============================================================================
# Initialization
# ============================================================================

# Global instances
_group_manager = None
_preset_manager = None

def get_group_manager() -> LayerGroupManager:
    """Get global layer group manager."""
    global _group_manager
    if _group_manager is None:
        _group_manager = LayerGroupManager()
    return _group_manager

def get_preset_manager() -> FilterPresetManager:
    """Get global filter preset manager."""
    global _preset_manager
    if _preset_manager is None:
        _preset_manager = FilterPresetManager()
    return _preset_manager
