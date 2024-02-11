from bs4 import BeautifulSoup
import pandas as pd
import requests
from dateutil import parser
import time
import datetime as dt
from backoff import on_exception, expo

class TradingEconomicsCalendar:
    def __init__(self, url="https://tradingeconomics.com/calendar", from_date_str="2020-01-01T00:00:00Z", to_date_str="2023-01-01T00:00:00Z"):
        self.url = url
        self.from_date = parser.parse(from_date_str)
        self.to_date = parser.parse(to_date_str)
        self.session = requests.Session()
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
            "Referer": "https://www.google.com/",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Pragma": "no-cache",
        }

    def extract_date_from_header(self, header):
        tr = header.select_one("tr")
        ths = tr.select("th")
        for th in ths:
            if th.has_attr("colspan"):
                date_text = th.get_text().strip()
                return parser.parse(date_text)
        return None

    def extract_data_point(self, key, element):
        for e in ['span', 'a']:
            data_element = element.select_one(f"{e}#{key}")
            if data_element is not None:
                return data_element.get_text()
        return ''

    def extract_data_for_key(self, row, key):
        return row.attrs.get(key, '')

    def extract_data_dict(self, item_date, table_rows):
        data = []

        for row in table_rows:
            data.append({
                'date': item_date,
                'country': self.extract_data_for_key(row, 'data-country'),
                'category': self.extract_data_for_key(row, 'data-category'),
                'event': self.extract_data_for_key(row, 'data-event'),
                'symbol': self.extract_data_for_key(row, 'data-symbol'),
                'actual': self.extract_data_point('actual', row),
                'previous': self.extract_data_point('previous', row),
                'forecast': self.extract_data_point('forecast', row)
            })

        return data

    @on_exception(expo, requests.exceptions.RequestException, max_tries=3)
    def fetch_calendar_data(self, start_date):
        final_data = []
        while start_date < self.to_date:
            formatted_start_date = dt.datetime.strftime(start_date, "%Y-%m-%d 00:00:00")
            end_date = start_date + dt.timedelta(days=6)
            formatted_end_date = dt.datetime.strftime(end_date, "%Y-%m-%d 00:00:00")

            headers = dict(self.default_headers)
            headers.update({
                "Cookie": f"calendar-importance=3; cal-custom-range={formatted_start_date}|{formatted_end_date}; TEServer=TEIIS3; cal-timezone-offset=0;"
            })

            response = self.session.get(self.url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.select_one("table#calendar")

            last_header_date = None
            rows_by_date = {}
            for child in table.children:
                if child.name == 'thead':
                    if 'class' in child.attrs and 'hidden-head' in child.attrs['class']:
                        continue
                    last_header_date = self.extract_date_from_header(child)
                    rows_by_date[last_header_date] = []
                elif child.name == "tr":
                    rows_by_date[last_header_date].append(child)

            for item_date, table_rows in rows_by_date.items():
                final_data += self.extract_data_dict(item_date, table_rows)

            start_date += dt.timedelta(days=7)
            time.sleep(3)

        return final_data

    def create_dataframe(self):
        data = self.fetch_calendar_data(self.from_date)
        return pd.DataFrame(data)

    def get_fx_calendar(self):
        return self.create_dataframe()


if __name__ == "__main__":
    calendar = TradingEconomicsCalendar()
    print(calendar.get_fx_calendar())
