from dailyfx_com import DailyFXScraper
import time
import json
scraping_interval = 3600

if __name__ == "__main__":
#    scraper = DailyFXScraper()
#    while True:
#        sentiment_dataframe = scraper.extract_sentiment_data()
#        print(sentiment_dataframe)
#        sentiment_dataframe.to_csv("data/scraping/dailyfx_sentiment.csv", mode='a', index=False, header=False)
#        time.sleep(scraping_interval)
    scraper = DailyFXScraper()
    while True:
        sentiment_dataframe = scraper.extract_sentiment_data()
        data = sentiment_dataframe.to_dict(orient='records')
        with open("data/scraping/dailyfx_sentiment.json", "a") as f:
            json.dump(data, f, indent=4)
            f.write("\n")
        time.sleep(scraping_interval)
