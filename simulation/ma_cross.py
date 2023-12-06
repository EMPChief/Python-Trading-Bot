import pandas as pd
from infrastructure.instrument_collection import Instrument, InstrumentCollection as ic
import os
import pandas as pd
from datetime import datetime
from simulation.ma_excel import create_ma_result

class MAResult:
    """
    A class for analyzing trades based on moving averages.

    Attributes:
    - pairname (str): Name of the trading pair.
    - df_trades (pd.DataFrame): DataFrame containing trade data.
    - ma_l (int): Long-term moving average period.
    - ma_s (int): Short-term moving average period.
    - granularity (str): Granularity of the analysis.
    - result (dict): Result of the analysis obtained using the `result_ob` method.
    """

    def __init__(self, df_trades, pairname, ma_l, ma_s, granularity):
        """
        Initialize TradeAnalyzer instance.

        Parameters:
        - df_trades (pd.DataFrame): DataFrame containing trade data.
        - pairname (str): Name of the trading pair.
        - ma_l (int): Long-term moving average period.
        - ma_s (int): Short-term moving average period.
        - granularity (str): Granularity of the analysis.
        """
        self.pairname = pairname  # Description: Name of the trading pair.
        # Description: DataFrame containing trade data.
        self.df_trades = df_trades
        self.ma_l = ma_l  # Description: Long-term moving average period.
        self.ma_s = ma_s  # Description: Short-term moving average period.
        # Description: Granularity of the analysis.
        self.granularity = granularity
        self.result = self.result_ob()  # Description: Result of the analysis.

    def __repr__(self):
        """
        Return a string representation of the TradeAnalyzer instance.
        Description: This method provides a human-readable representation of the TradeAnalyzer instance.
        """
        return str(self.result)

    def result_ob(self):
        """
        Perform trade analysis and return a dictionary with the results.

        Returns:
        dict: Dictionary containing the following trade analysis results:
            - 'pair': Name of the trading pair.
            - 'ma_l': Long-term moving average period.
            - 'ma_s': Short-term moving average period.
            - 'total_gain': Total gain from all trades.
            - 'mean_gain': Mean gain from all trades.
            - 'min_gain': Minimum gain from all trades.
            - 'max_gain': Maximum gain from all trades.
            - 'cross': Concatenation of short-term and long-term moving averages.
            - 'number_of_trades': Number of trades in the DataFrame.
            - 'granularity': Granularity of the analysis.
        Description: This method calculates and returns a dictionary with various trade analysis results.
        """
        return dict(
            pair=self.pairname,
            num_trades=self.df_trades.shape[0],
            total_gain=int(self.df_trades.GAIN.sum()),
            mean_gain=int(self.df_trades.GAIN.mean()),
            min_gain=int(self.df_trades.GAIN.min()),
            max_gain=int(self.df_trades.GAIN.max()),
            ma_l=self.ma_l,
            ma_s=self.ma_s,
            cross=f"{self.ma_s}_{self.ma_l}",
            granularity=self.granularity
        )


ic = ic()
BUY = 1
SELL = -1
NONE = 0
def get_ma_col(x): return f"MA_{x}"
def add_cross(x): return f"{x.ma_s}_{x.ma_l}"


def is_trade(row):
    """
    Determine whether to execute a trade based on the given conditions.

    Parameters:
    - row (pd.Series): Row of a DataFrame representing a data point.
    - ma_l (int): Long-term moving average period.
    - ma_s (int): Short-term moving average period.

    Returns:
    int: Trade signal indicating whether to BUY, SELL, or NONE.

    Description:
    This function takes a row of data, along with long-term (ma_l) and short-term (ma_s) moving average periods,
    and determines the trade signal based on the change in DELTA (price change). It returns BUY if DELTA becomes positive
    after being negative in the previous row, SELL if DELTA becomes negative after being positive in the previous row,
    and NONE otherwise.
    """
    if row.DELTA >= 0 and row.DELTA_PREV < 0:
        return BUY
    if row.DELTA < 0 and row.DELTA_PREV >= 0:
        return SELL
    return NONE


def load_price_data(pair, granularity, ma_list):
    """
    Load price data from a saved pickle file and calculate moving averages.

    Parameters:
    - pair (str): Name of the trading pair.
    - granularity (str): Granularity of the data.
    - ma_list (list): List of moving average periods to calculate.

    Returns:
    pd.DataFrame: DataFrame containing loaded price data with calculated moving averages.

    Description:
    This function reads price data from a pickle file located at "./data/{pair}_{granularity}.csv".
    It then calculates moving averages for each period in the ma_list and returns the resulting DataFrame.
    """
    df = pd.read_csv(f"./data/candles/{pair}_{granularity}.csv")

    for ma in ma_list:
        df[get_ma_col(ma)] = df.mid_c.rolling(window=ma).mean()

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def get_trades(df_analysis, instrument, granularity):
    """
    Extract trade-related information from the analysis DataFrame.

    Parameters:
    - df_analysis (pd.DataFrame): DataFrame containing analysis results.
    - instrument: The financial instrument being traded.
    - granularity (str): Granularity of the analysis.

    Returns:
    pd.DataFrame: DataFrame containing trade-related information.

    Description:
    This function filters the analysis DataFrame to extract rows where trades occur (TRADE is not NONE).
    It calculates the price difference (DIFF) between short-term and long-term moving averages,
    fills NaN values with 0, and computes the gain for each trade in terms of the instrument's pip location.
    Additional columns, such as 'granularity', 'pair', and 'GAIN_C' (cumulative gain),
    are added for further analysis.
    """
    df_trades = df_analysis[df_analysis.TRADE != NONE].copy()
    df_trades["DIFF"] = df_trades.mid_c.diff().shift(-1)
    df_trades.fillna(0, inplace=True)
    df_trades["GAIN"] = df_trades.DIFF / instrument.pipLocation
    df_trades["GAIN"] = df_trades["GAIN"] * df_trades["TRADE"]
    df_trades["granularity"] = granularity
    df_trades["pair"] = instrument.name
    df_trades["GAIN_C"] = df_trades["GAIN"].cumsum()
    return df_trades


def assess_pair(price_data, ma_l, ma_s, instrument, granularity):
    """
    Perform an assessment of a trading pair based on moving averages.

    Parameters:
    - price_data (pd.DataFrame): DataFrame containing price data.
    - ma_l (int): Long-term moving average period.
    - ma_s (int): Short-term moving average period.
    - instrument: The financial instrument being traded.
    - granularity (str): Granularity of the analysis.

    Returns:
    MAResult: An instance of the MAResult class representing the assessment results.

    Description:
    This function takes price data, calculates the price difference (DELTA) between short-term (ma_s)
    and long-term (ma_l) moving averages, determines trade signals using the `is_trade` function,
    extracts trade-related information using the `get_trades` function, and returns the assessment results
    as an instance of the MAResult class.
    """
    df_analysis = price_data.copy()
    df_analysis["DELTA"] = df_analysis[ma_s] - df_analysis[ma_l]
    df_analysis["DELTA_PREV"] = df_analysis["DELTA"].shift(1)
    df_analysis["TRADE"] = df_analysis.apply(is_trade, axis=1)
    df_trades = get_trades(df_analysis, instrument, granularity)
    df_trades["ma_l"] = ma_l
    df_trades["ma_s"] = ma_s
    df_trades["cross"] = df_trades.apply(add_cross, axis=1)
    return MAResult(
        df_trades,
        instrument.name,
        ma_l,
        ma_s,
        granularity
    )


def append_df_to_file(df, filename):
    """
    Append a DataFrame to a file or create a new file if it doesn't exist.

    Parameters:
    - df (pd.DataFrame): DataFrame to be appended.
    - filename (str): Name of the file to which the DataFrame will be appended or created.

    Description:
    If the file already exists, the function reads its contents, concatenates the existing DataFrame
    with the new DataFrame (df), resets the index, and saves the combined DataFrame back to the file.
    If the file doesn't exist, it creates a new file with the given DataFrame.
    Finally, it prints the filename, shape of the DataFrame, and the last two rows of the DataFrame.
    """
    if os.path.isfile(filename):
        fd = pd.read_csv(filename)
        df = pd.concat([fd, df])
    df.reset_index(drop=True, inplace=True)
    df.to_csv(filename, index=False)
    print(filename, df.shape)
    print(df.tail(2))


def get_fullname(filepath, filename):
    """
    Get the full path for a file.

    Parameters:
    - filepath (str): Path to the directory containing the file.
    - filename (str): Name of the file.

    Returns:
    str: Full path of the file.

    Description:
    This function takes a filepath and a filename and returns the full path of the file by concatenating
    the filepath and filename with a '/' separator.
    """
    return f"{filepath}/{filename}.csv"


def process_macro(result_list, filepath):
    """
    Process a list of results and save them to a file.

    Parameters:
    - result_list (list): List of result objects.
    - filepath (str): Path to the directory where the file will be saved.

    Description:
    This function extracts the results from a list of result objects, converts them into a DataFrame,
    and appends the DataFrame to a file named "ma_res_{current_date}.csv" in the specified filepath.
    The current_date is obtained using the current date in the format "%Y-%m-%d".
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    rl = [x.result for x in result_list]
    df = pd.DataFrame.from_dict(rl)
    append_df_to_file(df, get_fullname(filepath, f"ma_res_{current_date}"))


def process_trades(result_list, filepath):
    """
    Process a list of trade results and save them to a file.

    Parameters:
    - result_list (list): List of result objects.
    - filepath (str): Path to the directory where the file will be saved.

    Description:
    This function extracts the trade results from a list of result objects, concatenates them into a single DataFrame,
    and appends the DataFrame to a file named "ma_trades_{current_date}.csv" in the specified filepath.
    The current_date is obtained using the current date in the format "%Y-%m-%d".
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    df = pd.concat([x.df_trades for x in result_list])
    append_df_to_file(df, get_fullname(filepath, f"ma_trades_{current_date}"))


def process_results(result_list, filepath):
    """
    Process a list of results, including macro and trade results, and save them to files.

    Parameters:
    - result_list (list): List of result objects.
    - filepath (str): Path to the directory where the files will be saved.

    Description:
    This function calls the `process_macro` and `process_trades` functions to save macro and trade results
    to separate files in the specified filepath.
    """
    process_macro(result_list, filepath)
    process_trades(result_list, filepath)

    # rl = [x.result for x in result_list]
    # df = pd.DataFrame.from_dict(rl)
    # print(df)
    # print(result_list[0].df_trades.head(2))


def analyse_pair(instrument, granularity, ma_long, ma_short, filepath):
    """
    Analyze a trading pair based on different combinations of long-term and short-term moving averages.

    Parameters:
    - instrument: The financial instrument being traded.
    - granularity (str): Granularity of the analysis.
    - ma_long (list): List of long-term moving average periods.
    - ma_short (list): List of short-term moving average periods.
    - filepath (str): Path to the directory where result files will be saved.

    Description:
    This function loads price data for the specified trading pair and moving average periods.
    It then assesses the trading pair for each combination of long-term and short-term moving averages,
    excluding combinations where ma_l and ma_s are the same.
    The assessment results are saved to separate files for macro and trade results.
    """
    ma_list = set(ma_long + ma_short)
    pair = instrument.name

    price_data = load_price_data(pair, granularity, ma_list)
    results_list = []
    for ma_l in ma_long:
        for ma_s in ma_short:
            if ma_l <= ma_s:
                continue

            ma_result = assess_pair(
                price_data,
                get_ma_col(ma_l),
                get_ma_col(ma_s),
                instrument,
                granularity
            )
            # print(ma_result)
            results_list.append(ma_result)
    process_results(results_list, filepath)


def run_ma_sim(curr_list=["EUR", "USD"],
               granularity=["H4"],
               ma_long=[20, 40, 80, 120, 150, 200],
               ma_short=[10, 20, 30, 40, 50, 100],
               filepath="./data"):
    """
    Run a moving average simulation for multiple currency pairs, granularities, and moving average periods.

    Parameters:
    - curr_list (list): List of currency pairs.
    - granularity (list): List of granularities.
    - ma_long (list): List of long-term moving average periods.
    - ma_short (list): List of short-term moving average periods.
    - filepath (str): Path to the directory where result files will be saved.

    Description:
    This function loads instruments, iterates through combinations of currency pairs, granularities,
    and moving average periods, and runs the moving average simulation using the `analyse_pair` function.
    """
    ic.LoadInstruments("./data")
    for g in granularity:
        for p1 in curr_list:
            for p2 in curr_list:
                pair = f"{p1}_{p2}"
                if pair in ic.instruments_dict.keys():
                    analyse_pair(
                        ic.instruments_dict[pair], g, ma_long, ma_short, filepath)
            create_ma_result(g)
