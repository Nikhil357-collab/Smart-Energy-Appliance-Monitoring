import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ------------------------
# PAGE CONFIG
# ------------------------

st.set_page_config(
    page_title="Smart Home Energy Monitoring",
    page_icon="⚡",
    layout="wide"
)

# Auto refresh every 15 seconds
st_autorefresh(
    interval=15000,  # milliseconds
    key="energy_dashboard_refresh"
)
# ------------------------
# RGB BACKGROUND CSS
# ------------------------

st.markdown("""
<style>

.stApp{
background: linear-gradient(
135deg,
rgb(8,15,40),
rgb(25,45,90),
rgb(0,120,255)
);
color:white;
}

[data-testid="stMetricValue"]{
color:white;
font-size:28px;
font-weight:bold;
}

[data-testid="stMetricLabel"]{
color:white;
}

div[data-testid="metric-container"]{
background:rgba(255,255,255,0.08);
padding:15px;
border-radius:15px;
box-shadow:0px 4px 15px rgba(0,0,0,0.3);
}

h1,h2,h3{
color:white;
}

</style>
""", unsafe_allow_html=True)

# ------------------------
# ENV VARIABLES
# ------------------------

load_dotenv()

CHANNEL_ID = os.getenv("CHANNEL_ID")
READ_API_KEY = os.getenv("READ_API_KEY")

# ------------------------
# THINGSPEAK DATA
# ------------------------

@st.cache_data(ttl=15)
def load_data():

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

            "Alert": (feed["field6"] or "NORMAL")
        })

    df = pd.DataFrame(records)

    df["Time"] = pd.to_datetime(df["Time"])

    return df

# ------------------------
# LOAD DATA
# ------------------------

df = load_data()

if len(df) == 0:
    st.error("No data received from ThingSpeak")
    st.stop()

latest = df.iloc[-1]

# ------------------------
# HEADER
# ------------------------

st.title("⚡ Smart Home Energy Monitoring Dashboard")

st.caption("ESP32 + ThingSpeak + Streamlit")

# ------------------------
# KPI CARDS
# ------------------------

c1,c2,c3 = st.columns(3)

with c1:
    st.metric("Voltage (V)", round(latest["Voltage"],2))

with c2:
    st.metric("Current (A)", round(latest["Current"],2))

with c3:
    st.metric("Power (W)", round(latest["Power"],2))

c4,c5,c6 = st.columns(3)

with c4:
    st.metric("Energy (kWh)", round(latest["Energy"],4))

with c5:
    st.metric("Cost (₹)", round(latest["Cost"],2))

with c6:

    if str(latest["Alert"]).upper() in ["HIGH_USAGE","1"]:
        st.error("⚠ HIGH USAGE")
    else:
        st.success("✅ NORMAL")

# ------------------------
# CHARTS
# ------------------------

st.subheader("Power Consumption Trend")

fig1 = px.line(
    df,
    x="Time",
    y="Power",
    markers=True,
    title="Power Usage Over Time"
)

st.plotly_chart(fig1, use_container_width=True)

# ------------------------

st.subheader("Energy Consumption Trend")

fig2 = px.area(
    df,
    x="Time",
    y="Energy",
    title="Energy Usage"
)

st.plotly_chart(fig2, use_container_width=True)

# ------------------------

st.subheader("Cost Analysis")

fig3 = px.bar(
    df,
    x="Time",
    y="Cost",
    title="Estimated Electricity Cost"
)

st.plotly_chart(fig3, use_container_width=True)

# ------------------------

st.subheader("Voltage vs Current")

fig4 = px.scatter(
    df,
    x="Voltage",
    y="Current",
    size="Power",
    title="Electrical Parameters"
)

st.plotly_chart(fig4, use_container_width=True)

# ------------------------
# RAW DATA
# ------------------------

st.subheader("Live Data Table")

st.dataframe(
    df.tail(20),
    use_container_width=True
)

# ------------------------
# DOWNLOAD CSV
# ------------------------

csv = df.to_csv(index=False)

st.download_button(
    "Download CSV Report",
    csv,
    "energy_report.csv",
    "text/csv"
)

# ------------------------
# AUTO REFRESH INFO
# ------------------------

st.info("Dashboard refreshes every 15 seconds (ThingSpeak update cycle).")