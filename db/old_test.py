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