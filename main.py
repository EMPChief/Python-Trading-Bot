from api.oanda_api import OandaApi
from infrastructure.instrument_collection import Instrument, InstrumentCollection

if __name__ == "__main__":
    api = OandaApi()
    
    instrumentCollection = InstrumentCollection()
    
    instrumentCollection.CreateFile(api.get_account_instruments(), "./data")
    
    #instrumentCollection.LoadInstruments("./data")
    #instrumentCollection.PrintInstruments()
    
