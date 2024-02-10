import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime

class DailyFXScraper:
    def __init__(self, url="https://www.dailyfx.com/sentiment"):
        self.url = url

    def load_page(self):
        response = requests.get(self.url)
        soup = bs(response.content, "html.parser")
        return soup

    def extract_rows(self, soup):
        return soup.select(".dfx-technicalSentimentCard")

    def extract_pair_data(self, row):
        pair_data = []
        for rows in row:
            card = rows.select_one(".dfx-technicalSentimentCard__pairAndSignal")
            change_values = rows.select(".dfx-technicalSentimentCard__changeValue")
            pair_data.append(dict(
                pair=card.select_one("a").get_text().replace("/", "_").strip(),
                sentiment=card.select_one("span").get_text().strip(),
                longs_daily=change_values[0].get_text().strip(),
                shorts_daily=change_values[1].get_text().strip(),
                longs_weekly=change_values[3].get_text().strip(),
                shorts_weekly=change_values[4].get_text().strip(),
                scraping_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        return pair_data

    def clean_dataframe(self, dataframe):
        dataframe.columns = dataframe.columns.str.strip().str.replace('\n', '')
        dataframe.columns = dataframe.columns.str.lower()
        dataframe.replace({'%': ''}, regex=True, inplace=True)
        dataframe = dataframe.apply(pd.to_numeric, errors='ignore')
        return dataframe

    def extract_sentiment_data(self):
        soup = self.load_page()
        row = self.extract_rows(soup)
        pair_data = self.extract_pair_data(row)
        dataframe = pd.DataFrame(pair_data)
        dataframe = self.clean_dataframe(dataframe)
        return dataframe
