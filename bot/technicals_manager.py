import pandas as pd
import numpy as np
from technicals.indicators import BollingerBands, IchimokuCloud, CMF, ATR
from models.trade_decision import TradeDecision
from api.oanda_api import OandaApi
from models.trade_settings import TradeSettings
import constants.defs as defs

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

ADDROWS = 20


def apply_signal(row, trade_settings: TradeSettings):
    bb_settings = trade_settings.bollinger_bands_settings
    ichimoku_settings = trade_settings.ichimoku_cloud_settings

    if row['SPREAD'] <= bb_settings['maxspread'] and row['GAIN'] >= bb_settings['mingain']:
        if row['mid_c'] > row['BB_UP'] and row['mid_o'] < row['BB_UP']:
            bb_signal = defs.SELL
        elif row['mid_c'] < row['BB_LW'] and row['mid_o'] > row['BB_LW']:
            bb_signal = defs.BUY
        else:
            bb_signal = defs.NONE
    else:
        bb_signal = defs.NONE
    if row['mid_c'] > row['Senkou_Span_A'] and row['mid_c'] > row['Senkou_Span_B']:
        ichimoku_signal = defs.BUY
    elif row['mid_c'] < row['Senkou_Span_A'] and row['mid_c'] < row['Senkou_Span_B']:
        ichimoku_signal = defs.SELL
    else:
        ichimoku_signal = defs.NONE

    # Combining Signals
    if bb_signal == defs.BUY and ichimoku_signal == defs.BUY:
        return defs.BUY
    elif bb_signal == defs.SELL and ichimoku_signal == defs.SELL:
        return defs.SELL
    else:
        return defs.NONE


def apply_SL(row, trade_settings: TradeSettings):
    atr = row['ATR']
    if row.SIGNAL == defs.BUY:
        return row.mid_c - atr * trade_settings.bollinger_bands_settings['riskreward']
    elif row.SIGNAL == defs.SELL:
        return row.mid_c + atr * trade_settings.bollinger_bands_settings['riskreward']
    return defs.NONE


def apply_TP(row, trade_settings: TradeSettings):
    atr = row['ATR']
    if row.SIGNAL == defs.BUY:
        return row.mid_c + atr * trade_settings.bollinger_bands_settings['riskreward']
    elif row.SIGNAL == defs.SELL:
        return row.mid_c - atr * trade_settings.bollinger_bands_settings['riskreward']
    return defs.NONE


def fetch_candles(pair, row_count, candle_time, granularity, api: OandaApi, log_message, attempts=3):
    for _ in range(attempts):
        row_count = int(row_count)

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

    # Extract the required parameters for each indicator
    bollinger_params = {
        "n": int(trade_settings.bollinger_bands_settings['n_ma']),
        "n_std": float(trade_settings.bollinger_bands_settings['n_std'])
    }

    ichimoku_params = {
        "n1": int(trade_settings.ichimoku_cloud_settings['n1']),
        "n2": int(trade_settings.ichimoku_cloud_settings['n2']),
        "n3": int(trade_settings.ichimoku_cloud_settings['n3'])
    }

    cmf_params = {
        "n_cmf": int(trade_settings.cmf_settings['n_cmf'])
    }

    atr_params = {
        "n_atr": int(trade_settings.atr_settings['n_atr'])
    }

    df = ATR(df, **atr_params)
    df = IchimokuCloud(df, **ichimoku_params)
    df = BollingerBands(df, **bollinger_params)
    df = CMF(df, **cmf_params)

    df['GAIN'] = 0.5 * (
        abs(df.mid_c - df.BB_MA) + abs(df.mid_c -
                                       df.Senkou_Span_A) + abs(df.mid_c - df.CMF)
    )

    df['SIGNAL'] = df.apply(apply_signal, axis=1,
                            trade_settings=trade_settings)
    df['TP'] = df.apply(apply_TP, axis=1, trade_settings=trade_settings)
    df['SL'] = df.apply(apply_SL, axis=1, trade_settings=trade_settings)
    df['LOSS'] = abs(df.mid_c - df.SL)

    log_cols = ['PAIR', 'time', 'mid_c', 'mid_o',
                'SL', 'TP', 'SPREAD', 'GAIN', 'LOSS', 'SIGNAL']
    log_message(f"process_candles:\n{df[log_cols].tail()}", pair)

    return df[log_cols].iloc[-1]


def get_trade_decision(candle_time, pair, granularity, api: OandaApi, trade_settings: TradeSettings, log_message):
    max_rows = (
        trade_settings.bollinger_bands_settings['n_ma']
        + trade_settings.ichimoku_cloud_settings['n1']
        + trade_settings.ichimoku_cloud_settings['n3']
        + trade_settings.cmf_settings['n_cmf']
        + ADDROWS
    )

    log_message(
        f"tech_manager: max_rows:{max_rows} candle_time:{candle_time} granularity:{granularity}", pair)

    df = fetch_candles(pair, max_rows, candle_time,
                       granularity, api, log_message)

    if df is not None:
        last_row = process_candles(df, pair, trade_settings, log_message)
        return TradeDecision(last_row)

    return None
