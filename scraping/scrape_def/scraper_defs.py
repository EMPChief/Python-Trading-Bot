import json
import pandas as pd
import time


def scrape_dailyfx_data(scraper, data_path):
    print("Scraping DailyFX data...")
    sentiment_dataframe = scraper.extract_sentiment_data()
    print(sentiment_dataframe)
    sentiment_dataframe.to_csv(
        f"{data_path}/dailyfx_sentiment.csv", mode='a', index=False, header=False)
    data = sentiment_dataframe.to_dict(orient='records')
    with open(f"{data_path}/dailyfx_sentiment.json", "a") as f:
        json.dump(data, f, indent=4)
        f.write("\n")


def scrape_investor_data(investing_scraper, data_path):
    print("Scraping investing.com data...")
    investor_response = investing_scraper.scrape_all_data()
    investor_response.to_csv(
        f"{data_path}/investing_data.csv", mode='a', index=False, header=False)
    data = investor_response.to_dict(orient='records')
    with open(f"{data_path}/investing_data.json", "a") as f:
        json.dump(data, f, indent=4)
        f.write("\n")


def scrape_reuters_data(reuters_scraper, data_path):
    print("Scraping Reuters data...")
    reuters_response = reuters_scraper.create_dataframe()
    reuters_response.to_csv(
        f"{data_path}/reuters_data.csv", mode='a', index=False, header=False)
    data = reuters_response.to_dict(orient='records')
    with open(f"{data_path}/reuters_data.json", "a") as f:
        json.dump(data, f, indent=4)
        f.write("\n")


def scrape_tradingeconomics_data(tradingeconomics_scraper, data_path):
    print("Scraping tradingeconomics.com data...")
    tradingeconomics_response = tradingeconomics_scraper.create_dataframe()
    tradingeconomics_response['date'] = tradingeconomics_response['date'].apply(
        lambda x: x.strftime("%Y-%m-%d"))
    tradingeconomics_response.to_csv(
        f"{data_path}/tradingeconomics_data.csv", mode='a', index=False, header=False)
    data = tradingeconomics_response.to_dict(orient='records')
    with open(f"{data_path}/tradingeconomics_data.json", "a") as f:
        json.dump(data, f, indent=4)
        f.write("\n")
