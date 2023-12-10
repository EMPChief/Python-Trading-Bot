import pandas as pd
import numpy as np
import pandas as pd


def BollingerBands(df: pd.DataFrame, n=20, s=2):
    """
    Calculate Bollinger Bands for a given DataFrame.

    Bollinger Bands are a technical analysis tool that consists of a moving average (MA) and two standard deviation bands
    plotted above and below it. The MA represents the average price over a specified period, while the bands represent
    the volatility of the price.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c', 'mid_h', and 'mid_l'.
        n (int): The number of periods to consider for the moving average. Default is 20.
        s (int): The number of standard deviations to use for the bands. Default is 2.

    Returns:
        pd.DataFrame: The input DataFrame with additional columns: 'BB_MA', 'BB_UP', and 'BB_LW' representing the
        Bollinger Bands.

    """
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
    """
    Calculates the Average True Range (ATR) for the given DataFrame.

    ATR is a measure of market volatility. It is typically derived from the 14-day moving average of a series of true range indicators.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'mid_c' (mid closing prices), 'mid_h' (mid high prices), and 'mid_l' (mid low prices).
        n (int): The period for the ATR calculation. Default is 14.

    Returns:
        df (pd.DataFrame): DataFrame with added 'ATR_n' column.
    """
    prev_c = df.mid_c.shift(1)
    tr1 = df.mid_h - df.mid_l
    tr2 = abs(df.mid_h - prev_c)
    tr3 = abs(prev_c - df.mid_l)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df[f"ATR_{n}"] = tr.rolling(window=n).mean()
    return df


def RSI(df: pd.DataFrame, n=14):
    """
    Calculates the Relative Strength Index (RSI) for the given DataFrame.

    RSI is a momentum oscillator that measures the speed and change of price movements. It is primarily used to attempt to identify overbought or oversold conditions in the trading of an asset.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'mid_c' (mid closing prices).
        n (int): The period for the RSI calculation. Default is 14.

    Returns:
        df (pd.DataFrame): DataFrame with added 'RSI_n' column.
    """
    delta = df.mid_c.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.rolling(window=n).mean()
    avg_loss = losses.rolling(window=n).mean()
    rs = avg_gain / avg_loss
    df[f"RSI_{n}"] = 100 - (100 / (1 + rs))
    return df


def MACD(df: pd.DataFrame, n_slow=26, n_fast=12, n_signal=9):
    """
    Calculates the Moving Average Convergence Divergence (MACD) for the given DataFrame.

    MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price. The MACD is calculated by subtracting the 26-period Exponential Moving Average (EMA) from the 12-period EMA.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'mid_c' (mid closing prices).
        n_slow (int): The period for the slow EMA calculation. Default is 26.
        n_fast (int): The period for the fast EMA calculation. Default is 12.
        n_signal (int): The period for the signal line EMA calculation. Default is 9.

    Returns:
        df (pd.DataFrame): DataFrame with added 'MACD', 'SIGNAL', and 'HIST' (MACD Histogram) columns.
    """
    ema_long = df.mid_c.ewm(span=n_slow, min_periods=n_slow).mean()
    ema_short = df.mid_c.ewm(span=n_fast, min_periods=n_fast).mean()
    df['MACD'] = ema_short - ema_long
    df['SIGNAL'] = df.MACD.ewm(span=n_signal, min_periods=n_signal).mean()
    df['HIST'] = df.MACD - df.SIGNAL
    return df


def VWAP(df: pd.DataFrame):
    """
    Calculates the Volume Weighted Average Price (VWAP) for the given DataFrame.

    VWAP is a trading benchmark used by traders that gives the average price a security has traded at throughout the day, based on both volume and price. It is important because it provides traders with insight into both the trend and value of a security.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'mid_c' (mid closing prices), 'mid_h' (mid high prices), 'mid_l' (mid low prices), and 'volume'.

    Returns:
        df (pd.DataFrame): DataFrame with added 'VWAP' column.
    """
    tp = (df.mid_h + df.mid_l + df.mid_c) / 3
    vwap = (tp * df.volume).cumsum() / df.volume.cumsum()
    df['VWAP'] = vwap
    return df


def ADX(df: pd.DataFrame, n=14) -> pd.DataFrame:
    """
    Calculate the Average Directional Index (ADX) for a given DataFrame.

    ADX is a technical analysis indicator used to determine the strength of a trend. It is calculated based on the
    positive and negative directional movement indicators (DMI) and the average true range (ATR).

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_h', 'mid_l', and 'mid_c'.
        n (int): The number of periods to consider for the calculation. Default is 14.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'ADX' representing the Average Directional Index.

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
    Calculate the Stochastic Oscillator for a given DataFrame.

    The Stochastic Oscillator is a momentum indicator that compares a security's closing price to its price range over a
    given period of time. It consists of two lines: %K and %D.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c', 'mid_h', and 'mid_l'.
        n (int): The number of periods to consider. Default is 14.

    Returns:
        pd.DataFrame: The input DataFrame with additional columns '%K' and '%D' representing the Stochastic Oscillator.

    """
    low_min = df.mid_l.rolling(window=n).min()
    high_max = df.mid_h.rolling(window=n).max()
    df['%K'] = (df.mid_c - low_min) / (high_max - low_min) * 100
    df['%D'] = df['%K'].rolling(window=3).mean()
    return df


def MovingAverage(df: pd.DataFrame, n=50):
    """
    Calculate the Moving Average (MA) for a given DataFrame.

    The Moving Average is a widely used technical analysis indicator that smooths out price data by creating a
    constantly updated average price over a specified period of time.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary column: 'mid_c'.
        n (int): The number of periods to consider. Default is 50.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'MA_{n}' representing the Moving Average.

    """
    df[f'MA_{n}'] = df.mid_c.rolling(window=n).mean()
    return df


def ExponentialMovingAverage(df: pd.DataFrame, n=50):
    """
    Calculate the Exponential Moving Average (EMA) for a given DataFrame.

    The Exponential Moving Average is a type of moving average that gives more weight to recent prices, making it more
    responsive to price changes.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary column: 'mid_c'.
        n (int): The number of periods to consider. Default is 50.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'EMA_{n}' representing the Exponential Moving Average.

    """
    df[f'EMA_{n}'] = df.mid_c.ewm(span=n, adjust=False).mean()
    return df


def CommodityChannelIndex(df: pd.DataFrame, n=20):
    """
    Calculate the Commodity Channel Index (CCI) for a given DataFrame.

    The Commodity Channel Index is a momentum-based oscillator used to identify cyclical trends in a security. It measures
    the relationship between an asset's price and its statistical average.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_h', 'mid_l', 'mid_c'.
        n (int): The number of periods to consider. Default is 20.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'CCI' representing the Commodity Channel Index.

    """
    TP = (df.mid_h + df.mid_l + df.mid_c) / 3
    df['CCI'] = (TP - TP.rolling(window=n).mean()) / \
        (0.015 * TP.rolling(window=n).std())
    return df


def Momentum(df: pd.DataFrame, n=14):
    """
    Calculate the Momentum indicator for a given DataFrame.

    Momentum is a technical analysis indicator that measures the rate of change of a security's price over a specified
    period of time. It is used to identify the strength and direction of a trend.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary column: 'mid_c'.
        n (int): The number of periods to consider. Default is 14.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'Momentum' representing the Momentum indicator.

    """
    df['Momentum'] = df.mid_c - df.mid_c.shift(n)
    return df


def RateOfChange(df: pd.DataFrame, n=14):
    """
    Calculate the Rate of Change (ROC) for a given DataFrame.

    The Rate of Change is a momentum oscillator that measures the percentage change in price over a specified period of
    time. It is used to identify overbought and oversold conditions.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary column: 'mid_c'.
        n (int): The number of periods to consider. Default is 14.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'ROC' representing the Rate of Change.

    """
    df['ROC'] = ((df.mid_c - df.mid_c.shift(n)) / df.mid_c.shift(n)) * 100
    return df


def OnBalanceVolume(df: pd.DataFrame):
    """
    Calculate the On-Balance Volume (OBV) for a given DataFrame.

    The On-Balance Volume is a technical analysis indicator that uses volume flow to predict changes in stock price. It
    measures buying and selling pressure as a cumulative indicator.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c' and 'volume'.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'OBV' representing the On-Balance Volume.

    """
    df['OBV'] = (np.sign(df.mid_c.diff()) * df.volume).fillna(0).cumsum()
    return df


def ADL(df: pd.DataFrame):
    """
    Calculate the Accumulation/Distribution Line (ADL) for a given DataFrame.

    The Accumulation/Distribution Line is a volume-based indicator that measures the cumulative flow of money into or out
    of a security. It is used to confirm price trends and identify potential reversals.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c', 'mid_l', 'mid_h', and 'volume'.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'ADL' representing the Accumulation/Distribution Line.

    """
    clv = ((df.mid_c - df.mid_l) - (df.mid_h - df.mid_c)) / \
        (df.mid_h - df.mid_l)
    clv = clv.fillna(0)  # Replace NaNs resulting from zero division with 0
    df['ADL'] = (clv * df.volume).cumsum()
    return df


def Aroon(df: pd.DataFrame, n=14):
    """
    Calculate the Aroon indicator for a given DataFrame.

    The Aroon indicator is a technical analysis tool used to identify the strength and direction of a trend. It consists
    of two lines: Aroon Up and Aroon Down.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_h' and 'mid_l'.
        n (int): The number of periods to consider. Default is 14.

    Returns:
        pd.DataFrame: The input DataFrame with additional columns 'Aroon_Up' and 'Aroon_Down' representing the Aroon indicator.

    """
    df['Aroon_Up'] = df.mid_h.rolling(n).apply(
        lambda x: float(np.argmax(x) + 1) / n * 100)
    df['Aroon_Down'] = df.mid_l.rolling(n).apply(
        lambda x: float(np.argmin(x) + 1) / n * 100)
    return df


def Aroon_Oscillator(df: pd.DataFrame, n=14):
    """
    Calculate the Aroon Oscillator for a given DataFrame.

    The Aroon Oscillator is a trend-following indicator that measures the difference between the Aroon Up and Aroon Down
    lines. It is used to identify the strength and direction of a trend.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_h' and 'mid_l'.
        n (int): The number of periods to consider. Default is 14.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'Aroon_Oscillator' representing the Aroon Oscillator.

    """
    df = Aroon(df, n)
    df['Aroon_Oscillator'] = df['Aroon_Up'] - df['Aroon_Down']
    return df


def CMF(df: pd.DataFrame, n=20):
    """
    Calculate the Chaikin Money Flow (CMF) for a given DataFrame.

    The Chaikin Money Flow is a technical analysis indicator that measures the accumulation and distribution of money flow
    in a security. It combines price and volume to determine the strength of a trend.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c', 'mid_l', 'mid_h', and 'volume'.
        n (int): The number of periods to consider. Default is 20.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'CMF' representing the Chaikin Money Flow.

    """
    mf_multiplier = (df.mid_c - df.mid_l - df.mid_h +
                     df.mid_c) / (df.mid_h - df.mid_l)
    mf_volume = mf_multiplier * df.volume
    df['CMF'] = mf_volume.rolling(n).sum() / df.volume.rolling(n).sum()
    return df


def EVM(df: pd.DataFrame, n=14):
    """
    Calculate the Ease of Movement (EVM) for a given DataFrame.

    The Ease of Movement is a volume-based oscillator that measures the relationship between price change and volume. It is
    used to identify the strength and direction of a trend.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c', 'mid_l', 'mid_h', and 'volume'.
        n (int): The number of periods to consider. Default is 14.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'EVM' representing the Ease of Movement.

    """
    dm = ((df.mid_h + df.mid_l) / 2) - \
        ((df.mid_h.shift(1) + df.mid_l.shift(1)) / 2)
    br = (df.volume / 1e6) / ((df.mid_h - df.mid_l))
    df['EVM'] = dm / br.rolling(n).mean()
    return df


def ForceIndex(df: pd.DataFrame, n=2):
    """
    Calculate the Force Index for a given DataFrame.

    The Force Index is a technical analysis indicator that measures the strength of a price trend by combining price and volume.
    It helps identify significant changes in price and can be used to confirm the strength of a trend.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c', 'mid_l', 'mid_h', and 'volume'.
        n (int): The number of periods to consider for the rolling average. Default is 2.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'ForceIndex' representing the Force Index.

    """
    df['ForceIndex'] = df.volume * (df.mid_c - df.mid_c.shift(1))
    df['ForceIndex'] = df['ForceIndex'].rolling(n).mean()
    return df


def MassIndex(df: pd.DataFrame, n=9, n2=25):
    """
    Calculate the Mass Index for a given DataFrame.

    The Mass Index is a technical analysis indicator that measures the volatility of a security's price movement. It helps
    identify potential trend reversals by detecting periods of price compression followed by price expansion.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c', 'mid_l', and 'mid_h'.
        n (int): The number of periods to consider for the first exponential moving average. Default is 9.
        n2 (int): The number of periods to consider for the second exponential moving average. Default is 25.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'MassIndex' representing the Mass Index.

    """
    hl_diff = df.mid_h - df.mid_l
    ema1 = hl_diff.ewm(span=n, adjust=False).mean()
    ema2 = ema1.ewm(span=n, adjust=False).mean()
    mass = ema1 / ema2
    df['MassIndex'] = mass.rolling(n2).sum()
    return df


def MFI(df: pd.DataFrame, n=14):
    """
    Calculate the Money Flow Index (MFI) for a given DataFrame.

    The Money Flow Index is a technical analysis indicator that measures the strength and direction of money flow in and out
    of a security. It helps identify overbought and oversold conditions and potential trend reversals.

    Args:
        df (pd.DataFrame): The input DataFrame containing the necessary columns: 'mid_c', 'mid_l', 'mid_h', and 'volume'.
        n (int): The number of periods to consider for the rolling sum. Default is 14.

    Returns:
        pd.DataFrame: The input DataFrame with an additional column 'MFI' representing the Money Flow Index.

    """
    typical_price = (df.mid_h + df.mid_l + df.mid_c) / 3
    money_flow = typical_price * df.volume
    positive_money_flow = money_flow.where(
        df.mid_c > df.mid_c.shift(1), 0).rolling(n).sum()
    negative_money_flow = money_flow.where(
        df.mid_c < df.mid_c.shift(1), 0).rolling(n).sum()
    money_flow_ratio = positive_money_flow / negative_money_flow
    df['MFI'] = 100 - (100 / (1 + money_flow_ratio))
    return df
