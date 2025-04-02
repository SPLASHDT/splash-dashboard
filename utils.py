import os
import re
from dotenv import load_dotenv
from urllib.parse import urlencode
from datetime import datetime
import pandas as pd


def loadConfigFile():
    """Load configuration file based on environment variable value"""

    environment = os.getenv("SPLASH_ENV")

    if environment == "local":
        config_file_path = "config/.env"
    elif environment == "docker":
        config_file_path = "config/.env.docker"
    elif environment == "staging":
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
        bool: True if a list of words end with the suffix.
        Returns None if the input is invalid.
    """

    if not isinstance(text, str) or not isinstance(suffix, str):
        return None

    escaped_suffix = re.escape(suffix)
    pattern = r"\b\w*" + escaped_suffix + r"\b"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return bool(matches)


def add_resource(base_url, resource):
    """Add resource name to base query url

    Args:
        base_url (string): Base query url
        resource (string): Resource name e.g. significant-wave-height

    Returns:
        string: Query url with resource name
    """

    if not resource:
        return base_url

    return base_url + resource


def add_query_params(base_url, params):
    """
    Adds query parameters to a base URL.

    Args:
        base_url: The base URL as a string.
        params: A dictionary of key-value pairs representing the query parameters.

    Returns:
        string: The URL with the added query parameters as a string.  Returns the original
        base_url if params is None or empty.  Handles cases where the base_url
        already has query parameters.
    """

    if not params:
        return base_url

    encoded_params = urlencode(params)
    if "?" in base_url:
        return base_url + "&" + encoded_params
    else:
        return base_url + "?" + encoded_params


def format_date_to_str(param_date, format):
    """Format date to specific format

    Args:
        param_date (string): String representing date
        format (string): Target format for date

    Returns:
        string: Formatted string representing date
    """

    return param_date.strftime(format)


def format_range_date(param_date):
    """Format range date to mm-dd-yyyy

    Args:
        param_date (string): String representing date

    Returns:
        string: Formatted string representing date
    """

    cur_param_date = datetime.strptime(param_date, "%Y-%m-%d %H:%M:%S")

    return cur_param_date.strftime("%m-%d-%Y")


def get_dataset_params(site_location_val):
    """Get option and start date based on selected location

    Args:
        site_location_val (string): Selected option of dropdown box

    Returns:
        string, date: Option value and forecast start date
    """

    if site_location_val == "Dawlish":
        option = "dawlish"
        start_date = format_date_to_str(datetime.now().date(), "%d-%m-%Y")
    elif find_words_with_suffix(site_location_val, "Storm Bert"):
        option = "storm_bert"
        start_date = "21-11-2024"
    elif find_words_with_suffix(site_location_val, "no overtopping"):
        option = "no_overtopping"
        start_date = "10-12-2024"
    else:
        option = "penzance"
        start_date = format_date_to_str(datetime.now().date(), "%d-%m-%Y")
    return option, start_date


def convert_feature_list_to_df(data_list, feature_name):
    """Convert feature list to dataframe

    Args:
        data_list (list): Data list
        feature_name (string): Feature's name

    Returns:
        Dataframe: Feature's dataframe
    """

    if not isinstance(data_list, list):
        return None

    if not data_list:
        return pd.DataFrame(columns=["time", feature_name])

    try:
        df_data = []
        for item in data_list:
            try:
                time_obj = datetime.strptime(item["time"], "%a, %d %b %Y %H:%M:%S GMT")
                time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"Warning: Invalid time format: {item['time']}")
                time_str = None

            df_data.append({"time": time_str, feature_name: item[feature_name]})

        df = pd.DataFrame(df_data)
        df = df.reset_index(drop=True)

        return df
    except (KeyError, TypeError) as e:
        print(f"Error converting list to DataFrame: {e}")
        return None


def convert_list_to_dataframe(json_data, list_key):
    """
    Converts a JSON list to a pandas DataFrame.

    Args:
        json_data (dict): The JSON data as a dictionary.
        list_key (str): The key of the list within the JSON data.

    Returns:
        DataFrame: A DataFrame containing the list data, or None if an error occurs.
    """

    try:
        data_list = json_data[list_key]
        df = pd.DataFrame({list_key: data_list})
        return df
    except KeyError:
        print(f"Error: Key '{list_key}' not found in JSON data.")
        return None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return None


def convert_overtopping_data_to_df(data_list):
    """Converts a list of dictionaries to a Pandas DataFrame with a numerical index.

    Args:
        data_list: A list of dictionaries.

    Returns:
       Dataframe: A Pandas DataFrame with a numerical index starting from 0, or None if the
       input list is invalid. Handles potential errors in time string parsing.
    """

    if not isinstance(data_list, list):
        return None

    if not data_list:
        return pd.DataFrame(columns=["time", "overtopping_count", "confidence"])

    try:
        df_data = []
        for item in data_list:
            try:
                time_obj = datetime.strptime(item["time"], "%a, %d %b %Y %H:%M:%S GMT")
                time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"Warning: Invalid time format: {item['time']}")
                time_str = None

            df_data.append(
                {
                    "time": time_str,
                    "overtopping_count": item["overtopping_count"],
                    "confidence": item["confidence"],
                }
            )

        df = pd.DataFrame(df_data)

        df = df.reset_index(drop=True)

        return df
    except (KeyError, TypeError) as e:
        print(f"Error converting list to DataFrame: {e}")
        return None


def get_dataframes_to_save(n_clicks, trigger_id, dfs_to_store):
    """
    Function to retrieve and organize DataFrames.

    Args:
        n_clicks: Click count.
        trigger_id: Trigger ID.
        dfs_to_store: List of DataFrames to process (should have an even length).

    Returns:
        Tuple: Tuple of DataFrames (previous and current).
    """

    if len(dfs_to_store) % 2 != 0:
        raise ValueError("dfs_to_store must have an even number of elements.")

    results = []
    for i in range(0, len(dfs_to_store), 2):
        previous_df, current_df = get_dataframe_to_save(
            n_clicks, trigger_id, dfs_to_store[i], dfs_to_store[i + 1]
        )
        results.extend([previous_df, current_df])
    return tuple(results)


def get_dataframe_to_save(n_clicks, trigger_id, generated_df, stored_current_df):
    """Get dataframe to save

    Args:
        n_clicks (integer): Number of clicks of submit button
        trigger_id (string): Element's id which has triggered an event
        generated_df (Dataframe): Adjusted forecast dataframe
        stored_current_df (Dataframe): Forecast dataframe

    Returns:
        Dataframes: Forecast and adjusted forecast dataframes
    """

    if (
        n_clicks is None
        or n_clicks == 0
        or trigger_id is not None
        and trigger_id != "submit-button"
    ):
        tmp_previous_df = pd.DataFrame()
        tmp_current_df = generated_df
    else:
        saved_current_df = pd.DataFrame(stored_current_df)
        saved_current_df["stage"] = "forecast"
        tmp_previous_df = saved_current_df
        tmp_current_df = generated_df

    return tmp_previous_df, tmp_current_df
