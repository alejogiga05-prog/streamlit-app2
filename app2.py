import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta
import numpy as np

# ==========================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================================
st.set_page_config(
    page_title="Dashboard Industrial Predictivo",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
<h1 style='text-align:center; color:#0A81AB;'>🔩 Dashboard Predictivo - Extreme Manufacturing</h1>
<p style='text-align:center;'>Monitoreo y proyección de sensores DHT22 (temperatura/humedad) y MPU6050 (vibración)</p>
<hr style="border:1px solid #ccc;">
""", unsafe_allow_html=True)

# ==========================================================
# CREDENCIALES
# ==========================================================
INFLUXDB_URL = st.secrets["INFLUXDB_URL"]
INFLUXDB_TOKEN = st.secrets["INFLUXDB_TOKEN"]
INFLUXDB_ORG = st.secrets["INFLUXDB_ORG"]
INFLUXDB_BUCKET = st.secrets["INFLUXDB_BUCKET"]

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

# ==========================================================
# FUNCIÓN PARA CONSULTAR DATOS
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
# CONTROLES LATERALES
# ==========================================================
st.sidebar.header("🎛️ Filtros")

end_date = datetime.now()
start_date = st.sidebar.date_input("📅 Fecha inicial", value=end_date - timedelta(days=3))
end_date = st.sidebar.date_input("📅 Fecha final", value=end_date)

start_ts = datetime.combine(start_date, datetime.min.time()).isoformat() + "Z"
end_ts = datetime.combine(end_date, datetime.max.time()).isoformat() + "Z"

# ==========================================================
# SENSOR DHT22
# ==========================================================
st.subheader("🌡 Sensor DHT22 - Temperatura / Humedad")

fields_dht = ["temperatura", "humedad", "sensacion_termica"]
df_dht = query_data("studio-dht22", fields_dht, start_ts, end_ts)

if not df_dht.empty:
    df_dht["temp_trend"] = df_dht["temperatura"].rolling(window=5).mean()

    # --- MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌞 Temp actual", f"{df_dht['temperatura'].iloc[-1]:.2f} °C")
    col2.metric("🌡 Promedio", f"{df_dht['temperatura'].mean():.2f} °C")
    col3.metric("📉 Mínimo", f"{df_dht['temperatura'].min():.2f} °C")
    col4.metric("📈 Máximo", f"{df_dht['temperatura'].max():.2f} °C")

    # --- PROYECCIÓN DE TEMPERATURA ---
    df_dht["timestamp_num"] = pd.to_datetime(df_dht["time"]).astype(int) / 10**9
    x = df_dht["timestamp_num"].values
    y = df_dht["temperatura"].values

    # Ajuste lineal (y = m*x + b)
    m, b = np.polyfit(x, y, 1)

    # Proyección de 6 horas hacia el futuro
    future_hours = 6
    future_time = np.linspace(x[-1], x[-1] + future_hours * 3600, 20)
    future_temp = m * future_time + b

    # Combinar datos actuales y proyectados
    future_df = pd.DataFrame({
        "time": pd.to_datetime(future_time, unit="s"),
        "temperatura_proyectada": future_temp
    })

    # --- GRÁFICO ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_dht["time"], y=df_dht["temperatura"],
                             mode="lines+markers", name="Temperatura real", line=dict(color="#FF5733")))
    fig.add_trace(go.Scatter(x=future_df["time"], y=future_df["temperatura_proyectada"],
                             mode="lines", name="Proyección 6h", line=dict(color="blue", dash="dash")))

    fig.update_layout(title="Evolución y Proyección de Temperatura (6h)",
                      xaxis_title="Tiempo", yaxis_title="°C")
    st.plotly_chart(fig, use_container_width=True)

    # --- DATOS ---
    st.write("📄 **Datos del sensor DHT22**")
    st.dataframe(df_dht)

    # --- PREDICCIÓN NUMÉRICA ---
    pred_temp_6h = future_temp[-1]
    st.info(f"📊 **Temperatura proyectada en 6 horas:** {pred_temp_6h:.2f} °C")

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

    # --- PROYECCIÓN DE VIBRACIÓN ---
    df_mpu["timestamp_num"] = pd.to_datetime(df_mpu["time"]).astype(int) / 10**9
    x_v = df_mpu["timestamp_num"].values
    y_v = df_mpu["vibration_avg"].values
    m_v, b_v = np.polyfit(x_v, y_v, 1)

    future_time_v = np.linspace(x_v[-1], x_v[-1] + 6 * 3600, 20)
    future_vib = m_v * future_time_v + b_v
    future_df_v = pd.Dat
