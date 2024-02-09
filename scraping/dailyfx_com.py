import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

class DailyFXScraper:
    def __init__(self, url="https://www.dailyfx.com/sentiment"):
        self.url = url

    def load_page(self):
        resp = requests.get(self.url)
        soup = bs(resp.content, "html.parser")
        return soup

    def extract_sentiment_data(self):
        soup = self.load_page()
        rows = self.extract_rows(soup)
        pair_data = self.extract_pair_data(rows)
        dataframe = pd.DataFrame(pair_data)
        dataframe = self.clean_dataframe(dataframe)
        return dataframe

    def extract_rows(self, soup):
        return soup.select(".dfx-technicalSentimentCard")

    def extract_pair_data(self, rows):
        pair_data = []
        for row in rows:
            card = row.select_one(".dfx-technicalSentimentCard__pairAndSignal")
            change_values = row.select(".dfx-technicalSentimentCard__changeValue")
            pair_data.append(dict(
                pair=card.select_one("a").get_text().replace("/", "_").strip(),
                sentiment=card.select_one("span").get_text().strip(),
                longs_daily=change_values[0].get_text().strip(),
                shorts_daily=change_values[1].get_text().strip(),
                longs_weekly=change_values[3].get_text().strip(),
                shorts_weekly=change_values[4].get_text().strip()
            ))
        return pair_data

    def clean_dataframe(self, dataframe):
        dataframe.columns = dataframe.columns.str.strip().str.replace('\n', '')
        dataframe.columns = dataframe.columns.str.lower()
        dataframe.replace({'%': ''}, regex=True, inplace=True)
        dataframe = dataframe.apply(pd.to_numeric, errors='ignore')
        return dataframe