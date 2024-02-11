from pymongo import MongoClient, errors
from constants.defs import MONGO_CONNECTION_STRING

class DataDataBase:
    LEARNING_COLLECTION = "forex_sample"
    
    def __init__(self):
        self.client = MongoClient(MONGO_CONNECTION_STRING)
        self.db = self.client.forex_learning
        
    def test_connection(self):
        print(self.db.list_collection_names())
        
    def add_one(self, collection, list_obj):
        try:
            _ = self.db[collection].insert_one(list_obj)
        except errors.InvalidOperation as e:
            print(f"add_one error: {e}")
            return
    def add_many(self, collection, obj):
        try:
            _ = self.db[collection].insert_many(obj)
        except errors.InvalidOperation as e:
            print(f"add_many error: {e}")
            return
if __name__ == "__main__":
    db = DataDataBase()
    db.test_connection()
