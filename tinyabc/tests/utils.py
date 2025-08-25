import os.path
import struct
from tinyabc.properties import ScalarProperty
import math


def get_fixture(name):
    return os.path.join(os.path.dirname(__file__), "fixtures", name)


def struct_property_encoder(prop):
    if isinstance(prop, ScalarProperty):
        return [
            struct.unpack(
                "<{}{}".format(prop.extent, prop.pod_type_format), prop.get_sample(i)
            )[0 if prop.extent == 1 else slice(None)]
            for i in range(0, prop.num_samples)
        ]
    else:
        samples = []
        for i in range(0, prop.num_samples):
            items = []
            offset = 0
            for j in range(prop.num_elements[prop.get_sample_index(i)]):
                if prop.pod_type_format not in ("string", "wstring"):
                    chunk = prop.get_sample(i)[offset : offset + prop.get_pod_size()]
                    offset += prop.get_pod_size()
                    items.append(
                        struct.unpack(
                            "<{}{}".format(prop.extent, prop.pod_type_format),
                            chunk,
                        )[0 if prop.extent == 1 else slice(None)]
                    )
                elif prop.pod_type_format == "string":
                    end_of_string_index = bytes(prop.get_sample(i)[offset:]).index(
                        b"\x00"
                    )
                    chunk = prop.get_sample(i)[offset : offset + end_of_string_index]
                    items.append(bytes(chunk).decode("utf8"))
                    offset += end_of_string_index + 1
                elif prop.pod_type_format == "wstring":
                    end_of_string_index = bytes(prop.get_sample(i)[offset:]).index(
                        b"\x00\x00\x00\x00"
                    )
                    chunk = prop.get_sample(i)[offset : offset + end_of_string_index]
                    items.append(bytes(chunk).decode("utf32"))
                    offset += end_of_string_index + 4
                else:
                    raise Exception(
                        "unsupported pod type: {}".format(prop.pod_type_format)
                    )
            samples.append(items)

        return samples
