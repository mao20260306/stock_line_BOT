import os
import requests
import yfinance as yf

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


stocks = ["4661","7809","6762","6702","4183","8306"]

message = "本日の株価\n\n"

for code in stocks:

    try:

        ticker = yf.Ticker(f"{code}.T")

        hist = ticker.history(period="1d")

        if hist.empty:
            message += f"{code} : データなし\n"
            continue

        price = hist["Close"].iloc[-1]

        message += f"{code} : {round(price,2)}円\n"

    except Exception as e:

        print("error:", e)
        message += f"{code} : エラー\n"


send_line(message)

print("token length:", len(os.environ["LINE_TOKEN"]))
print("user id:", os.environ["USER_ID"])
