import pandas as pd
import numpy as np
from technicals.indicators import BollingerBands, IchimokuCloud, CMF
from models.trade_decision import TradeDecision
from api.oanda_api import OandaApi
from models.trade_settings import TradeSettings
import constants.defs as defs

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

ADDROWS = 20


def apply_signal(row, trade_settings: TradeSettings):
    if row.SPREAD <= trade_settings.maxspread and row.GAIN >= trade_settings.mingain:
        if row.mid_c > row.BB_UP and row.mid_o < row.BB_UP:
            return defs.SELL
        elif row.mid_c < row.BB_LW and row.mid_o > row.BB_LW:
            return defs.BUY
    return defs.NONE


def apply_SL(row, trade_settings: TradeSettings):
    if row.SIGNAL == defs.BUY:
        return row.mid_c - (row.GAIN / trade_settings.riskreward)
    elif row.SIGNAL == defs.SELL:
        return row.mid_c + (row.GAIN / trade_settings.riskreward)
    return 0.0


def apply_TP(row):
    if row.SIGNAL == defs.BUY:
        return row.mid_c + row.GAIN
    elif row.SIGNAL == defs.SELL:
        return row.mid_c - row.GAIN
    return 0.0


def fetch_candles(pair, row_count, candle_time, granularity, api: OandaApi, log_message, attempts=3):
    for _ in range(attempts):
        df = api.get_candles_df(pair, count=row_count, granularity=granularity)

        if df is not None and df.shape[0] != 0 and df.iloc[-1].time == candle_time:
            return df

        log_message(
            "tech_manager fetch_candles failed to get candles or time not correct, retrying...", pair)

    log_message(
        "tech_manager fetch_candles failed after multiple attempts", pair)
    return None


def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message):
    df.reset_index(drop=True, inplace=True)
    df['PAIR'] = pair
    df['SPREAD'] = df.ask_c - df.bid_c

    df = IchimokuCloud(df, **trade_settings.ichimoku_cloud_settings)
    df = BollingerBands(df, **trade_settings.bollinger_bands_settings)
    df = CMF(df, trade_settings.cmf_settings)

    df['GAIN'] = 0.5 * (
        abs(df.mid_c - df.BB_MA) + abs(df.mid_c -
                                       df.Senkou_Span_A) + abs(df.mid_c - df.CMF)
    )

    df['SIGNAL'] = df.apply(apply_signal, axis=1,
                            trade_settings=trade_settings)
    df['TP'] = df.apply(apply_TP, axis=1)
    df['SL'] = df.apply(apply_SL, axis=1, trade_settings=trade_settings)
    df['LOSS'] = abs(df.mid_c - df.SL)

    log_cols = ['PAIR', 'time', 'mid_c', 'mid_o',
                'SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']
    log_message(f"process_candles:\n{df[log_cols].tail()}", pair)

    return df[log_cols].iloc[-1]


def get_trade_decision(candle_time, pair, granularity, api: OandaApi,
                       trade_settings: TradeSettings, log_message):

    bollinger_settings = trade_settings.bollinger_bands_settings
    ichimoku_settings = trade_settings.ichimoku_cloud_settings
    cmf_settings = trade_settings.cmf_settings

    max_rows = max(
        bollinger_settings.get('n_ma', 0),
        ichimoku_settings.get('n1', 0) + ichimoku_settings.get('n3', 0),
        cmf_settings.get('n_cmf', 0),
    ) + ADDROWS

    log_message(
        f"tech_manager: max_rows:{max_rows} candle_time:{candle_time} granularity:{granularity}", pair)

    df = fetch_candles(pair, max_rows, candle_time,
                       granularity, api, log_message)

    if df is not None:
        last_row = process_candles(df, pair, trade_settings, log_message)
        return TradeDecision(last_row)

    return None
