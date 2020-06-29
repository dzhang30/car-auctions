import re
from collections import defaultdict
from typing import Dict, List, Optional, Set

import numpy as np
import pandas as pd

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


def get_car_makes(car_makes_file_path: str) -> pd.DataFrame:
    makes_df = utils.read_csv_to_lower_case(car_makes_file_path)
    makes_df['make'] = makes_df['make'].str.replace(r'[^a-zA-Z0-9]', '')
    return makes_df


def get_car_models(car_models_file_path: str) -> pd.DataFrame:
    makes_and_models_df = utils.read_csv_to_lower_case(car_models_file_path)

    makes_and_models_df['make'] = makes_and_models_df['make'].str.replace(r'[^a-zA-Z0-9]', '')
    makes_and_models_df['model'] = makes_and_models_df['model'].str.replace(r'[^a-zA-Z0-9]', '')

    return makes_and_models_df


def build_car_auction_dataframe(main_df: pd.DataFrame, models_by_makes: Dict[str, Set]) -> pd.DataFrame:
    url = main_df['description_url'].str.extract('https://bringatrailer.com/listing/(.+)/$', expand=False)
    url_components = url.str.split('-', expand=False)

    main_df['year'] = extract_year_series(url_components, main_df)
    main_df['make'] = extract_make_series(url_components, main_df, models_by_makes)
    main_df['model'] = extract_model_series(main_df, models_by_makes)  # *run this after extracting both Year and Make*
    main_df['no reserve'] = extract_no_reserve_series(main_df)
    main_df['mileage'] = extract_mileage_series(main_df)

    return main_df


def extract_mileage_series(main_df: pd.DataFrame) -> pd.Series:
    original_mileage = main_df['description_name'].str.extract(r'([0-9k,]+)-mile', expand=False, flags=re.IGNORECASE)
    cleaned_mileage = original_mileage.str.replace(',', '').str.replace('k', '000')

    return cleaned_mileage


def extract_year_series(url_components: pd.Series, main_df: pd.DataFrame) -> pd.Series:
    # get years from the description_url column first
    years = pd.to_numeric(url_components.str[0], errors='coerce', downcast='integer')
    invalid_years_bool_idx = np.logical_or.reduce([years.isnull(), years < 1900, years > 2039])

    # try to get the remaining missing years from the description_name column
    valid_year_regex = r'(?:^|\D)(?P<Year>19[0-9]{1}[0-9]{1}|20[0-3]{1}[0-9]{1})(?:$|\D)'
    matched_years = main_df.loc[invalid_years_bool_idx, 'description_name'].str.extract(valid_year_regex, expand=False)

    years[invalid_years_bool_idx] = matched_years
    years_int = years.fillna(0).astype('int')
    years_int.loc[years_int == 0] = ''

    return years_int


def extract_make_series(url_components: pd.Series, main_df: pd.DataFrame, models_by_makes: Dict[str, Set]) -> pd.Series:
    # get makes from the description_url column first
    makes = url_components.apply(lambda row: _filter_by_known_makes(row, models_by_makes))
    missing_makes_bool_idx = makes.isnull()

    # try to get the remaining missing makes from the description_name column
    matched_makes = main_df.loc[missing_makes_bool_idx].apply(
        lambda row: _filter_by_known_makes(row['description_name'].split(' '), models_by_makes), axis=1)

    makes[missing_makes_bool_idx] = matched_makes
    return makes


def extract_no_reserve_series(main_df: pd.DataFrame) -> pd.Series:
    no_reserve = main_df['description_name'].str.extract(r'(no reserve|reseve):', expand=False, flags=re.IGNORECASE)
    no_reserve.replace(['no reserve', 'no reseve', np.NaN], ['yes', 'yes', 'no'], inplace=True)

    return no_reserve


def extract_model_series(main_df: pd.DataFrame, models_by_makes: Dict[str, Set]) -> pd.Series:
    main_df['description_name'] = main_df['description_name'].str.replace('-', ' ')
    models = main_df.apply(lambda row: _filter_by_known_models(row, models_by_makes), axis=1)

    return models


def _filter_by_known_makes(column_val: Optional[List], models_by_makes: Dict[str, Set]) -> Optional[str]:
    if isinstance(column_val, list):
        column_val_without_nums = [col_part for col_part in column_val if not col_part.isnumeric()]
        column_substrings = utils.create_substrings_from_list_of_strings(column_val_without_nums)

        for col_substring in column_substrings:
            if col_substring in models_by_makes:
                return col_substring

    return pd.NA


def _filter_by_known_models(row: pd.Series, models_by_makes: Dict[str, Set]) -> Optional[str]:
    description_name = row['description_name']
    description_name_list = description_name.split()
    desciption_name_substrings = utils.create_substrings_from_list_of_strings(description_name_list)

    make = row['make']
    if make in models_by_makes:
        models_for_make = models_by_makes[make]
        for potential_model_substring in desciption_name_substrings:
            if potential_model_substring in models_for_make:
                return potential_model_substring

    return pd.NA


@utils.timer
def main():
    models_by_makes = get_models_by_makes('../car_makes.csv', '../car_models.csv')
    car_auctions_df = utils.read_csv_to_lower_case('../copy_bring_a_trailer.csv')
    car_auction_data = build_car_auction_dataframe(car_auctions_df, models_by_makes)

    return car_auction_data


if __name__ == '__main__':
    main()
