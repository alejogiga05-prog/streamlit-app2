import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Título de la app ---
st.title("🌡️ Monitoreo Industrial de Temperatura")

# --- Datos simulados ---
st.subheader("Datos de temperatura simulados")
dias = pd.date_range("2025-01-01", periods=7)
temperaturas = np.random.uniform(18, 35, size=7)
df = pd.DataFrame({"Fecha": dias, "Temperatura (°C)": temperaturas})

st.dataframe(df)

# --- Gráfico ---
fig = px.line(df, x="Fecha", y="Temperatura (°C)", title="Variación de la temperatura")
st.plotly_chart(fig)

# --- Promedio ---
promedio = df["Temperatura (°C)"].mean()
st.metric("Temperatura promedio", f"{promedio:.2f} °C")

# --- Mensaje ---
if promedio > 30:
    st.warning("⚠️ La temperatura promedio es muy alta.")
else:
    st.success("✅ Temperatura dentro de los límites normales.")
