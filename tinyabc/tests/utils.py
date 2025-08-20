import os.path


def get_fixture(name):
    return os.path.join(os.path.dirname(__file__), "fixtures", name)
