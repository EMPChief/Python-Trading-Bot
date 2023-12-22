from multiprocessing import Process
import pandas as pd
from dateutil import parser
from technicals.indicators import MACD, RSI, IchimokuCloud, CMF, ExponentialMovingAverage, RateOfChange
from simulation.guru_tester import GuruTester
from infrastructure.instrument_collection import InstrumentCollection

BUY = 1
SELL = -1
NONE = 0


def apply_signal(row):
    buy_signals = 0
    sell_signals = 0

    # Ensure column exists before accessing
    if 'RSI' in row and row['RSI'] < 30:
        buy_signals += 1
    elif 'RSI' in row and row['RSI'] > 70:
        sell_signals += 1

    if 'IchimokuSignal' in row and row['IchimokuSignal'] == BUY:
        buy_signals += 1
    elif 'IchimokuSignal' in row and row['IchimokuSignal'] == SELL:
        sell_signals += 1

    if 'CMF' in row and row['CMF'] > 0:
        buy_signals += 1
    elif 'CMF' in row and row['CMF'] < 0:
        sell_signals += 1

    if 'EMA' in row and row['EMA'] > row['mid_c']:
        sell_signals += 1
    elif 'EMA' in row and row['EMA'] < row['mid_c']:
        buy_signals += 1

    if 'ROC' in row and row['ROC'] > 0:
        buy_signals += 1
    elif 'ROC' in row and row['ROC'] < 0:
        sell_signals += 1

    if 'direction' in row and row.direction == BUY and row.mid_l > row.EMA:
        buy_signals += 1
    elif 'direction' in row and row.direction == SELL and row.mid_h < row.EMA:
        sell_signals += 1

    if buy_signals >= 3:
        return BUY
    elif sell_signals >= 3:
        return SELL
    return NONE


def apply_cross(row):
    if 'macd_delta' in row and row.macd_delta > 0 and row.macd_delta_prev < 0:
        return BUY
    if 'macd_delta' in row and row.macd_delta < 0 and row.macd_delta_prev > 0:
        return SELL
    return NONE


def prepare_data(df: pd.DataFrame, slow, fast, signal, ema):
    df_an = df.copy()
    df_an = MACD(df_an, n_slow=slow, n_fast=fast, n_signal=signal)
    df_an['macd_delta'] = df_an.MACD - df_an.SIGNAL
    df_an['macd_delta_prev'] = df_an.macd_delta.shift(1)
    df_an['direction'] = df_an.apply(apply_cross, axis=1)
    df_an['EMA'] = df_an.mid_c.ewm(span=ema, min_periods=ema).mean()

    df_an = RSI(df_an, n=14)
    df_an = IchimokuCloud(df_an, n1=9, n2=26, n3=52)
    df_an = CMF(df_an, n_cmf=20)
    df_an = ExponentialMovingAverage(df_an, n=50)
    df_an = RateOfChange(df_an, n=14)

    df_an.dropna(inplace=True)
    df_an.reset_index(drop=True, inplace=True)
    return df_an


def load_data(pair, time_d=1):
    try:
        start = parser.parse("2014-01-01T00:00:00Z")
        end = parser.parse("2023-10-01T00:00:00Z")

        df = pd.read_csv(
            f"./data/candles/{pair}_H{time_d}.csv", parse_dates=['time'])
        df_m5 = pd.read_csv(
            f"./data/candles/{pair}_M5.csv", parse_dates=['time'])

        df = df[(df['time'] >= start) & (df['time'] < end)]
        df_m5 = df_m5[(df_m5['time'] >= start) & (df_m5['time'] < end)]

        df.reset_index(drop=True, inplace=True)
        df_m5.reset_index(drop=True, inplace=True)

        return df, df_m5
    except Exception as e:
        print(f"An error occurred while loading data: {e}")
        return None, None


def simulate_params(pair, df, df_m5, slow, fast, signal, ema, time_d):
    prepped_df = prepare_data(df, slow, fast, signal, ema)
    gt = GuruTester(prepped_df, apply_signal, df_m5,
                    use_spread=True, time_d=time_d)
    gt.run_test()

    gt.df_results['slow'] = slow
    gt.df_results['fast'] = fast
    gt.df_results['signal'] = signal
    gt.df_results['ema'] = ema
    gt.df_results['pair'] = pair

    return gt.df_results


def run_pair(pair, param_set):
    time_d = param_set['time_d']
    slow, fast, signal, ema = param_set['slow'], param_set['fast'], param_set['signal'], param_set['ema']

    df, df_m5 = load_data(pair, time_d)

    results = []
    trades = []

    sim_res_df = simulate_params(
        pair, df, df_m5, slow, fast, signal, ema, time_d)
    r = sim_res_df.result.sum()
    trades.append(sim_res_df)
    results.append({
        'pair': pair,
        'slow': slow,
        'fast': fast,
        'ema': ema,
        'result': r,
        'signal': signal
    })

    pd.concat(trades).to_csv(
        f"./data/result/trades/macd_ema_trades_{pair}_{time_d}_{slow}_{fast}_{signal}_{ema}.csv")
    return pd.DataFrame.from_dict(results)


def run_process(pair, param_set):
    print("PROCESS", pair, "STARTED")
    results = run_pair(pair, param_set)
    results.to_csv(
        f"./data/result/macd_ema_res_{pair}_{param_set['time_d']}_{param_set['slow']}_{param_set['fast']}_{param_set['signal']}_{param_set['ema']}.csv")
    print("PROCESS", pair, "ENDED")


def get_sim_pairs(l_curr, ic: InstrumentCollection):
    pairs = []
    for p1 in l_curr:
        for p2 in l_curr:
            pair = f"{p1}_{p2}"
            if pair in ic.instruments_dict.keys():
                pairs.append(pair)
    return pairs


def run_ema_macd(ic: InstrumentCollection):
    param_sets = [
        {'time_d': 4, 'slow': 26, 'fast': 12, 'signal': 9, 'ema': 50},
        {'time_d': 4, 'slow': 30, 'fast': 15, 'signal': 9, 'ema': 60},
        {'time_d': 6, 'slow': 26, 'fast': 12, 'signal': 9, 'ema': 50},
        {'time_d': 4, 'slow': 52, 'fast': 26, 'signal': 9, 'ema': 100},
        {'time_d': 2, 'slow': 26, 'fast': 12, 'signal': 9, 'ema': 30},
        {'time_d': 8, 'slow': 40, 'fast': 20, 'signal': 9, 'ema': 50},
        {'time_d': 4, 'slow': 26, 'fast': 13, 'signal': 9, 'ema': 55},
        {'time_d': 4, 'slow': 24, 'fast': 12, 'signal': 9, 'ema': 50},
        {'time_d': 4, 'slow': 26, 'fast': 14, 'signal': 9, 'ema': 45},
        {'time_d': 4, 'slow': 30, 'fast': 10, 'signal': 9, 'ema': 70}
    ]

    pairs = get_sim_pairs(
        ['USD', 'GBP', 'JPY', 'SEK', 'CHF', 'AUD', 'CAD', 'HKD'], ic)

    for param_set in param_sets:
        for pair in pairs:
            p = Process(target=run_process, args=(pair, param_set))
            p.start()
            p.join()

    print("ALL DONE")
