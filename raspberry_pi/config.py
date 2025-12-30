# config.py
# MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"
MQTT_ALERT_TOPIC = "sensor/alerts"

# CSV log
CSV_FILE = "sensor_log.csv"

# Thresholds (will publish alert when exceeded)
THRESHOLDS = {
    "LM35_Temp": 36.0,
    "CDS_Light": 800,
    "DHT_Temp": 36.0,
    "DHT_Humd": 70.0
}

# InfluxDB configuration
INFLUX_ENABLED = True

# Use InfluxDB v2 client (influxdb-client). If False, code will try to use InfluxDB v1 client.
INFLUX_USE_V2 = True

# InfluxDB v2 settings (only used if INFLUX_USE_V2=True)
INFLUX_V2_URL = "http://localhost:8086"
INFLUX_V2_ORG = "home-lab"
INFLUX_V2_BUCKET = "sensor_bucket"
INFLUX_V2_TOKEN = "ThRYHt9IdQK6jogjWf2eaXxN1dTAO8udCTMi85QJl1bLeH3EwFSbPipDtxQ6TipXlDXuBFNtgAUGBshltUiXuQ=="
INFLUX_USE_V2 = True

# InfluxDB v1 settings (only used if INFLUX_USE_V2=False)
INFLUX_V1_HOST = "localhost"
INFLUX_V1_PORT = 8086
INFLUX_V1_USERNAME = ""
INFLUX_V1_PASSWORD = ""
INFLUX_V1_DATABASE = "sensor_db"
