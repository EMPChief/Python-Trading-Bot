import json
import pandas as pd
def scrape_dailyfx_data(scraper, data_path):
    print("Scraping DailyFX data...")
    sentiment_dataframe = scraper.extract_sentiment_data()
    print(sentiment_dataframe)
    sentiment_dataframe.to_csv(
        f"{data_path}/dailyfx_sentiment.csv", mode='a', index=False, header=True)
    data = sentiment_dataframe.to_dict(orient='records')
    with open(f"{data_path}/dailyfx_sentiment.json", "a") as f:
        json.dump(data, f, indent=4)
        f.write("\n")

def scrape_investor_data(investing_scraper, data_path):
    print("Scraping investing.com data...")
    investor_response = investing_scraper.scrape_all_data()
    investor_response.to_csv(
        f"{data_path}/investing_data.csv", mode='a', index=False, header=True)
    data = investor_response.to_dict(orient='records')
    with open(f"{data_path}/investing_data.json", "a") as f:
        json.dump(data, f, indent=4)
        f.write("\n")
