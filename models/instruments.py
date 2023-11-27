class Instrument:
    """
    A class representing a financial instrument.

    Attributes:
        name (str): The name of the instrument.
        ins_type (str): The type of the instrument.
        display_name (str): The display name of the instrument.
        pip_location (int): The location of the pip (power of 10).
        trade_units_precision (int): The precision of trade units.
        margin_rate (float): The margin rate for the instrument.
    """

    def __init__(self, name, ins_type, display_name, pip_location, trade_units_precision, margin_rate):
        """
        Initializes an Instrument object.

        Args:
            name (str): The name of the instrument.
            ins_type (str): The type of the instrument.
            display_name (str): The display name of the instrument.
            pip_location (int): The location of the pip (power of 10).
            trade_units_precision (int): The precision of trade units.
            margin_rate (float): The margin rate for the instrument.
        """
        self.name = name
        self.ins_type = ins_type
        self.display_name = display_name
        self.pip_location = pow(10, pip_location)
        self.trade_units_precision = trade_units_precision
        self.margin_rate = float(margin_rate)

    def __repr__(self):
        """
        Returns a string representation of the Instrument object.

        Returns:
            str: A string representation of the object.
        """
        return str(vars(self))

    @classmethod
    def FromApiObject(cls, api_object):
        """
        Creates an Instrument object from an API response object.

        Args:
            api_object (dict): The API response object.

        Returns:
            Instrument: An Instrument object created from the API response.
        """
        return Instrument(
            api_object.get('name', ''),
            api_object.get('ins_type', ''),
            api_object.get('displayName', ''),
            api_object.get('pipLocation', ''),
            api_object.get('tradeUnitsPrecision', ''),
            api_object.get('marginRate', '')
        )
