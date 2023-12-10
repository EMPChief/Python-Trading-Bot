import pandas as pd
import numpy as np
import pandas as pd


def BollingerBands(df: pd.DataFrame, n=20, s=2):
    # Calculate Bollinger Bands
    typical_p = (df.mid_c + df.mid_h + df.mid_l) / 3
    rolling_window = typical_p.rolling(window=n)

    # Calculate Moving Average (BB_MA)
    df['BB_MA'] = rolling_window.mean()

    # Calculate Standard Deviation
    stddev = rolling_window.std()

    # Calculate Upper and Lower Bands (BB_UP and BB_LW)
    df['BB_UP'] = df['BB_MA'] + stddev * s
    df['BB_LW'] = df['BB_MA'] - stddev * s
    return df


def KeltnerChannels(df: pd.DataFrame, n_ema=20, n_atr=10):
    # Calculate Exponential Moving Average (EMA)
    df['EMA'] = df.mid_c.ewm(span=n_ema, min_periods=n_ema).mean()

    # Calculate Average True Range (ATR)
    df = ATR(df, n=n_atr)
    c_atr = f"ATR_{n_atr}"

    # Calculate Keltner Channels (KeUp and KeLo)
    df['KeUp'] = df[c_atr] * 2 + df.EMA
    df['KeLo'] = df.EMA - df[c_atr] * 2
    df.drop(columns=c_atr, inplace=True)
    return df


def ATR(df: pd.DataFrame, n=14):
    # Calculate Average True Range (ATR)
    prev_c = df.mid_c.shift(1)
    tr1 = df.mid_h - df.mid_l
    tr2 = abs(df.mid_h - prev_c)
    tr3 = abs(prev_c - df.mid_l)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df[f"ATR_{n}"] = tr.rolling(window=n).mean()
    return df


def RSI(df: pd.DataFrame, n=14):
    # Calculate Relative Strength Index (RSI)
    delta = df.mid_c.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.rolling(window=n).mean()
    avg_loss = losses.rolling(window=n).mean()
    rs = avg_gain / avg_loss
    df[f"RSI_{n}"] = 100 - (100 / (1 + rs))
    return df


def MACD(df: pd.DataFrame, n_slow=26, n_fast=12, n_signal=9):
    # Calculate Moving Average Convergence Divergence (MACD)
    ema_long = df.mid_c.ewm(span=n_slow, min_periods=n_slow).mean()
    ema_short = df.mid_c.ewm(span=n_fast, min_periods=n_fast).mean()
    df['MACD'] = ema_short - ema_long

    # Calculate Signal Line (SIGNAL)
    df['SIGNAL'] = df.MACD.ewm(span=n_signal, min_periods=n_signal).mean()

    # Calculate MACD Histogram (HIST)
    df['HIST'] = df.MACD - df.SIGNAL
    return df


def VWAP(df: pd.DataFrame):
    # Calculate Volume Weighted Average Price (VWAP)
    tp = (df.mid_h + df.mid_l + df.mid_c) / 3
    vwap = (tp * df.volume).cumsum() / df.volume.cumsum()
    df['VWAP'] = vwap
    return df


def VWAP(df: pd.DataFrame):
    # Calculate the Volume Weighted Average Price (VWAP)
    tp = (df.mid_h + df.mid_l + df.mid_c) / 3
    vwap = (tp * df.volume).cumsum() / df.volume.cumsum()
    df['VWAP'] = vwap
    return df


def ADX(df: pd.DataFrame, n=14) -> pd.DataFrame:
    # Calculate the Average Directional Index (ADX)
    # Calculate True Range (TR)
    tr1 = df.mid_h - df.mid_l
    tr2 = np.abs(df.mid_h - df.mid_c.shift(1))
    tr3 = np.abs(df.mid_l - df.mid_c.shift(1))
    tr = np.maximum.reduce([tr1, tr2, tr3])

    # Calculate Positive Directional Movement (+DM) and Negative Directional Movement (-DM)
    tr_pos = np.where(df.mid_h > df.mid_h.shift(1), tr, 0)
    tr_neg = np.where(df.mid_l < df.mid_l.shift(1), tr, 0)

    # Calculate Average True Range (ATR), Smoothed Positive Directional Indicator (+DI),
    # Smoothed Negative Directional Indicator (-DI), and ADX
    atr = tr.rolling(window=n).mean()
    tr_pos_smoothed = tr_pos.rolling(window=n).mean()
    tr_neg_smoothed = tr_neg.rolling(window=n).mean()
    pos_di = (tr_pos_smoothed / atr) * 100
    neg_di = (tr_neg_smoothed / atr) * 100
    dx = np.abs((pos_di - neg_di) / (pos_di + neg_di)) * 100
    df['ADX'] = dx.rolling(window=n).mean()
    return df


def StochasticOscillator(df: pd.DataFrame, n=14):
    # Calculate the Stochastic Oscillator
    low_min = df.mid_l.rolling(window=n).min()
    high_max = df.mid_h.rolling(window=n).max()
    df['%K'] = (df.mid_c - low_min) / (high_max - low_min) * 100
    df['%D'] = df['%K'].rolling(window=3).mean()
    return df


def MovingAverage(df: pd.DataFrame, n=50):
    # Calculate the Moving Average (MA) for a given DataFrame.
    # MA is the average of a set of prices over a specified period of time.
    df[f'MA_{n}'] = df.mid_c.rolling(window=n).mean()
    return df


def ExponentialMovingAverage(df: pd.DataFrame, n=50):
    # Calculate the Exponential Moving Average (EMA) for a given DataFrame.
    # EMA gives more weight to recent prices, making it more responsive to price changes.
    df[f'EMA_{n}'] = df.mid_c.ewm(span=n, adjust=False).mean()
    return df


def CommodityChannelIndex(df: pd.DataFrame, n=20):
    # Calculate the Commodity Channel Index (CCI) for a given DataFrame.
    # CCI is a momentum-based oscillator used to identify cyclical trends in a security.

    # Typical Price (TP) calculation
    TP = (df.mid_h + df.mid_l + df.mid_c) / 3

    # CCI calculation
    df['CCI'] = (TP - TP.rolling(window=n).mean()) / \
        (0.015 * TP.rolling(window=n).std())
    return df


def Momentum(df: pd.DataFrame, n=14):
    # Calculate the Momentum indicator for a given DataFrame.
    # Momentum measures the rate of change of a security's price over a specified period of time.
    df['Momentum'] = df.mid_c - df.mid_c.shift(n)
    return df


def RateOfChange(df: pd.DataFrame, n=14):
    # Calculate the Rate of Change (ROC) for a given DataFrame.
    # ROC is a momentum oscillator that measures the percentage change in price over a specified period of time.
    df['ROC'] = ((df.mid_c - df.mid_c.shift(n)) / df.mid_c.shift(n)) * 100
    return df


def OnBalanceVolume(df: pd.DataFrame):
    # Calculate the On-Balance Volume (OBV) for a given DataFrame.
    # OBV uses volume flow to predict changes in stock price and measures buying and selling pressure.

    # Price change direction
    price_direction = np.sign(df.mid_c.diff())

    # OBV calculation
    df['OBV'] = (price_direction * df.volume).fillna(0).cumsum()
    return df


def ADL(df: pd.DataFrame):
    # Calculate the Accumulation/Distribution Line (ADL) for a given DataFrame.
    # ADL measures the cumulative flow of money into or out of a security.

    # Money Flow calculation
    clv = ((df.mid_c - df.mid_l) - (df.mid_h - df.mid_c)) / \
        (df.mid_h - df.mid_l)
    clv = clv.fillna(0)  # Replace NaNs resulting from zero division with 0

    # ADL calculation
    df['ADL'] = (clv * df.volume).cumsum()
    return df


def Aroon(df: pd.DataFrame, n=14):
    # Calculate the Aroon indicator for a given DataFrame.
    # Aroon identifies the strength and direction of a trend using two lines: Aroon Up and Aroon Down.

    # Aroon Up and Down calculation
    df['Aroon_Up'] = df.mid_h.rolling(n).apply(
        lambda x: float(np.argmax(x) + 1) / n * 100)
    df['Aroon_Down'] = df.mid_l.rolling(n).apply(
        lambda x: float(np.argmin(x) + 1) / n * 100)
    return df


def Aroon_Oscillator(df: pd.DataFrame, n=14):
    # Calculate the Aroon Oscillator for a given DataFrame.
    # Aroon Oscillator measures the difference between Aroon Up and Aroon Down lines.
    df = Aroon(df, n)
    df['Aroon_Oscillator'] = df['Aroon_Up'] - df['Aroon_Down']
    return df


def CMF(df: pd.DataFrame, n=20):
    # Calculate the Chaikin Money Flow (CMF) for a given DataFrame.
    # CMF combines price and volume to determine the strength of a trend.

    # Money Flow Multiplier and Volume calculation
    mf_multiplier = (df.mid_c - df.mid_l - df.mid_h +
                     df.mid_c) / (df.mid_h - df.mid_l)
    mf_volume = mf_multiplier * df.volume

    # CMF calculation
    df['CMF'] = mf_volume.rolling(n).sum() / df.volume.rolling(n).sum()
    return df


def EVM(df: pd.DataFrame, n=14):
    # Calculate the Ease of Movement (EVM) for a given DataFrame.
    # EVM measures the relationship between price change and volume to identify the strength and direction of a trend.

    # Distance Moved and Box Ratio calculation
    dm = ((df.mid_h + df.mid_l) / 2) - \
        ((df.mid_h.shift(1) + df.mid_l.shift(1)) / 2)
    br = (df.volume / 1e6) / ((df.mid_h - df.mid_l))

    # EVM calculation
    df['EVM'] = dm / br.rolling(n).mean()
    return df


def ForceIndex(df: pd.DataFrame, n=2):
    # Calculate the Force Index for a given DataFrame.
    # Force Index measures the strength of a price trend by combining price and volume.

    # Force Index calculation
    df['ForceIndex'] = df.volume * (df.mid_c - df.mid_c.shift(1))
    df['ForceIndex'] = df['ForceIndex'].rolling(n).mean()
    return df


def MassIndex(df: pd.DataFrame, n=9, n2=25):
    # Calculate the Mass Index for a given DataFrame.
    # Mass Index measures the volatility of a security's price movement.

    # High-Low Range and Exponential Moving Averages calculation
    hl_diff = df.mid_h - df.mid_l
    ema1 = hl_diff.ewm(span=n, adjust=False).mean()
    ema2 = ema1.ewm(span=n, adjust=False).mean()

    # Mass Index calculation
    mass = ema1 / ema2
    df['MassIndex'] = mass.rolling(n2).sum()
    return df


def MFI(df: pd.DataFrame, n=14):
    # Calculate the Money Flow Index (MFI) for a given DataFrame.
    # MFI measures the strength and direction of money flow in and out of a security.

    # Typical Price and Money Flow calculation
    typical_price = (df.mid_h + df.mid_l + df.mid_c) / 3
    money_flow = typical_price * df.volume
    positive_money_flow = money_flow.where(
        df.mid_c > df.mid_c.shift(1), 0).rolling(n).sum()
    negative_money_flow = money_flow.where(
        df.mid_c < df.mid_c.shift(1), 0).rolling(n).sum()

    # Money Flow Index
