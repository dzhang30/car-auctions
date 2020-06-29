import os
from configparser import ConfigParser

import pandas as pd

from car_auctions.run import run_car_auctions_etl
from car_auctions import utils

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.max_colwidth', 100)

CONFIG_FILE_NAME = 'car_auctions.cfg'
DATA_FILES_DIR_NAME = 'data_files'
OUT_FILES_FILES_DIR_NAME = 'out_files'


def main(car_auctions_config: ConfigParser) -> None:
    extractor_conf = car_auctions_config['extractor_settings']
    default_data_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILES_DIR_NAME)
    car_auctions_fp = utils.add_default_dir_path(extractor_conf['main_car_auctions_csv_fp'], default_data_files_dir)
    compr_makes_fp = utils.add_default_dir_path(extractor_conf['comprehensive_makes_csv_fp'], default_data_files_dir)
    makes_and_models_fp = utils.add_default_dir_path(extractor_conf['makes_and_models_csv_fp'], default_data_files_dir)

    loader_conf = car_auctions_config['loader_settings']
    default_out_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUT_FILES_FILES_DIR_NAME)
    output_fp = utils.add_default_dir_path(loader_conf['output_transformed_csv_fp'], default_out_files_dir)

    run_car_auctions_etl(car_auctions_fp, compr_makes_fp, makes_and_models_fp, output_fp)


if __name__ == '__main__':
    car_auctions_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE_NAME)
    car_auctions_config = utils.read_config_file(car_auctions_config_path)

    main(car_auctions_config)
