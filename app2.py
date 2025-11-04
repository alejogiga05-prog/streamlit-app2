"""
=========================================================
Dashboard IoT – Digitalización de Plantas Productivas
Autor: Alejandro Giraldo Garzón
Descripción:
    Aplicación Streamlit que se conecta a InfluxDB Cloud 
    para consultar datos historizados de sensores industriales,
    graficarlos y realizar regresión lineal.
Versión: 1.0 (2025)
=========================================================
"""

# =========================================
# IMPORTS
# =========================================
import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px


# =========================================
# CONFIGURACIÓN DE PÁGINA
# =========================================
st.set_page_config(
    page_title="Dashboard IoT | Digitalización de Plantas",
    layout="wide"
)
st.title("Dashboard IoT – Digitalización de Plantas Productivas")


# =========================================
# CONEXIÓN A INFLUXDB (USANDO SECRETS)
# =========================================
url = "https://us-east-1-1.aws.cloud2.influxdata.com"
token = st.secrets["INFLUX_TOKEN"]
org = st.secrets["ORG"]
bucket = st.secrets["BUCKET"]

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()


# =========================================
# CONTROLES INTERACTIVOS
# =========================================
st.sidebar.header("Opciones de consulta")
rango = st.sidebar.slider("Seleccionar rango de datos a visualizar (minutos):", 10, 200, 60)
variable = st.sidebar.selectbox("Variable a consultar:", ["Humedad", "Temperatura", "Vibración"])


# =========================================
# CONSULTA A INFLUXDB (MISMA QUE USABAS)
# =========================================
query = f'''
from(bucket: "{bucket}")
  |> range(start: -{rango}m)
  |> filter(fn: (r) => r["_measurement"] == "SENSORES")
  |> filter(fn: (r) => r["_field"] == "{variable}")
'''

result = query_api.query(org=org, query=query)

# Convertir resultado a DataFrame
df = pd.DataFrame([record.values for table in result for record in table.records])

if not df.empty:
    df["_time"] = pd.to_datetime(df["_time"])
    st.success(f"Datos recibidos correctamente: {len(df)} registros")
else:
    st.error("No se encontraron datos para el rango seleccionado.")
    st.stop()


# =========================================
# GRÁFICA PRINCIPAL
# =========================================
fig = px.line(df, x="_time", y="_value", title=f"{variable} en el tiempo")
st.plotly_chart(fig, use_container_width=True)


# =========================================
# REGRESIÓN LINEAL
# =========================================
df["t"] = np.arange(len(df)).reshape(-1, 1)
model = LinearRegression().fit(df[["t"]], df["_value"])
df["pred"] = model.pr
