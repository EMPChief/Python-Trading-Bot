from api.oanda_api import OandaApi
from infrastructure.instrument_collection import instrumentCollection
from streaming.streamer import run_streaming_application
from db.db import DataDataBase

def db_test_add():
    db = DataDataBase()
    sample_documents = [
        {"name": "John", "eye": "blue", "like": "red", "hate": "green"},
        {"name": "Alice", "eye": "brown", "like": "blue", "hate": "yellow"},
        {"name": "Bob", "eye": "green", "like": "yellow", "hate": "blue"}
    ]
    db.add_many(DataDataBase.LEARNING_COLLECTION, sample_documents)
    db.add_one(DataDataBase.LEARNING_COLLECTION, {"name": "Jane", "eye": "blue", "like": "green", "hate": "red"})


if __name__ == '__main__':
#    api = OandaApi()
#    instrumentCollection.LoadInstruments("./data")
#    run_streaming_application()
    db_test_add()

