# Raspberry Pi Pico 溫濕度 MQTT 發布程式

這個程式讓 Raspberry Pi Pico 2 / Pico W 讀取 DHT11/DHT22 溫濕度感測器，並將數據發布到 MQTT Broker。

## 📋 功能

- ✅ WiFi 連接
- ✅ DHT11/DHT22 溫濕度感測器讀取
- ✅ MQTT 數據發布
- ✅ 自動重連機制
- ✅ LED 狀態指示

## 🔧 硬體需求

- Raspberry Pi Pico 2 或 Pico W（需要 WiFi 功能）
- DHT11 或 DHT22 溫濕度感測器
- 連接線

## 📡 接線說明（DHT22）

```
DHT22          Pico
-----          ----
VCC    ->      3.3V
GND    ->      GND
DATA   ->      GPIO 16 (可在 config.py 中修改)
```

**注意：** DHT11/DHT22 的 DATA 腳位建議連接一個 4.7kΩ 上拉電阻到 3.3V。

## 📦 安裝步驟

### 1. 上傳檔案到 Pico

將以下檔案上傳到 Pico：
- `main.py` - 主程式
- `config.py` - 設定檔（可選，如果沒有會使用預設值）

### 2. 修改設定

編輯 `config.py` 或直接在 `main.py` 中修改：

```python
# WiFi 設定
WIFI_SSID = "您的WiFi名稱"
WIFI_PASSWORD = "您的WiFi密碼"

# MQTT 設定
MQTT_BROKER = "192.168.0.210"  # 樹莓派的 IP 地址
```

**如何查看樹莓派 IP 地址：**
```bash
hostname -I
```

### 3. 確認 MQTT Broker 運行

在樹莓派上確認 mosquitto 正在運行：
```bash
sudo systemctl status mosquitto
```

如果沒有運行，啟動它：
```bash
sudo systemctl start mosquitto
```

## 🚀 使用方式

### 方法 1：使用 Thonny IDE

1. 打開 Thonny IDE
2. 連接 Pico
3. 打開 `main.py`
4. 點擊「運行」按鈕

### 方法 2：上傳後自動運行

將 `main.py` 上傳到 Pico 後，重新啟動 Pico，程式會自動運行。

## 📊 數據格式

程式會發布以下 JSON 格式的數據到 MQTT 主題 `客廳/感測器`：

```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "light_status": "未知"
}
```

這個格式與 `app_flask.py` 期望的格式完全一致。

## 🔍 故障排除

### WiFi 連接失敗

- 確認 WiFi SSID 和密碼正確
- 確認 Pico 在 WiFi 訊號範圍內
- 檢查 WiFi 是否支援 2.4GHz（Pico W 不支援 5GHz）

### MQTT 連接失敗

- 確認樹莓派 IP 地址正確
- 確認 mosquitto 正在運行
- 確認防火牆沒有阻擋 1883 端口
- 檢查 Pico 和樹莓派是否在同一個網路

### 感測器讀取失敗

- 確認接線正確
- 確認 GPIO 腳位設定正確
- 檢查感測器是否損壞
- 確認上拉電阻已連接（建議 4.7kΩ）

### 數據沒有出現在網頁上

- 確認 MQTT 主題名稱一致：`客廳/感測器`
- 檢查 Flask 應用程式是否正在運行
- 查看 Flask 應用程式的日誌

## 📝 設定說明

### config.py 設定項目

| 設定項 | 說明 | 預設值 |
|--------|------|--------|
| `WIFI_SSID` | WiFi 網路名稱 | `YOUR_WIFI_SSID` |
| `WIFI_PASSWORD` | WiFi 密碼 | `YOUR_WIFI_PASSWORD` |
| `MQTT_BROKER` | MQTT Broker IP 地址 | `192.168.0.210` |
| `MQTT_PORT` | MQTT 端口 | `1883` |
| `MQTT_TOPIC` | MQTT 主題 | `客廳/感測器` |
| `MQTT_CLIENT_ID` | MQTT 客戶端 ID | `pico_sensor_001` |
| `DHT_PIN` | DHT 感測器 GPIO 腳位 | `16` |
| `DHT_TYPE` | 感測器類型 | `dht.DHT22` |
| `PUBLISH_INTERVAL` | 發布間隔（秒） | `10` |

## 💡 進階使用

### 修改發布間隔

在 `config.py` 中修改 `PUBLISH_INTERVAL`：
```python
PUBLISH_INTERVAL = 30  # 改為 30 秒發布一次
```

### 使用 DHT11 感測器

在 `config.py` 中修改：
```python
DHT_TYPE = dht.DHT11
```

### 修改 GPIO 腳位

在 `config.py` 中修改：
```python
DHT_PIN = 20  # 改為 GPIO 20
```

## 📚 相關檔案

- `app_flask.py` - Flask 應用程式（接收 MQTT 數據）
- `main.py` - Pico 主程式
- `config.py` - 設定檔

## 🎯 測試

上傳程式後，您應該會看到類似以下的輸出：

```
==================================================
 Raspberry Pi Pico 溫濕度 MQTT 發布程式
==================================================
正在連接 WiFi: YourWiFi...
✅ WiFi 連接成功！
   IP 地址: 192.168.0.105

正在連接 MQTT Broker: 192.168.0.210...
✅ MQTT 連接成功！

開始發布數據到主題: 客廳/感測器
發布間隔: 10 秒
==================================================
📤 已發布: 溫度=25.5°C, 濕度=60.0%
📊 總共已發布 1 次
📤 已發布: 溫度=25.6°C, 濕度=60.1%
📊 總共已發布 2 次
...
```

同時，在 Flask 應用程式的網頁上應該會看到即時更新的溫濕度數據。


