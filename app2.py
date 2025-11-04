
import pandas as pd
from influxdb_client import InfluxDBClient
import matplotlib.pyplot as plt

# --- Parámetros de conexión ---
INFLUXDB_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUXDB_TOKEN = "JcKXoXE30JQvV9Ggb4-zv6sQc0Zh6B6Haz5eMRW0FrJEduG2KcFJN9-7RoYvVORcFgtrHR-Q_ly-52pD7IC6JQ=="
INFLUXDB_ORG = "0925ccf91ab36478"
INFLUXDB_BUCKET = "EXTREME_MANUFACTURING"

# --- Inicializar cliente ---
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

# --- Consulta de datos DHT22 ---
query_dht22 = '''
from(bucket: "EXTREME_MANUFACTURING")
  |> range(start: -15d, stop: -10d)
  |> filter(fn: (r) => r._measurement == "studio-dht22")
  |> filter(fn: (r) => r._field == "humedad" or r._field == "temperatura" or r._field == "sensacion_termica")
'''

tables_dht22 = query_api.query(org=INFLUXDB_ORG, query=query_dht22)
data_dht22 = []
for table in tables_dht22:
    for record in table.records:
        data_dht22.append((record.get_time(), record.get_field(), record.get_value()))

# --- Consulta de datos MPU6050 ---
query_mpu = '''
from(bucket: "EXTREME_MANUFACTURING")
  |> range(start: -8d, stop: -7d)
  |> filter(fn: (r) => r._measurement == "mpu6050")
  |> filter(fn: (r) =>
      r._field == "accel_x" or r._field == "accel_y" or r._field == "accel_z" or
      r._field == "gyro_x" or r._field == "gyro_y" or r._field == "gyro_z" or
      r._field == "temperature")
'''

tables_mpu = query_api.query(org=INFLUXDB_ORG, query=query_mpu)
data_mpu = []
for table in tables_mpu:
    for record in table.records:

        # --- Visualización de datos DHT22 ---
df_dht22 = pd.DataFrame(data_dht22, columns=["time", "field", "value"])
df_dht22 = df_dht22.pivot(index="time", columns="field", values="value")
df_dht22.plot(subplots=True, figsize=(10,6), title="Variables DHT22")
plt.show()

# --- Visualización de datos MPU6050 ---
df_mpu = pd.DataFrame(data_mpu, columns=["time", "field", "value"])
df_mpu = df_mpu.pivot(index="time", columns="field", values="value")
df_mpu.plot(subplots=True, figsize=(10,8), title="Variables MPU6050")
plt.show()

        data_mpu.append((record.get_time(), record.get_field(), record.get_value()))
