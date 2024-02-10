from dailyfx_com import DailyFXScraper
import time
import pandas as pd

scraping_interval = 3600

if __name__ == "__main__":
    scraper = DailyFXScraper()
    while True:
        sentiment_dataframe = scraper.extract_sentiment_data()
        print(sentiment_dataframe)
        sentiment_dataframe.to_csv("data/scraping/sentiment.csv", mode='a', index=False, header=False)
        time.sleep(scraping_interval)
