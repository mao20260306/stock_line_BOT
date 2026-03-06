import requests
import os

LINE_TOKEN = os.environ["LINE_TOKEN"]
USER_ID = "Uf58b68ff9e8be35ab0d09bc91c14a05c"

def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "to": USER_ID,
        "messages": [{
            "type": "text",
            "text": message
        }]
    }

    requests.post(url, headers=headers, json=data)


stocks = ["4661","7809","6762","6702","4183","8306"]

message = "本日の株価\n"

for code in stocks:
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={code}.T"
    r = requests.get(url).json()

    price = r["quoteResponse"]["result"][0]["regularMarketPrice"]

    message += f"{code} : {price}円\n"

send_line(message)
