import pandas as pd
import datetime as dt
from dateutil import parser

from infrastructure.instrument_collection import InstrumentCollection
from api.oanda_api import OandaApi

CANDLE_COUNT = 3000

INCREMENTS = {
    'M5': 5 * CANDLE_COUNT,
    'M15': 15 * CANDLE_COUNT,
    'H1': 60 * CANDLE_COUNT,
    'H4': 240 * CANDLE_COUNT,
    'D1': 1440 * CANDLE_COUNT,
}


def save_file(final_df: pd.DataFrame, file_prefix, granularity, pair):
    """
    Saves a pandas DataFrame containing candle data to a CSV file with a specified filename.

    Parameters:
        - final_df (pd.DataFrame): The DataFrame containing candle data.
        - file_prefix (str): The prefix for the CSV file name.
        - granularity (str): The granularity of the candle data.
        - pair (str): The currency pair for which the data is collected.
    """
    filename = f"{file_prefix}{pair}_{granularity}.csv"

    final_df.drop_duplicates(subset=['time'], inplace=True)
    final_df.sort_values(by='time', inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    final_df.to_csv(filename)

    s1 = f"*** {pair} {granularity} {final_df.time.min()
                                     } {final_df.time.max()}"
    print(f"*** {s1} --> {final_df.shape[0]} candles ***")


def fetch_candles(pair, granularity, date_f: dt.datetime, date_t: dt.datetime, api: OandaApi):
    """
    Fetches candle data for a given currency pair and granularity within a specified date range.

    Parameters:
        - pair (str): The currency pair for which to fetch data.
        - granularity (str): The granularity of the candle data.
        - date_f (dt.datetime): The start date for the data retrieval.
        - date_t (dt.datetime): The end date for the data retrieval.
        - api (OandaApi): An instance of the OandaApi class.

    Returns:
        - pd.DataFrame or None: The fetched candle data if successful, otherwise None.
    """

    attempts = 0

    while attempts < 3:

        candles_df = api.get_candles_df(
            pair,
            granularity=granularity,
            date_f=date_f,
            date_t=date_t
        )

        if candles_df is not None:
            break

        attempts += 1

    if candles_df is not None and candles_df.empty == False:
        return candles_df
    else:
        return None


def collect_data(pair, granularity, date_f, date_t, file_prefix, api: OandaApi):
    """
    Collects candle data iteratively for a specified currency pair and granularity, saving it to CSV files.

    Parameters:
        - pair (str): The currency pair for which to collect data.
        - granularity (str): The granularity of the candle data.
        - date_f (str): The start date for the data collection in string format.
        - date_t (str): The end date for the data collection in string format.
        - file_prefix (str): The prefix for the CSV file names.
        - api (OandaApi): An instance of the OandaApi class.
    """

    time_step = INCREMENTS[granularity]

    end_date = parser.parse(date_t)
    from_date = parser.parse(date_f)

    candle_dfs = []

    to_date = from_date

    while to_date < end_date:
        to_date = from_date + dt.timedelta(minutes=time_step)
        if to_date > end_date:
            to_date = end_date

        candles = fetch_candles(
            pair,
            granularity,
            from_date,
            to_date,
            api
        )

        if candles is not None:
            candle_dfs.append(candles)
            print(f"{pair} {granularity} {from_date} {
                  to_date} --> {candles.shape[0]} candles loaded")
        else:
            print(f"{pair} {granularity} {from_date} {to_date} --> NO CANDLES")

        from_date = to_date

    if len(candle_dfs) > 0:
        final_df = pd.concat(candle_dfs)
        save_file(final_df, file_prefix, granularity, pair)
    else:
        print(f"{pair} {granularity} --> NO DATA SAVED!")


def run_collection(ic: InstrumentCollection, api: OandaApi):
    """
    Runs the data collection for specified currency pairs and granularities.

    Parameters:
        - ic (InstrumentCollection): An instance of the InstrumentCollection class.
        - api (OandaApi): An instance of the OandaApi class.
    """
    our_curr = ["AUD", "CAD", "JPY", "USD", "EUR", "GBP", "NZD"]
    for p1 in our_curr:
        for p2 in our_curr:
            pair = f"{p1}_{p2}"
            if pair in ic.instruments_dict.keys():
                for granularity in ["M5","M15", "M30", "H1","H2", "H4"]:
                    print(pair, granularity)
                    collect_data(
                        pair,
                        granularity,
                        "2017-01-07T00:00:00Z",
                        "2023-11-30T00:00:00Z",
                        "./data/candles/",
                        api
                    )
