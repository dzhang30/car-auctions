import os
from typing import List


def validate_file_path(file_path: str) -> None:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'The file_path {file_path} does not exist')


def create_substrings_from_list_of_strings(list_of_strings: List[str]) -> List[str]:
    substrings = []
    for i in range(len(list_of_strings)):
        for j in range(i, len(list_of_strings)):
            substrings.append(''.join(list_of_strings[i:j + 1]))

    return substrings
