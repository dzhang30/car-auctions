import os
import datetime

import pandas as pd


class DataLoader:

    @staticmethod
    def load_transformed_dataframe_to_csv(output_csv_fp: str, transformed_df: pd.DataFrame):
        output_csv_dir_path = os.path.dirname(output_csv_fp)
        os.makedirs(output_csv_dir_path, exist_ok=True)

        current_utc_time = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H:%M")
        output_csv_fp_parts = output_csv_fp.split('/')
        output_csv_filename = output_csv_fp_parts.pop()
        output_csv_filename_time_aware = output_csv_filename.replace('.', f'_{current_utc_time}.')

        output_csv_fp_parts.append(output_csv_filename_time_aware)
        final_output_csv_fp = '/'.join(output_csv_fp_parts)

        transformed_df.to_csv(final_output_csv_fp)
