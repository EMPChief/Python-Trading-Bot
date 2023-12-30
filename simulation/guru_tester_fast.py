import pandas as pd
import datetime as dt

BUY = 1
SELL = -1
NONE = 0


def calculate_take_profit(row, profit_factor):
    if row['SIGNAL'] != NONE:
        if row['SIGNAL'] == BUY:
            return (row['ask_c'] - row['ask_o']) * profit_factor + row['ask_c']
        else:
            return (row['bid_c'] - row['bid_o']) * profit_factor + row['bid_c']
    return 0.0


def calculate_stop_loss(row):
    return row['ask_o'] if row['SIGNAL'] == BUY else row['bid_o'] if row['SIGNAL'] == SELL else 0.0


def remove_market_spread(df):
    for ask_bid in ["ask", "bid"]:
        for ohlc in ["o", "h", "l", "c"]:
            column_name = f"{ask_bid}_{ohlc}"
            df[column_name] = df[f"mid_{ohlc}"]


def apply_trading_signals(df, profit_factor, signal_function):
    df["SIGNAL"] = df.apply(signal_function, axis=1)
    df["TP"] = df.apply(calculate_take_profit, axis=1,
                        PROFIT_FACTOR=profit_factor)
    df["SL"] = df.apply(calculate_stop_loss, axis=1)


def create_signal_data(df, time_delta=1):
    signal_df = df[df.SIGNAL != NONE].copy()
    signal_df['m5_start'] = [
        x + dt.timedelta(hours=time_delta) for x in signal_df.time]
    signal_df.drop(['time', 'mid_o', 'mid_h', 'mid_l', 'bid_o', 'bid_h',
                   'bid_l', 'ask_o', 'ask_h', 'ask_l', 'direction'], axis=1, inplace=True)
    signal_df.rename(columns={'bid_c': 'start_price_BUY',
                     'ask_c': 'start_price_SELL', 'm5_start': 'time'}, inplace=True)
    return signal_df


# Define constants for index positions
INDEX_start_price_BUY = 0
INDEX_start_price_SELL = 1
INDEX_SIGNAL = 2
INDEX_TP = 3
INDEX_SL = 4
INDEX_time = 5
INDEX_bid_h = 6
INDEX_bid_l = 7
INDEX_ask_h = 8
INDEX_ask_l = 9
INDEX_name = 10


class Trade:
    def __init__(self, values, index, profit_factor, loss_factor):
        self.running = True
        self.start_index_m5 = values[INDEX_name][index]
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor
        self.start_price = values[INDEX_start_price_BUY][index] if values[
            INDEX_SIGNAL][index] == BUY else values[INDEX_start_price_SELL][index]
        self.trigger_price = self.start_price
        self.SIGNAL = values[INDEX_SIGNAL][index]
        self.TP = values[INDEX_TP][index]
        self.SL = values[INDEX_SL][index]
        self.result = 0.0
        self.start_time = values[INDEX_time][index]
        self.end_time = None

    def close_trade(self, values, index, result, trigger_price):
        self.running = False
        self.result = result
        self.end_time = values[INDEX_time][index]
        self.trigger_price = trigger_price

    def update(self, values, index):
        if self.SIGNAL == BUY and values[INDEX_bid_h][index] >= self.TP or values[INDEX_bid_l][index] <= self.SL:
            result = self.profit_factor if values[INDEX_bid_h][index] >= self.TP else self.loss_factor
            self.close_trade(
                values, index, result, values[INDEX_bid_h][index] if self.SIGNAL == BUY else values[INDEX_bid_l][index])
        elif self.SIGNAL == SELL and values[INDEX_ask_l][index] <= self.TP or values[INDEX_ask_h][index] >= self.SL:
            result = self.profit_factor if values[INDEX_ask_l][index] <= self.TP else self.loss_factor
            self.close_trade(
                values, index, result, values[INDEX_ask_l][index] if self.SIGNAL == SELL else values[INDEX_ask_h][index])


class GuruTesterFast:
    def __init__(self, main_df, signal_function, minute_5_df, use_spread=True, loss_factor=-1.0, profit_factor=1.5, time_delta=1):
        self.main_df = main_df.copy()
        self.use_spread = use_spread
        self.signal_function = signal_function
        self.minute_5_df = minute_5_df.copy()
        self.loss_factor = loss_factor
        self.profit_factor = profit_factor
        self.time_delta = time_delta
        self.prepare_data()

    def prepare_data(self):
        if not self.use_spread:
            remove_market_spread(self.main_df)
            remove_market_spread(self.minute_5_df)
        apply_trading_signals(
            self.main_df, self.profit_factor, self.signal_function)
        slim_minute_5_df = self.minute_5_df[[
            'time', 'bid_h', 'bid_l', 'ask_h', 'ask_l']].copy()
        signals_df = create_signal_data(
            self.main_df, time_delta=self.time_delta)
        self.merged_data = pd.merge(
            slim_minute_5_df, signals_df, on='time', how='left').fillna(0)
        self.merged_data.SIGNAL = self.merged_data.SIGNAL.astype(int)

    def run_test(self):
        print("Running test...")
        active_trades = []
        completed_trades = []
        value_refs = [self.merged_data.start_price_BUY.array,
                      self.merged_data.start_price_SELL.array, ...]

        for index in range(self.merged_data.shape[0]):
            if value_refs[INDEX_SIGNAL][index] != NONE:
                active_trades.append(
                    Trade(value_refs, index, self.profit_factor, self.loss_factor))
            for trade in active_trades:
                trade.update(value_refs, index)
                if not trade.running:
                    completed_trades.append(trade)
            active_trades = [trade for trade in active_trades if trade.running]
        self.test_results = pd.DataFrame(
            [vars(trade) for trade in completed_trades])
