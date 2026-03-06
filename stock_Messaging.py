import os
import requests
import pandas as pd
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
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=data)
    print("LINE status:", response.status_code)
    print(response.text)

# CSV読み込み（重複銘柄対応）
df = pd.read_csv(
    "テスト.csv",
    encoding="utf-8-sig",   # 日本語対応
    on_bad_lines='skip',    # フォーマットおかしい行はスキップ
    sep=","                 # 区切り文字はCSVに合わせる
)

# 銘柄ごとにまとめる（平均取得単価計算）
df_grouped = df.groupby("銘柄コード").apply(
    lambda x: pd.Series({
        "株数": x["株数"].sum(),
        "平均取得単価": (x["取得単価"] * x["株数"]).sum() / x["株数"].sum()
    })
).reset_index()

message = "本日の保有株\n\n"
total_profit = 0

for _, row in df_grouped.iterrows():
    code = str(row["銘柄コード"])
    shares = row["株数"]
    avg_price = row["平均取得単価"]

    try:
        ticker = yf.Ticker(f"{code}.T")
        hist = ticker.history(period="1d")
        if hist.empty:
            message += f"{code} : データなし\n"
            continue
        price = hist["Close"].iloc[-1]
        profit = (price - avg_price) * shares
        total_profit += profit

        message += (
            f"{code}\n"
            f"株価:{round(price,1)}円\n"
            f"平均取得:{round(avg_price,1)}円\n"
            f"損益:{round(profit):,}円\n\n"
        )
    except Exception as e:
        print(e)
        message += f"{code} : エラー\n\n"

message += f"\n合計損益\n{round(total_profit):,}円"

send_line(message)
