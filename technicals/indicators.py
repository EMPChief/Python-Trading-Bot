import pandas as pd
import numpy as np
import pandas as pd


def BollingerBands(df: pd.DataFrame, n=20, s=2):
    """
    Calculate Bollinger Bands.

    Args:
        df (pd.DataFrame): The DataFrame to calculate Bollinger Bands on.
        n (int): The number of days to use for the moving average.
        s (float): The standard deviation multiplier.

    Returns:
        pd.DataFrame: The DataFrame with Bollinger Bands added.
    """

    typical_p = (df.mid_c + df.mid_h + df.mid_l) / 3
    df['BB_MA'] = typical_p.rolling(window=n).mean()
    stddev = typical_p.rolling(window=n).std()
    df['BB_UP'] = df['BB_MA'] + stddev * s
    df['BB_LW'] = df['BB_MA'] - stddev * s
    return df


def KeltnerChannels(df: pd.DataFrame, n_ema=20, n_atr=10):
    """
    Calculate Keltner Channels.

    Args:
        df (pd.DataFrame): The DataFrame to calculate Keltner Channels on.
        n_ema (int): The number of days to use for the EMA.
        n_atr (int): The number of days to use for the ATR.

    Returns:
        pd.DataFrame: The DataFrame with Keltner Channels added.
    """

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
    """
    Calculate Average True Range (ATR).

    Args:
        df (pd.DataFrame): The DataFrame to calculate ATR on.
        n (int): The number of days to use for the ATR.

    Returns:
        pd.DataFrame: The DataFrame with ATR added.
    """

    # Calculate True Range (TR)
    prev_c = df.mid_c.shift(1)
    tr1 = df.mid_h - df.mid_l
    tr2 = abs(df.mid_h - prev_c)
    tr3 = abs(prev_c - df.mid_l)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calculate Average True Range (ATR)
    df[f"ATR_{n}"] = tr.rolling(window=n).mean()
    return df


def RSI(df: pd.DataFrame, n=14):
    """
    Calculate Relative Strength Index (RSI).

    Args:
        df (pd.DataFrame): The DataFrame to calculate RSI on.
        n (int): The number of days to use for the RSI.

    Returns:
        pd.DataFrame: The DataFrame with RSI added.
    """

    # Calculate Delta
    delta = df.mid_c.diff()

    # Calculate Gains and Losses
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    # Calculate Average Gain (avg_gain) and Average Loss (avg_loss)
    avg_gain = gains.rolling(window=n).mean()
    avg_loss = losses.rolling(window=n).mean()

    # Calculate Relative Strength (RS)
    rs = avg_gain / avg_loss

    # Calculate Relative Strength Index (RSI)
    df[f"RSI_{n}"] = 100 - (100 / (1 + rs))
    return df


def MACD(df: pd.DataFrame, n_slow=26, n_fast=12, n_signal=9):
    """
    Calculate Moving Average Convergence Divergence (MACD).

    Args:
        df (pd.DataFrame): The DataFrame to calculate MACD on.
        n_slow (int): The number of days to use for the slow EMA.
        n_fast (int): The number of days to use for the fast EMA.
        n_signal (int): The number of days to use for the signal line.

    Returns:
        pd.DataFrame: The DataFrame with MACD added.
    """

    # Calculate Exponential Moving Average (EMA)
    ema_long = df.mid_c.ewm(span=n_slow, min_periods=n_slow).mean()
    ema_short = df.mid_c.ewm(span=n_fast, min_periods=n_fast).mean()

    # Calculate MACD
    df['MACD'] = ema_short - ema_long

    # Calculate Signal Line (SIGNAL)
    df['SIGNAL'] = df.MACD.ewm(span=n_signal, min_periods=n_signal).mean()

    # Calculate MACD Histogram (HIST)
    df['HIST'] = df.MACD - df.SIGNAL
    return df


def VWAP(df: pd.DataFrame):
    """
    Calculate Volume Weighted Average Price (VWAP).

    Args:
        df (pd.DataFrame): The DataFrame to calculate VWAP on.

    Returns:
        pd.DataFrame: The DataFrame with VWAP added.
    """

    # Calculate Volume Weighted Average Price (VWAP)
    tp = (df.mid_h + df.mid_l + df.mid_c) / 3
    vwap = (tp * df.volume).cumsum() / df.volume.cumsum()
    df['VWAP'] = vwap
    return df


def VWAP(df: pd.DataFrame):
    """
    Calculate the Volume Weighted Average Price (VWAP).

    Args:
        df (pd.DataFrame): The DataFrame to calculate VWAP on.

    Returns:
        pd.DataFrame: The DataFrame with VWAP added.
    """

    # Calculate Volume Weighted Average Price (VWAP)
    tp = (df.mid_h + df.mid_l + df.mid_c) / 3
    vwap = (tp * df.volume).cumsum() / df.volume.cumsum()
    df['VWAP'] = vwap
    return df


def ADX(df: pd.DataFrame, n=14) -> pd.DataFrame:
    """
    Calculate the Average Directional Index (ADX).

    Args:
        df (pd.DataFrame): The DataFrame to calculate ADX on.
        n (int): The number of days to use for the ADX.

    Returns:
        pd.DataFrame: The DataFrame with ADX added.
    """

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
    """
    Calculate the Stochastic Oscillator.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Stochastic Oscillator on.
        n (int): The number of days to use for the Stochastic Oscillator.

    Returns:
        pd.DataFrame: The DataFrame with the Stochastic Oscillator added.
    """

    # Calculate Low Minimum (low_min) and High Maximum (high_max)
    low_min = df.mid_l.rolling(window=n).min()
    high_max = df.mid_h.rolling(window=n).max()

    # Calculate %K and %D
    df['%K'] = (df.mid_c - low_min) / (high_max - low_min) * 100
    df['%D'] = df['%K'].rolling(window=3).mean()
    return df


def MovingAverage(df: pd.DataFrame, n=50):
    """
    Calculate the Moving Average (MA) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Moving Average on.
        n (int): The number of days to use for the Moving Average.

    Returns:
        pd.DataFrame: The DataFrame with the Moving Average added.
    """

    # Calculate the Moving Average (MA)
    df[f'MA_{n}'] = df.mid_c.rolling(window=n).mean()
    return df


def ExponentialMovingAverage(df: pd.DataFrame, n=50):
    """
    Calculate the Exponential Moving Average (EMA) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Exponential Moving Average on.
        n (int): The number of days to use for the Exponential Moving Average.

    Returns:
        pd.DataFrame: The DataFrame with the Exponential Moving Average added.
    """

    # Calculate the Exponential Moving Average (EMA)
    df[f'EMA_{n}'] = df.mid_c.ewm(span=n, adjust=False).mean()
    return df


def CommodityChannelIndex(df: pd.DataFrame, n=20):
    """
    Calculate the Commodity Channel Index (CCI) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Commodity Channel Index on.
        n (int): The number of days to use for the Commodity Channel Index.

    Returns:
        pd.DataFrame: The DataFrame with the Commodity Channel Index added.
    """

    # Calculate the Typical Price (TP)
    TP = (df.mid_h + df.mid_l + df.mid_c) / 3

    # Calculate the Commodity Channel Index (CCI)
    df['CCI'] = (TP - TP.rolling(window=n).mean()) / \
        (0.015 * TP.rolling(window=n).std())
    return df


def Momentum(df: pd.DataFrame, n=14):
    """
    Calculate the Momentum indicator for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Momentum indicator on.
        n (int): The number of days to use for the Momentum indicator.

    Returns:
        pd.DataFrame: The DataFrame with the Momentum indicator added.
    """

    # Calculate the Momentum
    df['Momentum'] = df.mid_c - df.mid_c.shift(n)
    return df


def RateOfChange(df: pd.DataFrame, n=14):
    """
    Calculate the Rate of Change (ROC) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Rate of Change on.
        n (int): The number of days to use for the Rate of Change.

    Returns:
        pd.DataFrame: The DataFrame with the Rate of Change added.
    """

    # Calculate the Rate of Change (ROC)
    df['ROC'] = ((df.mid_c - df.mid_c.shift(n)) / df.mid_c.shift(n)) * 100
    return df


def OnBalanceVolume(df: pd.DataFrame):
    """
    Calculate the On-Balance Volume (OBV) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the On-Balance Volume on.

    Returns:
        pd.DataFrame: The DataFrame with the On-Balance Volume added.
    """

    # Calculate the Price Change Direction
    price_direction = np.sign(df.mid_c.diff())

    # Calculate the On-Balance Volume (OBV)
    df['OBV'] = (price_direction * df.volume).fillna(0).cumsum()
    return df


def ADL(df: pd.DataFrame):
    """
    Calculate the Accumulation/Distribution Line (ADL) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Accumulation/Distribution Line on.

    Returns:
        pd.DataFrame: The DataFrame with the Accumulation/Distribution Line added.
    """

    # Calculate the Money Flow
    clv = ((df.mid_c - df.mid_l) - (df.mid_h - df.mid_c)) / \
        (df.mid_h - df.mid_l)
    clv = clv.fillna(0)  # Replace NaNs resulting from zero division with 0

    # Calculate the Accumulation/Distribution Line (ADL)
    df['ADL'] = (clv * df.volume).cumsum()
    return df


def Aroon(df: pd.DataFrame, n=14):
    """
    Calculate the Aroon indicator for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Aroon indicator on.
        n (int): The number of days to use for the Aroon indicator.

    Returns:
        pd.DataFrame: The DataFrame with the Aroon indicator added.
    """

    # Calculate the Aroon Up and Down
    df['Aroon_Up'] = df.mid_h.rolling(n).apply(
        lambda x: float(np.argmax(x) + 1) / n * 100)
    df['Aroon_Down'] = df.mid_l.rolling(n).apply(
        lambda x: float(np.argmin(x) + 1) / n * 100)
    return df


def Aroon_Oscillator(df: pd.DataFrame, n=14):
    """
    Calculate the Aroon Oscillator for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Aroon Oscillator on.
        n (int): The number of days to use for the Aroon Oscillator.

    Returns:
        pd.DataFrame: The DataFrame with the Aroon Oscillator added.
    """

    # Calculate the Aroon Up and Down
    df = Aroon(df, n)
    df['Aroon_Oscillator'] = df['Aroon_Up'] - df['Aroon_Down']
    return df


def CMF(df: pd.DataFrame, n=20):
    """
    Calculate the Chaikin Money Flow (CMF) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Chaikin Money Flow on.
        n (int): The number of days to use for the Chaikin Money Flow.

    Returns:
        pd.DataFrame: The DataFrame with the Chaikin Money Flow added.
    """

    # Calculate the Money Flow Multiplier and Volume
    mf_multiplier = (df.mid_c - df.mid_l - df.mid_h +
                     df.mid_c) / (df.mid_h - df.mid_l)
    mf_volume = mf_multiplier * df.volume

    # Calculate the Chaikin Money Flow (CMF)
    df['CMF'] = mf_volume.rolling(n).sum() / df.volume.rolling(n).sum()
    return df


def EVM(df: pd.DataFrame, n=14):
    """
    Calculate the Ease of Movement (EVM) for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Ease of Movement on.
        n (int): The number of days to use for the Ease of Movement.

    Returns:
        pd.DataFrame: The DataFrame with the Ease of Movement added.
    """

    # Calculate the Distance Moved and Box Ratio
    dm = ((df.mid_h + df.mid_l) / 2) - \
        ((df.mid_h.shift(1) + df.mid_l.shift(1)) / 2)
    br = (df.volume / 1e6) / ((df.mid_h - df.mid_l))

    # Calculate the Ease of Movement (EVM)
    df['EVM'] = dm / br
    return df

# add ichidoku cloud


def IchimokuCloud(df: pd.DataFrame, n1=9, n2=26, n3=52):
    """
    Calculate the Ichimoku Cloud for a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to calculate the Ichimoku Cloud on.
        n1 (int): The number of days to use for the Tenkan-sen.
        n2 (int): The number of days to use for the Kijun-sen.
        n3 (int): The number of days to use for the Senkou Span A.

    Returns:
        pd.DataFrame: The DataFrame with the Ichimoku Cloud added.
    """

    # Calculate the Tenkan-sen (Conversion Line)
    df['Tenkan_sen'] = (df.mid_h.rolling(n1).max() +
                        df.mid_l.rolling(n1).min()) / 2

    # Calculate the Kijun-sen (Base Line)
    df['Kijun_sen'] = (df.mid_h.rolling(n2).max() +
                       df.mid_l.rolling(n2).min()) / 2

    # Calculate the Senkou Span A (Leading Span A)
    df['Senkou_Span_A'] = ((df['Tenkan_sen'] + df['Kijun_sen']) / 2).shift(n3)

    # Calculate the Senkou Span B (Leading Span B)
    df['Senkou_Span_B'] = (
        (df.mid_h.rolling(n3).max() + df.mid_l.rolling(n3).min()) / 2).shift(n3)

    # Calculate the Chikou Span (Lagging Span)
    df['Chikou_Span'] = df.mid_c.shift(-n2)

    return df
