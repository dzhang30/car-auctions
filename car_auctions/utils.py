import functools
import os
import time
from configparser import ConfigParser
from typing import List, Any

import pandas as pd


def timer(func: Any) -> Any:
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        print(f'Elapsed time for {func.__name__}: {elapsed_time:0.4f} seconds')
        return value

    return wrapper_timer


def read_config_file(config_path: str) -> ConfigParser:
    """
    Read the config file (.ini, .cfg, or similar format)

    :param config_path: path to the config file
    :param logger: logger for forensics
    :return: a ConfigParser object that contains the sections of the config file
    """
    config = ConfigParser()
    file_read = config.read(config_path)

    if not file_read:
        err_msg = 'Could not open/read the config file: {0}'.format(config_path)
        raise OSError(err_msg)

    return config


def add_default_dir_path(file_path: str, default_directory_path: str):
    if not os.path.dirname(file_path):
        return os.path.join(default_directory_path, file_path)


def validate_file_path(file_path: str) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'The file path {file_path} does not exist')


def validate_dir_path(dir_path: str) -> None:
    if not os.path.isdir(dir_path):
        raise FileNotFoundError(f'The directory path {dir_path} does not exist')


def read_csv_to_lower_cased_df(csv_file_path: str) -> pd.DataFrame:
    validate_file_path(csv_file_path)

    csv_df = pd.read_csv(csv_file_path)
    csv_df.columns = [column_name.lower() for column_name in csv_df.columns]
    csv_df = csv_df.applymap(lambda s: s.lower() if type(s) == str else s)

    return csv_df


def create_substrings_from_list_of_strings(list_of_strings: List[str]) -> List[str]:
    substrings = []
    for i in range(len(list_of_strings)):
        for j in range(i, len(list_of_strings)):
            substrings.append(''.join(list_of_strings[i:j + 1]))

    return substrings
