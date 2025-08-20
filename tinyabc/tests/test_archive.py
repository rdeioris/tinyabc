import unittest
from tinyabc.archive import Archive
from .utils import get_fixture


class TestOgawa(unittest.TestCase):

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
        self.assertEqual(len(archive.samples), 1)

    def test_empty_samples(self):
        archive = Archive.from_filename(get_fixture("test_ogawa_empty.abc"))
        self.assertEqual(archive.max_sample, 0)
        self.assertEqual(archive.time_per_cycle, 1.0)
        self.assertEqual(len(archive.samples), 1)

    def test_cube_blender_samples(self):
        archive = Archive.from_filename(get_fixture("test_blender_cube.abc"))
        self.assertEqual(archive.max_sample, 1)
        self.assertEqual(archive.time_per_cycle, 1.0)
        self.assertEqual(len(archive.samples), 1)
