import datetime as dt
import cloudscraper
from bs4 import BeautifulSoup as bs
import dateutil.parser as parser
import pytz
import pandas as pd

pd.set_option("display.max_rows", None)


def get_header_date(thead):
    ths = thead.select("th")
    for th in ths:
        if th.has_attr("colspan"):
            date_text = th.get_text().strip()
            return parser.parse(date_text)
    return None

def fetch_calendar(from_date):
    session = cloudscraper.create_scraper()
    
    norway_tz = pytz.timezone('Europe/Oslo')
    from_date_norway = from_date.astimezone(norway_tz)
    from_date_str = dt.datetime.strftime(from_date_norway, "%Y-%m-%d 00:00:00")
    to_date_norway = from_date_norway + dt.timedelta(days=6)
    to_date_str = dt.datetime.strftime(to_date_norway, "%Y-%m-%d 00:00:00")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Cookie": f"calendar-importance=3; cal-custom-range={from_date_str}|{to_date_str}; TEServer=TEIIS3; cal-timezone-offset=0;",
        "Referer": "https://www.google.com/",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Pragma": "no-cache",
    }

    response = session.get("https://tradingeconomics.com/calendar", headers=headers)
    return response

def soupify_calendar(response_content):
    soup = bs(response_content, "html.parser")
    return soup

def select_calendar_table(soup):
    return soup.select_one("table#calendar")

def extract_data_from_headers(select_td):
    last_header_date = None
    header_data = {}

    for c in select_td.children:
        if c.name == 'thead':
            if 'class' in c.attrs and 'hidden-head' in c.attrs['class']:
                continue
            last_header_date = get_header_date(c)
            if last_header_date:
                header_data[last_header_date] = []
        elif c.name == "tr":
            if last_header_date:
                header_data[last_header_date].append(c)

    return header_data
                
if __name__ == "__main__":
    from_date = parser.parse("2023-04-11 00:00:00").replace(tzinfo=pytz.utc)
    calendar_response = fetch_calendar(from_date)
    soup = soupify_calendar(calendar_response.content)
    select_td = select_calendar_table(soup)
    header_data = extract_data_from_headers(select_td)
    print(header_data)
