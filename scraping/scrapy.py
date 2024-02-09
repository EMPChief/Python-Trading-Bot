from scraping.dailyfx_com import DailyFXScraper



if __name__ == "__main__":
    scraper = DailyFXScraper()
    sentiment_dataframe = scraper.extract_sentiment_data()
    print(sentiment_dataframe)
