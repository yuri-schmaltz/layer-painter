import bpy
from . import panel_assets


classes = (
    panel_assets.LP_PT_AssetsPanel,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()


def unregister():
    unreg_classes()
