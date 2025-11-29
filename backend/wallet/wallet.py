# backend/wallet/wallet.py
from datetime import datetime, timedelta
from .database import get_db
import google.generativeai as genai
import os

db = get_db()
genai.configure(api_key=os.getenv("AIzaSyB6Kr5V4TIwXSUqfUZMWE_xAS0t7tn8lgY"))

def get_user_cards(user_id):
    return list(db["cards"].find({"user_id": user_id}, {"_id": 0}))

def get_wallet_ai_suggestion(query):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        res = model.generate_content(f"Financial suggestion based on: {query}")
        return res.text
    except Exception as e:
        return f"Error: {str(e)}"

def get_user_data():
    user = db["users"].find_one({}, {"_id": 0})
    return user

def get_last_30_days_summary():
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    transactions = list(db["transactions"].find({"date": {"$gte": thirty_days_ago}}))

    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    saving = sum(t["amount"] for t in transactions if t["type"] == "saving")

    return {"income": income, "expense": expense, "saving": saving}
import calendar

def get_monthly_summary():
    transactions = db["transactions"]

    pipeline = [
        {"$group": {
            "_id": {"$month": "$date"},
            "total_amount": {"$sum": "$amount"}
        }},
        {"$sort": {"_id": 1}}
    ]
    summary = list(transactions.aggregate(pipeline))

    # Convert month numbers to readable names
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    result = [{"month": months[item["_id"] - 1], "amount": item["total_amount"]} for item in summary]

    return result

def get_graph_data():
    graph_data = list(db["graph_data"].find({}, {"_id": 0}))
    return graph_data

def get_all_transactions():
    transactions = list(db["transactions"].find({}, {"_id": 0}).sort("date", -1))
    for t in transactions:
        t["date"] = t["date"].strftime("%Y-%m-%d %H:%M")
    return transactions
