import copy
from queue import Queue
import random
import threading
import time
from streaming.stream_base import StreamBase

class PriceProcessor(StreamBase):

    def __init__(self, shared_prices, price_lock: threading.Lock, price_events, log_name, pair, work_queue: Queue):
        super().__init__(shared_prices, price_lock, price_events, log_name)
        self.pair = pair
        self.work_queue = work_queue

    def process_price(self):
        price_snapshot = None

        try:
            self.price_lock.acquire()
            price_snapshot = copy.deepcopy(self.shared_prices[self.pair])
        except Exception as error:
            self.log_message(f"CRASH: {error}", error=True)
        finally:
            self.price_lock.release()

        if price_snapshot is None:
            self.log_message("NO PRICE", error=True)
        else:
            self.log_message(f"Found price: {price_snapshot}")
            time.sleep(random.randint(2, 5))
            self.log_message(f"Done processing price: {price_snapshot}")
            if random.randint(0, 5) == 3:
                self.log_message(f"Adding work: {price_snapshot}")
                self.work_queue.put(price_snapshot)

    def run(self):
        while True:
            self.price_events[self.pair].wait()
            self.process_price()
            self.price_events[self.pair].clear()
