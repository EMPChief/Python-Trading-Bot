import datetime as dt
import time
import cloudscraper
import pandas as pd
import logging
from backoff import on_exception, expo
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class InvestingComScraper:
    def __init__(self):
        self.data_keys = [
            'pair_name',
            'ti_buy',
            'ti_sell',
            'ma_buy',
            'ma_sell',
            'S1',
            'S2',
            'S3',
            'pivot',
            'R1',
            'R2',
            'R3',
            'percent_bullish',
            'percent_bearish'
        ]

    @on_exception(expo, requests.exceptions.RequestException, max_tries=3)
    def fetch_data(self, pair_id, time_frame):
        logging.info(f"Fetching data for pair_id={
                     pair_id}, time_frame={time_frame}...")
        url = "https://www.investing.com/common/technical_studies/technical_studies_data.php"
        session = cloudscraper.create_scraper()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Referer": "https://www.google.com/",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Pragma": "no-cache",
        }
        params = {
            'action': 'get_studies',
            'pair_ID': pair_id,
            'time_frame': time_frame
        }

        try:
            response = session.get(url, params=params, headers=headers)
            text = response.content.decode("utf-8")

            index_start = text.index("pair_name=")
            index_end = text.index("*;*quote_link")

            data_str = text[index_start:index_end]

            return self.process_data(data_str.split('*;*'), pair_id, time_frame)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data for pair_id={
                          pair_id}, time_frame={time_frame}: {e}")
            raise

    def process_data(self, text_list, pair_id, time_frame):
        logging.info(f"Processing data for pair_id={
                     pair_id}, time_frame={time_frame}...")
        data = {}
        data['pair_id'] = pair_id
        data['time_frame'] = time_frame
        data['updated'] = dt.datetime.utcnow()

        for item in text_list:
            temp_item = item.split("=")
            if len(temp_item) == 2 and temp_item[0] in self.data_keys:
                data[temp_item[0]] = temp_item[1]

        if 'pair_name' in data:
            data['pair_name'] = data['pair_name'].replace("/", "_")

        return data

    def scrape_all_data(self):
        data = []
        for pair_id in range(1, 17):
            for time_frame in [3600, 86400]:
                logging.info(f"Scraping data for pair_id={
                             pair_id}, time_frame={time_frame}...")
                fetched_data = self.fetch_data(pair_id, time_frame)
                if fetched_data:
                    data.append(fetched_data)
                time.sleep(0.5)

        dataframe = pd.DataFrame(data)
        dataframe['updated'] = dataframe['updated'].astype(str)
        numeric_columns = ['ti_buy', 'ti_sell', 'ma_buy',
                           'ma_sell', 'S1', 'S2', 'S3', 'pivot', 'R1', 'R2', 'R3']
        dataframe[numeric_columns] = dataframe[numeric_columns].apply(
            pd.to_numeric, errors='coerce')

        return dataframe
