from datetime import datetime
from uuid import UUID


def serialize_data(data):
    """
    Recursively convert various data types to serializable formats.

    This function processes dictionaries and lists, converting any datetime objects to ISO
    8601 strings, and UUID objects to their string representation. Other data types are
    returned unchanged. It handles recursive structures if present.

    Parameters:
    -----------

        - data: The input data to serialize, which can be a dict, list, datetime, UUID, or
          other types.

    Returns:
    --------

        The serialized representation of the input data, with datetime objects converted to
        ISO format and UUIDs to strings.
    """
    # Fast-path for common atomic types
    if type(data) is datetime:
        return data.isoformat()  # Convert datetime to ISO 8601 string
    elif type(data) is UUID:
        return str(data)
    elif type(data) is dict:
        # Avoid extra method lookups inside dict comprehension
        items = data.items()
        return {key: serialize_data(value) for key, value in items}
    elif type(data) is list:
        # Avoid generic isinstance for potential performance gain with large lists
        return [serialize_data(item) for item in data]
    else:
        return data
