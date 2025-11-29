from pymongo import MongoClient
import os
from datetime import datetime, timedelta

def get_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["wallet_db"]
    return db

def get_user_cards(user_id):
    return list(db["cards"].find({"user_id": user_id}, {"_id": 0}))

def get_stock_list(user_id):
    return list(db['stocks'].find({"user_id" : user_id}, {"_id": 0}))

db = get_db()
users_collection = db["users"]
transactions_collection = db["transactions"]
graph_collection = db["graph_data"]
stocks_collection = db["stocks"]  # NEW COLLECTION
crypto_collection = db["crypto_portfolio"]

def insert_dummy_data():
    # ---------------- USERS ----------------
    if users_collection.count_documents({}) == 0:
        users_collection.insert_one({
            "username": "Soham G",
            "cards": ["VISA Platinum ****1234", "HDFC Debit ****5678"],
            "balance": 150000
        })

    # ---------------- TRANSACTIONS ----------------
    if transactions_collection.count_documents({}) == 0:
        dummy_transactions = [
            # January
            {"type": "income", "amount": 20000, "name": "Company Salary", "date": datetime(2025, 1, 5, 10, 30)},
            {"type": "expense", "amount": 5000, "name": "Amazon Shopping", "date": datetime(2025, 1, 10, 15, 45)},
            {"type": "saving", "amount": 3000, "name": "FD Investment", "date": datetime(2025, 1, 15, 9, 0)},
            # February
            {"type": "income", "amount": 21000, "name": "Company Salary", "date": datetime(2025, 2, 5, 10, 15)},
            {"type": "expense", "amount": 6000, "name": "Netflix + Food", "date": datetime(2025, 2, 12, 18, 30)},
            {"type": "saving", "amount": 3500, "name": "Mutual Funds", "date": datetime(2025, 2, 20, 11, 45)},
            # March
            {"type": "income", "amount": 22000, "name": "Freelance", "date": datetime(2025, 3, 6, 9, 0)},
            {"type": "expense", "amount": 7000, "name": "Electricity + Rent", "date": datetime(2025, 3, 9, 16, 10)},
            {"type": "saving", "amount": 4000, "name": "SIP Plan", "date": datetime(2025, 3, 15, 8, 40)},
            # April
            {"type": "income", "amount": 25000, "name": "Company Salary", "date": datetime(2025, 4, 3, 10, 0)},
            {"type": "expense", "amount": 8000, "name": "Travel", "date": datetime(2025, 4, 15, 12, 30)},
            {"type": "saving", "amount": 5000, "name": "Stocks", "date": datetime(2025, 4, 20, 19, 0)},
            # Last 30 days
            {"type": "income", "amount": 26000, "name": "Company Salary", "date": datetime.now() - timedelta(days=10)},
            {"type": "expense", "amount": 9000, "name": "Groceries", "date": datetime.now() - timedelta(days=8)},
            {"type": "saving", "amount": 6000, "name": "Gold Savings", "date": datetime.now() - timedelta(days=5)},
        ]
        transactions_collection.insert_many(dummy_transactions)

    # ---------------- GRAPH DATA ----------------
    if graph_collection.count_documents({}) == 0:
        dummy_graph_data = [
            {"month": "Jan", "savings": 22000, "expenses": 15000},
            {"month": "Feb", "savings": 25000, "expenses": 18000},
            {"month": "Mar", "savings": 27000, "expenses": 20000},
            {"month": "Apr", "savings": 30000, "expenses": 22000},
            {"month": "May", "savings": 32000, "expenses": 25000},
        ]
        graph_collection.insert_many(dummy_graph_data)

    # ---------------- STOCK PORTFOLIO (NEW) ----------------
    if stocks_collection.count_documents({}) == 0:
        dummy_stocks = {
            "username": "Soham G",
            "total_profit": 0,   # Auto-calculated below
            "portfolio": [
                {
                    "symbol": "AAPL",
                    "quantity": 10,
                    "buy_price": 150,
                    "current_price": 180,
                    "profit": (180 - 150) * 10,
                    "actions": ["buy", "sell"]
                },
                {
                    "symbol": "TSLA",
                    "quantity": 5,
                    "buy_price": 600,
                    "current_price": 650,
                    "profit": (650 - 600) * 5,
                    "actions": ["buy", "sell"]
                },
                {
                    "symbol": "TATASTEEL",
                    "quantity": 20,
                    "buy_price": 110,
                    "current_price": 140,
                    "profit": (140 - 110) * 20,
                    "actions": ["buy", "sell"]
                }
            ]
        }

        if crypto_collection.count_documents({}) == 0:
          dummy_crypto = {
            "username": "Soham G",
            "total_profit": 0,   # Auto-calculated below
            "portfolio": [
                {
                    "symbol": "BTC",
                    "quantity": 0.5,
                    "buy_price": 50000,
                    "current_price": 55000,
                    "profit": (55000 - 50000) * 0.5,
                    "actions": ["buy", "sell"]
                },
                {
                    "symbol": "ETH",
                    "quantity": 2,
                    "buy_price": 3000,
                    "current_price": 3500,
                    "profit": (3500 - 3000) * 2,
                    "actions": ["buy", "sell"]
                },
                {
                    "symbol": "SOL",
                    "quantity": 10,
                    "buy_price": 100,
                    "current_price": 120,
                    "profit": (120 - 100) * 10,
                    "actions": ["buy", "sell"]
                }
            ]
        }
        crypto_collection.insert_one(dummy_crypto)

        # Calculate total profit
        dummy_stocks["total_profit"] = sum(stock["profit"] for stock in dummy_stocks["portfolio"])

        stocks_collection.insert_one(dummy_stocks)

insert_dummy_data()
