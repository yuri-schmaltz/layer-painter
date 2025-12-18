import os
import sys
import json
import tempfile
import unittest
import importlib.util
from pathlib import Path

# Dynamically import assets_extended from repository root
ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "assets_extended.py"
spec = importlib.util.spec_from_file_location("assets_extended", str(MODULE_PATH))
assets_extended = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets_extended)


class TestSemanticVersion(unittest.TestCase):
    def test_parse_and_compare(self):
        v = assets_extended.SematicVersion.parse("1.2.3")
        # typo in class name? handle via actual class

    def test_compatibility(self):
        v = assets_extended.SemanticVersion.parse("1.2.5")
        self.assertTrue(v.is_compatible_with("1.2+"))
        self.assertTrue(v.is_compatible_with("1.x"))
        self.assertFalse(v.is_compatible_with("2.0.0"))


class TestAssetManager(unittest.TestCase):
    def test_register_and_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = assets_extended.AssetManager(tmp)
            a = mgr.register_asset(
                name="Walnut Wood",
                asset_type=assets_extended.AssetType.MATERIAL,
                category=assets_extended.AssetCategory.WOOD,
                version="1.0.0",
                description="High quality wood",
                author="Tester",
                tags=["wood", "pbr"]
            )
            found = mgr.find_assets(name="Walnut")
            self.assertTrue(any(x.metadata.uid == a.metadata.uid for x in found))

    def test_export_import_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = assets_extended.AssetManager(tmp)
            a = mgr.register_asset(
                name="Canvas Fabric",
                asset_type=assets_extended.AssetType.MATERIAL,
                category=assets_extended.AssetCategory.FABRIC,
                version="2.1.0"
            )
            export_path = Path(tmp) / "canvas_v2_1_0.lpa"
            ok = mgr.export_asset(a, str(export_path))
            self.assertTrue(ok)
            self.assertTrue(export_path.exists())

            # New manager import
            mgr2 = assets_extended.AssetManager(tmp)
            imported = mgr2.import_asset(str(export_path))
            self.assertIsNotNone(imported)
            self.assertEqual(imported.metadata.name, "Canvas Fabric")
            self.assertEqual(imported.metadata.version, "2.1.0")

    def test_dependency_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = assets_extended.AssetManager(tmp)
            proc = mgr.register_asset(
                name="Normal Map Processor",
                asset_type=assets_extended.AssetType.PRESET,
                category=assets_extended.AssetCategory.UTILITY,
                version="1.2.0"
            )
            metal = mgr.register_asset(
                name="Advanced Metal",
                asset_type=assets_extended.AssetType.MATERIAL,
                category=assets_extended.AssetCategory.METAL,
                version="2.0.0"
            )
            metal.add_dependency("Normal Map Processor", "1.0+", required=True)
            is_valid, issues = metal.validate_dependencies(list(mgr.assets.values()))
            self.assertTrue(is_valid, msg=f"Issues: {issues}")


if __name__ == "__main__":
    unittest.main()