from flask import Flask, request
from datetime import datetime
import os

app = Flask(__name__)

balance = 10000
position = None

entry_price = None
trades = 0


def log(msg):
    print(msg, flush=True)


@app.route('/webhook', methods=['POST'])
def webhook():
    global balance, position, entry_price, trades

    data = request.json

    if not data:
        return "No data", 400

    action = data.get("action")
    symbol = data.get("symbol")
    price = float(data.get("price", 0))

    time = datetime.now().strftime("%H:%M:%S")

    # 🟢 BUY
    if action == "BUY" and position is None:
        position = "LONG"
        entry_price = price
        trades += 1

        log(f"[{time}] BUY {symbol} @ {entry_price}")

    # 🔴 SELL
    elif action == "SELL" and position == "LONG":
        position = None

        exit_price = price
        profit = exit_price - entry_price

        balance += profit

        log(f"[{time}] SELL {symbol} @ {exit_price} | PnL: {profit:.2f} | Balance: {balance:.2f}")

        entry_price = None

    return "OK"


@app.route('/status', methods=['GET'])
def status():
    return {
        "balance": round(balance, 2),
        "position": position,
        "entry_price": entry_price,
        "trades": trades
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
