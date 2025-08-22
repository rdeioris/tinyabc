import unittest
from tinyabc.archive import Archive
from .utils import get_fixture, struct_property_encoder


class TestSchema(unittest.TestCase):

    def test_blender_anim(self):
        archive = Archive.from_filename(get_fixture("test_blender_anim.abc"))
        tree = archive["/MovingNode"].properties.totree(encoder=struct_property_encoder)
        self.assertEqual(
            tree[".xform"][".inherits"], [True, True, True, True, True, True]
        )
        self.assertEqual(tree[".xform"][".ops"], [48, 48, 48, 48, 48, 48])
        self.assertEqual(tree[".xform"]["isNotConstantIdentity"], [True])
        self.assertEqual(tree[".xform"][".animChans"], [13])
        # fmt: off
        self.assertEqual(
            tree[".xform"][".vals"],
            [
                (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0),
                (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0),
                (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.2962963581085205, 0.0, 1.0),
                (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 3.7037036418914795, 0.0, 1.0),
                (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 5.0, 0.0, 1.0),
                (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 3.0, 0.0, 1.0)
            ]
        )
        self.assertEqual(tree["visible"], [1, 1, 1, 1, 1, 1])
