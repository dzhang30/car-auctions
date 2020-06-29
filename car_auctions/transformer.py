import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from car_auctions import utils


@dataclass
class CarAuctionsTransformer:
    main_df: pd.DataFrame
    models_by_make: Dict[str, Dict]

    def __post_init__(self):
        base_description_url_regex = 'https://bringatrailer.com/listing/(.+)/$'
        description_urls = self.main_df['description_url'].str.extract(base_description_url_regex, expand=False)
        self._description_urls_components = description_urls.str.split('-', expand=False)

    def transform_car_auction_dataframe(self) -> pd.DataFrame:
        self.main_df['year'] = self.get_transformed_year_series()
        self.main_df['make'] = self.get_transformed_make_series()
        self.main_df['model'] = self.get_transformed_model_series()  # run this after extracting both year and make
        self.main_df['no reserve'] = self.get_transformed_no_reserve_series()
        self.main_df['mileage'] = self.get_transformed_mileage_series()

        return self.main_df

    def get_transformed_year_series(self) -> pd.Series:
        # get years from the description_url column first
        years = pd.to_numeric(self._description_urls_components.str[0], errors='coerce', downcast='integer')
        invalid_yrs_bool_idx = np.logical_or.reduce([years.isnull(), years < 1900, years > 2039])

        # try to get the remaining missing years from the description_name column
        year_regex = r'(?:^|\D)(?P<Year>19[0-9]{1}[0-9]{1}|20[0-3]{1}[0-9]{1})(?:$|\D)'
        matched_yrs = self.main_df.loc[invalid_yrs_bool_idx, 'description_name'].str.extract(year_regex, expand=False)

        years[invalid_yrs_bool_idx] = matched_yrs
        years_int = years.fillna(0).astype('int')
        years_int.loc[years_int == 0] = ''

        return years_int

    def get_transformed_make_series(self) -> pd.Series:
        # get makes from the description_url column first
        makes = self._description_urls_components.apply(lambda row: self._filter_by_known_makes(row))
        missing_makes_bool_idx = makes.isnull()

        # try to get the remaining missing makes from the description_name column
        matched_makes = self.main_df.loc[missing_makes_bool_idx].apply(
            lambda row: self._filter_by_known_makes(row['description_name'].split(' ')), axis=1)

        makes[missing_makes_bool_idx] = matched_makes
        return makes

    def get_transformed_model_series(self, ) -> pd.Series:
        self.main_df['description_name'] = self.main_df['description_name'].str.replace('-', ' ')
        models = self.main_df.apply(lambda row: self._filter_by_known_models(row), axis=1)

        return models

    def get_transformed_no_reserve_series(self) -> pd.Series:
        no_reserve_regex = r'(no reserve|reseve):'
        no_reserve = self.main_df['description_name'].str.extract(no_reserve_regex, expand=False, flags=re.IGNORECASE)
        no_reserve.replace(['no reserve', 'no reseve', np.NaN], ['yes', 'yes', 'no'], inplace=True)

        return no_reserve

    def get_transformed_mileage_series(self) -> pd.Series:
        og_mileage = self.main_df['description_name'].str.extract(r'([0-9k,]+)-mile', expand=False, flags=re.IGNORECASE)
        cleaned_mileage = og_mileage.str.replace(',', '').str.replace('k', '000')

        return cleaned_mileage

    def _extract_description_url_components(self) -> pd.Series:
        url = self.main_df['description_url'].str.extract('https://bringatrailer.com/listing/(.+)/$', expand=False)
        url_components = url.str.split('-', expand=False)

        return url_components

    def _filter_by_known_makes(self, row: Optional[List]) -> Optional[str]:
        if isinstance(row, list):
            row_val_without_nums = [row_part for row_part in row if not row_part.isnumeric()]
            row_substrings = utils.create_substrings_from_list_of_strings(row_val_without_nums)

            for substring in row_substrings:
                if substring in self.models_by_make:
                    return self.models_by_make[substring]['og_make_name']

        return pd.NA

    def _filter_by_known_models(self, row: pd.Series) -> Optional[str]:
        description_name = row['description_name']
        description_name_list = description_name.split()
        desciption_name_substrings = utils.create_substrings_from_list_of_strings(description_name_list)

        make = row['make']
        make_models = self.models_by_make.get(make)
        if make_models:
            for potential_model_substring in desciption_name_substrings:
                if potential_model_substring in make_models:
                    return make_models[potential_model_substring]

        return pd.NA
