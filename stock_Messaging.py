import os
import requests

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
        "messages": [{
            "type": "text",
            "text": message
        }]
    }

    requests.post(url, headers=headers, json=data)



stocks = ["4661","7809","6762","6702","4183","8306"]

message = "本日の株価\n\n"

for code in stocks:

    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={code}.T"

    try:

        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            message += f"{code} : 株価取得失敗\n"
            continue

        data = res.json()

        result = data["quoteResponse"]["result"]

        if len(result) == 0:
            message += f"{code} : データなし\n"
            continue

        price = result[0]["regularMarketPrice"]

        message += f"{code} : {price}円\n"

    except Exception as e:
        message += f"{code} : エラー\n"


send_line(message)
