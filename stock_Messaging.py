from datetime import datetime
import os
import sys
import jpholiday
import pandas as pd
import requests
import yfinance as yf

LINE_TOKEN = os.environ["LINE_TOKEN"]
USER_ID = os.environ["USER_ID"]


def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"to": USER_ID, "messages": [{"type": "text", "text": message}]}
    r = requests.post(url, headers=headers, json=data)
    print("LINE status:", r.status_code)
    print(r.text)


# --- 【追加】土日祝日の判定 ---
today = datetime.now()

# 曜日判定 (5=土曜日, 6=日曜日)
is_weekend = today.weekday() >= 5
# 祝日判定
is_holiday = jpholiday.is_holiday(today)

if is_weekend or is_holiday:
    print(f"本日は土日または祝日のため、実行をスキップします。({today.strftime('%Y-%m-%d')})")
    sys.exit(0)  # エラーにせず正常終了させる
# ------------------------------

# 【修正】GitHub ActionsでダウンロードしたCSVファイルを読み込み
csv_file = "99_GitHubデータ.csv"

if not os.path.exists(csv_file):
    print(f"エラー: {csv_file} が見つかりません。")
    sys.exit(1)

df = pd.read_csv(csv_file)
df.columns = df.columns.str.strip().str.lower()  # 列名を小文字化

# 銘柄ごとに株数と平均取得単価を集計
df_grouped = df.groupby("code").apply(
    lambda x: pd.Series(
        {
            "name": x["name"].iloc[0],
            "avg_buy": (x["buy_price"] * x["shares"]).sum() / x["shares"].sum(),
            "shares": x["shares"].sum(),
        }
    )
)

message = "本日の株価・前日差・評価損益\n\n"
message += "-" * 29 + "\n"

total_profit = 0

for code, row in df_grouped.iterrows():
    ticker = f"{code}.T"
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")  # 過去2日分
        if len(hist) < 2:
            raise ValueError("過去2日のデータが不足")
        today_close = hist["Close"][-1]
        yesterday_close = hist["Close"][-2]
        diff = today_close - yesterday_close
        diff_pct = diff / yesterday_close * 100
        profit = (today_close - row["avg_buy"]) * row["shares"]
        total_profit += profit

        # 見やすいフォーマットに整形
        message += (
            f"{code:<6} {row['name'][:10]:<10}\n"
            f"  差額  : {diff:.0f}\n"
            f"  差率  : {diff_pct:.2f}%\n"
            f"  損益  : {profit:.0f}\n"
            f"{'-'*10}\n"
        )
    except Exception as e:
        message += f"{code:<6} {'取得失敗':>28}\n"

message += "-" * 29 + "\n"
message += f"{'合計':<6} {'':>8} {'':>8} {total_profit:>10.0f}\n"

send_line(message)
