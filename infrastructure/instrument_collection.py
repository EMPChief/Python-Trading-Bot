from models.instruments import Instrument
import json
from db.db import DataBaseMongo

class InstrumentCollection:
    FILENAME = "instruments.json"
    API_KEYS = ['name', 'type', 'displayName', 'pipLocation',
                'displayPrecision', 'tradeUnitsPrecision', 'marginRate']

    def __init__(self):
        self.instruments_dict = {}

    def LoadInstruments(self, path):
        self.instruments_dict = {}
        file_name = f"{path}/{self.FILENAME}"
        with open(file_name, "r") as file:
            data = json.load(file)
            for key, value in data.items():
                self.instruments_dict[key] = Instrument.FromApiObject(value)

    def CreateFile(self, data, path):
        if data is None:
            print("InstrumentCollection.CreateFile: data is None")
            return
        instruments_dict = {}
        for instrument_data in data:
            key = instrument_data['name']
            instruments_dict[key] = {k: instrument_data[k]
                                     for k in self.API_KEYS}
        file_name = f"{path}/{self.FILENAME}"
        with open(file_name, "w") as file:
            file.write(json.dumps(instruments_dict, indent=2))
        
    def DB_LoadInstruments(self):
        self.instruments_dict = {}
        data = DataBaseMongo().query_single(DataBaseMongo.INSTRUMENT_COLLECTION)
        for key, value in data.items():
            self.instruments_dict[key] = Instrument.FromApiObject(value)

    def DB_CreateFile(self, data):
        if data is None:
            print("InstrumentCollection.CreateFile: data is None")
            return
        instruments_dict = {}
        for instrument_data in data:
            key = instrument_data['name']
            instruments_dict[key] = {k: instrument_data[k]
                                     for k in self.API_KEYS}
        database = DataBaseMongo()
        database.delete_many(DataBaseMongo.INSTRUMENT_COLLECTION)
        database.add_one(DataBaseMongo.INSTRUMENT_COLLECTION, instruments_dict)


    def PrintInstruments(self):
        """
        Prints the instruments and the total count.
        """
        [print(key, value) for key, value in self.instruments_dict.items()]
        print(len(self.instruments_dict.keys()), 'instruments')


instrumentCollection = InstrumentCollection()
