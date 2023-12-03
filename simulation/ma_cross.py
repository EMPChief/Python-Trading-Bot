import pandas as pd
from infrastructure.instrument_collection import Instrument, InstrumentCollection as ic
ic = ic() 
BUY = 1
SELL = 2
NONE = 0
get_ma_col = lambda x: f"MA__{x}"

def is_trade(row, ma_l, ma_s):
    if row[ma_l] >= 0 and row[ma_s] < 0:
        return BUY
    elif row[ma_l] < 0 and row[ma_s] >= 0:
        return SELL
    return NONE

def load_price_data(pair, granularity, ma_list):
    df = pd.read_pickle(f"./data/{pair}_{granularity}.pkl")
    for ma in ma_list:
        df[get_ma_col(ma)] = df.mid_c.rolling(window=ma).mean()
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def get_trades(df_analysis, instrument):
    df_trades = df_analysis[df_analysis.TRADE != NONE].copy()
    df_trades['DIFF'] = df_trades.mid_c.diff().shift(-1)
    df_trades.fillna(0, inplace=True)
    df_trades['GAIN'] = df_trades['DIFF'] / instrument.pipLocation
    df_trades['GAIN'] = df_trades['GAIN'] * df_trades['TRADE']
    total_gain = df_trades['GAIN'].sum()
    return dict(total_gain=total_gain, df_trades=df_trades)


def assess_pair(price_data, ma_l, ma_s, instrument):
    df_analysis = price_data.copy()
    df_analysis['DELTA'] = df_analysis[ma_s] - df_analysis[ma_l]
    df_analysis['DELTA_PREV'] = df_analysis['DELTA'].shift(1)
    df_analysis['TRADE'] = df_analysis.apply(lambda row: is_trade(row, ma_l, ma_s), axis=1)
    #rint(instrument.name, ma_l, ma_s)
    #print(df_analysis.head())
    return get_trades(df_analysis, instrument)

def analyse_pair(instrument, granularity, ma_long, ma_short):
    ma_list = set(ma_long + ma_short)
    pair = instrument.name
    
    price_data = load_price_data(pair, granularity, ma_list)
    #print(pair)
    #print(price_data.head())
    
    for ma_l in ma_long:
        for ma_s in ma_short:
            if ma_l == ma_s:
                continue
            result = assess_pair(
                price_data,
                get_ma_col(ma_l),
                get_ma_col(ma_s),
                instrument
            )
            tg = result['total_gain']
            nt = result['df_trades'].shape[0]
            print(f"Pair name: {pair}\nGranularity: {granularity}\nMA Long: {ma_l}\nMA Short: {ma_s}\nTotal Gain: {tg}\nHow many trades: {nt}")

def run_ma_sim(curr_list=["EUR", "USD", "GBP", "JPY", "CHF", "AUD"],
               granularity=["H1"],
               ma_long=[20, 40, 80]):
    ic.LoadInstruments("./data")
    for g in granularity:
        for p1 in curr_list:
            for p2 in curr_list:
                pair = f"{p1}_{p2}"
                if pair in ic.instruments_dict.keys():
                    analyse_pair(ic.instruments_dict[pair], g, ma_long, ma_long)
                    

