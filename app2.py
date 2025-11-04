
import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px

# -----------------------------
# 1. CONFIGURACIÓN DE LA APP
# -----------------------------
st.set_page_config(layout="wide", page_title="Dashboard IoT - Producción")

st.title("📊 Digitalización de Plantas Productivas - Dashboard IoT")

# -----------------------------
# 2. CONEXIÓN A INFLUXDB
# -----------------------------
url = st.secrets["https://us-east-1-1.aws.cloud2.influxdata.com"]
token = st.secrets["JcKXoXE30JQvV9Ggb4-zv6sQc0Zh6B6Haz5eMRW0FrJEduG2KcFJN9-7RoYvVORcFgtrHR-Q_ly-52pD7IC6JQ=="]
org = st.secrets["0925ccf91ab36478"]
bucket = st.secrets["EXTREME_MANUFACTURING"]

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# -----------------------------
# 3. CONSULTA DINÁMICA
# -----------------------------
rango = st.sidebar.selectbox("Seleccionar rango de tiempo", ["1h", "6h", "12h", "24h", "7d"])
variable = st.sidebar.selectbox("Variable", ["temperature", "humidity", "vibration"])

query = f'''
from(bucket: "{bucket}")
|> range(start: -{rango})
|> filter(fn: (r) => r._measurement == "sensor_data")
|> filter(fn: (r) => r._field == "{variable}")
'''

result = query_api.query_data_frame(org=org, query=query)

if result.empty:
    st.warning("No hay datos disponibles para el rango seleccionado.")
    st.stop()

df = result[["_time", "_value"]].rename(columns={"_time": "fecha", "_value": variable})
df["fecha"] = pd.to_datetime(df["fecha"])

# -----------------------------
# 4. VISUALIZACIÓN
# -----------------------------
fig = px.line(df, x="fecha", y=variable, title=f"📈 {variable} en el tiempo")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 5. MÉTRICAS (KPI)
# -----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Valor actual", round(df[variable].iloc[-1], 2))
col2.metric("Promedio", round(df[variable].mean(), 2))
col3.metric("Máximo", round(df[variable].max(), 2))
col4.metric("Mínimo", round(df[variable].min(), 2))

# -----------------------------
# 6. MODELO PREDICTIVO (REGRESIÓN LINEAL)
# -----------------------------
df["index"] = np.arange(len(df))
X = df[["index"]]
y = df[[variable]]

model = LinearRegression().fit(X, y)
df["pred"] = model.predict(X)

fig_pred = px.line(df, x="fecha", y=["pred", variable"], title="🔮 Predicción (Regresión Lineal)")
st.plotly_chart(fig_pred, use_container_width=True)
