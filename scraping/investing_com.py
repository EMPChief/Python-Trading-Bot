
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import datetime as dt
import time
import cloudscraper

data_keys = [
    'pair_name', 
    'last_value', 
    'current_direction',
    'pair_updatetime',
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
    'change_percent',
    'percent_bullish', 
    'percent_bearish'
]

def get_data_object(text_list, pair_id, time_frame):
    data = {}
    data['pair_id'] = pair_id
    data['time_frame'] = time_frame
    data['updated'] = dt.datetime.utcnow()

    for item in text_list:
        temp_item = item.split("=")
        if len(temp_item) == 2 and temp_item[0] in data_keys:
            data[temp_item[0]] = temp_item[1]

    if 'pair_name' in data:
        data['pair_name'] = data['pair_name'].replace("/", "_")

    return data


def scrape_investing_com(pair_id, time_frame):
    url = "https://www.investing.com/common/technical_studies/technical_studies_data.php"
    session = cloudscraper.create_scraper()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Referer": "https://www.google.com/",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Pragma": "no-cache",
    }
    params = dict(
        action='get_studies',
        pair_ID=pair_id,
        time_frame=time_frame
    )

    response = session.get(url, params=params, headers=headers)
    text = response.content.decode("utf-8")

    index_start = text.index("pair_name=")
    index_end = text.index("*;*quote_link")

    data_str = text[index_start:index_end]

    return get_data_object(data_str.split('*;*'), pair_id, time_frame)


if __name__ == "__main__":
    pair_id = 1
    time_frame = 3600
    response = scrape_investing_com(pair_id, time_frame)
    print(response)
