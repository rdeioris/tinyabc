registered_schemas = {}


def register_schema(name):
    def wrapper(cls):
        registered_schemas[name] = cls
        return cls

    return wrapper


class Schema:
    def __init__(self, _object, default_property_encoder=None):
        self._object = _object
        self.default_property_encoder = default_property_encoder

    def get_field(self, path, sample_index, encoder=None):
        current = self._object.properties
        for item in path:
            current = current[item]
        sample = current.get_sample(sample_index)
        if not encoder:
            encoder = self.default_property_encoder
        return encoder(current, sample) if encoder else sample


@register_schema("AbcGeom_GeomBase_v1")
class AbcGeom_GeomBase_v1(Schema):
    pass


@register_schema("AbcGeom_PolyMesh_v1")
class AbcGeom_PolyMesh_v1(AbcGeom_GeomBase_v1):

    def get_P(self, sample_index=0, encoder=None):
        return self.get_field((".geom", "P"), sample_index, encoder)

    def get_N(self, sample_index=0, encoder=None):
        return self.get_field((".geom", "N"), sample_index, encoder)

    def get_face_indices(self, sample_index=0, encoder=None):
        return self.get_field((".geom", ".faceIndices"), sample_index, encoder)

    def get_face_counts(self, sample_index=0, encoder=None):
        return self.get_field((".geom", ".faceCounts"), sample_index, encoder)
