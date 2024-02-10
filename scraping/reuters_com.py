import datetime as dt
import time
import cloudscraper
import pandas as pd
import logging
from backoff import on_exception, expo
import requests
url = "https://www.reuters.com/business/finance"

def load_reuters():
    