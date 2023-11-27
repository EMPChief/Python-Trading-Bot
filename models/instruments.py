class Instrument:
    """
    A class representing a financial instrument.

    Attributes:
        name (str): The name of the instrument.
        ins_type (str): The type of the instrument.
        displayName (str): The display name of the instrument.
        pipLocation (int): The location of the pip (power of 10).
        tradeUnitsPrecision (int): The precision of trade units.
        marginRate (float): The margin rate for the instrument.
    """

    def __init__(self, name, ins_type, displayName, pipLocation, tradeUnitsPrecision, marginRate):
        """
        Initializes an Instrument object.

        Args:
            name (str): The name of the instrument.
            ins_type (str): The type of the instrument.
            displayName (str): The display name of the instrument.
            pipLocation (int): The location of the pip (power of 10).
            tradeUnitsPrecision (int): The precision of trade units.
            marginRate (float): The margin rate for the instrument.
        """
        self.name = name
        self.ins_type = ins_type
        self.displayName = displayName
        self.pipLocation = pow(10, pipLocation)
        self.tradeUnitsPrecision = tradeUnitsPrecision
        self.marginRate = float(marginRate)

    def __repr__(self):
        """
        Returns a string representation of the Instrument object.

        Returns:
            str: A string representation of the object.
        """
        return str(vars(self))

    @classmethod
    def FromApiObject(cls, ob):
        """
        Creates an Instrument object from an API response object.

        Args:
            ob (dict): The API response object.

        Returns:
            Instrument: An Instrument object created from the API response.
        """
        return Instrument(
            ob.get('name', ''),
            ob.get('ins_type', ''),
            ob.get('displayName', ''),
            ob.get('pipLocation', ''),
            ob.get('tradeUnitsPrecision', ''),
            ob.get('marginRate', '')
        )
