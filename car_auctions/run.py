from car_auctions import utils
from car_auctions.etl_process.extractor import CarAuctionsExtractor
from car_auctions.etl_process.loader import DataLoader
from car_auctions.etl_process.transformer import CarAuctionsTransformer


@utils.timer
def run_car_auctions_etl(main_car_auctions_fp: str, comprehensive_makes_fp: str, makes_and_models_fp: str,
                         output_fp: str) -> None:
    data_extractor = CarAuctionsExtractor(main_car_auctions_fp, comprehensive_makes_fp, makes_and_models_fp)
    models_by_makes_reference = data_extractor.get_models_by_makes()
    extracted_car_auctions_df = data_extractor.get_main_car_auctions_df()

    data_transformer = CarAuctionsTransformer(extracted_car_auctions_df, models_by_makes_reference)
    transformed_car_auctions_data = data_transformer.transform_car_auction_dataframe()

    DataLoader.load_transformed_dataframe_to_csv(output_fp, transformed_car_auctions_data)
