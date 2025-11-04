from cognee.infrastructure.engine import DataPoint

_subclass_cache = {}


def convert_node_to_data_point(node_data: dict) -> DataPoint:
    subclass = find_subclass_by_name(DataPoint, node_data["type"])

    return subclass(**node_data)


def get_all_subclasses(cls):
    subclasses = []
    for subclass in cls.__subclasses__():
        subclasses.append(subclass)
        subclasses.extend(get_all_subclasses(subclass))  # Recursively get subclasses

    return subclasses


def find_subclass_by_name(cls, name):
    if cls not in _subclass_cache:
        _subclass_cache[cls] = {subclass.__name__: subclass for subclass in get_all_subclasses(cls)}

    return _subclass_cache[cls].get(name)
