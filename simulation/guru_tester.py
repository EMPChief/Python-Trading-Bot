import numpy as np
import pandas as pd
import datetime as dt

BUY = 1
SELL = -1
NONE = 0


def apply_take_profit_vectorized(df, PROFIT_FACTOR):
    conditions_buy = df['SIGNAL'] == BUY
    conditions_sell = df['SIGNAL'] == SELL

    df['TP'] = np.select(
        [conditions_buy, conditions_sell],
        [(df['ask_c'] - df['ask_o']) * PROFIT_FACTOR + df['ask_c'],
         (df['bid_c'] - df['bid_o']) * PROFIT_FACTOR + df['bid_c']],
        default=0.0
    )


def apply_stop_loss_vectorized(df):
    conditions_buy = df['SIGNAL'] == BUY
    df['SL'] = np.where(conditions_buy, df['ask_o'], df['bid_o'])


def remove_spread_vectorized(df):
    for a in ["ask", "bid"]:
        for b in ["o", "h", "l", "c"]:
            c = f"{a}_{b}"
            df[c] = df[f"mid_{b}"]


def apply_signals(df, PROFIT_FACTOR, sig):
    df["SIGNAL"] = df.apply(sig, axis=1)
    apply_take_profit_vectorized(df, PROFIT_FACTOR)
    apply_stop_loss_vectorized(df)


def create_signals(df, time_d=1):
    df_signals = df[df.SIGNAL != NONE].copy()
    df_signals['m5_start'] = pd.to_datetime(
        df_signals['time']) + pd.to_timedelta(time_d, unit='hours')

    buy_condition = df_signals['SIGNAL'] == BUY
    sell_condition = df_signals['SIGNAL'] == SELL

    df_signals['start_price_BUY'] = np.where(
        buy_condition, df_signals['bid_c'], df_signals['ask_c'])
    df_signals['start_price_SELL'] = np.where(
        buy_condition, df_signals['ask_c'], df_signals['bid_c'])

    df_signals.drop(['time', 'mid_o', 'mid_h', 'mid_l', 'bid_o', 'bid_h', 'bid_l',
                     'ask_o', 'ask_h', 'ask_l', 'direction'], axis=1, inplace=True)

    df_signals.rename(columns={
        'm5_start': 'time'
    }, inplace=True)

    return df_signals


class Trade:
    def __init__(self, row, profit_factor, loss_factor):
        self.running = True
        self.start_index_m5 = row.name
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor

        self.start_price_buy = row.start_price_BUY
        self.trigger_price_buy = row.start_price_BUY
        self.start_price_sell = row.start_price_SELL
        self.trigger_price_sell = row.start_price_SELL

        self.SIGNAL = row.SIGNAL
        self.start_price = np.where(
            row.SIGNAL == BUY, self.start_price_buy, self.start_price_sell)
        self.trigger_price = np.where(
            row.SIGNAL == BUY, self.trigger_price_buy, self.trigger_price_sell)
        self.TP = row.TP
        self.SL = row.SL
        self.result = 0.0
        self.end_time = row.time
        self.start_time = row.time

    def close_trade(self, row, result, trigger_price):
        self.running = False
        self.result = result
        self.end_time = row.time
        self.trigger_price = trigger_price

    def update(self, row):
        bid_h, bid_l, ask_l, ask_h = row.bid_h, row.bid_l, row.ask_l, row.ask_h

        if self.SIGNAL == BUY:
            tp_condition = bid_h >= self.TP
            sl_condition = bid_l <= self.SL
        else:
            tp_condition = ask_l <= self.TP
            sl_condition = ask_h >= self.SL

        if tp_condition:
            self.close_trade(row, self.profit_factor, np.where(
                self.SIGNAL == BUY, bid_h, ask_l))
        elif sl_condition:
            self.close_trade(row, self.loss_factor, np.where(
                self.SIGNAL == BUY, bid_l, ask_h))


class GuruTester:
    def __init__(self, df_big,
                 apply_signal,
                 df_m5,
                 use_spread=True,
                 LOSS_FACTOR=-1.0,
                 PROFIT_FACTOR=1.5,
                 time_d=1):
        self.df_big = df_big.copy()
        self.use_spread = use_spread
        self.apply_signal = apply_signal
        self.df_m5 = df_m5.copy()
        self.LOSS_FACTOR = LOSS_FACTOR
        self.PROFIT_FACTOR = PROFIT_FACTOR
        self.time_d = time_d

        self.prepare_data()

    def prepare_data(self):
        if not self.use_spread:
            remove_spread_vectorized(self.df_big)
            remove_spread_vectorized(self.df_m5)

        apply_signals(self.df_big, self.PROFIT_FACTOR, self.apply_signal)

        df_m5_slim = self.df_m5[['time', 'bid_h',
                                'bid_l', 'ask_h', 'ask_l']].copy()
        df_signals = create_signals(self.df_big, time_d=self.time_d)

        df_m5_slim['time'] = pd.to_datetime(df_m5_slim['time'])
        df_signals['time'] = pd.to_datetime(df_signals['time'])

        self.merged = pd.merge(
            left=df_m5_slim, right=df_signals, on='time', how='left')
        self.merged.fillna(0, inplace=True)
        self.merged.SIGNAL = self.merged.SIGNAL.astype(int)

    def run_test(self):
        open_trades_m5 = []
        closed_trades_m5 = []

        for index, row in self.merged.iterrows():
            if row.SIGNAL != NONE:
                open_trades_m5.append(
                    Trade(row, self.PROFIT_FACTOR, self.LOSS_FACTOR))

            for ot in open_trades_m5:
                ot.update(row)
                if not ot.running:
                    closed_trades_m5.append(ot)
            open_trades_m5 = [x for x in open_trades_m5 if x.running]

        self.df_results = pd.DataFrame.from_dict(
            [vars(x) for x in closed_trades_m5])
