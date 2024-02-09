import threading
from infrastructure.log_wrapper import LogWrapper


class StreamBase(threading.Thread):

    def __init__(self, shared_prices: dict, price_lock: threading.Lock, price_events: dict, logname: str):
        super().__init__()
        self.shared_prices = shared_prices
        self.price_lock = price_lock
        self.price_events = price_events
        self.log = LogWrapper(logname)

    def log_message(self, msg: str, error: bool = False):
        if error == True:
            self.log.logger.error(msg)
        else:
            self.log.logger.debug(msg)
