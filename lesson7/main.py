import wifi_connect as wifi
import time
from umqtt.simple import MQTTClient

# MQTT 設定
MQTT_BROKER = "172.20.10.2"  # Raspberry Pi 的 IP 位址（請確認正確）
MQTT_PORT = 1883
CLIENT_ID = "pico_w_publisher"
TOPIC = "pico/test"
MAX_RETRIES = 5  # 最大重試次數
RETRY_DELAY = 2  # 重試間隔（秒）

# 嘗試連線 WiFi
wifi.connect()

# 顯示 IP
pico_ip = wifi.get_ip()
print(f"Pico W IP: {pico_ip}")
print(f"目標 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")

# 建立 MQTT 連線（帶重試機制）
print("正在連接 MQTT Broker...")
client = None

for attempt in range(1, MAX_RETRIES + 1):
    try:
        client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"✅ 已連接到 {MQTT_BROKER}:{MQTT_PORT}")
        break
    except OSError as e:
        error_code = e.args[0] if e.args else "未知"
        print(f"❌ 連接失敗 (嘗試 {attempt}/{MAX_RETRIES}): 錯誤碼 {error_code}")
        
        if attempt < MAX_RETRIES:
            print(f"等待 {RETRY_DELAY} 秒後重試...")
            time.sleep(RETRY_DELAY)
        else:
            print("❌ 無法連接到 MQTT Broker，請檢查：")
            print(f"   1. Mosquitto 服務是否運行: sudo systemctl status mosquitto")
            print(f"   2. Broker IP 是否正確: {MQTT_BROKER}")
            print(f"   3. 防火牆是否允許端口 {MQTT_PORT}")
            raise

if client is None:
    raise RuntimeError("無法建立 MQTT 連接")

# 每隔 10 秒發布一次訊息
counter = 0
while True:
    counter += 1
    message = f"Hello from Pico W! #{counter}"
    
    print("-" * 30)
    client.publish(TOPIC, message)
    print(f"已發布訊息: {message}")
    print(f"主題: {TOPIC}")
    
    print("等待 10 秒後再次發布...")
    time.sleep(10)