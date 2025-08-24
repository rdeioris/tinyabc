import unittest
from tinyabc.archive import Archive
from tinyabc.schema import AbcGeom_PolyMesh_v1
from .utils import get_fixture, struct_property_encoder
from tinyabc.encoders import numpy_property

try:
    import numpy

    has_numpy = True
except ImportError:
    has_numpy = False


class TestSchema(unittest.TestCase):

    def test_blender_cone_get_schema(self):
        archive = Archive.from_filename(get_fixture("test_blender_cone.abc"))
        self.assertEqual(archive["/Cone/Mesh"].get_schema(), "AbcGeom_PolyMesh_v1")

    def test_blender_cone_to_schema(self):
        archive = Archive.from_filename(get_fixture("test_blender_cone.abc"))
        self.assertIsInstance(archive["/Cone/Mesh"].to_schema(), AbcGeom_PolyMesh_v1)

    @unittest.skipIf(not has_numpy, "numpy not available")
    def test_blender_cone_AbcGeom_PolyMesh_v1(self):
        archive = Archive.from_filename(get_fixture("test_blender_cone.abc"))
        polymesh = archive["/Cone/Mesh"].to_schema()
        face_indices = polymesh.get_face_indices(encoder=numpy_property)
        positions = polymesh.get_P(encoder=numpy_property)
        self.assertEqual(len(face_indices), 128)
        self.assertEqual(len(positions), 33)

    def test_blender_vertex_anim(self):
        archive = Archive.from_filename(get_fixture("test_blender_vertexanim.abc"))
        samples = archive.root.children[0].children[0].properties['.geom'].totree(encoder=struct_property_encoder)['P']
        self.assertEqual(len(samples), 31)
