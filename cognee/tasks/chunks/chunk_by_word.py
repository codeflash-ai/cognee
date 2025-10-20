import re
from typing import Iterator, Tuple


SENTENCE_ENDINGS = r"[.;!?…。！？]"
PARAGRAPH_ENDINGS = r"[\n\r]"


def is_real_paragraph_end(last_char: str, current_pos: int, text: str) -> bool:
    """
    Determine if the current position represents a valid paragraph end.

    The function checks if the last character indicates a possible sentence ending, then
    verifies if the subsequent characters lead to a valid paragraph end based on specific
    conditions.

    Parameters:
    -----------

        - last_char (str): The last processed character
        - current_pos (int): Current position in the text
        - text (str): The input text

    Returns:
    --------

        - bool: True if this is a real paragraph end, False otherwise
    """
    # Compile patterns once for improved efficiency
    # These must remain readable from their constants
    # This avoids recompiling every function call
    if not hasattr(is_real_paragraph_end, "_sentence_endings"):
        is_real_paragraph_end._sentence_endings = re.compile(SENTENCE_ENDINGS)
        is_real_paragraph_end._paragraph_endings = re.compile(PARAGRAPH_ENDINGS)

    sentence_endings = is_real_paragraph_end._sentence_endings
    paragraph_endings = is_real_paragraph_end._paragraph_endings

    if sentence_endings.match(last_char):
        return True

    j = current_pos + 1
    text_len = len(text)
    if j >= text_len:
        return False

    # Scan ahead quickly for paragraph endings or spaces
    while j < text_len:
        next_character = text[j]
        # Avoid calling re.match for every character by using set lookup for spaces/newlines
        # Only call regex if necessary
        # Directly compare for space and use regex for other endings
        if paragraph_endings.match(next_character) or next_character == " ":
            j += 1
            if j >= text_len:
                return False
        else:
            break

    if j < text_len and text[j].isupper():
        return True
    return False


def chunk_by_word(data: str) -> Iterator[Tuple[str, str]]:
    """
    Chunk text into words and sentence endings, preserving whitespace.

    Whitespace is included with the preceding word. Outputs can be joined with "" to
    recreate the original input.

    Parameters:
    -----------

        - data (str): The input string of text to be chunked into words and sentence
          endings.
    """
    current_chunk = ""
    i = 0

    while i < len(data):
        character = data[i]

        current_chunk += character

        if character == " ":
            yield (current_chunk, "word")
            current_chunk = ""
            i += 1
            continue

        if re.match(SENTENCE_ENDINGS, character):
            # Look ahead for whitespace
            next_i = i + 1
            while next_i < len(data) and data[next_i] == " ":
                current_chunk += data[next_i]
                next_i += 1

            is_paragraph_end = next_i < len(data) and re.match(PARAGRAPH_ENDINGS, data[next_i])
            yield (current_chunk, "paragraph_end" if is_paragraph_end else "sentence_end")
            current_chunk = ""
            i = next_i
            continue

        i += 1

    if current_chunk:
        yield (current_chunk, "word")
