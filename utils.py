import os 
import re
from dotenv import load_dotenv

def loadConfigFile():
    environment = os.getenv("SPLASH_ENV")

    if environment == 'local':
        config_file_path = "config/.env"
    elif environment == 'staging':
        config_file_path = "config/.env.staging"
    else: 
        config_file_path = "config/.env.production"

    load_dotenv(config_file_path)

def find_words_with_suffix(text, suffix):
    """
    Finds all words in a text that end with a specified suffix.

    Args:
        text: The input text string.
        suffix: The suffix to search for (case-insensitive).

    Returns:
        A list of words that end with the suffix.  Returns an empty list if no matches are found.
        Returns None if the input is invalid.
    """

    if not isinstance(text, str) or not isinstance(suffix, str):
      return None # Or raise a TypeError if you prefer

    # Escape special regex characters in the suffix to avoid unexpected behavior
    escaped_suffix = re.escape(suffix)

    # Use a word boundary (\b) to ensure we match whole words only
    pattern = r"\b\w*" + escaped_suffix + r"\b"  # \b ensures word boundaries
    # i flag for case-insensitive matching
    matches = re.findall(pattern, text, re.IGNORECASE) 
    return bool(matches)