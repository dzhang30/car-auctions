import functools
import os
import time
from typing import List

import pandas as pd


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return value

    return wrapper_timer


def validate_file_path(file_path: str) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'The csv file_path {file_path} does not exist')


def read_csv_to_lower_case(csv_file_path: str) -> pd.DataFrame:
    validate_file_path(csv_file_path)

    csv_df = pd.read_csv(csv_file_path)
    csv_df.columns = [column_name.lower() for column_name in csv_df.columns]
    # csv_df = csv_df.apply(lambda x: x.astype(str).str.lower())
    csv_df = csv_df.applymap(lambda s: s.lower() if type(s) == str else s)

    return csv_df


def create_substrings_from_list_of_strings(list_of_strings: List[str]) -> List[str]:
    substrings = []
    for i in range(len(list_of_strings)):
        for j in range(i, len(list_of_strings)):
            substrings.append(''.join(list_of_strings[i:j + 1]))

    return substrings
