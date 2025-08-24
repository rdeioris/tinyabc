def numpy_property(node, sample):
    import numpy

    struct_to_numpy_table = {"i": numpy.int32, "I": numpy.uint32, "f": numpy.float32}
    np_array = numpy.frombuffer(
        sample, dtype=struct_to_numpy_table[node.pod_type_format]
    )
    if node.extent > 1:
        return np_array.reshape((-1, node.extent))
    return np_array
