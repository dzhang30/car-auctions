import time
from collections import defaultdict
from typing import Dict, List, Optional, Set

import pandas as pd
import numpy as np

from car_auctions import utils

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.max_colwidth', 100)


def get_models_by_makes(car_makes_file_path: str, car_models_file_path: str) -> Dict[str, Set]:
    makes = get_car_makes(car_makes_file_path)
    models = get_car_models(car_models_file_path)  # this df also contains a model column

    models_and_makes = pd.concat([makes, models])
    models_and_makes.reset_index(drop=True, inplace=True)
    models_and_makes_dict = models_and_makes.to_dict('index')

    models_by_makes = defaultdict(set)
    for _, row in models_and_makes_dict.items():
        make = row['make']
        model = row['model']
        if row['model'] is not np.NaN:
            models_by_makes[make].add(model)
        else:
            models_by_makes[make] = set()

    return models_by_makes


def get_car_makes(car_makes_file_path: str) -> pd.Series:
    utils.validate_file_path(car_makes_file_path)

    makes_df = pd.read_csv(car_makes_file_path)
    makes_df['make'] = makes_df['make'].str.lower().str.replace(r'[^a-zA-Z0-9]', '')
    return makes_df


def get_car_models(car_models_file_path: str) -> pd.Series:
    utils.validate_file_path(car_models_file_path)

    makes_and_models_df = pd.read_csv(car_models_file_path)
    makes_and_models_df['make'] = makes_and_models_df['make'].str.lower().str.replace(r'[^a-zA-Z0-9]', '')
    makes_and_models_df['model'] = makes_and_models_df['model'].str.lower().str.replace(r'[^a-zA-Z0-9 ]', '')

    return makes_and_models_df


def build_car_auction_dataframe(car_auctions_file_path: str, car_makes: Dict[str, Set]) -> pd.DataFrame:
    utils.validate_file_path(car_auctions_file_path)
    main_df = pd.read_csv(car_auctions_file_path)

    # populate mileage
    main_df['Mileage'] = extract_mileage_series(main_df)

    # parse description_url
    url = main_df['description_url'].str.extract('https://bringatrailer.com/listing/(.+)/$', expand=False)
    url_components = url.str.split('-', expand=False)

    # populate year
    main_df['Year'] = extract_year_series(url_components, main_df)
    # print(main_df['Year'].isnull().sum())

    # populate make
    main_df['Make'] = extract_make_series(url_components, main_df, car_makes)
    # print(main_df['Make'].isnull().sum())

    # populate no reserve
    main_df['No Reserve'] = extract_no_reserve_series(main_df)

    return main_df


def extract_mileage_series(main_df: pd.DataFrame) -> pd.Series:
    original_mileage = main_df['description_name'].str.extract(r'([0-9k,]+)-Mile', expand=False)
    cleaned_mileage = original_mileage.str.replace(',', '').str.replace('k', '000')

    return cleaned_mileage


def extract_year_series(url_components: pd.Series, main_df: pd.DataFrame) -> pd.Series:
    # get years from the description_url column
    years = pd.to_numeric(url_components.str[0], errors='coerce', downcast='integer')
    invalid_years_bool_idx = np.logical_or.reduce([years.isnull(), years < 1900, years > 2039])

    # try to get the remaining missing years from the description_name column
    valid_year_regex = r'(?:^|\D)(?P<Year>19[0-9]{1}[0-9]{1}|20[0-3]{1}[0-9]{1})(?:$|\D)'
    matched_years = main_df.loc[invalid_years_bool_idx, 'description_name'].str.extract(valid_year_regex, expand=False)

    years[invalid_years_bool_idx] = matched_years
    return years


def extract_make_series(url_components: pd.Series, main_df: pd.DataFrame, car_makes: Dict[str, Set]) -> pd.Series:
    # get makes from the description_url column
    makes = url_components.apply(lambda row: _filter_by_known_makes(row, car_makes))
    missing_makes_bool_idx = makes.isnull()

    # try to get the remaining missing makes from the description_name column
    matched_makes = main_df.loc[missing_makes_bool_idx].apply(
        lambda row: _filter_by_known_makes(row['description_name'].split(' '), car_makes), axis=1)

    makes[missing_makes_bool_idx] = matched_makes
    return makes


def extract_no_reserve_series(main_df: pd.DataFrame) -> pd.Series:
    no_reserve: pd.Series = main_df['description_name'].str.extract(r'(No Reserve):', expand=False)
    no_reserve.replace(['No Reserve', np.NaN], ['Yes', 'No'], inplace=True)

    return no_reserve


def _filter_by_known_makes(column_val: Optional[List], car_makes: Dict[str, Set]) -> Optional[str]:
    if isinstance(column_val, list):
        column_val_without_nums = [col_part for col_part in column_val if not col_part.isnumeric()]
        column_substrings = utils.create_substrings_from_list_of_strings(column_val_without_nums)

        for col_substring in column_substrings:
            if col_substring in car_makes:
                return col_substring

    return pd.NA


if __name__ == '__main__':
    a = time.time()

    models_by_makes = get_models_by_makes('../car_makes.csv', '../car_models.csv')
    car_auction_data = build_car_auction_dataframe('../bring_a_trailer.csv', models_by_makes)

    b = time.time()
    print(b - a)
