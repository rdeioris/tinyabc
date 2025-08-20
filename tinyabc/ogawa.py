from __future__ import annotations
from typing import List, Union
import struct


class OgawaException(Exception):
    pass


class Ogawa:
    class Group:
        def __init__(self, storage: Ogawa, offset):
            self.children: List[Union[Ogawa.Group, Ogawa.Data]] = []

            if offset == 0:
                return

            num_children = struct.unpack("<Q", storage.view[offset : offset + 8])[0]
            for i in range(0, num_children):
                node = storage._read_node_header(offset + 8 + (8 * i))
                self.children.append(node)

        def is_group(self, _index):
            return isinstance(self.children[_index], Ogawa.Group)

        def is_data(self, _index):
            return isinstance(self.children[_index], Ogawa.Data)

        def get_data(self, _index):
            return self.children[_index]

    class Data:
        def __init__(self, storage: Ogawa, offset):
            self.size = 0

            if offset == 0:
                self.view = b""
                return

            self.size = struct.unpack("<Q", storage.view[offset : offset + 8])[0]
            self.view = storage.view[offset + 8 : offset + 8 + self.size]

        def read_u8(self, offset):
            return self.view[offset]

        def read_u16(self, offset):
            return struct.unpack("<H", self.view[offset : offset + 2])[0]

        def read_u32(self, offset):
            return struct.unpack("<I", self.view[offset : offset + 4])[0]

        def read_u64(self, offset):
            return struct.unpack("<Q", self.view[offset : offset + 8])[0]

        def read_f32(self, offset):
            return struct.unpack("<f", self.view[offset : offset + 4])[0]

        def read_f64(self, offset):
            return struct.unpack("<d", self.view[offset : offset + 8])[0]

        def split_and_encode(self, separator, encoder):
            start = 0
            for i in range(0, self.size):
                if self.view[i : i + 1] == separator:
                    yield encoder(self.view[start:i])
                    start = i + 1
            yield encoder(self.view[start:])

    def __init__(self, data=None):
        if data:
            self.data = data
            self.view = memoryview(self.data)
            self.magic = self.data[0:5]
            if self.magic != b"Ogawa":
                raise OgawaException("Invalid magic value")
            self.wflag = self.data[5]
            self.version = tuple(self.data[6:8])
            self.root = self._read_node_header(8)
        else:
            self.data = b""
            self.view = memoryview(self.data)
            self.magic = b"Ogawa"
            self.wflag = 0
            self.version = (0, 1)
            self.root = Ogawa.Group(self, 0)

    @staticmethod
    def from_filename(filename):
        with open(filename, "rb") as handle:
            return Ogawa.from_file(handle)

    @staticmethod
    def from_file(handle):
        return Ogawa(handle.read())

    @staticmethod
    def from_tree(tree):
        ogawa = Ogawa()

        def _add_node(parent, node):
            # enforce string to be utf8
            if isinstance(node, str):
                node = node.encode("utf8")
            try:
                memoryview(node)
                new_data = Ogawa.Data(ogawa, 0)
                new_data.view = node
                parent.children.append(new_data)
            except:
                new_group = Ogawa.Group(ogawa, 0)
                parent.children.append(new_group)
                for child in node:
                    _add_node(new_group, child)

        for node in tree:
            _add_node(ogawa.root, node)

        return ogawa

    def _read_node_header(self, offset):
        value = struct.unpack("<Q", self.data[offset : offset + 8])[0]
        if value >> 63 == 0:
            return Ogawa.Group(self, value)
        value &= 0x7FFFFFFFFFFFFFFF
        return Ogawa.Data(self, value)

    def totree(self, encoder=None):
        def _build_node(parent, node):
            if isinstance(node, Ogawa.Data):
                if encoder:
                    parent.append(encoder(node.view))
                else:
                    parent.append(node.view)
            else:
                new_list = []
                for child in node.children:
                    _build_node(new_list, child)
                parent.append(new_list)

        tree = []
        for child in self.root.children:
            _build_node(tree, child)
        return tree

    def __iter__(self):
        return iter(self.totree())

    def collect_data(self):
        chunks = {}

        def _collect(chunks, node):
            if isinstance(node, Ogawa.Data):
                chunks[node] = node.view
            else:
                for child in node.children:
                    _collect(chunks, child)

        for child in self.root.children:
            _collect(chunks, child)

        return chunks

    def serialize(self, optimize=False):
        blob = bytearray()

        blob += self.magic + struct.pack("<BBB", 0xFF, self.version[0], self.version[1])

        blob += bytes(8)

        chunks = self.collect_data()
        offsets = {}

        current_offset = len(blob)

        for chunk in chunks:
            bytechunk = bytes(chunks[chunk])
            blob += struct.pack("<Q", len(bytechunk)) + bytechunk
            offsets[chunk] = current_offset
            current_offset = len(blob)

        def _serialize_node(blob, node, node_offset):
            if isinstance(node, Ogawa.Data):
                blob[node_offset : node_offset + 8] = struct.pack(
                    "<Q", offsets[node] | 0x8000000000000000
                )
            else:
                group_blob = struct.pack("<Q", len(node.children)) + bytes(
                    8 * len(node.children)
                )
                group_offset = len(blob)
                blob += group_blob
                for i, child in enumerate(node.children):
                    _serialize_node(blob, child, group_offset + 8 + (i * 8))
                blob[node_offset : node_offset + 8] = struct.pack("<Q", group_offset)

        root_group_offset = len(blob)

        blob += struct.pack("<Q", len(self.root.children))

        current_offset = len(blob)

        blob += bytes(8 * len(self.root.children))

        for child in self.root.children:
            _serialize_node(blob, child, current_offset)
            current_offset += 8

        # update the root group offset
        blob[8:16] = struct.pack("<Q", root_group_offset)

        return blob
