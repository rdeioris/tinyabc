import unittest
from tinyabc.ogawa import Ogawa
from .utils import get_fixture


class TestOgawa(unittest.TestCase):

    empty_fixture_version = (
        b"_ai_AlembicVersion=Alembic 1.8.8 (built May 30 2025 09:24:57)"
    )

    def test_empty_from_bytes(self):
        with open(get_fixture("test_ogawa_empty.abc"), "rb") as handle:
            ogawa = Ogawa(handle.read())
            self.assertEqual(ogawa.magic, b"Ogawa")
            self.assertEqual(ogawa.wflag, 0xFF)
            self.assertEqual(ogawa.version, (0, 1))
            self.assertIsInstance(ogawa.root, Ogawa.Group)
            self.assertEqual(len(ogawa.root.children), 6)
            self.assertIsInstance(ogawa.root.children[0], Ogawa.Data)
            self.assertIsInstance(ogawa.root.children[1], Ogawa.Data)
            self.assertIsInstance(ogawa.root.children[2], Ogawa.Group)
            self.assertIsInstance(ogawa.root.children[3], Ogawa.Data)
            self.assertIsInstance(ogawa.root.children[4], Ogawa.Data)
            self.assertIsInstance(ogawa.root.children[5], Ogawa.Data)
            self.assertEqual(ogawa.root.children[0].size, 4)
            self.assertEqual(ogawa.root.children[1].size, 4)
            self.assertEqual(len(ogawa.root.children[2].children), 2)
            self.assertEqual(
                ogawa.root.children[3].view, TestOgawa.empty_fixture_version
            )
            self.assertIsInstance(ogawa.root.children[2].children[0], Ogawa.Group)
            self.assertIsInstance(ogawa.root.children[2].children[1], Ogawa.Data)
            self.assertEqual(len(ogawa.root.children[2].children[0].children), 0)
            self.assertEqual(ogawa.root.children[2].children[1].size, 32)
            self.assertEqual(ogawa.root.children[4].size, 24)
            self.assertEqual(ogawa.root.children[5].size, 0)

    def test_empty_from_file(self):
        with open(get_fixture("test_ogawa_empty.abc"), "rb") as handle:
            ogawa = Ogawa.from_file(handle)
            self.assertEqual(ogawa.magic, b"Ogawa")
            self.assertEqual(ogawa.wflag, 0xFF)
            self.assertEqual(ogawa.version, (0, 1))
            self.assertIsInstance(ogawa.root, Ogawa.Group)
            self.assertEqual(len(ogawa.root.children), 6)
            self.assertIsInstance(ogawa.root.children[0], Ogawa.Data)
            self.assertIsInstance(ogawa.root.children[1], Ogawa.Data)
            self.assertIsInstance(ogawa.root.children[2], Ogawa.Group)
            self.assertIsInstance(ogawa.root.children[3], Ogawa.Data)
            self.assertIsInstance(ogawa.root.children[4], Ogawa.Data)
            self.assertIsInstance(ogawa.root.children[5], Ogawa.Data)
            self.assertEqual(ogawa.root.children[0].size, 4)
            self.assertEqual(ogawa.root.children[1].size, 4)
            self.assertEqual(len(ogawa.root.children[2].children), 2)
            self.assertEqual(
                ogawa.root.children[3].view, TestOgawa.empty_fixture_version
            )
            self.assertIsInstance(ogawa.root.children[2].children[0], Ogawa.Group)
            self.assertIsInstance(ogawa.root.children[2].children[1], Ogawa.Data)
            self.assertEqual(len(ogawa.root.children[2].children[0].children), 0)
            self.assertEqual(ogawa.root.children[2].children[1].size, 32)
            self.assertEqual(ogawa.root.children[4].size, 24)
            self.assertEqual(ogawa.root.children[5].size, 0)

    def test_empty_from_filename(self):
        ogawa = Ogawa.from_filename(get_fixture("test_ogawa_empty.abc"))
        self.assertEqual(ogawa.magic, b"Ogawa")
        self.assertEqual(ogawa.wflag, 0xFF)
        self.assertEqual(ogawa.version, (0, 1))
        self.assertIsInstance(ogawa.root, Ogawa.Group)
        self.assertEqual(len(ogawa.root.children), 6)
        self.assertIsInstance(ogawa.root.children[0], Ogawa.Data)
        self.assertIsInstance(ogawa.root.children[1], Ogawa.Data)
        self.assertIsInstance(ogawa.root.children[2], Ogawa.Group)
        self.assertIsInstance(ogawa.root.children[3], Ogawa.Data)
        self.assertIsInstance(ogawa.root.children[4], Ogawa.Data)
        self.assertIsInstance(ogawa.root.children[5], Ogawa.Data)
        self.assertEqual(ogawa.root.children[0].size, 4)
        self.assertEqual(ogawa.root.children[1].size, 4)
        self.assertEqual(len(ogawa.root.children[2].children), 2)
        self.assertEqual(ogawa.root.children[3].view, TestOgawa.empty_fixture_version)
        self.assertIsInstance(ogawa.root.children[2].children[0], Ogawa.Group)
        self.assertIsInstance(ogawa.root.children[2].children[1], Ogawa.Data)
        self.assertEqual(len(ogawa.root.children[2].children[0].children), 0)
        self.assertEqual(ogawa.root.children[2].children[1].size, 32)
        self.assertEqual(ogawa.root.children[4].size, 24)
        self.assertEqual(ogawa.root.children[5].size, 0)

    def test_empty_to_tree_with_encoder(self):
        ogawa = Ogawa.from_filename(get_fixture("test_ogawa_empty.abc"))
        self.assertEqual(
            ogawa.totree(encoder=bytes),
            [
                b"\x00\x00\x00\x00",
                b"8*\x00\x00",
                [
                    [],
                    b"\x19\t\xf5k\xfc\x06'#\xc7Q\xe8\xb4e\xeer\x8b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                ],
                b"_ai_AlembicVersion=Alembic 1.8.8 (built May 30 2025 09:24:57)",
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                b"",
            ],
        )

    def test_new(self):
        ogawa = Ogawa()
        self.assertEqual(ogawa.totree(), [])

    def test_serialize(self):
        ogawa = Ogawa.from_filename(get_fixture("test_ogawa_empty.abc"))
        ogawa_copy = Ogawa(ogawa.serialize())
        self.assertEqual(
            ogawa_copy.totree(encoder=bytes),
            [
                b"\x00\x00\x00\x00",
                b"8*\x00\x00",
                [
                    [],
                    b"\x19\t\xf5k\xfc\x06'#\xc7Q\xe8\xb4e\xeer\x8b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                ],
                b"_ai_AlembicVersion=Alembic 1.8.8 (built May 30 2025 09:24:57)",
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                b"",
            ],
        )

    def test_from_tree_simple(self):
        ogawa = Ogawa.from_tree([b"hello", b"world"])
        self.assertEqual(ogawa.totree(), [b"hello", b"world"])

    def test_from_tree_groups(self):
        ogawa = Ogawa.from_tree([[[b"hello"]], [[b"world"]]])
        self.assertEqual(ogawa.totree(), [[[b"hello"]], [[b"world"]]])

    def test_from_tree_strings(self):
        ogawa = Ogawa.from_tree(
            [
                [[b"hello", [b"test", [[], [b"test001", b"test002"]]], "string"]],
                [[b"world"]],
                "another string",
            ]
        )
        self.assertEqual(
            ogawa.totree(),
            [
                [[b"hello", [b"test", [[], [b"test001", b"test002"]]], b"string"]],
                [[b"world"]],
                b"another string",
            ],
        )

    def test_simple_tree_from_filename(self):
        ogawa = Ogawa.from_filename(get_fixture("test_ogawa_simple.abc"))
        self.assertEqual(
            ogawa.totree(encoder=bytes),
            [
                b"\x00\x00\x00\x00",
                b"8*\x00\x00",
                [
                    [],
                    [
                        [[], b"\x00\x00\x10\x00\x06.xform"],
                        b"\xf6\x00>\xcdneE[\xd5\xad=.t\xd8\xed|\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                    ],
                    b"\n\x00\x00\x00dummyXform\x02\x19\t\xf5k\xfc\x06'#\xc7Q\xe8\xb4e\xeer\x8b\x0fl\xc3rO\xf4@\x12\x06\xf6\x0b\x98\xc2\xb3\xce\xb7",
                ],
                b"_ai_AlembicVersion=Alembic 1.8.8 (built May 30 2025 09:24:57)",
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                b"\x17schema=AbcGeom_Xform_v3>schema=AbcGeom_Xform_v3;schemaObjTitle=AbcGeom_Xform_v3:.xform",
            ],
        )
