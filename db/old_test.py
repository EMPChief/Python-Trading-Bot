"""
def db_test_add():
    db = DataDataBase()
    sample_documents = [
        {"name": "John", "eye": "blue", "like": "red", "hate": "green"},
        {"name": "Alice", "eye": "brown", "like": "blue", "hate": "yellow"},
        {"name": "Bob", "eye": "green", "like": "yellow", "hate": "blue"}
    ]
    db.add_many(DataDataBase.LEARNING_COLLECTION, sample_documents)
    db.add_one(DataDataBase.LEARNING_COLLECTION, {"name": "Jane", "eye": "blue", "like": "green", "hate": "red"})
"""

"""
def db_test():
    db = DataBaseMongo()
    d = db.query_all(DataBaseMongo.LEARNING_COLLECTION, name='John')
    print(d)
"""
"""
def db_test():
    db = DataBaseMongo()
    d = db.query_single(DataBaseMongo.LEARNING_COLLECTION, name='tester')
    print(d)
"""

"""
def db_test():
    db = DataBaseMongo()
    d = db.query_distinct(DataBaseMongo.LEARNING_COLLECTION, "hate")
    print(d)
"""
"""
if __name__ == '__main__':
    api = OandaApi()
    instruments_data = api.get_account_instruments()
    instrumentCollection.LoadInstruments("./data")
    instrumentCollection.DB_CreateFile(instruments_data)
    instrumentCollection.DB_LoadInstruments()
    print(instrumentCollection.instruments_dict)
    run_streaming_application()
    calendar = TradingEconomicsCalendar()
    calendar.fetch_and_save_to_database()
"""