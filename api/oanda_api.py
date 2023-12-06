import requests
import constants.defs as defs
import pandas as pd
from dateutil import parser
from datetime import datetime as dt


class OandaApi:
    """
    A simple wrapper class for making requests to the Oanda API.

    Attributes:
        session (requests.Session): A session object for making HTTP requests.
    """

    def __init__(self):
        """
        Initializes the OandaApi object.

        This constructor sets up the session with the required headers for making API requests.
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {defs.API_KEY}'
        })

    def make_request(self, url, verb='get', code=200, params=None, data=None, headers=None):
        """
        Makes an HTTP request to the specified URL using the provided parameters.

        Args:
            url (str): The API endpoint to make the request to.
            verb (str, optional): The HTTP verb for the request (default is 'get').
            code (int, optional): The expected HTTP status code for a successful response (default is 200).
            params (dict, optional): The query parameters for the request (default is None).
            data (dict, optional): The request payload data (default is None).
            headers (dict, optional): Additional headers for the request (default is None).

        Returns:
            tuple: A tuple containing a boolean indicating success and the response data in JSON format.
        """
        full_url = f'{defs.OANDA_URL}{url}'
        try:
            response = None
            if verb == 'get':
                response = self.session.get(
                    full_url, params=params, data=data, headers=headers)
            if response is None:
                return False, {'error': 'verb not found'}
            if response.status_code == code:
                return True, response.json()
            else:
                return False, response.json()
        except Exception as e:
            return False, {'error': str(e)}

    def get_account_ep(self, ep, data_key):
        """
        Retrieves specific data from the Oanda API for the account.

        Args:
            ep (str): The API endpoint for the specific data.
            data_key (str): The key in the API response containing the desired data.

        Returns:
            dict or None: The requested data if successful, otherwise None.
        """
        url = f"accounts/{defs.ACCOUNT_ID}/{ep}"
        ok, data = self.make_request(url)
        if ok == True and data_key in data:
            return data[data_key]
        else:
            print("ERROR get_account_ep", data)
            return None

    def get_account_summary(self):
        """
        Retrieves the summary data for the account.

        Returns:
            dict or None: The account summary data if successful, otherwise None.
        """
        return self.get_account_ep("summary", "account")

    def get_account_instruments(self):
        """
        Retrieves the list of instruments for the account.

        Returns:
            dict or None: The list of instruments if successful, otherwise None.
        """
        return self.get_account_ep("instruments", "instruments")

    def fetch_candles(self, pair_name, count=10, granularity="H1",
                      price="MBA", date_f=None, date_t=None):
        url = f"instruments/{pair_name}/candles"
        params = dict(
            granularity=granularity,
            price=price
        )

        if date_f is not None and date_t is not None:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params["from"] = dt.strftime(date_f, date_format)
            params["to"] = dt.strftime(date_t, date_format)
        else:
            params["count"] = count

        ok, data = self.make_request(url, params=params)

        if ok == True and 'candles' in data:
            return data['candles']
        else:
            print("ERROR fetch_candles()", params, data)
            return None

    def get_candles_df(self, pair_name, **kwargs):

        data = self.fetch_candles(pair_name, **kwargs)

        if data is None:
            return None
        if len(data) == 0:
            return pd.DataFrame()

        prices = ['mid', 'bid', 'ask']
        ohlc = ['o', 'h', 'l', 'c']

        final_data = []
        for candle in data:
            if candle['complete'] == False:
                continue
            new_dict = {}
            new_dict['time'] = parser.parse(candle['time'])
            new_dict['volume'] = candle['volume']
            for p in prices:
                if p in candle:
                    for o in ohlc:
                        new_dict[f"{p}_{o}"] = float(candle[p][o])
            final_data.append(new_dict)
        df = pd.DataFrame.from_dict(final_data)
        return df
