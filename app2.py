import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

st.title("🔍 Comparativa: Temperatura vs Vibración")

# === Carga de datos ===
df_mpu = pd.read_csv("datos_mpu.csv")  # Ajusta el nombre de tu archivo

# Mostrar columnas para verificar
st.write("Columnas del DataFrame:", df_mpu.columns)

# Asegúrate de usar los nombres correctos según tu CSV
x = df_mpu["temperatura"].values.reshape(-1, 1)
y = df_mpu["vibracion"].values  # cámbialo según tu columna real

# === Modelo de regresión ===
modelo = LinearRegression()
modelo.fit(x, y)

# Predicciones (tendencia actual)
y_pred = modelo.predict(x)

# === Visualización ===
fig = px.scatter(
    df_mpu,
    x="temperatura",
    y="vibracion",
    title="Relación entre Temperatura y Vibración",
    color_discrete_sequence=["#9B59B6"]
)

# Añadir línea de tendencia
fig.add_scatter(x=df_mpu["temperatura"], y=y_pred, mode='lines', name='Tendencia', line=dict(color='red'))

st.plotly_chart(fig)

# === Proyecciones futuras ===
# Generar temperaturas futuras (por ejemplo, los próximos 5 puntos)
future_temps = np.linspace(df_mpu["temperatura"].min(), df_mpu["temperatura"].max() + 10, 5).reshape(-1, 1)
future_preds = modelo.predict(future_temps)

future_df = pd.DataFrame({
    "Temperatura proyectada": future_temps.flatten(),
    "Vibración estimada": future_preds
})

st.subheader("📈 Proyecciones basadas en el modelo")
st.dataframe(future_df)

# === Métricas del modelo ===
st.write("**Coeficiente (pendiente):**", modelo.coef_[0])
st.write("**Intersección:**", modelo.intercept_)
st.write(f"**Ecuación del modelo:** Vibración = {modelo.coef_[0]:.3f} * Temperatura + {modelo.intercept_:.3f}")
