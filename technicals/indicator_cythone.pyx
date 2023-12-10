# indicator_cythone.pyx
import numpy as np
import pandas as pd
from libc.math cimport fabs
cimport pandas as pd
from cpython cimport array

def BollingerBands(object df, int n=20, int s=2):
    cdef array.array sum_mid = df['mid_c'] + df['mid_h'] + df['mid_l']
    cdef array.array typical_p = (sum_mid).astype('double') / 3
    cdef array.array stddev = typical_p.rolling(window=n).std()
    
    # Explicitly cast to double
    df['BB_MA'] = typical_p.rolling(window=n).mean().astype('double')
    df['BB_UP'] = (df['BB_MA'] + stddev * s).astype('double')
    df['BB_LW'] = (df['BB_MA'] - stddev * s).astype('double')
    
    return df

def ATR(object df, int n=14):
    cdef array.array prev_c = df['mid_c'].shift(1)
    cdef array.array tr1 = df['mid_h'] - df['mid_l']
    cdef array.array tr2 = fabs(df['mid_h'] - prev_c)
    cdef array.array tr3 = fabs(prev_c - df['mid_l'])
    cdef array.array tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    df[f"ATR_{n}"] = tr.rolling(window=n).mean()
    return df

def KeltnerChannels(object df, int n_ema=20, int n_atr=10):
    df['EMA'] = df['mid_c'].ewm(span=n_ema, min_periods=n_ema).mean()
    df = ATR(df, n=n_atr)
    cdef bytes c_atr = f"ATR_{n_atr}".encode('utf-8')
    df['KeUp'] = df[c_atr] * 2 + df['EMA']
    df['KeLo'] = df['EMA'] - df[c_atr] * 2
    df.drop(c_atr, axis=1, inplace=True)
    return df

def RSI(object df, int n=14):
    cdef double alpha = 1.0 / n
    cdef array.array gains = df['mid_c'].diff()
    cdef array.array wins = gains.apply(lambda x: x if x >= 0 else 0.0)
    cdef array.array losses = gains.apply(lambda x: x * -1 if x < 0 else 0.0)

    cdef array.array wins_rma = wins.ewm(min_periods=n, alpha=alpha).mean()
    cdef array.array losses_rma = losses.ewm(min_periods=n, alpha=alpha).mean()

    # Add a small epsilon to avoid division by zero
    cdef array.array rs = wins_rma / (losses_rma + 1e-10)

    df[f"RSI_{n}"] = 100.0 - (100.0 / (1.0 + rs))
    return df

def MACD(object df, int n_slow=26, int n_fast=12, int n_signal=9):
    cdef array.array ema_long = df['mid_c'].ewm(min_periods=n_slow, span=n_slow).mean()
    cdef array.array ema_short = df['mid_c'].ewm(min_periods=n_fast, span=n_fast).mean()

    df['MACD'] = ema_short - ema_long
    df['SIGNAL'] = df['MACD'].ewm(min_periods=n_signal, span=n_signal).mean()
    df['HIST'] = df['MACD'] - df['SIGNAL']

    return df
