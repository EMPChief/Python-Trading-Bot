from api.oanda_api import OandaApi
from infrastructure.instrument_collection import Instrument, InstrumentCollection
from simulation.ma_cross import run_ma_sim
from dateutil import parser
from infrastructure.collect_data import run_collection
if __name__ == "__main__":
    api = OandaApi()

    instrumentCollection.LoadInstruments("./data")
    run_collection(instrumentCollection, api)
