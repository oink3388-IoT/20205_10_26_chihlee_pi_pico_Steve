"""
MQTT 溫濕度感測器發布程式 - 主程式
適用於 Raspberry Pi Pico 2 / Pico W

使用方式：
1. 修改 config.py 中的 WiFi 和 MQTT 設定
2. 將此程式上傳到 Pico
3. 確保已安裝必要的 MicroPython 套件：
   - umqtt.simple (通常內建)
   - dht (通常內建)
4. 連接 DHT11/DHT22 到指定的 GPIO 腳位
5. 執行此程式

接線說明（DHT22）：
- VCC -> 3.3V
- GND -> GND
- DATA -> GPIO 16 (可在 config.py 中修改)
"""

import network
import time
from umqtt.simple import MQTTClient
import json
from machine import Pin
import dht

# 導入設定（如果 config.py 存在）
try:
    from config import (
        WIFI_SSID, WIFI_PASSWORD,
        MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_CLIENT_ID,
        DHT_PIN, DHT_TYPE, PUBLISH_INTERVAL
    )
except ImportError:
    # 如果沒有 config.py，使用預設值
    print("⚠️  未找到 config.py，使用預設設定")
    WIFI_SSID = "YOUR_WIFI_SSID"
    WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
    MQTT_BROKER = "192.168.0.210"
    MQTT_PORT = 1883
    MQTT_TOPIC = "客廳/感測器"
    MQTT_CLIENT_ID = "pico_sensor_001"
    DHT_PIN = 16
    DHT_TYPE = "DHT22"  # 字串格式，會在程式中轉換
    PUBLISH_INTERVAL = 10

# 初始化感測器
# 根據設定選擇感測器類型
if isinstance(DHT_TYPE, str):
    if DHT_TYPE.upper() == "DHT11":
        sensor = dht.DHT11(Pin(DHT_PIN))
    else:
        sensor = dht.DHT22(Pin(DHT_PIN))
else:
    # 如果直接傳入 dht.DHT11 或 dht.DHT22 物件
    sensor = DHT_TYPE(Pin(DHT_PIN))

# 初始化 LED
try:
    led = Pin("LED", Pin.OUT)
except:
    try:
        led = Pin(25, Pin.OUT)
    except:
        led = None

def connect_wifi():
    """連接 WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"正在連接 WiFi: {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # 等待連接，最多等待 20 秒
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print(".", end="")
        
        if wlan.isconnected():
            print(f"\n✅ WiFi 連接成功！")
            print(f"   IP 地址: {wlan.ifconfig()[0]}")
            return True
        else:
            print(f"\n❌ WiFi 連接失敗！")
            return False
    else:
        print(f"✅ WiFi 已連接")
        print(f"   IP 地址: {wlan.ifconfig()[0]}")
        return True

def read_sensor():
    """讀取溫濕度感測器數據"""
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        return temperature, humidity
    except Exception as e:
        print(f"❌ 讀取感測器失敗: {e}")
        return None, None

def publish_data(client, temperature, humidity):
    """發布數據到 MQTT Broker"""
    # 構建 JSON 數據（與 app_flask.py 期望的格式一致）
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "light_status": "未知"  # 如果沒有光感測器，設為未知
    }
    
    payload = json.dumps(data)
    
    try:
        client.publish(MQTT_TOPIC, payload.encode())
        print(f"📤 已發布: 溫度={temperature}°C, 濕度={humidity}%")
        return True
    except Exception as e:
        print(f"❌ 發布失敗: {e}")
        return False

def main():
    """主程式"""
    print("=" * 50)
    print(" Raspberry Pi Pico 溫濕度 MQTT 發布程式")
    print("=" * 50)
    
    # 連接 WiFi
    if not connect_wifi():
        print("無法連接 WiFi，程式結束")
        return
    
    # 連接 MQTT Broker
    print(f"\n正在連接 MQTT Broker: {MQTT_BROKER}...")
    try:
        mqtt_client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
        mqtt_client.connect()
        print(f"✅ MQTT 連接成功！")
    except Exception as e:
        print(f"❌ MQTT 連接失敗: {e}")
        print(f"   請確認：")
        print(f"   1. 樹莓派 IP 地址是否正確: {MQTT_BROKER}")
        print(f"   2. MQTT Broker (mosquitto) 是否正在運行")
        return
    
    # LED 指示燈閃爍表示連接成功
    if led:
        for _ in range(3):
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.2)
    
    print(f"\n開始發布數據到主題: {MQTT_TOPIC}")
    print(f"發布間隔: {PUBLISH_INTERVAL} 秒")
    print("=" * 50)
    
    # 主循環
    publish_count = 0
    while True:
        try:
            # 讀取感測器
            temperature, humidity = read_sensor()
            
            if temperature is not None and humidity is not None:
                # 發布數據
                if publish_data(mqtt_client, temperature, humidity):
                    publish_count += 1
                    print(f"📊 總共已發布 {publish_count} 次")
                    
                    # LED 快速閃爍表示成功
                    if led:
                        led.on()
                        time.sleep(0.1)
                        led.off()
                else:
                    # 發布失敗，嘗試重新連接
                    print("嘗試重新連接 MQTT...")
                    try:
                        mqtt_client.disconnect()
                        time.sleep(2)
                        mqtt_client.connect()
                        print("✅ MQTT 重新連接成功")
                    except Exception as e:
                        print(f"❌ MQTT 重新連接失敗: {e}")
            else:
                print("⚠️  感測器讀取失敗，跳過本次發布")
            
            # 等待下次發布
            time.sleep(PUBLISH_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n程式被中斷")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            time.sleep(5)  # 發生錯誤時等待 5 秒再繼續
    
    # 清理
    try:
        mqtt_client.disconnect()
        print("✅ MQTT 已斷開連接")
    except:
        pass

if __name__ == "__main__":
    main()
