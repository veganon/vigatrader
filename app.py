from flask import Flask, request
from datetime import datetime
import os

app = Flask(__name__)

balance = 10000.0
position = None
entry_price = None
shares = 0.0
trades = 0

risk_percent = 0.10
stop_loss_percent = 0.01
take_profit_percent = 0.02


def log(msg):
    print(msg, flush=True)


@app.route('/webhook', methods=['POST'])
def webhook():
    global balance, position, entry_price, shares, trades

    data = request.json
    if not data:
        return "No data", 400

    action = data.get("action")
    symbol = data.get("symbol", "SPUS")
    price = float(data.get("price", 0))

    if price <= 0:
        return "Invalid price", 400

    time = datetime.now().strftime("%H:%M:%S")

    if action == "BUY" and position is None:
        trade_amount = balance * risk_percent
        shares = trade_amount / price
        entry_price = price
        position = "LONG"
        trades += 1

        log(f"[{time}] BUY {symbol} @ {price:.2f} | Amount: {trade_amount:.2f} | Shares: {shares:.4f}")

    elif action in ["SELL", "STOP", "TAKE_PROFIT"] and position == "LONG":
        pnl = (price - entry_price) * shares
        balance += pnl

        log(f"[{time}] {action} {symbol} @ {price:.2f} | PnL: {pnl:.2f} | Balance: {balance:.2f}")

        position = None
        entry_price = None
        shares = 0.0

    else:
        log(f"[{time}] IGNORED {action} {symbol} | Position: {position}")

    return "OK"


@app.route('/status', methods=['GET'])
def status():
    stop_price = None
    take_profit_price = None

    if position == "LONG" and entry_price:
        stop_price = entry_price * (1 - stop_loss_percent)
        take_profit_price = entry_price * (1 + take_profit_percent)

    return {
        "balance": round(balance, 2),
        "position": position,
        "entry_price": entry_price,
        "shares": round(shares, 4),
        "stop_loss_price": round(stop_price, 2) if stop_price else None,
        "take_profit_price": round(take_profit_price, 2) if take_profit_price else None,
        "risk_percent": risk_percent,
        "stop_loss_percent": stop_loss_percent,
        "take_profit_percent": take_profit_percent,
        "trades": trades
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
