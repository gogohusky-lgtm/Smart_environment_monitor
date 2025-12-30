# main.py
from flask import Flask, render_template, jsonify, request
import paho.mqtt.client as mqtt
import json
import threading
from config import (MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_ALERT_TOPIC,
                    THRESHOLDS, CSV_FILE, INFLUX_ENABLED, INFLUX_USE_V2,
                    INFLUX_V2_URL, INFLUX_V2_TOKEN, INFLUX_V2_ORG, INFLUX_V2_BUCKET,
                    INFLUX_V1_HOST, INFLUX_V1_PORT, INFLUX_V1_USERNAME, INFLUX_V1_PASSWORD, INFLUX_V1_DATABASE)
import csv
from datetime import datetime
import time
import traceback

app = Flask(__name__)
latest_data = {}
data_lock = threading.Lock()
history = []  # list of dicts, limited length
HISTORY_LIMIT = 600  # keep recent N points

# Influx clients (initialized later)
influx_client = None
influx_write_api = None
influx_v1_client = None

def init_csv():
    try:
        # use 'x' to only create if doesn't exist
        with open(CSV_FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "LM35_Temp", "DHT_Temp", "DHT_Humd", "CDS_Light", "raw_json"])
    except FileExistsError:
        pass

def save_to_csv(data):
    # always append, include raw JSON for debugging
    try:
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                data.get("LM35_Temp"),
                data.get("DHT_Temp"),
                data.get("DHT_Humd"),
                data.get("CDS_Light"),
                json.dumps(data, ensure_ascii=False)
            ])
    except Exception as e:
        print("CSV write error:", e)

def send_influx(data):
    if not INFLUX_ENABLED:
        return

    from influxdb_client import Point

    p = (
        Point("environment")
        .tag("source", "arduino_uno")
        .field("LM35_Temp", float(data["LM35_Temp"]))
        .field("DHT_Temp", float(data["DHT_Temp"]))
        .field("DHT_Humd", float(data["DHT_Humd"]))
        .field("CDS_Light", float(data["CDS_Light"]))
    )

    influx_write_api.write(
        bucket=INFLUX_V2_BUCKET,
        org=INFLUX_V2_ORG,
        record=p
    )

def check_thresholds_and_alert(data, mqtt_client):
    alerts = []
    try:
        for key, thresh in THRESHOLDS.items():
            if key in data and data[key] is not None:
                try:
                    val = float(data[key])
                    if thresh is not None and val >= thresh:
                        alerts.append({"metric": key, "value": val, "threshold": thresh, "time": datetime.now().isoformat()})
                except Exception:
                    continue
        if alerts and mqtt_client is not None:
            # publish alerts as JSON list
            mqtt_client.publish(MQTT_ALERT_TOPIC, json.dumps({"alerts": alerts}))
            print("Published alerts:", alerts)
    except Exception as e:
        print("Threshold check error:", e)

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("MQTT connected with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global latest_data, history
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        # ensure numeric fields if possible
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()
        # Save latest and history safely
        with data_lock:
            latest_data = data
            history.append(data.copy())
            if len(history) > HISTORY_LIMIT:
                history = history[-HISTORY_LIMIT:]
        print("MQTT Received:", data)
        # Save CSV
        save_to_csv(data)
        # Write to InfluxDB
        send_influx(data)
        # Check thresholds
        check_thresholds_and_alert(data, client)
    except Exception as e:
        print("MQTT parse error:", e)
        traceback.print_exc()

def setup_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            break
        except Exception as e:
            print("MQTT connect failed, retrying in 5s:", e)
            time.sleep(5)
    return client

def setup_influx():
    global influx_client, influx_write_api, influx_v1_client
    if not INFLUX_ENABLED:
        print("InfluxDB disabled in config.")
        return
    try:
        if INFLUX_USE_V2:
            # try import v2 client
            from influxdb_client import InfluxDBClient, WriteOptions
            influx_client = InfluxDBClient(url=INFLUX_V2_URL, token=INFLUX_V2_TOKEN, org=INFLUX_V2_ORG)
            influx_write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))
            print("InfluxDB v2 client initialized.")
        else:
            # v1
            from influxdb import InfluxDBClient as InfluxDBClientV1
            influx_v1_client = InfluxDBClientV1(host=INFLUX_V1_HOST, port=INFLUX_V1_PORT,
                                                username=INFLUX_V1_USERNAME, password=INFLUX_V1_PASSWORD,
                                                database=INFLUX_V1_DATABASE)
            # create db if not exists
            databases = influx_v1_client.get_list_database()
            if not any(d["name"] == INFLUX_V1_DATABASE for d in databases):
                influx_v1_client.create_database(INFLUX_V1_DATABASE)
            print("InfluxDB v1 client initialized.")
    except Exception as e:
        print("InfluxDB setup error:", e)
        traceback.print_exc()

# Flask routes
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/data")
def data():
    with data_lock:
        return jsonify(latest_data)

@app.route("/history")
def get_history():
    # optional ?n=50
    n = request.args.get("n", default=200, type=int)
    with data_lock:
        data_slice = history[-n:]
        return jsonify(data_slice)

if __name__ == "__main__":
    init_csv()
    setup_influx()
    mqtt_client = setup_mqtt()
    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        try:
            mqtt_client.loop_stop()
        except Exception:
            pass
        try:
            if influx_client:
                influx_client.close()
        except Exception:
            pass
