from scraping.class_dailyfx_com import DailyFXScraper
from scraping.class_investing_com import InvestingComScraper
from scraping.class_reuters_com import ReutersComScraper
from scraping.class_tradingeconomics_com import TradingEconomicsCalendar
from scraping.func_testing import scrape_dailyfx_data, scrape_investor_data, scrape_reuters_data, scrape_tradingeconomics_data
import time

scraping_interval = 3600
data_path = "data/scraping"

if __name__ == "__main__":
    scraper = DailyFXScraper()
    investing_scraper = InvestingComScraper()
    reuters_scraper = ReutersComScraper()
    tradingeconomics_scraper = TradingEconomicsCalendar()

    while True:
        print("Scraping data...")
        # scrape_dailyfx_data(scraper, data_path)
        # scrape_investor_data(investing_scraper, data_path)
        # scrape_reuters_data(reuters_scraper, data_path)
        # scrape_tradingeconomics_data(tradingeconomics_scraper, data_path)
        print("Done scraping data.")
        time.sleep(scraping_interval)
