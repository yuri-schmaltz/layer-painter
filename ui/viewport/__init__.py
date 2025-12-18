import bpy
from . import layer_settings, layers, material, export, assets


classes = (
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()
    layer_settings.register()
    layers.register()
    material.register()
    export.register()
    assets.register()


def unregister():
    unreg_classes()
    layer_settings.unregister()
    layers.unregister()
    material.unregister()
    export.unregister()
    assets.unregister()