import os
import pandas as pd
import yfinance as yf
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
        "messages": [{"type": "text", "text": message}]
    }
    r = requests.post(url, headers=headers, json=data)
    print("LINE status:", r.status_code)
    print(r.text)

# CSV 読み込み
df = pd.read_csv("テスト.csv")
df.columns = df.columns.str.strip().str.lower()  # 列名を小文字化

# 銘柄ごとに株数と平均取得単価を集計
df_grouped = df.groupby("code").apply(
    lambda x: pd.Series({
        "avg_buy": (x["buy_price"] * x["shares"]).sum() / x["shares"].sum(),
        "shares": x["shares"].sum()
    })
)

message = "本日の株価と評価損益\n\n"

for code, row in df_grouped.iterrows():
    ticker = f"{code}.T"  # 日本株の場合
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"][-1]
        profit = (price - row["avg_buy"]) * row["shares"]
        message += f"{code} : {price:.0f}円 | 評価損益 {profit:.0f}円\n"
    except Exception as e:
        message += f"{code} : 株価取得失敗\n"

# 合計評価損益を追加
message += f"\n合計評価損益: {total_profit:.0f}円"

send_line(message)
