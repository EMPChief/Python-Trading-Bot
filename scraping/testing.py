import scrapy
import pandas as pd
from datetime import datetime
from scrapy.crawler import CrawlerProcess
class DailyFXScraper(scrapy.Spider):
    name = 'dailyfx'
    start_urls = ['https://www.dailyfx.com/sentiment']

    custom_settings = {
        'LOG_FORMAT': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        'LOG_LEVEL': 'DEBUG',
        'FEEDS': {
            'sentiment_data.csv': {
                'format': 'csv',
                'overwrite': False,
                'fields': [
                    'pair', 'sentiment', 'longs_daily',
                    'shorts_daily', 'longs_weekly', 'shorts_weekly',
                    'scraping_time'
                ],
            },
        }
    }

    def parse(self, response):
        rows = response.css('.dfx-technicalSentimentCard')

        for row in rows:
            card = row.css('.dfx-technicalSentimentCard__pairAndSignal')
            change_values = row.css('.dfx-technicalSentimentCard__changeValue')

            yield {
                'pair': card.css('a::text').get().replace("/", "_").strip(),
                'sentiment': card.css('span::text').get().strip(),
                'longs_daily': change_values[0].css('::text').get().strip(),
                'shorts_daily': change_values[1].css('::text').get().strip(),
                'longs_weekly': change_values[3].css('::text').get().strip(),
                'shorts_weekly': change_values[4].css('::text').get().strip(),
                'scraping_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def clean_dataframe(self, dataframe):
        if dataframe.columns.dtype == 'O':
            dataframe.columns = dataframe.columns.str.strip().str.replace('\n', '')
            dataframe.columns = dataframe.columns.str.lower()
            dataframe.replace({'%': ''}, regex=True, inplace=True)
        dataframe = dataframe.apply(pd.to_numeric, errors='ignore')
        return dataframe



    def parse_sentiment_data(self, response):
        dataframe = pd.DataFrame(response)
        dataframe = self.clean_dataframe(dataframe)
        return dataframe

    def closed(self, reason):
        self.log("Spider closed. Data saved to CSV file.")
        df = self.parse_sentiment_data(response=None)
        try:
            df.to_csv("/run/media/empchief/Extra/programming/Linux/github/trading-bot/sentiment_data.csv", index=False)
            self.log("CSV file saved successfully.")
        except Exception as e:
            self.log(f"Error saving CSV file: {e}")

if __name__ == "__main__":

    process = CrawlerProcess()
    process.crawl(DailyFXScraper)
    process.start()
