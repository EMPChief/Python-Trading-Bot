import json
import time
from pathlib import Path
from bot.candle_manager import CandleManager
from bot.technicals_manager import get_trade_decision
from bot.trade_manager import place_trade
from infrastructure.log_wrapper import LogWrapper
from models.trade_settings import TradeSettings
from api.oanda_api import OandaApi
import constants.defs as defs
import logging


class Bot:

    ERROR_LOG = "error"
    MAIN_LOG = "main"
    GRANULARITY = "M1"
    SLEEP = 10

    def __init__(self, api: OandaApi = None):
        self.api = api if api else OandaApi()
        self.load_settings()
        self.setup_logs()
        self.candle_manager = CandleManager(
            self.api, self.trade_settings, self.log_message, Bot.GRANULARITY)
        self.log_to_main("Bot started")
        self.log_to_error("Bot started")

    def load_settings(self):
        try:
            settings_path = Path(__file__).parent / "settings.json"
            with settings_path.open() as f:
                data = json.load(f)
            self.trade_settings = {k: TradeSettings(
                v, k) for k, v in data['pairs'].items()}
            self.trade_risk = data['trade_risk']
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
            raise

    def setup_logs(self):
        self.logs = {k: LogWrapper(k) for k in self.trade_settings.keys()}
        for k in self.trade_settings:
            self.log_message(f"{self.trade_settings[k]}", k)
        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG)
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)

    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self, msg):
        self.log_message(msg, Bot.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)

    def process_candles(self, triggered):
        if triggered:
            self.log_message(
                f"process_candles triggered:{triggered}", Bot.MAIN_LOG)
            for p in triggered:
                last_time = self.candle_manager.timings[p].last_time
                try:
                    trade_decision = get_trade_decision(
                        last_time, p, Bot.GRANULARITY, self.api, self.trade_settings[p], self.log_message)
                    if trade_decision and trade_decision.signal != defs.NONE:
                        self.log_message(f"Place Trade: {trade_decision}", p)
                        self.log_to_main(f"Place Trade: {trade_decision}")
                        place_trade(
                            trade_decision, self.api, self.log_message, self.log_to_error, self.trade_risk)
                except Exception as e:
                    self.log_to_error(f"Error in process_candles for {p}: {e}")

    def run(self):
        while True:
            time.sleep(Bot.SLEEP)
            try:
                self.process_candles(self.candle_manager.update_timings())
            except Exception as error:
                self.log_to_error(f"Error in run loop: {error}")
