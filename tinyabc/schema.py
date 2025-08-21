class Object:
    def __init__(self, archive, parent, name, metadata, tree):
        self.parent = parent
        self.name = name
        self.metadata = metadata
        self.children = []
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
            key = [i for i, o in enumerate(self.children) if o.name == key][0]
        return self.children[key]


class Property:
    pass
