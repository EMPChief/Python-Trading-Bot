import requests
import pandas as pd
import json
API_KEY = "a2faf0838c2aacce44be67cea8b40c06-48d69bac26199a4d5850294881134c34"
ACCOUNT_ID = "101-004-21509763-001"
OANDA_URL = "https://www.api-fxpractice.com/v3"
session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
})
