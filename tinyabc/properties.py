import struct
import math


class PropertyException(Exception):
    pass


class CompoundProperty:
    def __init__(self, name, archive, tree):
        self.name = name
        self.children = []
        if not tree.children:
            return
        offset = 0
        properties_headers_size = tree.children[-1].size
        property_index = 0
        while offset < properties_headers_size:
            offset = self._parse_header(
                self, archive, tree.children[-1], offset, tree.children[property_index]
            )
            property_index += 1

    def _parse_header(self, parent, archive, header_node, offset, property_node):
        info = header_node.read_u32(offset)
        offset += 4
        property_type = info & 0x3
        size_hint = (info >> 2) & 0x3
        size_hint_reader = [
            (header_node.read_u8, 1),
            (header_node.read_u16, 2),
            (header_node.read_u32, 4),
        ][size_hint]

        metadata_index = -1

        # only scalar and array here
        if property_type != 0:
            pod_type = (info >> 4) & 0xF
            pod_type_format = [
                "?",
                "B",
                "b",
                "H",
                "h",
                "I",
                "i",
                "Q",
                "q",
                "e",
                "f",
                "d",
                "string",
                "wstring",
            ][pod_type]
            has_time_sampling_index = (info >> 8) & 1
            has_first_and_last_changed_index = (info >> 9) & 1
            homogenous = (info >> 10) & 1
            zero_first_and_last_changed_index = (info >> 11) & 1
            extent = (info >> 12) & 0xFF
            metadata_index = (info >> 20) & 0xFF

            next_sample_index = size_hint_reader[0](offset)
            offset += size_hint_reader[1]

            if has_first_and_last_changed_index:
                first_changed_index = size_hint_reader[0](offset)
                offset += size_hint_reader[1]
                last_changed_index = size_hint_reader[0](offset)
                offset += size_hint_reader[1]
            elif zero_first_and_last_changed_index:
                first_changed_index = 0
                last_changed_index = 0
            else:
                first_changed_index = 1
                last_changed_index = next_sample_index - 1

            if has_time_sampling_index:
                time_sampling_index = size_hint_reader[0](offset)
                offset += size_hint_reader[1]
                # TODO use it
                time_sampling = 0
            else:
                time_sampling = 0

        name_size = size_hint_reader[0](offset)
        offset += size_hint_reader[1]

        name = bytes(header_node.view[offset : offset + name_size]).decode(
            archive.encoding
        )
        offset += name_size

        if metadata_index == 0xFF:
            raise A

        if property_type == 0:
            parent.children.append(CompoundProperty(name, archive, property_node))
        elif property_type == 1:
            parent.children.append(
                ScalarProperty(
                    name,
                    pod_type_format,
                    extent,
                    next_sample_index,
                    first_changed_index,
                    last_changed_index,
                    {},
                    property_node,
                )
            )
        else:  # we cover both 2 and 3 here, as 3 means "scalar like"
            parent.children.append(
                ArrayProperty(
                    name,
                    pod_type_format,
                    extent,
                    next_sample_index,
                    first_changed_index,
                    last_changed_index,
                    {},
                    property_node,
                )
            )

        return offset

    def totree(self, encoder=None):
        tree = {}

        def _process_property(parent, prop):
            if isinstance(prop, CompoundProperty):
                new_parent = {}
                for child in prop.children:
                    _process_property(new_parent, child)
                parent[prop.name] = new_parent
            else:
                parent[prop.name] = encoder(prop) if encoder else prop

        for child in self.children:
            _process_property(tree, child)
        return tree

    def __getitem__(self, key):
        if isinstance(key, str):
            matching = [i for i, o in enumerate(self.children) if o.name == key]
            if matching:
                key = matching[0]
            else:
                raise KeyError(key)
        return self.children[key]


class Property:
    def __init__(
        self,
        name,
        pod_type_format,
        extent,
        next_sample_index,
        first_changed_index,
        last_changed_index,
        meta,
        node,
    ):
        self.name = name
        self.pod_type_format = pod_type_format
        self.extent = extent
        self.next_sample_index = next_sample_index
        self.num_samples = self.next_sample_index
        self.first_changed_index = first_changed_index
        self.last_changed_index = last_changed_index
        self.metadata = meta
        self.setup_frames(node)

    def get_pod_size(self):
        if self.pod_type_format not in ("string", "wstring"):
            return struct.calcsize(self.pod_type_format) * self.extent
        raise PropertyException("Unsupported pod type: {}".format(self.pod_type_format))

    def get_sample(self, _index, encoder=None):

        true_index = self.get_sample_index(_index)        

        if self.pod_type_format not in ("string", "wstring"):
            sample = self.frames[true_index]
            return encoder(sample) if encoder else sample
        
    def get_sample_index(self, _index):
        if _index >= self.next_sample_index or _index < 0:
            return None

        true_index = _index - self.first_changed_index + 1
        if _index < self.first_changed_index or (
            self.first_changed_index == 0 and self.last_changed_index == 0
        ):
            true_index = 0
        elif _index >= self.last_changed_index:
            true_index = self.last_changed_index - self.first_changed_index + 1

        return true_index


class ScalarProperty(Property):
    def setup_frames(self, node):
        self.frames = [child.view[16:] for child in node.children]


class ArrayProperty(Property):
    def setup_frames(self, node):
        self.frames = [child.view[16:] for child in node.children[::2]]
        self.dims = [
            (
                struct.unpack("<I", child.view)
                if child.size > 0
                else ((node.children[_index * 2].size - 16) // self.get_pod_size(),)
            )
            for _index, child in enumerate(node.children[1::2])
        ]
        self.num_elements = [math.prod(dims) for dims in self.dims]
