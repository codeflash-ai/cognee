from cognee.infrastructure.engine import DataPoint

_SUBCLASS_CACHE = {}


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
    # Use cached mapping for efficiency
    cache = _SUBCLASS_CACHE.get(cls)
    if cache is None:
        # Build dict mapping class names to subclasses
        cache = {subclass.__name__: subclass for subclass in get_all_subclasses(cls)}
        _SUBCLASS_CACHE[cls] = cache
    return cache.get(name, None)
