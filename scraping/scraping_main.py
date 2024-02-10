from dailyfx_com import DailyFXScraper
from investing_com import InvestingComScraper
import time
import json
scraping_interval = 3600
data_path = "data/scraping"
if __name__ == "__main__":
#    scraper = DailyFXScraper()
    while True:
        print("Scraping data...")
#        print("Scraping DailyFX data...")
#        sentiment_dataframe = scraper.extract_sentiment_data()
#        print(sentiment_dataframe)
#        sentiment_dataframe.to_csv("data/scraping/dailyfx_sentiment.csv", mode='a', index=False, header=False)
#        time.sleep(scraping_interval)
#    scraper = DailyFXScraper()
#    while True:
#        sentiment_dataframe = scraper.extract_sentiment_data()
#        data = sentiment_dataframe.to_dict(orient='records')
#        with open("data/scraping/dailyfx_sentiment.json", "a") as f:
#            json.dump(data, f, indent=4)
#            f.write("\n")
        print("Scraping Investor data...")
        investing_scraper = InvestingComScraper()
        investor_response = investing_scraper.scrape_all_data()
        investor_response.to_csv(f"{data_path}/investor_data.csv", mode='a', index=False, header=False)
        data = investor_response.to_dict(orient='records')
        with open(f"{data_path}/investor_data.json", "a") as f:
            json.dump(data, f, indent=4)
            f.write("\n")
        print("Done scraping data.")
        time.sleep(scraping_interval)