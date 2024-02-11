import datetime as dt
import cloudscraper
import logging
from bs4 import BeautifulSoup as bs
import pandas as pd
from backoff import on_exception, expo


class ReutersComScraper:
    def __init__(self, url="https://www.reuters.com/business/finance"):
        self.url = url

    def _get_article(self, card):
        headline_elem = card.select_one('a[data-testid="Heading"]')
        link_elem = card.select_one('a[data-testid="Heading"]')
        if headline_elem and link_elem:
            headline = headline_elem.get_text()
            link = 'https://www.reuters.com' + link_elem.get('href')
            return {'headline': headline, 'link': link}
        else:
            logging.warning(
                "Failed to extract article. headline_elem: %s, link_elem: %s", headline_elem, link_elem)
            return None

    def _get_date(self, card):
        date_str = card.select_one('[data-testid="Label"]').get('datetime')
        return dt.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

    @on_exception(expo, Exception, max_time=60)
    def scrape_reuters(self):
        session = cloudscraper.create_scraper()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Referer": "https://www.google.com/",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Pragma": "no-cache",
        }
        response = session.get(self.url, headers=headers)
        soup = bs(response.content, "html.parser")

        articles = []
        cards = soup.select('[class^="media-story-card__body"]')
        for card in cards:
            article = self._get_article(card)
            if article:
                articles.append(article)
        return articles

    def create_dataframe(self):
        data = self.scrape_reuters()
        dataframe = pd.DataFrame(data)
        dataframe['scraping_time'] = dt.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")
        return dataframe


if __name__ == "__main__":
    scraper = ReutersComScraper()
    dataframe = scraper.create_dataframe()
    print(dataframe)
