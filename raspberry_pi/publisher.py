# publisher.py
import serial
import json
import time
import glob
import os
import paho.mqtt.client as mqtt
from datetime import datetime
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

SERIAL_BAUD = 9600
SERIAL_TIMEOUT = 1
PUBLISH_INTERVAL = 2.0  # seconds between read/publish loop iterations

def find_serial_port():
    # 嘗試多種常見路徑
    candidates = []
    candidates += glob.glob("/dev/ttyACM*")
    candidates += glob.glob("/dev/ttyUSB*")
    candidates += glob.glob("/dev/serial/by-id/*")
    # 移除 duplicates, 返回第一個存在的
    for p in candidates:
        try:
            if os.path.exists(p):
                return p
        except Exception:
            continue
    # fallback
    return "/dev/ttyACM0"

def open_serial(port):
    try:
        ser = serial.Serial(port, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)
        print(f"Opened serial port: {port}")
        return ser
    except Exception as e:
        print("Failed to open serial port", port, e)
        return None

def connect_mqtt():
    client = mqtt.Client()
    connected = False
    while not connected:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_start()
            connected = True
            print("Connected to MQTT broker:", MQTT_BROKER)
        except Exception as e:
            print("MQTT connect error:", e)
            time.sleep(5)
    return client

def main():
    port = find_serial_port()
    ser = open_serial(port)
    mqtt_client = connect_mqtt()

    last_publish = 0
    while True:
        if ser is None or not ser.is_open:
            print("Serial not open, retrying in 3s...")
            time.sleep(3)
            port = find_serial_port()
            ser = open_serial(port)
            continue

        try:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                # no data on this loop
                time.sleep(PUBLISH_INTERVAL)
                continue

            try:
                data = json.loads(line)
                # attach timestamp if not present
                if "timestamp" not in data:
                    data["timestamp"] = datetime.now().isoformat()
                mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
                print("Published:", data)
            except json.JSONDecodeError:
                # line might be partial or non-json; print for debug
                print("JSON decode error for line:", line)
            except Exception as e:
                print("Publish error:", e)
        except Exception as e:
            print("UART read error:", e)
            # if serial error, try to reopen
            try:
                ser.close()
            except Exception:
                pass
            ser = None
            time.sleep(2)

        time.sleep(PUBLISH_INTERVAL)

if __name__ == "__main__":
    main()
