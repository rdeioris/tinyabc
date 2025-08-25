import unittest
from tinyabc.archive import Archive
from .utils import get_fixture, struct_property_encoder


class TestArchive(unittest.TestCase):

    def test_empty_metadata(self):
        archive = Archive.from_filename(get_fixture("test_ogawa_empty.abc"))
        self.assertEqual(archive.version, 0)
        self.assertEqual(archive.file_version, 10808)
        self.assertEqual(
            archive.metadata,
            {"_ai_AlembicVersion": "Alembic 1.8.8 (built May 30 2025 09:24:57)"},
        )
        self.assertEqual(len(archive.indexed_metadata), 1)

    def test_empty_blender_metadata(self):
        archive = Archive.from_filename(get_fixture("test_blender_empty.abc"))
        self.assertEqual(archive.version, 0)
        self.assertEqual(archive.file_version, 10803)
        self.assertEqual(
            archive.metadata,
            {
                "FramesPerTimeUnit": "24.000000",
                "_ai_AlembicVersion": "Alembic 1.8.3 (built May 31 2025 09:39:20)",
                "_ai_Application": "Blender",
                "_ai_DateWritten": "Wed Aug 20 06:14:56 2025",
                "_ai_Description": "unknown",
                "blender_version": "v4.5.1 LTS",
            },
        )
        self.assertEqual(archive.indexed_metadata, [b"", b"interpretation=box"])

    def test_empty_blender_samples(self):
        archive = Archive.from_filename(get_fixture("test_blender_empty.abc"))
        self.assertEqual(archive.max_sample, 0)
        self.assertEqual(archive.time_per_cycle, 1.0)
        self.assertEqual(archive.samples, [0.0])

    def test_empty_samples(self):
        archive = Archive.from_filename(get_fixture("test_ogawa_empty.abc"))
        self.assertEqual(archive.max_sample, 0)
        self.assertEqual(archive.time_per_cycle, 1.0)
        self.assertEqual(archive.samples, [0.0])

    def test_blender_cube_samples(self):
        archive = Archive.from_filename(get_fixture("test_blender_cube.abc"))
        self.assertEqual(archive.max_sample, 1)
        self.assertEqual(archive.time_per_cycle, 1.0)
        self.assertEqual(archive.samples, [0.0])

    def test_empty_objects(self):
        archive = Archive.from_filename(get_fixture("test_ogawa_empty.abc"))
        self.assertEqual(archive.root.name, "ABC")

    def test_blender_cube_metadata(self):
        archive = Archive.from_filename(get_fixture("test_blender_cube.abc"))
        self.assertEqual(
            archive.root.metadata,
            {
                "FramesPerTimeUnit": "24.000000",
                "_ai_AlembicVersion": "Alembic 1.8.3 (built May 31 2025 09:39:20)",
                "_ai_Application": "Blender",
                "_ai_DateWritten": "Wed Aug 20 06:43:39 2025",
                "_ai_Description": "unknown",
                "blender_version": "v4.5.1 LTS",
            },
        )
        self.assertEqual(
            archive.root[0].metadata,
            {"schema": "AbcGeom_Xform_v3", "schemaObjTitle": "AbcGeom_Xform_v3:.xform"},
        )
        self.assertEqual(
            archive.root[0][0].metadata,
            {
                "schema": "AbcGeom_PolyMesh_v1",
                "schemaBaseType": "AbcGeom_GeomBase_v1",
                "schemaObjTitle": "AbcGeom_PolyMesh_v1:.geom",
            },
        )

    def test_blender_cube_metadata_by_name(self):
        archive = Archive.from_filename(get_fixture("test_blender_cube.abc"))
        self.assertEqual(
            archive.root["Cube"][0].metadata,
            {
                "schema": "AbcGeom_PolyMesh_v1",
                "schemaBaseType": "AbcGeom_GeomBase_v1",
                "schemaObjTitle": "AbcGeom_PolyMesh_v1:.geom",
            },
        )

    def test_blender_cube_metadata_by_path(self):
        archive = Archive.from_filename(get_fixture("test_blender_cube.abc"))
        self.assertEqual(
            archive["/Cube"][0].metadata,
            {
                "schema": "AbcGeom_PolyMesh_v1",
                "schemaBaseType": "AbcGeom_GeomBase_v1",
                "schemaObjTitle": "AbcGeom_PolyMesh_v1:.geom",
            },
        )
        self.assertEqual(
            archive["/Cube/Cube_001"].metadata,
            {
                "schema": "AbcGeom_PolyMesh_v1",
                "schemaBaseType": "AbcGeom_GeomBase_v1",
                "schemaObjTitle": "AbcGeom_PolyMesh_v1:.geom",
            },
        )
        self.assertEqual(
            archive["/Cube"]["Cube_001"].metadata,
            {
                "schema": "AbcGeom_PolyMesh_v1",
                "schemaBaseType": "AbcGeom_GeomBase_v1",
                "schemaObjTitle": "AbcGeom_PolyMesh_v1:.geom",
            },
        )

    def test_blender_tree(self):
        archive = Archive.from_filename(get_fixture("test_blender_tree.abc"))
        self.assertEqual(
            archive[
                "/Node_001/Node_001_001/Node_001_001_002/Node_001_001_002_001"
            ].name,
            "Node_001_001_002_001",
        )

    def test_blender_tree_wrong_path(self):
        archive = Archive.from_filename(get_fixture("test_blender_tree.abc"))
        self.assertRaises(
            KeyError,
            archive.__getitem__,
            "/Node_001/Node_001_001/Node_001_002_002/Node_001_001_002_001",
        )

    def test_blender_tree_wrong_name(self):
        archive = Archive.from_filename(get_fixture("test_blender_tree.abc"))
        self.assertRaises(
            KeyError,
            archive.root.__getitem__,
            "Node_Test",
        )

    def test_blender_tree_wrong_index(self):
        archive = Archive.from_filename(get_fixture("test_blender_tree.abc"))
        self.assertRaises(
            IndexError,
            archive.root.__getitem__,
            999,
        )

    def test_blender_tree_traverse(self):
        archive = Archive.from_filename(
            get_fixture("test_blender_light_with_custom_properties.abc")
        )
        tracker = {}
        tree = {}

        def _tree_filler(parent, node):
            node_dict = {
                "name": node.name,
                "metadata": node.metadata,
                "properties": node.properties.totree(encoder=struct_property_encoder),
                "children": [],
            }
            tracker[node] = node_dict
            if parent:
                tracker[parent]["children"].append(node_dict)
            else:
                tree.update(node_dict)

        archive.root.traverse(_tree_filler)
        self.assertEqual(
            len(tree["children"][0]["properties"][".xform"][".userProperties"].keys()),
            3,
        )
        self.assertTrue(
            "prop_001"
            in tree["children"][0]["properties"][".xform"][".userProperties"].keys()
        )
        self.assertTrue(
            "test001"
            in tree["children"][0]["properties"][".xform"][".userProperties"].keys()
        )
        self.assertTrue(
            "test002"
            in tree["children"][0]["properties"][".xform"][".userProperties"].keys()
        )
