import json
import time
from pathlib import Path  # Add this import
from bot.candle_manager import CandleManager
from bot.technicals_manager import get_trade_decision
from bot.trade_manager import place_trade, trade_is_open
from infrastructure.log_wrapper import LogWrapper
from models.trade_settings import TradeSettings
from api.oanda_api import OandaApi
import constants.defs as defs


class Bot:
    ERROR_LOG = "error"
    MAIN_LOG = "main"
    GRANULARITY = "M5"
    SLEEP = 10

    def __init__(self):
        self.load_settings()
        self.setup_logs()

        self.api = OandaApi()
        self.candle_manager = CandleManager(
            self.api, self.trade_settings, self.log_message, Bot.GRANULARITY)

        self.log_to_main("Bot started")
        self.log_to_error("Bot started")

        def load_settings(self):
            settings_path = Path(__file__).resolve(
            ).parent.parent / "bot" / "settings.json"
            print(f"Loading settings from: {settings_path}")

            if not settings_path.exists():
                print(f"Error: Settings file not found at {settings_path}")
                return

            with open(settings_path, "r") as f:
                data = json.loads(f.read())
                self.trade_settings = {k: TradeSettings(
                    v, k) for k, v in data['pairs'].items()}
                self.trade_risk = data['trade_risk']

    def setup_logs(self):
        self.logs = {}
        for k in self.trade_settings.keys():
            self.logs[k] = LogWrapper(k)
            self.log_message(f"{self.trade_settings[k]}", k)
        self.logs[Bot.ERROR_LOG] = LogWrapper(Bot.ERROR_LOG)
        self.logs[Bot.MAIN_LOG] = LogWrapper(Bot.MAIN_LOG)
        self.log_to_main(
            f"Bot started with {TradeSettings.settings_to_str(self.trade_settings)}")

    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self, msg):
        self.log_message(msg, Bot.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, Bot.ERROR_LOG)

    def process_candles(self, triggered):
        if len(triggered) > 0:
            self.log_message(
                f"process_candles triggered:{triggered}", Bot.MAIN_LOG)
            for p in triggered:
                last_time = self.candle_manager.timings[p].last_time
                trade_decision = get_trade_decision(last_time, p, Bot.GRANULARITY, self.api,
                                                    self.trade_settings[p],  self.log_message)
                if trade_decision is not None and trade_decision.signal != defs.NONE:
                    self.log_message(f"Place Trade: {trade_decision}", p)
                    self.log_to_main(f"Place Trade: {trade_decision}")
                    place_trade(trade_decision, self.api, self.log_message,
                                self.log_to_error, self.trade_risk)

    def close_all_trades(self):
        for pair in self.trade_settings.keys():
            open_trade = trade_is_open(pair, self.api)
            if open_trade is not None:
                self.api.close_trade(open_trade.id)
                self.log_to_main(
                    f"Closed trade {open_trade.id} for {pair} due to error or shutdown")

    def run(self):
        while True:
            time.sleep(Bot.SLEEP)
            try:
                self.process_candles(self.candle_manager.update_timings())
            except Exception as error:
                self.log_to_error(f"CRASH: {error}")
                self.close_all_trades()
                break
