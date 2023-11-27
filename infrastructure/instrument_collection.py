from models.instruments import Instrument
import json

class InstrumentCollection:
    """
    A class representing a collection of financial instruments.

    Attributes:
        FILENAME (str): The name of the JSON file used for storing instrument data.
        API_KEYS (list): A list of keys expected in the API response for each instrument.
        instruments_dict (dict): A dictionary to store instrument data.
    """

    FILENAME = "instruments.json"
    API_KEYS = ['name', 'type', 'displayName', 'pipLocation', 'displayPrecision', 'tradeUnitsPrecision', 'marginRate']

    def __init__(self):
        """
        Initializes the InstrumentCollection object.
        """
        self.instruments_dict = {}

    def LoadInstruments(self, path):
        """
        Loads instrument data from a JSON file and populates the instruments_dict.

        Args:
            path (str): The path to the directory containing the JSON file.
        """
        self.instruments_dict = {}
        file_name = f"{path}/{self.FILENAME}"
        with open(file_name, "r") as file:
            data = json.load(file)
            for key, value in data.items():
                self.instruments_dict[key] = Instrument.FromApiObject(value)

    def CreateFile(self, data, path):
        """
        Creates a JSON file with instrument data.

        Args:
            data (list): The list of instrument data to be stored in the file.
            path (str): The path to the directory where the file should be created.
        """
        if data is None:
            print("InstrumentCollection.CreateFile: data is None")
            return
        instruments_dict = {}
        for instrument_data in data:
            key = instrument_data['name']
            instruments_dict[key] = {k: instrument_data[k] for k in self.API_KEYS}

        file_name = f"{path}/{self.FILENAME}"
        with open(file_name, "w") as file:
            file.write(json.dumps(instruments_dict, indent=2))

    def PrintInstruments(self):
        """
        Prints the instruments and the total count.
        """
        [print(key, value) for key, value in self.instruments_dict.items()]
        print(len(self.instruments_dict.keys()), 'instruments')

instrumentCollection = InstrumentCollection()
