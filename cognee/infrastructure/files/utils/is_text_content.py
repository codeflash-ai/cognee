_ALLOWED_TEXT_BYTES = set(range(0x20, 0x7F)).union({0x0A, 0x0D, 0x09})

_NON_TEXT_TRANS = bytes(byte if byte not in _ALLOWED_TEXT_BYTES else 0 for byte in range(256))


def is_text_content(content):
    """
    Determine if the content is text-based.

    This function checks for various indicators of text content, including null bytes, byte
    order marks (BOMs), ASCII character ranges, and common line breaks. If none of these
    indicators are present, the function defaults to assuming the content is text-based.

    Parameters:
    -----------

        - content: The byte content to be checked for text characteristics.

    Returns:
    --------

        - bool: Returns True if the content is determined to be text, False otherwise.
    """
    # Check for null bytes
    if b"\0" in content:
        return False

    # Check for common text encodings (BOMs)
    if content.startswith(
        (
            b"\xef\xbb\xbf",  # UTF-8
            b"\xff\xfe",  # UTF-16 LE
            b"\xfe\xff",  # UTF-16 BE
            b"\x00\x00\xfe\xff",  # UTF-32 LE
            b"\xff\xfe\x00\x00",  # UTF-32 BE
        )
    ):
        return True

    # Check for ASCII characters
    if not content.translate(_NON_TEXT_TRANS).strip(b"\x00"):
        return True

    # Check for common line break characters
    if b"\n" in content or b"\r" in content:
        return True

    # If no obvious indicators found, assume it's a text file
    return True
