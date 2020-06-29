from collections import defaultdict
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd

from car_auctions import utils


@dataclass
class CarAuctionsExtractor:
    car_auctions_csv_fp: str
    comprehensive_makes_csv_fp: str
    makes_and_models_csv_fp: str

    def __post_init__(self):
        self._comprehensive_makes_df = self._extract_alphanum_df_from_csv(self.comprehensive_makes_csv_fp)
        self._makes_and_models_df = self._extract_alphanum_df_from_csv(self.makes_and_models_csv_fp)

    def get_main_car_auctions_df(self) -> pd.DataFrame:
        return utils.read_csv_to_lower_cased_df(self.car_auctions_csv_fp)

    def get_models_by_makes(self) -> Dict[str, Dict]:
        models_by_makes = defaultdict(dict)

        makes_and_models = pd.concat([self._comprehensive_makes_df, self._makes_and_models_df])
        makes_and_models.reset_index(drop=True, inplace=True)
        makes_and_models_dict = makes_and_models.to_dict('index')

        for _, row in makes_and_models_dict.items():
            original_make = row['original_make']
            original_model = row['original_model']
            cleaned_make = row['make']
            cleaned_model = row['model']

            if cleaned_make not in models_by_makes:
                models_by_makes[cleaned_make]['og_make_name'] = original_make

            if cleaned_model is not np.NaN:
                cleaned_model = cleaned_model.replace(' ', '')
                models_by_makes[cleaned_make][cleaned_model] = original_model

        return models_by_makes

    @staticmethod
    def _extract_alphanum_df_from_csv(csv_file_path: str) -> pd.DataFrame:
        df = utils.read_csv_to_lower_cased_df(csv_file_path)
        non_alphanum_and_blank_space_regex = r'[\W] *'
        for col in df.columns:
            df[f'original_{col}'] = df[col]
            df[col] = df[col].str.replace(non_alphanum_and_blank_space_regex, '')

        return df
