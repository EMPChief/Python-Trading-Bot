import numpy as np
import pandas as pd


def BollingerBands(df: pd.DataFrame, n=20, s=2):
    typical_p = (df.mid_c + df.mid_h + df.mid_l) / 3
    rolling_window = typical_p.rolling(window=n)
    df['BB_MA'] = rolling_window.mean()
    stddev = rolling_window.std()
    df['BB_UP'] = df['BB_MA'] + stddev * s
    df['BB_LW'] = df['BB_MA'] - stddev * s
    return df


def KeltnerChannels(df: pd.DataFrame, n_ema=20, n_atr=10):
    df['EMA'] = df.mid_c.ewm(span=n_ema, min_periods=n_ema).mean()
    df = ATR(df, n=n_atr)
    c_atr = f"ATR_{n_atr}"
    df['KeUp'] = df[c_atr] * 2 + df.EMA
    df['KeLo'] = df.EMA - df[c_atr] * 2
    df.drop(columns=c_atr, inplace=True)
    return df


def ATR(df: pd.DataFrame, n=14):
    prev_c = df.mid_c.shift(1)
    tr1 = df.mid_h - df.mid_l
    tr2 = abs(df.mid_h - prev_c)
    tr3 = abs(prev_c - df.mid_l)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df[f"ATR_{n}"] = tr.rolling(window=n).mean()
    return df


def RSI(df: pd.DataFrame, n=14):
    delta = df.mid_c.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.rolling(window=n).mean()
    avg_loss = losses.rolling(window=n).mean()
    rs = avg_gain / avg_loss
    df[f"RSI_{n}"] = 100 - (100 / (1 + rs))
    return df


def MACD(df: pd.DataFrame, n_slow=26, n_fast=12, n_signal=9):
    ema_long = df.mid_c.ewm(span=n_slow, min_periods=n_slow).mean()
    ema_short = df.mid_c.ewm(span=n_fast, min_periods=n_fast).mean()
    df['MACD'] = ema_short - ema_long
    df['SIGNAL'] = df.MACD.ewm(span=n_signal, min_periods=n_signal).mean()
    df['HIST'] = df.MACD - df.SIGNAL
    return df


def VWAP(df: pd.DataFrame) -> pd.DataFrame:
    tp = (df.mid_h + df.mid_l + df.mid_c) / 3
    vwap = (tp * df.volume).cumsum() / df.volume.cumsum()
    df['VWAP'] = vwap
    return df


def ADX(df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    tr1 = df.mid_h - df.mid_l
    tr2 = np.abs(df.mid_h - df.mid_c.shift(1))
    tr3 = np.abs(df.mid_l - df.mid_c.shift(1))
    tr = np.maximum.reduce([tr1, tr2, tr3])
    tr_pos = np.where(df.mid_h > df.mid_h.shift(1), tr, 0)
    tr_neg = np.where(df.mid_l < df.mid_l.shift(1), tr, 0)
    atr = tr.rolling(window=n).mean()
    tr_pos_smoothed = tr_pos.rolling(window=n).mean()
    tr_neg_smoothed = tr_neg.rolling(window=n).mean()
    pos_di = (tr_pos_smoothed / atr) * 100
    neg_di = (tr_neg_smoothed / atr) * 100
    dx = np.abs((pos_di - neg_di) / (pos_di + neg_di)) * 100
    df['ADX'] = dx.rolling(window=n).mean()
    return df
