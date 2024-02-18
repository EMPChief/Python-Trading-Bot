import logging
import os

LOG_FORMAT = "%(asctime)s %(message)s"
DEFAULT_LEVEL = logging.DEBUG


class LogWrapper:

    PATH = './data/logs'

    def __init__(self, name, mode="w"):
        self.create_directory()
        self.filename = f"{LogWrapper.PATH}/{name}.log"
        self.logger = logging.getLogger(name)
        self.logger.setLevel(DEFAULT_LEVEL)

        file_handler = logging.FileHandler(self.filename, mode=mode)
        formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f"LogWrapper init() {self.filename}")

    def create_directory(self):
        if not os.path.exists(LogWrapper.PATH):
            os.makedirs(LogWrapper.PATH)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def exception(self, message):
        self.logger.exception(message)
