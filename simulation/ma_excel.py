import pandas as pd
import os


class MAExcel:
    def __init__(self, df_ma_res, df_ma_trades, granularity):
        self.df_ma_res = df_ma_res
        self.df_ma_trades = df_ma_trades
        self.granularity = granularity

    def set_widths(self, pair, writer):
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
        for k, v in self.WIDTHS.items():
            worksheet.set_column(k, v)

    def get_line_chart(self, book, start_row, end_row, labels_col, data_col, title, sheetname):
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

    def add_chart(self, pair, cross, df, writer):
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

        chart = self.get_line_chart(workbook, 1, df.shape[0], 11, 12,
                                    f"GAIN_C for {pair} {cross}", pair)
        chart.set_size({'x_scale': 2.5, 'y_scale': 2.5})
        worksheet.insert_chart('O1', chart)

    def add_pair_charts(self, writer):
        """
        Add line charts for each trading pair to an Excel workbook.

        Parameters:
        - writer: Excel writer object.

        Example:
        ```python
        add_pair_charts(excel_writer)
        ```
        """
        cols = ['time', 'GAIN_C']
        df_temp = self.df_ma_res.drop_duplicates(subset="pair")

        for _, row in df_temp.iterrows():
            dft = self.df_ma_trades[(self.df_ma_trades.cross == row.cross) &
                                    (self.df_ma_trades.pair == row.pair)]
            dft[cols].to_excel(writer, sheet_name=row.pair,
                               index=False, startrow=0, startcol=11)
            self.set_widths(row.pair, writer)
            self.add_chart(row.pair, row.cross, dft, writer)

    def add_pair_sheets(self, writer):
        """
        Add worksheets for each trading pair to an Excel workbook.

        Parameters:
        - writer: Excel writer object.

        Example:
        ```python
        add_pair_sheets(excel_writer)
        ```
        """
        for p in self.df_ma_res.pair.unique():
            tdf = self.df_ma_res[self.df_ma_res.pair == p]
            tdf.to_excel(writer, sheet_name=p, index=False)

    def prepare_data(self):
        """
        Prepare dataframes for creating an Excel workbook.

        Example:
        ```python
        prepare_data()
        ```
        """
        self.df_ma_res.sort_values(
            by=['pair', 'total_gain'],
            ascending=[True, False],
            inplace=True)
        self.df_ma_trades['time'] = pd.to_datetime(
            self.df_ma_trades['time']).dt.tz_localize(None)

    def process_data(self, writer):
        """
        Process data and create an Excel workbook.

        Parameters:
        - writer: Excel writer object.

        Example:
        ```python
        process_data(excel_writer)
        ```
        """
        self.prepare_data()
        self.add_pair_sheets(writer)
        self.add_pair_charts(writer)

    def create_excel(self):
        """
        Create an Excel workbook with MA results and trades.

        Example:
        ```python
        create_excel()
        """
        excel_directory = "./data/excel/"

        os.makedirs(excel_directory, exist_ok=True)

        filename = f"{excel_directory}ma_sim_{self.granularity}.xlsx"

        writer = pd.ExcelWriter(filename, engine="xlsxwriter")

        self.process_data(writer)

        writer.close()


if __name__ == "__main__":
    df_ma_res = pd.read_csv("./data/result/ma_res_2023-12-08.csv")
    df_ma_trades = pd.read_csv("./data/result/ma_trades_2023-12-08.csv")

    ma_excel = MAExcel(df_ma_res, df_ma_trades, "M15")
    ma_excel.create_excel()

    ma_excel = MAExcel(df_ma_res, df_ma_trades, "M30")
    ma_excel.create_excel()

    ma_excel = MAExcel(df_ma_res, df_ma_trades, "H1")
    ma_excel.create_excel()

    ma_excel = MAExcel(df_ma_res, df_ma_trades, "H4")
    ma_excel.create_excel()
