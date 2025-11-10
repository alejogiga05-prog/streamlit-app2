import streamlit as st
import pandas as pd
import plotly.express as px
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Industrial", layout="wide")

# ==========================================================
# 🔒 Credenciales desde secrets.toml (Streamlit Cloud)
# ==========================================================
INFLUXDB_URL = st.secrets["INFLUXDB_URL"]
INFLUXDB_TOKEN = st.secrets["INFLUXDB_TOKEN"]
INFLUXDB_ORG = st.secrets["INFLUXDB_ORG"]
INFLUXDB_BUCKET = st.secrets["INFLUXDB_BUCKET"]

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

# ==========================================================
# 📥 Función para consultar datos
# ==========================================================
@st.cache_data(ttl=300)
def query_data(measurement, fields, start, end):
    fields_filter = " or ".join([f'r._field == "{f}"' for f in fields])

    query = f"""
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: {start}, stop: {end})
      |> filter(fn: (r) => r._measurement == "{measurement}")
      |> filter(fn: (r) => {fields_filter})
    """

    tables = query_api.query(org=INFLUXDB_ORG, query=query)
    data = [(record.get_time(), record.get_field(), record.get_value())
            for table in tables for record in table.records]

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=["time", "field", "value"])
    df = df.pivot(index="time", columns="field", values="value").reset_index()
    return df

# ==========================================================
# 🎚 Controles laterales
# ==========================================================
st.sidebar.header("Filtros")

end_date = datetime.now()
start_date = st.sidebar.date_input(
    "Fecha inicial:", value=end_date - timedelta(days=3)
)
end_date = st.sidebar.date_input("Fecha final:", value=end_date)

start_ts = datetime.combine(start_date, datetime.min.time()).isoformat() + "Z"
end_ts = datetime.combine(end_date, datetime.max.time()).isoformat() + "Z"

st.title("🔩 Tablero de Monitoreo Extreme Manufacturing")
st.write("Sensores: **DHT22 (temperatura/humedad)** y **MPU6050 (vibración)**")

# ==========================================================
# 🌡 SENSOR DHT22
# ==========================================================
st.subheader("🌡 Sensor DHT22 - Temperatura / Humedad")

fields_dht = ["temperatura", "humedad", "sensacion_termica"]
df_dht = query_data("studio-dht22", fields_dht, start_ts, end_ts)

if not df_dht.empty:
    df_dht["temp_trend"] = df_dht["temperatura"].rolling(window=5).mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temp actual", f"{df_dht['temperatura'].iloc[-1]:.2f} °C")
    col2.metric("Temp promedio", f"{df_dht['temperatura'].mean():.2f} °C")
    col3.metric("Temp min", f"{df_dht['temperatura'].min():.2f} °C")
    col4.metric("Temp max", f"{df_dht['temperatura'].max():.2f} °C")

    fig = px.line(df_dht, x="time", y=["temperatura", "temp_trend"],
                  title="Temperatura (Tendencia con promedio móvil)")
    st.plotly_chart(fig, use_container_width=True)

    st.write("📄 Datos del sensor DHT22")
    st.dataframe(df_dht)

    st.download_button(
        "⬇ Descargar datos DHT22",
        df_dht.to_csv().encode("utf-8"),
        "DHT22.csv",
    )
else:
    st.warning("⚠ No hay datos del DHT22 en este rango.")

# ==========================================================
# SENSOR MPU6050
# ==========================================================
st.subheader("📈 Sensor MPU6050 - Aceleración / Vibración")

fields_mpu = ["accel_x", "accel_y", "accel_z"]
df_mpu = query_data("mpu6050", fields_mpu, start_ts, end_ts)

if not df_mpu.empty:
    df_mpu["vibration_avg"] = df_mpu[["accel_x", "accel_y", "accel_z"]].mean(axis=1)
    df_mpu["vibration_trend"] = df_mpu["vibration_avg"].rolling(window=6).mean()

    fig2 = px.line(df_mpu, x="time",
                   y=["vibration_avg", "vibration_trend"],
                   title="Vibración (Promedio móvil)")

    st.plotly_chart(fig2, use_container_width=True)

    st.write("📄 Datos del sensor MPU6050")
    st.dataframe(df_mpu)

    st.download_button(
        "⬇ Descargar datos MPU6050",
        df_mpu.to_csv().encode("utf-8"),
        "MPU6050.csv",
    )
else:
    st.warning("⚠ No hay datos del MPU6050 en este rango.")

st.success("✅ Dashboard actualizado correctamente")


