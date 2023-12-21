class TradeSettings:
    def __init__(self, ob, pair):
        self.bollinger_bands_settings = {
            "n_ma": float(ob.get('bollinger_bands', {}).get('n_ma', 0)),
            "n_std": float(ob.get('bollinger_bands', {}).get('n_std', 0)),
            "maxspread": float(ob.get('bollinger_bands', {}).get('maxspread', 0)),
            "mingain": float(ob.get('bollinger_bands', {}).get('mingain', 0)),
            "riskreward": float(ob.get('bollinger_bands', {}).get('riskreward', 0))
        }
        self.ichimoku_cloud_settings = {
            "n1": float(ob.get('ichimoku_cloud', {}).get('n1', 0)),
            "n2": float(ob.get('ichimoku_cloud', {}).get('n2', 0)),
            "n3": float(ob.get('ichimoku_cloud', {}).get('n3', 0))
        }
        self.cmf_settings = {
            "n_cmf": float(ob.get('chaikin_money_flow', {}).get('n_cmf', 0))
        }

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for indicator, params in settings.items():
            ret_str += f"{indicator} Settings:\n"
            if isinstance(params, dict):
                for k, v in params.items():
                    ret_str += f"    {k}: {v}\n"
            else:
                ret_str += f"    {indicator}: {params}\n"
        return ret_str
