from pymongo import MongoClient
import os

def get_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["wallet_db"]
    return db
