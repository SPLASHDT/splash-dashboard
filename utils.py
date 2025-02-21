import os 
import re
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime

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


def add_query_params(base_url, params):
    """
    Adds query parameters to a base URL.

    Args:
        base_url: The base URL as a string.
        params: A dictionary of key-value pairs representing the query parameters.

    Returns:
        The URL with the added query parameters as a string.  Returns the original
        base_url if params is None or empty.  Handles cases where the base_url
        already has query parameters.
    """

    if not params:  # Handle empty or None params
        return base_url

    encoded_params = urlencode(params)  # Encode the parameters

    if "?" in base_url: # Check if base_url has existing query params
        return base_url + "&" + encoded_params
    else:
        return base_url + "?" + encoded_params


def get_formatted_today_date():
    start_date = datetime.now().date()
    return start_date.strftime("%d-%m-%Y")


def get_dataset_params(site_location_val):
    if site_location_val == "Dawlish":
        option = "dawlish"
        start_date = get_formatted_today_date()
    elif find_words_with_suffix(site_location_val, "Storm Bert"):
        option = "storm_bert"
        start_date = "21-11-2024"
    elif find_words_with_suffix(site_location_val, "no overtopping"):
        option = "no_overtopping"
        start_date = "10-12-2024"
    else: 
        option = "penzance"
        start_date = get_formatted_today_date()
    return option, start_date
