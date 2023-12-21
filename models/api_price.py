class ApiPrice:

    def __init__(self, api_ob, homeConversions):
        self.instrument = api_ob['instrument']
        self.ask = float(api_ob['asks'][0]['price'])
        self.bid = float(api_ob['bids'][0]['price'])
        base_instrument = self.instrument.split('_')[1]
        matching_conversion = None
        for hc in homeConversions:
            if hc['currency'] == base_instrument:
                matching_conversion = hc
                break
        if matching_conversion:
            self.sell_conv = float(matching_conversion['positionValue'])
            self.buy_conv = float(matching_conversion['positionValue'])
        else:
            self.sell_conv = 0.0
            self.buy_conv = 0.0
            print(
                f"No matching conversion found for {base_instrument}. Setting sell_conv and buy_conv to 0.0.")

    def __repr__(self):
        return f"ApiPrice() {self.instrument} {self.ask} {self.bid} {self.sell_conv:.6f} {self.buy_conv:.6f}"
