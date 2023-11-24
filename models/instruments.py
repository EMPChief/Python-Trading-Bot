class Instrument:
    def __init__(self, name, ins_type, displayName, pipLocation, tradeUnitsPrecision, marginRate):
        self.name = name
        self.ins_type = ins_type
        self.displayName = displayName
        self.pipLocation = pow(10, pipLocation)
        self.tradeUnitsPrecision = tradeUnitsPrecision
        self.marginRate = float(marginRate)
    
    def __repr__(self):
        return str(vars(self))
    
    @classmethod
    def FromApiObject(cls, ob):
        return Instrument(
        ob.get('name', ''),
        ob.get('ins_type', ''),
        ob.get('displayName', ''),
        ob.get('pipLocation', ''),
        ob.get('tradeUnitsPrecision', ''),
        ob.get('marginRate', '')
        )