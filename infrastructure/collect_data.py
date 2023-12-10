from typing import List
import pandas as pd
import datetime as dt
from dateutil import parser
import os
import logging
from infrastructure.instrument_collection import InstrumentCollection
from api.oanda_api import OandaApi

logging.basicConfig(level=logging.INFO)

CANDLE_COUNT = 3000

INCREMENTS = {
    'M1': 1 * CANDLE_COUNT,
    'M5': 5 * CANDLE_COUNT,
    'M15': 15 * CANDLE_COUNT,
    'M30': 30 * CANDLE_COUNT,
    'H1': 60 * CANDLE_COUNT,
    'H2': 120 * CANDLE_COUNT,
    'H4': 240 * CANDLE_COUNT,
    'H8': 480 * CANDLE_COUNT,
    'D1': 1440 * CANDLE_COUNT,
    'W1': 10080 * CANDLE_COUNT,
    'MN1': 43200 * CANDLE_COUNT,
    'Q1': 129600 * CANDLE_COUNT,
    'Y1': 525600 * CANDLE_COUNT,
}

CURRENCIES = ["AUD", "CAD", "JPY", "USD", "EUR", "GBP",
              "NZD", "SEK", "CHF", "CNY", "HKD", "IDR", "INR"]
GRANULARITIES = ["M5", "M15", "M30", "H1", "H2", "H4"]


def generate_currency_pairs(currencies: List[str]) -> List[str]:
    return [f"{p1}_{p2}" for p1 in currencies for p2 in currencies if p1 != p2]


def save_file(final_df: pd.DataFrame, file_prefix, granularity, pair):
    filename = f"{file_prefix}{pair}_{granularity}.csv"
    final_df.drop_duplicates(subset=['time'], inplace=True)
    final_df.sort_values(by='time', inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    final_df.to_csv(filename)
    logging.info(
        f"*** {pair} {granularity} {final_df.time.min()} {final_df.time.max()} --> {final_df.shape[0]} candles ***")


def fetch_candles(pair, granularity, date_f: dt.datetime, date_t: dt.datetime, api: OandaApi):
    attempts = 0
    while attempts < 3:
        try:
            candles_df = api.get_candles_df(
                pair,
                granularity=granularity,
                date_f=date_f,
                date_t=date_t
            )
            if candles_df is not None:
                break
        except Exception as e:
            logging.error(f"Error fetching candles: {e}")
            attempts += 1

    if candles_df is not None and not candles_df.empty:
        return candles_df
    else:
        return None


def collect_data(pair, granularity, date_f, date_t, file_prefix, api: OandaApi):
    time_step = INCREMENTS[granularity]
    end_date = parser.parse(date_t)
    from_date = parser.parse(date_f)
    candle_dfs = []
    to_date = from_date

    while to_date < end_date:
        to_date = from_date + dt.timedelta(minutes=time_step)
        if to_date > end_date:
            to_date = end_date
        filename = f"{file_prefix}{pair}_{granularity}.csv"

        if os.path.exists(filename):
            existing_data = pd.read_csv(filename)

            if (existing_data['time'] >= from_date.isoformat()).any() and (existing_data['time'] <= to_date.isoformat()).any():
                logging.info(
                    f"{pair} {granularity} {from_date} to {to_date} --> Data already exists. Skipping...")
                return

        candles = fetch_candles(
            pair,
            granularity,
            from_date,
            to_date,
            api
        )

        if candles is not None:
            candle_dfs.append(candles)
            logging.info(
                f"{pair} {granularity} {from_date} to {to_date} --> {candles.shape[0]} candles loaded")
        else:
            logging.info(
                f"{pair} {granularity} {from_date} to {to_date} --> NO CANDLES")

        from_date = to_date

    if len(candle_dfs) > 0:
        final_df = pd.concat(candle_dfs)
        save_file(final_df, file_prefix, granularity, pair)
    else:
        logging.info(f"{pair} {granularity} --> NO DATA SAVED!")


def run_collection(ic: InstrumentCollection, api: OandaApi):
    for pair in generate_currency_pairs(CURRENCIES):
        if pair in ic.instruments_dict.keys():
            for granularity in GRANULARITIES:
                logging.info(f"Collecting data for {pair} {granularity}")
                collect_data(
                    pair,
                    granularity,
                    dt.datetime(2013, 1, 7).isoformat() + "Z",
                    dt.datetime(2023, 11, 30).isoformat() + "Z",
                    "./data/candles/",
                    api
                )
