import json
from queue import Queue
import threading
import time
from streaming.stream_price import PriceStreamer
from streaming.stream_processor import PriceProcessor
from streaming.stream_worker import WorkProcessor


def load_settings():
    with open("./bot/settings.json", "r") as file:
        return json.loads(file.read())


def run_streaming_application():
    settings = load_settings()

    shared_prices = {}
    shared_prices_events = {}
    shared_prices_lock = threading.Lock()
    work_queue = Queue()

    for currency_pair in settings['pairs'].keys():
        shared_prices_events[currency_pair] = threading.Event()
        shared_prices[currency_pair] = {}

    threads = []

    price_streamer_thread = PriceStreamer(
        shared_prices, shared_prices_lock, shared_prices_events)
    price_streamer_thread.daemon = True
    threads.append(price_streamer_thread)
    price_streamer_thread.start()

    work_processor_thread = WorkProcessor(work_queue)
    work_processor_thread.daemon = True
    threads.append(work_processor_thread)
    work_processor_thread.start()

    for currency_pair in settings['pairs'].keys():
        processing_thread = PriceProcessor(shared_prices, shared_prices_lock, shared_prices_events,
                                           f"PriceProcessor_{currency_pair}", currency_pair, work_queue)
        processing_thread.daemon = True
        threads.append(processing_thread)
        processing_thread.start()
    #Linux and mac:
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    #windows
    """
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    print("Application terminated successfully")
    """

if __name__ == '__main__':
    run_streaming_application()
