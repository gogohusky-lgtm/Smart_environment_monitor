# 感測器接線說明

## Arduino Uno 腳位配置

### DHT11
- VCC → 5V
- GND → GND
- DATA → D7
- （模組型已內建上拉電阻）

### LM35
- VCC → 5V
- GND → GND
- VOUT → A0

### CDS（光敏電阻）
- 一端 → 5V
- 另一端 → A1
- A1 → 10kΩ 電阻 → GND （上拉電阻）

## 為何使用 Arduino ADC？

由於 Raspberry Pi 無內建 ADC，
LM35 與 CDS 皆由 Arduino 進行類比讀取後再傳送至 RPi。

## UART 連線

- Arduino USB → Raspberry Pi USB
- 裝置通常為 `/dev/ttyACM0`
