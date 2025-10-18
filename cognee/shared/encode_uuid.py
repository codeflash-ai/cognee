from uuid import UUID


def encode_uuid(uuid: UUID) -> str:
    uuid_int = uuid.int
    base = 52
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Pre-allocate list for much faster concatenation
    encoded_chars = [""] * 36
    i = 35
    while i >= 0:
        uuid_int, remainder = divmod(uuid_int, base)
        uuid_int = uuid_int * 8
        encoded_chars[i] = charset[remainder]
        i -= 1
    return "".join(encoded_chars)
