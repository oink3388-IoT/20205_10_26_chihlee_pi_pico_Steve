"""
設定檔 - 請根據您的實際環境修改這些設定
"""

# WiFi 設定
WIFI_SSID = "YOUR_WIFI_SSID"  # 請修改為您的 WiFi 名稱
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"  # 請修改為您的 WiFi 密碼

# MQTT 設定
# 請將此 IP 改為您的樹莓派 IP 地址
# 可以在樹莓派上執行: hostname -I 來查看 IP
MQTT_BROKER = "192.168.0.210"  # 樹莓派的 IP 地址
MQTT_PORT = 1883
MQTT_TOPIC = "客廳/感測器"  # 與 app_flask.py 中的主題一致
MQTT_CLIENT_ID = "pico_sensor_001"

# 感測器設定
DHT_PIN = 16  # DHT11/DHT22 數據線連接的 GPIO 腳位
# DHT_TYPE 選項: "DHT11" 或 "DHT22"
DHT_TYPE = "DHT22"  # 根據您使用的感測器型號修改

# 發布間隔（秒）
PUBLISH_INTERVAL = 10  # 每 10 秒發布一次

