# Car-Auctions

Download python 3.8.3 via `pyenv` and create a virtual environment for this project called `car_auctions`
```
pyenv install 3.8.3

pyenv virtualenv 3.8.3 car_auctions

cd path/to/car_auctions/repo

pyenv local car_auctions
```

Setup the project requirements
```
pip install requirements.txt
``` 

Update the `car_auctions.cfg` file to specify the absolute paths of the csv files you want to perform the ETL on. 
The `data_files` and `out_files` directories in this repo are the default I/O directories for this project  
```
# Default settings:
[extractor_settings]
main_car_auctions_csv_fp = bring_a_trailer.csv
comprehensive_makes_csv_fp = comprehensive_makes.csv
makes_and_models_csv_fp = makes_and_models.csv

[loader_settings]
output_transformed_csv_fp = transformed_car_auctions.csv
```

Run the project and check the `out_files` directory (if you did not specify an absolute file path) for your results
```
python main.py
```