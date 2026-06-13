import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = os.getenv("CHANNEL_ID")
READ_API_KEY = os.getenv("READ_API_KEY")

CSV_FILE = "data/energy_log.csv"

while True:

    try:

        url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=100"

        response = requests.get(url)

        data = response.json()

        feeds = data["feeds"]

        records = []

        for feed in feeds:

            records.append({

                "Time": feed["created_at"],

                "Voltage": float(feed["field1"] or 0),

                "Current": float(feed["field2"] or 0),

                "Power": float(feed["field3"] or 0),

                "Energy": float(feed["field4"] or 0),

                "Cost": float(feed["field5"] or 0),

                "Alert": feed["field6"] if feed["field6"] else "NORMAL"

            })

        df = pd.DataFrame(records)

        os.makedirs("data", exist_ok=True)

        df.to_csv(CSV_FILE, index=False)

        latest = df.iloc[-1]

        print("\n" + "="*50)

        print("LATEST ESP32 DATA")

        print("="*50)

        print("Time:", latest["Time"])

        print("Voltage:", latest["Voltage"])

        print("Current:", latest["Current"])

        print("Power:", latest["Power"])

        print("Energy:", latest["Energy"])

        print("Cost:", latest["Cost"])

        print("Alert:", latest["Alert"])

        print("="*50)

    except Exception as e:

        print("Error:", e)

    time.sleep(15)