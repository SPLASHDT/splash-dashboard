import os 
import re
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime
import pandas as pd


# Load configuration file based on environment variable value
def loadConfigFile():
    environment = os.getenv("SPLASH_ENV")

    if environment == 'local':
        config_file_path = "config/.env"
    elif environment == 'docker':
        config_file_path = "config/.env.docker"
    elif environment == 'staging':
        config_file_path = "config/.env.staging"
    else: 
        config_file_path = "config/.env.production"

    load_dotenv(config_file_path)


# Find all words in a text that end with a specified suffix
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


# Add query parameters to a base URL
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


# Get today's date in string format
def get_formatted_today_date():
    start_date = datetime.now().date()
    return start_date.strftime("%d-%m-%Y")


# Get option and start date based on selected location
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


# Convert list to dataframe object
def convert_list_to_dataframe(data_list):
    """Converts a list of dictionaries to a Pandas DataFrame with a numerical index.

    Args:
        data_list: A list of dictionaries.

    Returns:
        A Pandas DataFrame with a numerical index starting from 0, or None if the 
        input list is invalid. Handles potential errors in time string parsing.
    """

    if not isinstance(data_list, list):
        return None

    if not data_list:
        return pd.DataFrame(columns=['time', 'overtopping_count', 'confidence'])

    try:
        df_data = []
        for item in data_list:
            try:
                time_obj = datetime.strptime(item['time'], "%a, %d %b %Y %H:%M:%S GMT")
                time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"Warning: Invalid time format: {item['time']}")
                time_str = None

            df_data.append({
                'time': time_str,
                'overtopping_count': item['overtopping_count'],
                'confidence': item['confidence']
            })

        df = pd.DataFrame(df_data)

        # The key change: Reset the index to a numerical one starting from 0
        df = df.reset_index(drop=True)  # drop=True discards the old index

        return df
    except (KeyError, TypeError) as e:
        print(f'Error converting list to DataFrame: {e}')
        return None

