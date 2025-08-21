from .ogawa import Ogawa
from .schema import Object, Property


class ArchiveException(Exception):
    pass


class Archive:

    def __init__(self, storage: Ogawa, encoding="utf8"):
        self.storage = storage
        self.encoding = encoding

        if len(self.storage.root.children) < 6:
            raise ArchiveException("Expected at least 6 nodes in storage")

        if not self.storage.root.is_data(0):
            raise ArchiveException("Expected node 0 (version) to be data")

        if not self.storage.root.is_data(1):
            raise ArchiveException("Expected node 1 (file_version) to be data")

        self.version = self.storage.root.get_data(0).read_u32(0)
        self.file_version = self.storage.root.get_data(1).read_u32(0)

        if not self.storage.root.is_data(3):
            raise ArchiveException("Expected node 3 (metadata) to be data")

        self.metadata = {}

        for item in self.storage.root.get_data(3).split_and_encode(b";", encoder=bytes):
            key, value = item.split(b"=")
            self.metadata[key.decode(self.encoding)] = value.decode(self.encoding)

        if not self.storage.root.is_data(4):
            raise ArchiveException("Expected node 4 (time_samples) to be data")

        self.max_sample = self.storage.root.get_data(4).read_u32(0)
        self.time_per_cycle = self.storage.root.get_data(4).read_f64(4)
        self.samples = []
        num_samples = self.storage.root.get_data(4).read_u32(12)
        for i in range(0, num_samples):
            self.samples.append(
                self.storage.root.get_data(4).read_f64(12 + 4 + (i * 8))
            )

        if not self.storage.root.is_data(5):
            raise ArchiveException("Expected node 3 (indexed_metadata) to be data")

        self.indexed_metadata = [b""]

        offset = 0
        while offset < self.storage.root.get_data(5).size:
            metadata_size = self.storage.root.get_data(5).read_u8(offset)
            offset += 1
            metadata = self.storage.root.get_data(5).view[
                offset : offset + metadata_size
            ]
            offset += metadata_size
            self.indexed_metadata.append(metadata)

        self.root = Object(
            self, None, "ABC", self.metadata, self.storage.root.get_group(2)
        )

    @staticmethod
    def from_filename(filename):
        return Archive(Ogawa.from_filename(filename))

    @staticmethod
    def from_filename(filename):
        return Archive(Ogawa.from_filename(filename))

    @staticmethod
    def from_file(handle):
        return Archive(Ogawa.from_file(handle))

    @staticmethod
    def from_tree(tree):
        return Archive(Ogawa.from_tree(tree))

    @staticmethod
    def from_buffer(data):
        return Archive(Ogawa(data))

    def __getitem__(self, key):
        if not key.startswith("/"):
            raise ArchiveException("Object path has to start with a /")
        parts = key.split("/")
        item = self.root
        for part in parts[1:]:
            item = item[part]
        return item
