from scraping.scrape_class.dailyfx_com import DailyFXScraper
from scraping.scrape_class.investing_com import InvestingComScraper
from scraping.scrape_class.reuters_com import ReutersComScraper
from scraping.scrape_class.tradingeconomics_com import TradingEconomicsCalendar
from scraping.scrape_def.scraper_defs import scrape_dailyfx_data, scrape_investor_data, scrape_reuters_data, scrape_tradingeconomics_data
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
        scrape_tradingeconomics_data(tradingeconomics_scraper, data_path)
        print("Done scraping data.")
        time.sleep(scraping_interval)
