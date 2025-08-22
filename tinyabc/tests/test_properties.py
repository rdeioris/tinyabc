import unittest
from tinyabc.archive import Archive
from .utils import get_fixture, struct_property_encoder


class TestProperties(unittest.TestCase):

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

    def test_blender_dims(self):
        archive = Archive.from_filename(get_fixture("test_blender_anim.abc"))
        self.assertEqual(
            archive["/MovingNode"].properties[".xform"][".animChans"].dims, [1]
        )

    def test_blender_cube(self):
        archive = Archive.from_filename(get_fixture("test_blender_cube.abc"))
        tree = archive["/Cube/Cube_001"].properties.totree(
            encoder=struct_property_encoder
        )
        self.assertEqual(
            tree,
            {
                ".geom": {
                    ".selfBnds": [(-1.0, -1.0, -1.0, 1.0, 1.0, 1.0)],
                    "P": [
                        [
                            (-1.0, -1.0, 1.0),
                            (-1.0, 1.0, 1.0),
                            (-1.0, -1.0, -1.0),
                            (-1.0, 1.0, -1.0),
                            (1.0, -1.0, 1.0),
                            (1.0, 1.0, 1.0),
                            (1.0, -1.0, -1.0),
                            (1.0, 1.0, -1.0),
                        ]
                    ],
                    ".faceIndices": [
                        [
                            2,
                            3,
                            1,
                            0,
                            6,
                            7,
                            3,
                            2,
                            4,
                            5,
                            7,
                            6,
                            0,
                            1,
                            5,
                            4,
                            0,
                            4,
                            6,
                            2,
                            5,
                            1,
                            3,
                            7,
                        ]
                    ],
                    ".faceCounts": [[4, 4, 4, 4, 4, 4]],
                    ".userProperties": {"meshtype": [True]},
                    ".arbGeomParams": {},
                    "uv": {
                        ".vals": [
                            [
                                (0.375, 0.25),
                                (0.625, 0.25),
                                (0.625, 0.0),
                                (0.375, 0.0),
                                (0.375, 0.5),
                                (0.625, 0.5),
                                (0.375, 0.75),
                                (0.625, 0.75),
                                (0.375, 1.0),
                                (0.625, 1.0),
                                (0.125, 0.75),
                                (0.125, 0.5),
                                (0.875, 0.75),
                                (0.875, 0.5),
                            ]
                        ],
                        ".indices": [
                            [
                                0,
                                1,
                                2,
                                3,
                                4,
                                5,
                                1,
                                0,
                                6,
                                7,
                                5,
                                4,
                                8,
                                9,
                                7,
                                6,
                                10,
                                6,
                                4,
                                11,
                                7,
                                12,
                                13,
                                5,
                            ]
                        ],
                    },
                    "N": [
                        [
                            (-1.0, 0.0, -0.0),
                            (-1.0, 0.0, -0.0),
                            (-1.0, 0.0, -0.0),
                            (-1.0, 0.0, -0.0),
                            (0.0, 0.0, -1.0),
                            (0.0, 0.0, -1.0),
                            (0.0, 0.0, -1.0),
                            (0.0, 0.0, -1.0),
                            (1.0, 0.0, -0.0),
                            (1.0, 0.0, -0.0),
                            (1.0, 0.0, -0.0),
                            (1.0, 0.0, -0.0),
                            (0.0, 0.0, 1.0),
                            (0.0, 0.0, 1.0),
                            (0.0, 0.0, 1.0),
                            (0.0, 0.0, 1.0),
                            (0.0, -1.0, -0.0),
                            (0.0, -1.0, -0.0),
                            (0.0, -1.0, -0.0),
                            (0.0, -1.0, -0.0),
                            (0.0, 1.0, -0.0),
                            (0.0, 1.0, -0.0),
                            (0.0, 1.0, -0.0),
                            (0.0, 1.0, -0.0),
                        ]
                    ],
                }
            },
        )
