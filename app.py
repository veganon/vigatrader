from flask import Flask, request
from datetime import datetime
import os

app = Flask(__name__)

balance = 10000
position = None


def log(msg):
    print(msg, flush=True)


@app.route('/webhook', methods=['POST'])
def webhook():
    global balance, position

    data = request.json

    if not data:
        return "No data", 400

    action = data.get("action")
    symbol = data.get("symbol")

    time = datetime.now().strftime("%H:%M:%S")

    # 🟢 BUY
    if action == "BUY" and position is None:
        position = "LONG"
        log(f"[{time}] Viga Trader BUY {symbol}")

    # 🔴 SELL
    elif action == "SELL" and position == "LONG":
        position = None
        profit = balance * 0.001
        balance += profit
        log(f"[{time}] Viga Trader SELL {symbol} | Balance: {balance:.2f}")

    return "OK"


# 🟢 مهم لـ Render (PORT الديناميكي)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
