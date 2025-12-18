import bpy
from pathlib import Path

try:
    from ...assets_extended import AssetManager
    asset_manager_available = True
except Exception:
    asset_manager_available = False


class LP_PT_AssetsPanel(bpy.types.Panel):
    bl_label = "Assets"
    bl_idname = "LP_PT_Assets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Layer Painter"

    @classmethod
    def poll(cls, context):
        return asset_manager_available

    def draw(self, context):
        layout = self.layout

        base_dir = Path.home() / "layer_painter_project"
        manager = AssetManager(str(base_dir))
        stats = manager.get_statistics()

        col = layout.column(align=True)
        col.label(text="Asset Library")
        col.label(text=f"Total assets: {stats['total_assets']}")
        col.label(text=f"Total size: {stats['total_size_mb']:.1f} MB")

        layout.separator()
        layout.label(text="By Type:")
        for k, v in stats['by_type'].items():
            row = layout.row()
            row.label(text=f"{k}: {v}")

        layout.separator()
        layout.operator("lp_assets.export_example", icon='EXPORT')


class LP_OT_AssetsExportExample(bpy.types.Operator):
    bl_idname = "lp_assets.export_example"
    bl_label = "Export First Asset (Example)"
    bl_description = "Exports the first asset in the library to /tmp for demonstration"

    def execute(self, context):
        base_dir = Path.home() / "layer_painter_project"
        manager = AssetManager(str(base_dir))
        assets = list(manager.assets.values())
        if not assets:
            self.report({'WARNING'}, "No assets in library")
            return {'CANCELLED'}
        first = assets[0]
        export_path = Path("/tmp") / f"{first.metadata.name.replace(' ', '_')}.lpa"
        ok = manager.export_asset(first, str(export_path))
        if ok:
            self.report({'INFO'}, f"Exported to {export_path}")
            return {'FINISHED'}
        self.report({'ERROR'}, "Export failed")
        return {'CANCELLED'}
