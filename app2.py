
import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

# -------------------------------------------------------
# CONFIGURACIÓN DEL TABLERO
# -------------------------------------------------------
st.set_page_config(page_title="Dashboard IoT | Digitalización de Plantas", layout="wide")
st.title("Dashboard IoT - Digitalización de Plantas Productivas")

# -------------------------------------------------------
# CONEXIÓN A INFLUXDB (se toman desde Secrets de Streamlit)
# -------------------------------------------------------
url = url = st.secrets["INFLUX_URL"]
token = st.secrets["INFLUX_TOKEN"]
org = st.secrets["INFLUX_ORG"]
bucket = st.secrets["INFLUX_BUCKET"]


org = st.secrets ["0925ccf91ab36478"]
bucket = st.secrets ["EXTREME_MANUFACTURING"]

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# -------------------------------------------------------
# CONTROLES INTERACTIVOS
# -------------------------------------------------------
st.sidebar.header("Filtros del tablero")

rango = st.sidebar.selectbox(
    "Seleccionar rango de tiempo:",
    ["1h", "6h", "12h", "24h", "7d"]
)

variable = st.sidebar.selectbox(
    "Seleccionar variable:",
    ["temperature", "humidity", "vibration"]
)

# -------------------------------------------------------
# CONSULTA INFLUXDB
# -------------------------------------------------------
query = f'''
from(bucket: "{bucket}")
|> range(start: -{rango})
|> filter(fn: (r) => r._measurement == "sensor_data")
|> filter(fn: (r) => r._field == "{variable}")
'''

result = query_api.query_data_frame(org=org, query=query)

if result.empty:
    st.warning("No hay datos disponibles para este rango de tiempo.")
    st.stop()

df = result[["_time", "_value"]].rename(columns={"_time": "fecha", "_value": variable})
df["fecha"] = pd.to_datetime(df["fecha"])

# -------------------------------------------------------
# VISUALIZACIÓN PRINCIPAL
# -----------------------
