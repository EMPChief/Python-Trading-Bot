import pandas as pd
import os


class ExcelStrategy:
    def __init__(self, df_res, df_trades, granularity):
        self.df_res = df_res
        self.df_trades = df_trades
        self.granularity = granularity

    ...

    def prepare_data(self):
        """
        Prepare dataframes for creating an Excel workbook.

        Example:
        ```python
        prepare_data()
        ```
        """
        self.df_res.sort_values(
            by=['pair', 'total_gain'],
            ascending=[True, False],
            inplace=True)
        self.df_trades['time'] = pd.to_datetime(
            self.df_trades['time']).dt.tz_localize(None)

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
        Create an Excel workbook with strategy results and trades.

        Example:
        ```python
        create_excel()
        """
        excel_directory = "./data/excel/"

        os.makedirs(excel_directory, exist_ok=True)

        filename = f"{excel_directory}strategy_sim_{self.granularity}.xlsx"

        writer = pd.ExcelWriter(filename, engine="xlsxwriter")

        self.process_data(writer)

        writer.close()
