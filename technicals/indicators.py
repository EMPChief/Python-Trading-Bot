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


def StochasticOscillator(df: pd.DataFrame, n: int = 14):
    low_min = df.mid_l.rolling(window=n).min()
    high_max = df.mid_h.rolling(window=n).max()
    df['%K'] = (df.mid_c - low_min) / (high_max - low_min) * 100
    df['%D'] = df['%K'].rolling(window=3).mean()
    return df


def MovingAverage(df: pd.DataFrame, n: int = 50):
    df[f'MA_{n}'] = df.mid_c.rolling(window=n).mean()
    return df


def ExponentialMovingAverage(df: pd.DataFrame, n: int = 50):
    df[f'EMA_{n}'] = df.mid_c.ewm(span=n, adjust=False).mean()
    return df


def CommodityChannelIndex(df: pd.DataFrame, n: int = 20):
    TP = (df.mid_h + df.mid_l + df.mid_c) / 3
    df['CCI'] = (TP - TP.rolling(window=n).mean()) / \
        (0.015 * TP.rolling(window=n).std())
    return df


def Momentum(df: pd.DataFrame, n: int = 14):
    df['Momentum'] = df.mid_c - df.mid_c.shift(n)
    return df


def RateOfChange(df: pd.DataFrame, n: int = 14):
    df['ROC'] = ((df.mid_c - df.mid_c.shift(n)) / df.mid_c.shift(n)) * 100
    return df


def OnBalanceVolume(df: pd.DataFrame):
    df['OBV'] = (np.sign(df.mid_c.diff()) * df.volume).fillna(0).cumsum()
    return df


def ADL(df: pd.DataFrame):
    clv = ((df.mid_c - df.mid_l) - (df.mid_h - df.mid_c)) / \
        (df.mid_h - df.mid_l)
    # NaNs (resulting from zero division) are replaced with 0
    clv = clv.fillna(0)
    df['ADL'] = (clv * df.volume).cumsum()
    return df


def Aroon(df: pd.DataFrame, n=14):
    df['Aroon_Up'] = df.mid_h.rolling(n).apply(
        lambda x: float(np.argmax(x) + 1) / n * 100)
    df['Aroon_Down'] = df.mid_l.rolling(n).apply(
        lambda x: float(np.argmin(x) + 1) / n * 100)
    return df


def Aroon_Oscillator(df: pd.DataFrame, n=14):
    df = Aroon(df, n)
    df['Aroon_Oscillator'] = df['Aroon_Up'] - df['Aroon_Down']
    return df


def CCI(df: pd.DataFrame, n=20):
    # The code for this function is already in your file
    return df


def CMF(df: pd.DataFrame, n=20):
    mf_multiplier = (df.mid_c - df.mid_l - df.mid_h +
                     df.mid_c) / (df.mid_h - df.mid_l)
    mf_volume = mf_multiplier * df.volume
    df['CMF'] = mf_volume.rolling(n).sum() / df.volume.rolling(n).sum()
    return df


def EVM(df: pd.DataFrame, n=14):
    dm = ((df.mid_h + df.mid_l) / 2) - \
        ((df.mid_h.shift(1) + df.mid_l.shift(1)) / 2)
    br = (df.volume / 1e6) / ((df.mid_h - df.mid_l))
    df['EVM'] = dm / br.rolling(n).mean()
    return df


def ForceIndex(df: pd.DataFrame, n=2):
    df['ForceIndex'] = df.volume * (df.mid_c - df.mid_c.shift(1))
    df['ForceIndex'] = df['ForceIndex'].rolling(n).mean()
    return df


def MassIndex(df: pd.DataFrame, n=9, n2=25):
    hl_diff = df.mid_h - df.mid_l
    ema1 = hl_diff.ewm(span=n, adjust=False).mean()
    ema2 = ema1.ewm(span=n, adjust=False).mean()
    mass = ema1 / ema2
    df['MassIndex'] = mass.rolling(n2).sum()
    return df


def MFI(df: pd.DataFrame, n=14):
    typical_price = (df.mid_h + df.mid_l + df.mid_c) / 3
    money_flow = typical_price * df.volume
    positive_money_flow = money_flow.where(
        df.mid_c > df.mid_c.shift(1), 0).rolling(n).sum()
    negative_money_flow = money_flow.where(
        df.mid_c < df.mid_c.shift(1), 0).rolling(n).sum()
    money_flow_ratio = positive_money_flow / negative_money_flow
    df['MFI'] = 100 - (100 / (1 + money_flow_ratio))
    return df
