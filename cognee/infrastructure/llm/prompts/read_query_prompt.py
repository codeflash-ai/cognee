from os import path

from cognee.root_dir import get_absolute_path
from cognee.shared.logging_utils import ERROR, get_logger

_DEFAULT_PROMPT_DIR = get_absolute_path("./infrastructure/llm/prompts")

_LOGGER = get_logger(level=ERROR)


def read_query_prompt(prompt_file_name: str, base_directory: str = None):
    """
    Read a query prompt from a file.

    Retrieve the contents of a specified prompt file, optionally using a provided base
    directory for the file path. If the base directory is not specified, a default path is
    used. Log errors if the file is not found or if another error occurs during file
    reading.

    Parameters:
    -----------

        - prompt_file_name (str): The name of the prompt file to be read.
        - base_directory (str): The base directory from which to read the prompt file. If
          None, a default path is used. (default None)

    Returns:
    --------

        Returns the contents of the prompt file as a string, or None if the file cannot be
        read due to an error.
    """

    try:
        if base_directory is None:
            base_directory = _DEFAULT_PROMPT_DIR

        file_path = path.join(base_directory, prompt_file_name)

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        _LOGGER.error(f"Error: Prompt file not found. Attempted to read: {file_path}")
        return None
    except Exception as e:
        _LOGGER.error(f"An error occurred: {e}")
        return None
