class Object:
    def __init__(self, archive, parent, name, metadata, tree):
        self.parent = parent
        self.name = name
        self.metadata = metadata
        self.children = []
        self.properties = {}

        p = CompoundProperty(archive, tree.children[0])

        if not tree:
            return

        # retrieve children
        objects_headers_group = tree.get_data(-1)
        objects_headers_group_size = objects_headers_group.size

        objects_headers_size = objects_headers_group_size - 32

        offset = 0
        child_object_index = 0
        while offset < objects_headers_size:
            child_name_size = objects_headers_group.read_u32(offset)
            offset += 4
            child_name = bytes(
                objects_headers_group.view[offset : offset + child_name_size]
            ).decode(archive.encoding)
            offset += child_name_size
            child_metadata_index_or_size = objects_headers_group.read_u8(offset)
            offset += 1
            if child_metadata_index_or_size < len(archive.indexed_metadata):
                child_metadata = self._build_metadata(
                    archive.indexed_metadata[child_metadata_index_or_size],
                    archive.encoding,
                )
            else:
                child_inline_metadata = objects_headers_group.view[
                    offset : offset + child_metadata_index_or_size
                ]
                offset += child_metadata_index_or_size
                child_metadata = self._build_metadata(
                    child_inline_metadata, archive.encoding
                )
            self.children.append(
                Object(
                    archive,
                    self,
                    child_name,
                    child_metadata,
                    tree.children[child_object_index + 1],
                )
            )
            child_object_index += 1

    def _build_metadata(self, blob, encoding):
        metadata = {}
        for item in bytes(blob).split(b";"):
            key, value = item.split(b"=")
            metadata[key.decode(encoding)] = value.decode(encoding)
        return metadata

    def __getitem__(self, key):
        if isinstance(key, str):
            matching = [i for i, o in enumerate(self.children) if o.name == key]
            if matching:
                key = matching[0]
            else:
                raise KeyError(key)
        return self.children[key]


class CompoundProperty:
    def __init__(self, archive, tree):
        self.children = {}
        if not tree.children:
            return
        offset = 0
        properties_headers_size = tree.children[-1].size
        property_index = 0
        while offset < properties_headers_size:
            offset = self._parse_header(
                archive, tree.children[-1], offset, tree.children[property_index]
            )
            property_index += 1

    def _parse_header(self, archive, header_node, offset, property_node):
        info = header_node.read_u32(offset)
        offset += 4
        property_type = info & 0x3
        size_hint = (info >> 2) & 0x3
        size_hint_reader = [
            (header_node.read_u8, 1),
            (header_node.read_u16, 2),
            (header_node.read_u32, 4),
        ][size_hint]

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

        if property_type == 0:
            self.children[name] = CompoundProperty(archive, property_node)
        elif property_type == 1:
            self.children[name] = ScalarProperty(
                name, pod_type_format, {}, property_node
            )
        elif property_type == 2:
            self.children[name] = ArrayProperty(
                name, pod_type_format, {}, property_node
            )

        return offset


class ScalarProperty:
    def __init__(self, name, pod_type_format, meta, node):
        self.name = name
        self.metadata = {}
        self.hash = node.children[0].view[:16]
        self.data = node.children[0].view[16:]


class ArrayProperty:
    def __init__(self, name, pod_type_format, meta, node):
        self.hash = node.children[0].view[:16]
        self.data = node.children[0].view[16:]
