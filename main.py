from api.oanda_api import OandaApi
from infrastructure.instrument_collection import instrumentCollection
from streaming.streamer import run_streaming_application

if __name__ == '__main__':
    api = OandaApi()
    instrumentCollection.LoadInstruments("./data")
    run_streaming_application()
