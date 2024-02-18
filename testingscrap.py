from scraping.class_investing_com import InvestingComScraper

if __name__ == '__main__':
    scraper = InvestingComScraper()
    data = scraper.scrape_data()
    print(data)
    scraper2 = InvestingComScraper(pair="GBP_USD", time_frame="M5")
    data2 = scraper2.scrape_data()
    print(data2)