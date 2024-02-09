import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

def extract_investing_com():
    url = ("https://www.investing.com/common/technical_studies/technical_studies_data.php")
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"
    }
    params = dict(
        action='get_studies',
        pair_ID=7,
        time_frame=3600
    )
    
    resp = requests.get(url, params=params, headers=headers)
    
    print(resp.content)
    print(resp.status_code)
    
if __name__ == "__main__":
    extract_investing_com()