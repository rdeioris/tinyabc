import os.path
import struct


def get_fixture(name):
    return os.path.join(os.path.dirname(__file__), "fixtures", name)


def struct_property_encoder(prop):
    return [
        struct.unpack(
            "<{}{}".format(prop.extent, prop.pod_type_format), prop.get_sample(i)
        )[0 if prop.extent == 1 else slice(None)]
        for i in range(0, prop.num_samples)
    ]
