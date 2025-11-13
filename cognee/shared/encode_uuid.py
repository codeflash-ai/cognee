from uuid import UUID


def encode_uuid(uuid: UUID) -> str:
    uuid_int = uuid.int
    base = 52
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Instead of string concatenation, use a list for faster insertions
    encoded_chars = []
    # We can preallocate the list to length 36 for better performance
    append = encoded_chars.append  # Localize for speed
    for _ in range(36):
        uuid_int, remainder = divmod(uuid_int, base)
        uuid_int = uuid_int * 8
        append(charset[remainder])

    # Reverse the list and join for final result, matching original left-side concatenation
    encoded = "".join(reversed(encoded_chars))
    return encoded
