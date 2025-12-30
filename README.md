# **Smart environment monitoring system**
## Executive Summary

This project demonstrates an end-to-end IoT environment monitoring system integrating microcontroller-based sensor acquisition, edge computing, real-time visualization, and time-series data storage.

An Arduino Uno is used for multi-sensor sampling and analog-to-digital conversion, while a Raspberry Pi 5 acts as an edge node responsible for data validation, MQTT-based messaging, and system-level integration. Sensor data is visualized in real time through a Flask-based dashboard and stored in InfluxDB for historical analysis using Grafana.

The project emphasizes a clear separation of responsibilities between hardware-level data acquisition and Linux-based edge processing. Although all services run on Raspberry Pi 5 in this demo, the data pipeline is designed to be deployable across multiple nodes, making it suitable as a practical showcase for embedded and IoT engineering roles.

---


## 智慧環境監測站（Arduino + Raspberry Pi + MQTT + InfluxDB + Grafana）

本專案是一個完整的 IoT 入門到中階整合範例，展示多感測器資料蒐集、跨裝置通訊、即時視覺化與時間序列資料儲存。

## 系統架構
本系統採用「感測 / 邊緣處理 / 資料管線 / 視覺化」的分層架構設計：

![系統架構圖](docs/system_architecture.png)

## Demo video
本影片展示由 Arduino 收集後，藉由 MQTT 傳輸至 Raspberry Pi 之即時感應器數據，並儲存於 influxDB，且藉由 Grafana 與 Flask 面板視覺化。

https://youtu.be/Ifh9Rky5IHM

## 使用的感測器

- DHT11：溫度 / 濕度（Digital）
- LM35：類比溫度感測器（Analog）
- CDS（光敏電阻）：光照強度（Analog，需上拉電阻）

## 硬體配置與職責劃分

Arduino Uno 負責：
- 感測器讀取
- 類比訊號 ADC 轉換（LM35 / CDS）
- 感測資料封裝為 JSON
- 每 2 秒經由 UART 傳送

Raspberry Pi 5 負責：
- UART 資料接收與解析
- 感測資料基本驗證與門檻判斷
- MQTT Publisher / Subscriber
- Flask 即時監控 Dashboard
- InfluxDB 時間序列資料寫入
- Grafana 歷史資料視覺化

## 軟體元件

- Python 3
- Flask
- paho-mqtt
- influxdb-client (v2)
- InfluxDB 2.x
- Grafana
- Mosquitto MQTT Broker

## 啟動順序

1. 啟動 MQTT Broker
2. 啟動 InfluxDB
3. 啟動 Grafana
4. Arduino 上電
5. Raspberry Pi：
   ```bash
   python publisher.py
   python main.py
6. 開啟瀏覽器：

    Flask Dashboard：http://localhost:5000

    influxdb: http://localhost:8086

    Grafana：http://localhost:3000

## 設計決策 & 已知限制

### 設計決策

- 使用 Arduino Uno 處理感測與 ADC，避免 Raspberry Pi 在 Linux 環境下直接處理即時硬體 I/O 與類比訊號。
- 感測資料於 Edge（Raspberry Pi）端進行基本驗證後再寫入資料庫，降低資料污染風險。
- 採用 MQTT 作為裝置間通訊協定，利於未來擴充多節點感測架構。
- Flask Dashboard 僅用於即時監看與除錯，歷史趨勢分析交由 Grafana 處理。

### 已知問題及限制

- DHT11 感測精度有限，僅適合示範用途，未適用於高精度環境監控。
- UART 傳輸目前未加入 CRC 或重送機制，假設傳輸環境穩定。
- InfluxDB Token 目前以設定檔方式載入，未實作進階金鑰管理或權限分級。
- 系統尚未加入 systemd service 或 container-based deployment，重啟需人工介入。


## 備註

- InfluxDB Token 請自行建立並填入 config.py
- 本專案設計目標為學習與展示用途


## 專案目錄結構
```text
smart_environment_monitor/
├── arduino/
│   └── DHT11-LM35-CDS.ino
│
├── docs/
│   └── wiring.md
│   ├── requirements.txt
│   └── system_architecture.png
│
├── raspberry_pi/
│   ├── main.py
│   ├── publisher.py
│   ├── config.py
│   └── templates/
│       └── dashboard.html
│
├── screenshots_demo
│   ├── flask_dashboard.png
│   └── grafana_dashboard.png
│   └── influxdb_dashboard.png
|
└── README.md
```

## License Notice

The source code in this repository is released under the MIT License.

Demo materials, including videos, photos, logs, and generated data under the following directories are provided for demonstration purposes only and are NOT covered by the MIT License:

- screenshots_demo/

These materials may not be redistributed or reused without explicit permission.