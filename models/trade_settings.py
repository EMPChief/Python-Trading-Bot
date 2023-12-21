class TradeSettings:
    def __init__(self, ob, pair):
        self.pair = pair
        self.bollinger_bands_settings = self._extract_settings(ob, 'bollinger_bands',
                                                               ['n_ma', 'n_std', 'maxspread', 'mingain', 'riskreward'])
        self.ichimoku_cloud_settings = self._extract_settings(ob, 'ichimoku_cloud',
                                                              ['n1', 'n2', 'n3'])
        self.cmf_settings = self._extract_settings(
            ob, 'chaikin_money_flow', ['n_cmf'])
        self.atr_settings = self._extract_settings(ob, 'atr',
                                                   ['n_atr', 'tp_multiplier', 'sl_multiplier'])

    def _extract_settings(self, ob, key, params):
        """Helper method to extract settings for a given indicator."""
        settings = {}
        for param in params:
            value = ob.get(key, {}).get(param, 0)
            # Parameters expected to be integers
            if param in ['n_ma', 'n1', 'n2', 'n3', 'n_cmf', 'n_atr']:
                try:
                    settings[param] = int(value)
                except ValueError:
                    print(
                        f"Invalid value for {param} in {key}: {value}. Defaulting to 0.")
                    settings[param] = 0
            else:
                settings[param] = float(value)
        return settings

    def __repr__(self):
        return f"TradeSettings(pair={self.pair}, " \
               f"bollinger_bands={self.bollinger_bands_settings}, " \
               f"ichimoku_cloud={self.ichimoku_cloud_settings}, " \
               f"cmf={self.cmf_settings}, " \
               f"atr_settings={self.atr_settings})"

    @classmethod
    def settings_to_str(cls, settings):
        """Converts the settings dictionary to a string representation."""
        ret_str = "Trade Settings:\n"
        for indicator, params in settings.items():
            ret_str += f"{indicator} Settings:\n"
            for k, v in (params.items() if isinstance(params, dict) else [(indicator, params)]):
                ret_str += f"    {k}: {v}\n"
        return ret_str
