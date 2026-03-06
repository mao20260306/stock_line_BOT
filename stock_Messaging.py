import os
import requests
import yfinance as yf
import csv

LINE_TOKEN = os.environ["LINE_TOKEN"]
USER_ID = os.environ["USER_ID"]


def send_line(message):

    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    print("LINE status:", response.status_code)
    print(response.text)


portfolio = []

with open("テスト.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        portfolio.append({
            "code": row["code"],
            "buy_price": float(row["buy_price"]),
            "shares": int(row["shares"])
        })


message = "本日の保有株\n\n"

total_profit = 0

for stock in portfolio:

    code = stock["code"]
    buy_price = stock["buy_price"]
    shares = stock["shares"]

    try:

        ticker = yf.Ticker(f"{code}.T")

        hist = ticker.history(period="1d")

        if hist.empty:
            message += f"{code} : データなし\n"
            continue

        price = hist["Close"].iloc[-1]

        profit = (price - buy_price) * shares

        total_profit += profit

        message += (
            f"{code}\n"
            f"株価:{round(price,1)}円\n"
            f"損益:{round(profit):,}円\n\n"
        )

    except Exception as e:

        print(e)
        message += f"{code} : エラー\n\n"


message += f"\n合計損益\n{round(total_profit):,}円"

send_line(message)
