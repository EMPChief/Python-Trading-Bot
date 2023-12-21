import datetime as dt


class CandleTiming:

    def __init__(self, last_time):
        self.last_time = self.validate_last_time(last_time)
        self.is_ready = False

    def validate_last_time(self, last_time):
        try:
            if not isinstance(last_time, dt.datetime):
                raise ValueError("last_time must be a datetime object.")
            return last_time
        except Exception as e:
            print(f"Error validating last_time: {e}")
            return dt.datetime.now()

    def __repr__(self):
        return f"last_candle:{dt.datetime.strftime(self.last_time, '%y-%m-%d %H:%M')} is_ready:{self.is_ready}"
