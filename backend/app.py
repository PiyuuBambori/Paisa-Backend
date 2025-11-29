from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from wallet.wallet import (
    get_wallet_ai_suggestion,
    get_user_data,
    get_last_30_days_summary,
    get_monthly_summary,
    get_all_transactions,
    get_user_cards
)

from flask import Flask, jsonify, request
from pymongo import MongoClient
import os


app = Flask(__name__)
CORS(app)

load_dotenv()

# Configure Gemini API
genai.configure(api_key="AIzaSyB6Kr5V4TIwXSUqfUZMWE_xAS0t7tn8lgY")

def get_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client["wallet_db"]

db = get_db()
stocks_collection = db["stocks"]

@app.route("/market/summary", methods=["GET"])
def market_summary():
    try:
        prompt = """
        Give a short, simple, human-friendly summary of today's global market conditions in 2 lines.
        Mention:
        - stock market mood (bullish / bearish)
        - tech sector vibe
        - any notable trend
        Make it conversational, like you're answering: "How's the market today?"
        """

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        return jsonify({
            "success": True,
            "summary": response.text
        })

    except Exception as e:
        print(e)
        return jsonify({"success": False, "summary": "Unable to load market summary."})
    
@app.route("/crypto/summary", methods=["GET"])
def crypto_summary():
    prompt = """
    Provide a simple, conversational explanation of today's cryptocurrency market.
    Mention:
    - Bitcoin sentiment (bullish/bearish)
    - Ethereum condition
    - Altcoin trends
    - Market mood summary
    Keep it friendly and short.
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        return jsonify({
            "success": True,
            "summary": response.text
        })
    except Exception as e:
        print(e)
        return jsonify({"success": False, "summary": "Unable to analyze crypto market."})
    
@app.route("/api/trader/stocks", methods=["GET"])
def get_stocks():
    data = stocks_collection.find_one({"username": "Soham G"}, {"_id": 0})
    
    if not data:
        return jsonify({"success": False, "msg": "No portfolio found"}), 404
    
    return jsonify({"success": True, "data": data})

@app.route("/api/trader/stocks/buy", methods=["POST"])
def buy_stock():
    body = request.json
    symbol = body.get("symbol")
    quantity = body.get("quantity")
    price = body.get("price")

    user = stocks_collection.find_one({"username": "Soham G"})

    if not user:
        return jsonify({"success": False, "msg": "User not found"}), 404

    portfolio = user["portfolio"]
    
    # Check if stock exists
    stock = next((s for s in portfolio if s["symbol"] == symbol), None)

    if stock:
        total_qty = stock["quantity"] + quantity
        stock["buy_price"] = ((stock["buy_price"] * stock["quantity"]) + (price * quantity)) / total_qty
        stock["quantity"] = total_qty
    else:
        portfolio.append({
            "symbol": symbol,
            "quantity": quantity,
            "buy_price": price,
            "current_price": price,
            "profit": 0
        })

    # Recalculate profit
    for s in portfolio:
        s["profit"] = (s["current_price"] - s["buy_price"]) * s["quantity"]

    total_profit = sum(s["profit"] for s in portfolio)

    # Update DB
    stocks_collection.update_one(
        {"username": "Soham G"},
        {"$set": {"portfolio": portfolio, "total_profit": total_profit}}
    )

    return jsonify({"success": True, "msg": "Stock bought"})

@app.route("/api/trader/stocks/sell", methods=["POST"])
def sell_stock():
    body = request.json
    symbol = body.get("symbol")
    quantity = body.get("quantity")
    price = body.get("price")

    user = stocks_collection.find_one({"username": "Soham G"})

    if not user:
        return jsonify({"success": False, "msg": "User not found"}), 404

    portfolio = user["portfolio"]

    stock = next((s for s in portfolio if s["symbol"] == symbol), None)

    if not stock:
        return jsonify({"success": False, "msg": "Stock not found"}), 404

    if stock["quantity"] < quantity:
        return jsonify({"success": False, "msg": "Not enough quantity"}), 400

    # Process sell
    stock["quantity"] -= quantity
    stock["current_price"] = price

    if stock["quantity"] == 0:
        portfolio.remove(stock)

    # Recalculate profit
    for s in portfolio:
        s["profit"] = (s["current_price"] - s["buy_price"]) * s["quantity"]

    total_profit = sum(s["profit"] for s in portfolio)

    stocks_collection.update_one(
        {"username": "Soham G"},
        {"$set": {"portfolio": portfolio, "total_profit": total_profit}}
    )

    return jsonify({"success": True, "msg": "Stock sold"})


def explain_portfolio(score, portfolio):
    tickers = [s["symbol"] for s in portfolio]

    prompt = f"""
    Analyze a stock portfolio with the following tickers: {tickers}.
    The portfolio score is {score}/100.

    Explain what this means in simple language. Mention:
    - portfolio strengths
    - diversification level
    - potential risks
    - suggestions to improve
    Keep it short and helpful.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    return response.text

stocks_col = db["stocks"]

@app.route("/portfolio/analyse", methods=["GET"])
def analyse_portfolio():
    user = stocks_col.find_one({"username": "Soham G"})
    if not user:
        return jsonify({"success": False, "msg": "User not found"})

    portfolio = user["portfolio"]

    score = ml_portfolio_score(portfolio)
    explanation = explain_portfolio(score, portfolio)

    return jsonify({
        "success": True,
        "score": score,
        "explanation": explanation
    })


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(question)
    
    return jsonify({"answer": response.text})

@app.route("/api/wallet/user", methods=["GET"])
def user_data():
    return jsonify(get_user_data())

@app.route("/api/wallet/summary30", methods=["GET"])
def summary_30():
    return jsonify(get_last_30_days_summary())

@app.route("/api/wallet/monthly", methods=["GET"])
def monthly_summary():
    data = get_monthly_summary()
    return jsonify(data)

@app.route("/api/wallet/graph", methods=["GET"])
def graph_data():
    from wallet.wallet import get_graph_data
    data = get_graph_data()
    return jsonify(data)

@app.route("/api/wallet/transactions", methods=["GET"])
def transactions():
    return jsonify(get_all_transactions())

@app.route("/api/wallet/ai", methods=["POST"])
def wallet_ai():
    query = request.get_json().get("query", "")
    return jsonify({"response": get_wallet_ai_suggestion(query)})

@app.route("/api/wallet/cards")
def get_cards():
    user_id = "soham"
    cards = get_user_cards(user_id)
    return jsonify(cards)

def explain_crypto_portfolio(portfolio):
    prompt = f"""
    You are an expert crypto portfolio analyst.

    Here is the full crypto portfolio JSON (with symbols, quantities, sectors, etc.):

    {portfolio}

    Based on this portfolio, provide a simple and helpful explanation:
    - diversification quality
    - risk exposure & volatility
    - Bitcoin dominance issues
    - potential sector imbalance
    - strengths
    - weaknesses
    - clear and actionable improvement suggestions

    Keep it friendly, short, and beginner-friendly.
    Keep it under 10 lines
    Dont use "*" write only words.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

@app.route("/crypto/portfolio/analyse", methods=["GET"])
def analyse_crypto_portfolio():
    col = db["crypto_portfolio"]
    usr = col.find_one({"username": "Soham G"}, {"_id": 0})

    if not usr:
        return jsonify({"success": False, "msg": "No crypto portfolio found"})

    portfolio = usr["portfolio"]
    explanation = explain_crypto_portfolio(portfolio)

    return jsonify({
        "success": True,
        "explanation": explanation
    })



#MLLLLLLLLLLLLLLLLL

import numpy as np
import pickle

# Load ML model
with open("m" \
"odels/portfolio_model.pkl", "rb") as f:
    portfolio_model = pickle.load(f)

def extract_features(portfolio):
    sectors = {}
    total_qty = sum(s["quantity"] for s in portfolio)

    for s in portfolio:
        sector = s.get("sector", "Tech")  # default Tech
        sectors[sector] = sectors.get(sector, 0) + s["quantity"]

    num_stocks = len(portfolio)
    sector_diversity = len(sectors)

    weights = [qty / total_qty for qty in sectors.values()]
    max_weight = max(weights)
    avg_weight = sum(weights) / len(weights)

    tech_qty = sum(s["quantity"] for s in portfolio if s.get("sector", "") == "Tech")
    tech_ratio = tech_qty / total_qty

    return np.array([[num_stocks, sector_diversity, max_weight, avg_weight, tech_ratio]])

def ml_portfolio_score(portfolio):
    features = extract_features(portfolio)
    score = portfolio_model.predict(features)[0]
    return int(max(0, min(100, score)))

def explain_portfolio(score, portfolio):
    tickers = [s["symbol"] for s in portfolio]

    prompt = f"""
    You are analyzing an investment portfolio.
    Tickers: {tickers}
    Portfolio Score: {score}/100

    Provide:
    - diversification commentary
    - tech exposure commentary
    - strengths
    - risks
    - simple & friendly suggestions
    - under 10 lines
    - dont use "*", only write words
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    app.run(debug=True)



