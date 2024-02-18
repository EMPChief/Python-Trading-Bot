import requests
import pandas as pd
import json
import constants.defs as defs
from infrastructure.log_wrapper import LogWrapper
from dateutil import parser
from datetime import datetime as dt
from infrastructure.instrument_collection import instrumentCollection as InstrumentCollection
from models.api_price import ApiPrice
from models.open_trade import OpenTrade


class OandaApi:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(defs.SECURE_HEADER)
        self.log = LogWrapper("OandaApi")

    def make_request(self, url, verb='get', expected_status=200, params=None, data=None, headers=None):
        full_url = f"{defs.OANDA_URL}/{url}"

        if data is not None:
            data = json.dumps(data)

        try:
            self.log.logger.debug(f"{full_url} {verb} {params} {data}")
            response = None
            if verb == "get":
                response = self.session.get(
                    full_url, params=params, data=data, headers=headers)
            elif verb == "post":
                response = self.session.post(
                    full_url, params=params, data=data, headers=headers)
            elif verb == "put":
                response = self.session.put(
                    full_url, params=params, data=data, headers=headers)

            self.log.logger.debug(f"response:{response.status_code}")
            if response is None:
                return False, {'error': 'verb not found'}

            if response.status_code == expected_status:
                return True, response.json()
            else:
                return False, response.json()

        except Exception as error:
            return False, {'Exception': error}

    def get_account_endpoint(self, endpoint, data_key):
        url = f"accounts/{defs.ACCOUNT_ID}/{endpoint}"
        ok, data = self.make_request(url)

        if ok and data_key in data:
            return data[data_key]
        else:
            print("ERROR get_account_endpoint()", data)
            return None

    def get_account_summary(self):
        return self.get_account_endpoint("summary", "account")

    def get_account_instruments(self):
        return self.get_account_endpoint("instruments", "instruments")

    def fetch_candles(self, pair_name, count=10, granularity="H1", price="MBA", date_from=None, date_to=None):
        url = f"instruments/{pair_name}/candles"
        params = dict(
            granularity=granularity,
            price=price
        )

        if date_from is not None and date_to is not None:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params["from"] = dt.strftime(date_from, date_format)
            params["to"] = dt.strftime(date_to, date_format)
        else:
            params["count"] = count

        ok, data = self.make_request(url, params=params)

        if ok and 'candles' in data:
            return data['candles']
        else:
            print("ERROR fetch_candles()", params, data)
            return None

    def get_candles_dataframe(self, pair_name, **kwargs):
        data = self.fetch_candles(pair_name, **kwargs)

        if data is None:
            return None
        if not data:
            return pd.DataFrame()

        prices = ['mid', 'bid', 'ask']
        ohlc = ['o', 'h', 'l', 'c']

        final_data = []
        for candle in data:
            if candle['complete'] is False:
                continue
            new_dict = {}
            new_dict['time'] = parser.parse(candle['time'])
            new_dict['volume'] = candle['volume']
            for p in prices:
                if p in candle:
                    for o in ohlc:
                        new_dict[f"{p}_{o}"] = float(candle[p][o])
            final_data.append(new_dict)
        dataframe = pd.DataFrame.from_dict(final_data)
        return dataframe

    def last_complete_candle(self, pair_name, granularity):
        dataframe = self.get_candles_dataframe(
            pair_name, granularity=granularity, count=10)
        if dataframe.shape[0] == 0:
            return None
        return dataframe.iloc[-1].time

    def web_api_candles(self, pair_name, granularity, count):
        dataframe = self.get_candles_dataframe(
            pair_name, granularity=granularity, count=count)
        if dataframe.shape[0] == 0:
            return None

        cols = ['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c']
        dataframe = dataframe[cols].copy()

        dataframe['time'] = dataframe.time.dt.strftime("%y-%m-%d %H:%M")

        return dataframe.to_dict(orient='list')

    def place_trade(self, pair_name: str, units: float, direction: int,
                    stop_loss: float = None, take_profit: float = None):

        url = f"accounts/{defs.ACCOUNT_ID}/orders"

        instrument = InstrumentCollection.instruments_dict[pair_name]
        units = round(units, instrument.tradeUnitsPrecision)

        if direction == defs.SELL:
            units *= -1

        data = dict(
            order=dict(
                units=str(units),
                instrument=pair_name,
                type="MARKET"
            )
        )

        if stop_loss is not None:
            sld = dict(price=str(round(stop_loss, instrument.displayPrecision)))
            data['order']['stopLossOnFill'] = sld

        if take_profit is not None:
            tpd = dict(
                price=str(round(take_profit, instrument.displayPrecision)))
            data['order']['takeProfitOnFill'] = tpd

        ok, response = self.make_request(
            url, verb="post", data=data, expected_status=201)

        if ok and 'orderFillTransaction' in response:
            return response['orderFillTransaction']['id']
        else:
            return None

    def close_trade(self, trade_id):
        url = f"accounts/{defs.ACCOUNT_ID}/trades/{trade_id}/close"
        ok, _ = self.make_request(url, verb="put", expected_status=200)

        if ok:
            print(f"Closed {trade_id} successfully")
        else:
            print(f"Failed to close {trade_id}")

        return ok

    def get_open_trade(self, trade_id):
        url = f"accounts/{defs.ACCOUNT_ID}/trades/{trade_id}"
        ok, response = self.make_request(url)

        if ok and 'trade' in response:
            return OpenTrade(response['trade'])

    def get_open_trades(self):
        url = f"accounts/{defs.ACCOUNT_ID}/openTrades"
        ok, response = self.make_request(url)

        if ok and 'trades' in response:
            return [OpenTrade(x) for x in response['trades']]

    def get_prices(self, instruments_list):
        url = f"accounts/{defs.ACCOUNT_ID}/pricing"

        params = dict(
            instruments=','.join(instruments_list),
            includeHomeConversions=True
        )

        ok, response = self.make_request(url, params=params)

        if ok and 'prices' in response and 'homeConversions' in response:
            return [ApiPrice(x, response['homeConversions']) for x in response['prices']]

        return None
