"""
Advanced Filtering System - Usage Examples

Examples of using Layer Painter's advanced filtering, grouping, and query system.
"""

from layer_painter.filtering import (
    LayerFilter, LayerGroup, LayerGroupManager, LayerQuery,
    BlendMode, BlendModeOperations, FilterPreset, FilterPresetManager,
    get_group_manager, get_preset_manager
)


# ============================================================================
# Example 1: Basic Layer Filtering
# ============================================================================

def example_basic_filtering(material):
    """Simple filtering examples."""
    
    # Get all PAINT layers
    paint_filter = LayerFilter(layer_type="PAINT")
    paint_layers = paint_filter.apply(material)
    print(f"Paint layers: {len(paint_layers)}")
    
    # Get all visible FILL layers
    visible_fill = LayerFilter(layer_type="FILL", enabled_only=True)
    layers = visible_fill.apply(material)
    print(f"Visible fill layers: {len(layers)}")
    
    # Get layers with high opacity
    opaque_filter = LayerFilter(min_opacity=0.8)
    opaque_layers = opaque_filter.apply(material)
    print(f"Opaque layers (>0.8): {len(opaque_layers)}")
    
    # Find layer by name
    base_layer = LayerFilter.by_name(material, "Base Color")
    if base_layer:
        print(f"Found layer: {base_layer.name}")
    
    # Find layers by partial name
    detail_layers = LayerFilter.by_name_partial(material, "detail")
    print(f"Layers containing 'detail': {len(detail_layers)}")


# ============================================================================
# Example 2: Preset Filters
# ============================================================================

def example_preset_filters(material):
    """Using built-in filter presets."""
    
    # Get visible paint layers
    visible_paint = LayerFilter.preset_visible_paint_layers(material)
    print(f"Visible paint layers: {len(visible_paint)}")
    
    # Get all hidden layers
    hidden_layers = LayerFilter.preset_hidden_layers(material)
    print(f"Hidden layers: {len(hidden_layers)}")
    
    # Get layers with Base Color channel
    color_layers = LayerFilter.preset_with_base_color(material)
    print(f"Layers with Base Color: {len(color_layers)}")
    
    # Get layers with Normal channel
    normal_layers = LayerFilter.preset_with_normal(material)
    print(f"Layers with Normal: {len(normal_layers)}")
    
    # Get first/last
    first_paint = LayerFilter.preset_paint_layers(material)
    if first_paint:
        print(f"First paint layer: {first_paint[0].name}")


# ============================================================================
# Example 3: Complex Queries with Chaining
# ============================================================================

def example_query_chaining(material):
    """Build complex queries using method chaining."""
    
    # Get visible paint layers with Base Color
    query = LayerQuery(material)
    layers = (query
        .paint()  # PAINT layers only
        .visible()  # Must be enabled
        .opacity_at_least(0.5)  # Opacity >= 0.5
        .with_channel("Base Color")  # Must have Base Color
        .execute())
    print(f"Visible, opaque paint layers with Base Color: {len(layers)}")
    
    # Query with custom filter
    query2 = LayerQuery(material)
    layers = (query2
        .named_like("Detail")  # Name contains "Detail"
        .custom(lambda l: len(l.channels) > 1)  # Has multiple channels
        .execute())
    print(f"Detail layers with multiple channels: {len(layers)}")
    
    # Check if any layers match criteria
    query3 = LayerQuery(material)
    has_transparent = (query3
        .fill()
        .opacity_at_most(0.3)
        .any())
    print(f"Has transparent fill layers: {has_transparent}")
    
    # Get first match
    query4 = LayerQuery(material)
    first_normal_layer = (query4
        .with_channel("Normal")
        .visible()
        .first())
    if first_normal_layer:
        print(f"First visible normal layer: {first_normal_layer.name}")


# ============================================================================
# Example 4: Layer Grouping & Organization
# ============================================================================

def example_layer_grouping(material):
    """Organize layers into groups."""
    
    # Create manual group
    group_manager = get_group_manager()
    
    base_group = group_manager.create_group(
        name="Base Layers",
        description="Foundation color and normal layers"
    )
    
    detail_group = group_manager.create_group(
        name="Detail Layers",
        description="Fine details and weathering"
    )
    
    # Add layers to groups (manually)
    paint_layers = LayerFilter.preset_paint_layers(material)
    if len(paint_layers) > 0:
        base_group.add_layer(paint_layers[0])
    
    # Show/hide entire group
    base_group.set_all_visible(visible=True)
    detail_group.set_all_visible(visible=False)
    
    # Set opacity for group
    base_group.set_all_opacity(0.8)
    
    # Auto-organize by type
    type_groups = group_manager.organize_by_type(material)
    print(f"Paint layers in group: {len(type_groups['Paint'].layers)}")
    print(f"Fill layers in group: {len(type_groups['Fill'].layers)}")
    
    # Auto-organize by channel
    channel_groups = group_manager.organize_by_channel(material)
    for channel_name, group in channel_groups.items():
        print(f"Layers for {channel_name}: {len(group.layers)}")
    
    # Auto-organize by opacity
    opacity_groups = group_manager.organize_by_opacity(material)
    for opacity_range, group in opacity_groups.items():
        print(f"{opacity_range}: {len(group.layers)} layers")


# ============================================================================
# Example 5: Blend Mode Operations
# ============================================================================

def example_blend_modes(material):
    """Work with blend modes."""
    
    # Get all supported modes
    modes = BlendModeOperations.get_supported_modes()
    print(f"Supported blend modes: {len(modes)}")
    
    # Apply specific blend mode
    paint_layers = LayerFilter.preset_paint_layers(material)
    if paint_layers:
        BlendModeOperations.apply_blend_mode(
            paint_layers[0], 
            BlendMode.MULTIPLY
        )
        print(f"Applied MULTIPLY to {paint_layers[0].name}")
    
    # Cycle through blend modes
    if paint_layers:
        next_mode = BlendModeOperations.cycle_blend_mode(paint_layers[0])
        print(f"Cycled to {next_mode.value}")
    
    # Apply screen blend between layers
    if len(paint_layers) >= 2:
        BlendModeOperations.screen_layers(
            paint_layers[0],
            paint_layers[1],
            output_channel="Base Color"
        )
        print("Applied SCREEN blend between layers")


# ============================================================================
# Example 6: Filter Presets
# ============================================================================

def example_filter_presets(material):
    """Use and manage filter presets."""
    
    preset_manager = get_preset_manager()
    
    # List available presets
    presets = preset_manager.list_presets()
    print(f"Available presets: {presets}")
    
    # Apply preset
    visible_paint_layers = preset_manager.apply_preset("Visible Paint", material)
    print(f"Visible paint layers: {len(visible_paint_layers)}")
    
    # Create custom preset
    from layer_painter.filtering import FilterCriteria
    
    custom_criteria = FilterCriteria(
        layer_type="PAINT",
        min_opacity=0.5,
        max_opacity=1.0,
        enabled_only=True
    )
    
    preset_manager.create_preset(
        name="My Opaque Paint Layers",
        criteria=custom_criteria,
        description="Visible paint layers with medium to full opacity"
    )
    
    # Use custom preset
    custom_layers = preset_manager.apply_preset("My Opaque Paint Layers", material)
    print(f"Custom preset matches: {len(custom_layers)} layers")


# ============================================================================
# Example 7: Advanced Operations
# ============================================================================

def example_advanced_operations(material):
    """Advanced filtering operations."""
    
    # Get nth layer from filtered results
    paint_filter = LayerFilter(layer_type="PAINT")
    third_paint_layer = paint_filter.by_index(material, 2)
    if third_paint_layer:
        print(f"Third paint layer: {third_paint_layer.name}")
    
    # Get layers in reverse order
    reverse_layers = paint_filter.reverse_order(material)
    print(f"Paint layers (reversed): {len(reverse_layers)}")
    
    # Count with filter
    paint_count = paint_filter.count(material)
    print(f"Total paint layers: {paint_count}")
    
    # Complex multi-criteria filter
    multi_filter = LayerFilter(
        layer_type="PAINT",
        min_opacity=0.3,
        max_opacity=0.9,
        enabled_only=True,
        name_contains="texture",
        has_channels=["Base Color", "Normal"]
    )
    
    matching_layers = multi_filter.apply(material)
    print(f"Layers matching all criteria: {len(matching_layers)}")
    
    # Filter operations on groups
    group_manager = get_group_manager()
    group = group_manager.organize_by_opacity(material)["Opaque (0.75-1.0)"]
    
    # Get subset of group
    subset = LayerQuery(material).custom(lambda l: l in group.layers).visible().execute()
    print(f"Visible opaque layers: {len(subset)}")


# ============================================================================
# Example 8: Practical Workflow - Batch Operations
# ============================================================================

def example_batch_operations(material):
    """Use filtering for batch operations."""
    
    # Show all paint layers, hide all fill layers
    paint_layers = LayerFilter.preset_paint_layers(material)
    for layer in paint_layers:
        layer.enabled = True
    
    fill_layers = LayerFilter.preset_fill_layers(material)
    for layer in fill_layers:
        layer.enabled = False
    
    print("Paint layers shown, fill layers hidden")
    
    # Set all visible layers to 0.8 opacity
    visible_filter = LayerFilter(enabled_only=True)
    for layer in visible_filter.apply(material):
        layer.opacity = 0.8
    
    print("All visible layers set to 0.8 opacity")
    
    # Apply multiply blend to all paint layers except first
    paint_layers = LayerFilter.preset_paint_layers(material)
    for i, layer in enumerate(paint_layers):
        if i > 0:  # Skip first
            BlendModeOperations.apply_blend_mode(layer, BlendMode.MULTIPLY)
    
    print(f"Applied MULTIPLY blend to {len(paint_layers)-1} paint layers")
    
    # Organize by channel and print stats
    group_manager = get_group_manager()
    channel_groups = group_manager.organize_by_channel(material)
    
    print("\nLayer organization by channel:")
    for channel_name, group in channel_groups.items():
        visible_count = len(group.get_visible_layers())
        total_count = len(group.layers)
        print(f"  {channel_name}: {visible_count}/{total_count} visible")


# ============================================================================
# Example 9: UI Integration Pattern
# ============================================================================

def example_ui_integration(context):
    """How to use filtering in UI panels."""
    
    """
    In ui/viewport/layers/panel_layers.py:
    
    from layer_painter.filtering import LayerFilter, LayerQuery
    
    class LP_PT_LayersPanel(bpy.types.Panel):
        bl_label = "Layers"
        
        def draw(self, context):
            layout = self.layout
            material = context.object.data.materials[0]
            
            # Show statistics
            paint_count = len(LayerFilter.preset_paint_layers(material))
            fill_count = len(LayerFilter.preset_fill_layers(material))
            layout.label(text=f"Paint: {paint_count}  Fill: {fill_count}")
            
            # Filter buttons
            if layout.operator("lp.show_all_paint"):
                for layer in LayerFilter.preset_paint_layers(material):
                    layer.enabled = True
            
            if layout.operator("lp.hide_all_fill"):
                for layer in LayerFilter.preset_fill_layers(material):
                    layer.enabled = False
            
            # Draw filtered layers
            for layer in LayerFilter.preset_visible_layers(material):
                row = layout.row()
                row.label(text=layer.name)
                row.prop(layer, "opacity", slider=True)
    """


# ============================================================================
# Example 10: Performance Tips
# ============================================================================

def example_performance_tips(material):
    """Performance optimization when filtering."""
    
    # Good: Reuse filters for multiple operations
    paint_filter = LayerFilter(layer_type="PAINT", enabled_only=True)
    
    # Get count
    count = paint_filter.count(material)
    
    # Get list
    layers = paint_filter.apply(material)
    
    # Get first
    first = paint_filter.first(material)
    
    # BAD (avoid):
    # count = len(LayerFilter(layer_type="PAINT", enabled_only=True).apply(material))
    # layers = LayerFilter(layer_type="PAINT", enabled_only=True).apply(material)
    # first = LayerFilter(layer_type="PAINT", enabled_only=True).first(material)
    
    # Cache query results for complex filters
    query = LayerQuery(material).paint().visible().opacity_at_least(0.5)
    results = query.execute()  # Execute once
    
    # Use results multiple times
    count = len(results)
    first = results[0] if results else None
    last = results[-1] if results else None
    
    print("Performance optimization applied")
