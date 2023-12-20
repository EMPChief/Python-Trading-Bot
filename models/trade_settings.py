class TradeSettings:

    def __init__(self, ob, pair):
        self.n_ma = ob.get('n_ma', 0)
        self.n_std = ob.get('n_std', 0)
        self.maxspread = ob.get('maxspread', 0)
        self.mingain = ob.get('mingain', 0)
        self.riskreward = ob.get('riskreward', 0)

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"
        return ret_str
