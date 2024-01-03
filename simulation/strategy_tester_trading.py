from multiprocessing import Process
import pandas as pd
from dateutil import parser
from technicals.indicators import MACD, RSI, CMF, EVM, IchimokuCloud
from simulation.guru_tester import GuruTester
from infrastructure.instrument_collection import InstrumentCollection

BUY = 1
SELL = -1
NONE = 0


def apply_trading_signal(row, rsi_buy_threshold=50, rsi_sell_threshold=50, cmf_threshold=0, evm_threshold=0):
    buy_signals = 0
    sell_signals = 0
    if row.mid_l > row.EMA:
        buy_signals += 1
    elif row.mid_h < row.EMA:
        sell_signals += 1
    if row.RSI > rsi_buy_threshold:
        buy_signals += 1
    elif row.RSI < rsi_sell_threshold:
        sell_signals += 1
    if row.CMF > cmf_threshold:
        buy_signals += 1
    elif row.CMF < -cmf_threshold:
        sell_signals += 1
    if row.EVM > evm_threshold:
        buy_signals += 1
    elif row.EVM < -evm_threshold:
        sell_signals += 1

    return BUY if buy_signals >= 3 else SELL if sell_signals >= 3 else NONE


def apply_macd_cross_signal(row):
    return BUY if row.macd_delta > 0 and row.macd_delta_prev < 0 else SELL if row.macd_delta < 0 and row.macd_delta_prev > 0 else NONE


def prepare_data_for_simulation(df, slow, fast, signal, ema, rsi_period, cmf_period, evm_period, ichimoku_params):
    df_analyzed = df.copy()
    df_analyzed = MACD(df_analyzed, n_slow=slow, n_fast=fast, n_signal=signal)
    df_analyzed['macd_delta'] = df_analyzed['MACD'] - df_analyzed['SIGNAL']
    df_analyzed['macd_delta_prev'] = df_analyzed['macd_delta'].shift(1)
    df_analyzed['EMA'] = df_analyzed['mid_c'].ewm(
        span=ema, min_periods=ema).mean()
    df_analyzed = RSI(df_analyzed, n=rsi_period)
    df_analyzed = CMF(df_analyzed, n_cmf=cmf_period)

    df_analyzed = EVM(df_analyzed, n=evm_period)
    df_analyzed = IchimokuCloud(df_analyzed, n1=ichimoku_params['conversion_line_period'],
                                n2=ichimoku_params['base_line_period'], n3=ichimoku_params['lagging_span_period'])
    df_analyzed.dropna(inplace=True)
    df_analyzed.reset_index(drop=True, inplace=True)
    df_analyzed['direction'] = df_analyzed.apply(
        apply_trading_signal, axis=1, rsi_buy_threshold=60, rsi_sell_threshold=40, cmf_threshold=0.05, evm_threshold=0.1)

    return df_analyzed


def load_data_for_pair(pair, timeframe=1):
    start_date = parser.parse("2015-11-01T00:00:00Z")
    end_date = parser.parse("2023-10-01T00:00:00Z")

    hourly_data = pd.read_csv(f"./data/candles/{pair}_H{timeframe}.csv")
    five_min_data = pd.read_csv(f"./data/candles/{pair}_M5.csv")

    hourly_data['time'] = pd.to_datetime(hourly_data['time'])
    five_min_data['time'] = pd.to_datetime(five_min_data['time'])

    hourly_data = hourly_data[(hourly_data.time >= start_date) & (
        hourly_data.time < end_date)]
    five_min_data = five_min_data[(five_min_data.time >= start_date) & (
        five_min_data.time < end_date)]

    hourly_data.reset_index(drop=True, inplace=True)
    five_min_data.reset_index(drop=True, inplace=True)

    return hourly_data, five_min_data


def simulate_with_parameters(pair, hourly_data, five_min_data, slow, fast, signal, ema, rsi_period, cmf_period, evm_period, ichimoku_params, timeframe):
    prepared_data = prepare_data_for_simulation(
        hourly_data, slow, fast, signal, ema, rsi_period, cmf_period, evm_period, ichimoku_params)
    tester = GuruTester(prepared_data, apply_trading_signal,
                        five_min_data, use_spread=True, time_d=timeframe)
    tester.run_test()

    results_df = pd.DataFrame()

    results_df['slow'] = slow
    results_df['fast'] = fast
    results_df['signal'] = signal
    results_df['ema'] = ema
    results_df['rsi_period'] = rsi_period
    results_df['cmf_period'] = cmf_period
    results_df['evm_period'] = evm_period
    ichimoku_params_df = pd.DataFrame(ichimoku_params, index=[0])

    if isinstance(tester.df_results, pd.DataFrame):
        # Append the data to the results DataFrame
        results_df = results_df.append(
            ichimoku_params_df, ignore_index=True)
    else:
        results_df = ichimoku_params_df

    results_df['pair'] = pair

    return results_df


def run_simulation_for_pair(pair):
    timeframe = 4
    hourly_data, five_min_data = load_data_for_pair(pair, timeframe=timeframe)

    results = []
    trades = []
    for slow in [26, 52, 78]:
        for fast in [12, 18, 24]:
            if slow <= fast:
                continue
            for signal in [9, 12, 15]:
                for ema in [50, 100, 150]:
                    for rsi_period in [14, 28, 42]:
                        for cmf_period in [20, 40, 60]:
                            for evm_period in [14, 28, 42]:
                                for ichimoku_params in [{'conversion_line_period': 9, 'base_line_period': 26, 'lagging_span_period': 52, 'displacement': 26}, {'conversion_line_period': 20, 'base_line_period': 60, 'lagging_span_period': 120, 'displacement': 30}, {'conversion_line_period': 10, 'base_line_period': 30, 'lagging_span_period': 60, 'displacement': 30}]:
                                    sim_results = simulate_with_parameters(
                                        pair, hourly_data, five_min_data, slow, fast, signal, ema, rsi_period, cmf_period, evm_period, ichimoku_params, timeframe)
                                    total_result = sim_results.result.sum()
                                    results.append({
                                        'pair': pair,
                                        'slow': slow,
                                        'fast': fast,
                                        'ema': ema,
                                        'signal': signal,
                                        'rsi_period': rsi_period,
                                        'cmf_period': cmf_period,
                                        'evm_period': evm_period,
                                        'ichimoku_params': ichimoku_params,
                                        'result': total_result,
                                    })
                                    print(
                                        f"--> {pair} {slow} {fast} {ema} {signal} {rsi_period} {cmf_period} {evm_period} {ichimoku_params} {total_result}")

    pd.concat(trades).to_csv(
        f"./data/result/trades/macd_ema_trades_{pair}.csv")
    return pd.DataFrame(results)


def run_simulation_process(pair):
    print(f"PROCESS {pair} STARTED")
    simulation_results = run_simulation_for_pair(pair)
    simulation_results.to_pickle(
        f"./data/result/macd_ema/macd_ema_res_{pair}.csv")
    print(f"PROCESS {pair} ENDED")


def generate_simulation_pairs(l_curr, instrument_collection):
    simulation_pairs = []
    for base_currency in l_curr:
        for quote_currency in l_curr:
            pair = f"{base_currency}_{quote_currency}"
            if pair in instrument_collection.instruments_dict:
                simulation_pairs.append(pair)
    return simulation_pairs


def run_full_stimulation(instrument_collection):
    simulation_pairs = generate_simulation_pairs(
        ['USD', 'GBP', 'JPY', 'NZD', 'AUD', 'CAD'], instrument_collection)
    process_limit = 4
    current_index = 0

    while current_index < len(simulation_pairs):
        processes = []
        remaining_pairs = len(simulation_pairs) - current_index
        process_limit = min(remaining_pairs, process_limit)

        for _ in range(process_limit):
            processes.append(Process(target=run_simulation_process,
                             args=(simulation_pairs[current_index],)))
            current_index += 1

        for process in processes:
            process.start()

        for process in processes:
            process.join()

    print("ALL SIMULATIONS COMPLETED")
