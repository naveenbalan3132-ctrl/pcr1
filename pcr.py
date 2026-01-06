import requests
import json
from datetime import datetime

BASE_URL = "https://www.nseindia.com"
URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

session = requests.Session()
session.headers.update(HEADERS)

session.get(BASE_URL)
resp = session.get(URL)
data = resp.json()

call_oi = 0
put_oi = 0

for row in data["records"]["data"]:
    if row.get("CE"):
        call_oi += row["CE"]["openInterest"]
    if row.get("PE"):
        put_oi += row["PE"]["openInterest"]

pcr = round(put_oi / call_oi, 3)

output = {
    "call_oi": call_oi,
    "put_oi": put_oi,
    "pcr": pcr,
    "timestamp": datetime.now().isoformat()
}

with open("pcr_data.json", "w") as f:
    json.dump(output, f, indent=4)

print("PCR data updated")
