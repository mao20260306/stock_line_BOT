import os
import requests

url = os.environ["ONEDRIVE_URL"]
r = requests.get(url)
with open("テスト.csv", "wb") as f:
    f.write(r.content)

print("CSV downloaded successfully")
