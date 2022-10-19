
# requires Python >=3.6
# pip install tardis-dev

from tardis_dev import datasets, get_exchange_details
import logging

# optionally enable debug logs
# logging.basicConfig(level=logging.DEBUG)

exchange = 'ftx'
exchange_details = get_exchange_details(exchange)   

# iterate over and download all data for every symbol
for symbol in exchange_details["datasets"]["symbols"]:
    # alternatively specify datatypes explicitly ['trades', 'incremental_book_L2', 'quotes'] etc
    # see available options https://docs.tardis.dev/downloadable-csv-files#data-types
    data_types = symbol["dataTypes"]  
    symbol_id = symbol["id"]
    from_date =  symbol["availableSince"]
    to_date = symbol["availableTo"]

    # skip groupped symbols
    if symbol_id in ['PERPETUALS', 'SPOT', 'FUTURES']:
        continue

    print(f"Downloading {exchange} {data_types} for {symbol_id} from {from_date} to {to_date}")

    # each CSV dataset format is documented at https://docs.tardis.dev/downloadable-csv-files#data-types
    # see https://docs.tardis.dev/downloadable-csv-files#download-via-client-libraries for full options docs
    datasets.download(
        exchange = exchange,
        data_types = data_types,
        from_date =  from_date,
        to_date = to_date,
        symbols = [symbol_id],
        # TODO set your API key here
        api_key = "YOUR_API_KEY",
        # path where CSV data will be downloaded into
        download_dir = "./datasets",
    )