import json
import threading
import requests
import pandas as pd
from timeit import default_timer as timer

import constants.defs as defs
from infrastructure.log_wrapper import LogWrapper
from models.live_api_price import LiveApiPrice
from streaming.stream_base import StreamBase

STREAM_URL = f"https://stream-fxpractice.oanda.com/v3"


class PriceStreamer(StreamBase):

    LOG_FREQUENCY_SECONDS = 60

    def __init__(self, shared_prices, price_lock: threading.Lock, price_events):
        super().__init__(shared_prices, price_lock, price_events, "PriceStreamer")
        self.currency_pairs = shared_prices.keys()
        print(self.currency_pairs)

    def fire_new_price_event(self, instrument):
        if not self.price_events[instrument].is_set():
            self.price_events[instrument].set()

    def update_live_price(self, live_price: LiveApiPrice):
        try:
            self.price_lock.acquire()
            self.shared_prices[live_price.instrument] = live_price
            self.fire_new_price_event(live_price.instrument)
        except Exception as error:
            self.log_message(f"Exception: {error}", error)
        finally:
            self.price_lock.release()

    def log_data(self):
        self.log_message("")
        data_frame = pd.DataFrame.from_dict(
            [v.get_dict() for _, v in self.shared_prices.items()])
        self.log_message(f"\n{data_frame}")

    def run(self):
        start_time = timer() - PriceStreamer.LOG_FREQUENCY_SECONDS + 10

        params = dict(
            instruments=','.join(self.currency_pairs)
        )

        url = f"{STREAM_URL}/accounts/{defs.ACCOUNT_ID}/pricing/stream"

        resp = requests.get(url, params=params,
                            headers=defs.SECURE_HEADER, stream=True)

        for price in resp.iter_lines():
            if price:
                decoded_price = json.loads(price.decode('utf-8'))
                if 'type' in decoded_price and decoded_price['type'] == 'PRICE':
                    live_price = LiveApiPrice(decoded_price)
                    self.update_live_price(live_price)
                    if timer() - start_time > PriceStreamer.LOG_FREQUENCY_SECONDS:
                        print(live_price.get_dict())
                        self.log_data()
                        start_time = timer()
