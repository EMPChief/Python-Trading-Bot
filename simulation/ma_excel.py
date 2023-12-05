from sys import float_repr_style
import pandas as pd
import sys
sys.path.append('../')

WIDTHS = {
    'L:L': 20,
    'B:F': 9
}

def set_widths(pair, writer):
    """
    Set column widths for a specific pair in the Excel writer.

    Parameters:
    - pair (str): The pair for which column widths are to be set.
    - writer: Excel writer object.

    Example:
    ```python
    set_widths("EURUSD", excel_writer)
    ```
    """
    worksheet = writer.sheets[pair]
    for k, v in WIDTHS.items():
        worksheet.set_column(k, v)

def get_line_chart(book, start_row, end_row, labels_col, data_col, title, sheetname):
    """
    Create a line chart in an Excel workbook.

    Parameters:
    - book: Excel workbook object.
    - start_row (int): Starting row for data in the worksheet.
    - end_row (int): Ending row for data in the worksheet.
    - labels_col (int): Column index for category labels.
    - data_col (int): Column index for chart data.
    - title (str): Title of the chart.
    - sheetname (str): Name of the worksheet.

    Returns:
    Chart object.

    Example:
    ```python
    chart = get_line_chart(workbook, 1, 10, 1, 2, "My Chart", "Sheet1")
    ```
    """
    chart = book.add_chart({'type': 'line'})
    chart.add_series({
        'categories': [sheetname, start_row, labels_col, end_row, labels_col],
        'values': [sheetname, start_row, data_col, end_row, data_col],
        'line': {'color': 'blue'}
    })
    chart.set_title({'name': title})
    chart.set_legend({'none': True})
    return chart

def add_chart(pair, cross, df, writer):
    """
    Add a line chart to an Excel worksheet based on the provided DataFrame.

    Parameters:
    - pair (str): Trading pair.
    - cross (str): Cross information.
    - df: DataFrame containing chart data.
    - writer: Excel writer object.

    Example:
    ```python
    add_chart("EURUSD", "MA Cross", df_data, excel_writer)
    ```
    """
    workbook = writer.book
    worksheet = writer.sheets[pair]

    chart = get_line_chart(workbook, 1, df.shape[0], 11, 12,
                           f"GAIN_C for {pair} {cross}", pair)
    chart.set_size({'x_scale': 2.5, 'y_scale': 2.5})
    worksheet.insert_chart('O1', chart)

def add_pair_charts(df_ma_res, df_ma_trades, writer):
    """
    Add line charts for each trading pair to an Excel workbook.

    Parameters:
    - df_ma_res: DataFrame with MA results.
    - df_ma_trades: DataFrame with MA trades.
    - writer: Excel writer object.

    Example:
    ```python
    add_pair_charts(df_results, df_trades, excel_writer)
    ```
    """
    cols = ['time', 'GAIN_C']
    df_temp = df_ma_res.drop_duplicates(subset="pair")

    for _, row in df_temp.iterrows():
        dft = df_ma_trades[(df_ma_trades.cross == row.cross) &
                           (df_ma_trades.pair == row.pair)]
        dft[cols].to_excel(writer, sheet_name=row.pair, index=False, startrow=0, startcol=11)
        set_widths(row.pair, writer)
        add_chart(row.pair, row.cross, dft, writer)

def add_pair_sheets(df_ma_res, writer):
    """
    Add worksheets for each trading pair to an Excel workbook.

    Parameters:
    - df_ma_res: DataFrame with MA results.
    - writer: Excel writer object.

    Example:
    ```python
    add_pair_sheets(df_results, excel_writer)
    ```
    """
    for p in df_ma_res.pair.unique():
        tdf = df_ma_res[df_ma_res.pair == p]
        tdf.to_excel(writer, sheet_name=p, index=False)

def prepare_data(df_ma_res, df_ma_trades):
    """
    Prepare dataframes for creating an Excel workbook.

    Parameters:
    - df_ma_res: DataFrame with MA results.
    - df_ma_trades: DataFrame with MA trades.

    Example:
    ```python
    prepare_data(df_results, df_trades)
    ```
    """
    df_ma_res.sort_values(
        by=['pair', 'total_gain'],
        ascending=[True, False],
        inplace=True)
    df_ma_trades['time'] = pd.to_datetime(df_ma_trades['time']).dt.tz_localize(None)


def process_data(df_ma_res, df_ma_trades, writer):
    """
    Process data and create an Excel workbook.

    Parameters:
    - df_ma_res: DataFrame with MA results.
    - df_ma_trades: DataFrame with MA trades.
    - writer: Excel writer object.

    Example:
    ```python
    process_data(df_results, df_trades, excel_writer)
    ```
    """
    prepare_data(df_ma_res, df_ma_trades)
    add_pair_sheets(df_ma_res, writer)
    add_pair_charts(df_ma_res, df_ma_trades, writer)

def create_excel(df_ma_res, df_ma_trades, granularity):
    """
    Create an Excel workbook with MA results and trades.

    Parameters:
    - df_ma_res: DataFrame with MA results.
    - df_ma_trades: DataFrame with MA trades.
    - granularity (str): Granularity for data processing.

    Example:
    ```python
    create_excel(df_results, df_trades, "H4")
    ```
    """
    filename = f"ma_sim_{granularity}.xlsx"
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")

    process_data(
        df_ma_res[df_ma_res.granularity == granularity].copy(),
        df_ma_trades[df_ma_trades.granularity == granularity].copy(),
        writer)

    writer.close()

if __name__ == "__main__":

    df_ma_res = pd.read_csv("./data/ma_res_2023-12-04.csv")
    df_ma_trades = pd.read_csv("./data/ma_trades_2023-12-04.csv")
    create_excel(df_ma_res, df_ma_trades, "M15")
    create_excel(df_ma_res, df_ma_trades, "M30")
    create_excel(df_ma_res, df_ma_trades, "H1")
    create_excel(df_ma_res, df_ma_trades, "H4")
