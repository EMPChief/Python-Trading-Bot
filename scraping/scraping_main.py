from dailyfx_com import DailyFXScraper
from investing_com import InvestingComScraper
import time
import json


scraping_interval = 180
data_path = "data/scraping"

if __name__ == "__main__":
    scraper = DailyFXScraper()
    investing_scraper = InvestingComScraper()
    while True:
        print("Scraping data...")
        
        # Scraping DailyFX data
        print("Scraping DailyFX data...")
        sentiment_dataframe = scraper.extract_sentiment_data()
        print(sentiment_dataframe)
        
        # Save DailyFX data to CSV
        sentiment_dataframe.to_csv(
            f"{data_path}/dailyfx_sentiment.csv", mode='a', index=False, header=True)

        # Save DailyFX data to JSON
        data = sentiment_dataframe.to_dict(orient='records')
        with open(f"{data_path}/dailyfx_sentiment.json", "a") as f:
            json.dump(data, f, indent=4)
            f.write("\n")

        # Scraping Investor.com data
        print("Scraping Investor data...")
        investor_response = investing_scraper.scrape_all_data()
        
        # Save Investor.com data to CSV
        investor_response.to_csv(
            f"{data_path}/investor_data.csv", mode='a', index=False, header=True)

        # Save Investor.com data to JSON
        data = investor_response.to_dict(orient='records')
        with open(f"{data_path}/investor_data.json", "a") as f:
            json.dump(data, f, indent=4)
            f.write("\n")
        
        print("Done scraping data.")
        time.sleep(scraping_interval)
