from collections import defaultdict
from typing import Dict

import numpy as np
import pandas as pd

from car_auctions import utils


class DataExtractor:

    def __init__(self, comprehensive_makes_file_path: str, makes_and_models_file_path: str) -> None:
        self._comprehensive_makes_df = self.extract_alphanum_df_from_csv(comprehensive_makes_file_path)
        self._makes_and_models_df = self.extract_alphanum_df_from_csv(makes_and_models_file_path)
        self._models_by_makes = defaultdict(dict)

    @property
    def models_by_makes(self) -> Dict[str, Dict]:
        if self._models_by_makes:
            return self._models_by_makes

        makes_and_models = pd.concat([self._comprehensive_makes_df, self._makes_and_models_df])
        makes_and_models.reset_index(drop=True, inplace=True)
        makes_and_models_dict = makes_and_models.to_dict('index')

        for _, row in makes_and_models_dict.items():
            make = row['make']
            model = row['model']
            if model is not np.NaN:
                cleansed_model = model.replace(' ', '')
                self._models_by_makes[make][cleansed_model] = model
            else:
                self._models_by_makes[make] = {}

        return self._models_by_makes

    @staticmethod
    def extract_alphanum_df_from_csv(csv_file_path: str) -> pd.DataFrame:
        df = utils.read_csv_to_lower_cased_df(csv_file_path)
        for col in df.columns:
            df[col] = df[col].str.replace(r'[\W] *', '')

        return df
