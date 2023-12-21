class TradeSettings:

    def __init__(self, ob, pair):
        self.bollinger_bands_settings = {
            "n_ma": ob.get('bb_n_ma', 0),
            "n_std": ob.get('bb_n_std', 0),
            "maxspread": ob.get('bb_maxspread', 0),
            "mingain": ob.get('bb_mingain', 0),
            "riskreward": ob.get('bb_riskreward', 0)
        }

        self.ichimoku_cloud_settings = {
            "n1": ob.get('ichimoku_n1', 0),
            "n2": ob.get('ichimoku_n2', 0),
            "n3": ob.get('ichimoku_n3', 0)
        }

        self.cmf_settings = {
            "n_cmf": ob.get('cmf_n', 0)
        }

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for k, v in settings.items():
            ret_str += f"{k}: {v}\n"
        return ret_str
