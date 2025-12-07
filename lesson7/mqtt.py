"""
MQTT 溫度感測器發布程式
適用於 Raspberry Pi Pico 2 / Pico W
功能：
- 連接 WiFi
- 讀取 Pico 2 內建溫度感應器
- 發布溫度數據到 MQTT Broker
"""
import network
import time
from umqtt.simple import MQTTClient
import json
from machine import Pin, ADC
# ==================== 設定區域 ====================
# WiFi 設定
WIFI_SSID = "iMask" # 請修改為您的 WiFi 名稱
WIFI_PASSWORD = "foxconn99" # 請修改為您的 WiFi 密碼
# MQTT 設定
MQTT_BROKER = "172.20.10.2" # 樹莓派的 IP 地址（請根據實際情況修改）
MQTT_PORT = 1883
MQTT_TOPIC = "客廳/感測器" # 與 app_flask.py 中的主題一致
MQTT_CLIENT_ID = "pico_sensor_001"
MQTT_KEEPALIVE = 60  # 新增：保持連線時間（秒）
# 感測器設定
# 使用 Pico 2 內建溫度感應器（ADC channel 4）
TEMPERATURE_SENSOR = ADC(4) # 內建溫度感應器固定在 ADC channel 4
# 發布間隔（秒）
PUBLISH_INTERVAL = 5 # 每 5 秒發布一次
# 注意：如果連接不穩定，可以增加此值（例如改為 10 秒）
# 連接策略選項
# 如果設為 True，每次發布後會斷開連接，發布前重新連接（更穩定但效率較低）
# 建議：如果遇到 ECONNRESET 錯誤，將此設為 True
USE_DISCONNECT_AFTER_PUBLISH = True # 設為 True 可以避免 ECONNRESET 錯誤
# LED 指示燈（可選）
LED_PIN = "LED" # Pico W 使用 "LED"，Pico 2 可能需要改為數字
# ==================================================
# 初始化內建溫度感應器
print("初始化 Pico 2 內建溫度感應器...")
# ADC(4) 是 Pico 2 內建溫度感應器，無需額外接線
# 初始化 LED
try:
    led = Pin(LED_PIN, Pin.OUT)
except:
    try:
        led = Pin(25, Pin.OUT) # 備用 LED 腳位
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
            print(f" IP 地址: {wlan.ifconfig()[0]}")
            return True
        else:
            print(f"\n❌ WiFi 連接失敗！")
            return False
    else:
        print(f"✅ WiFi 已連接")
        print(f" IP 地址: {wlan.ifconfig()[0]}")
        return True
def read_temperature():
    """讀取 Pico 2 內建溫度感應器
   
    返回:
        float: 溫度值（攝氏度），如果讀取失敗返回 None
    """
    try:
        # 讀取 ADC 值（0-65535，對應 0-3.3V）
        adc_value = TEMPERATURE_SENSOR.read_u16()
       
        # 轉換為電壓（0-3.3V）
        voltage = adc_value * 3.3 / 65535
       
        # 根據 Pico 2 規格書，溫度計算公式：
        # 溫度 = 27 - (電壓 - 0.706) / 0.001721
        temperature = 27 - (voltage - 0.706) / 0.001721
       
        # 驗證溫度是否在合理範圍內（-40 到 80°C）
        if -40 <= temperature <= 80:
            return round(temperature, 2) # 保留兩位小數
        else:
            print(f"⚠️ 溫度超出合理範圍: {temperature}°C")
            return None
           
    except Exception as e:
        print(f"❌ 讀取溫度感應器失敗: {e}")
        return None
def check_mqtt_connection(client):
    """檢查 MQTT 連接是否有效（通過處理待處理消息）"""
    try:
        # 處理任何待處理的 MQTT 消息
        # 這有助於保持連接活躍並檢測連接問題
        client.check_msg()
        return True
    except OSError:
        # 連接已斷開
        return False
    except:
        # 其他錯誤，假設連接仍然有效
        return True
def publish_data(client, temperature):
    """發布溫度數據到 MQTT Broker（使用更穩定的方式）"""
    # 構建 JSON 數據（與 app_flask.py 期望的格式一致）
    # 注意：Pico 2 沒有濕度感測器，設為 0
    data = {
        "temperature": temperature,
        "humidity": 0, # Pico 2 沒有濕度感測器
        "light_status": "未知" # 如果沒有光感測器，設為未知
    }
   
    # MicroPython 的 json.dumps 不支持 ensure_ascii 參數
    # 直接使用 json.dumps，然後編碼為 UTF-8 bytes
    # umqtt.simple 的 publish 方法需要 bytes 類型的消息
    payload_str = json.dumps(data)
    payload_bytes = payload_str.encode('utf-8')
   
    # 嘗試發布，最多重試 2 次
    for attempt in range(2):
        try:
            # 發布數據到 MQTT
            # umqtt.simple 的 publish 方法：publish(topic, msg)
            # topic 可以是字符串，msg 應該是 bytes
            client.publish(MQTT_TOPIC, payload_bytes)
           
            # 發布後立即處理消息，確保協議層完成
            try:
                client.check_msg()
            except:
                pass
           
            # 短暫延遲確保消息已發送
            time.sleep(0.1)
           
            # 顯示發布的詳細信息（用於調試）
            print(f"📤 已發布: 溫度={temperature}°C")
            print(f"   主題: {MQTT_TOPIC}")
            print(f"   數據: {payload_str}")
            return True
           
        except OSError as e:
            if attempt == 0:
                # 第一次失敗，可能是連接問題，返回 False 讓調用者重連
                print(f"❌ 發布失敗 (連接錯誤): {e}")
                return False
            else:
                # 第二次也失敗
                print(f"❌ 發布失敗 (重試後仍失敗): {e}")
                return False
        except Exception as e:
            print(f"❌ 發布失敗: {e}")
            return False
   
    return False
def create_mqtt_client():
    """創建 MQTT 客戶端"""
    # umqtt.simple 的 MQTTClient 構造函數格式：
    # MQTTClient(client_id, server, port=1883)
    # 注意：某些版本的 umqtt.simple 不支持 keepalive 參數
    # 使用最簡單的格式確保兼容性
    return MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
def reconnect_mqtt():
    """重新連接 MQTT Broker"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            mqtt_client = create_mqtt_client()
            # umqtt.simple 的 connect() 方法不接受參數
            mqtt_client.connect()
            print("✅ MQTT 重新連接成功")
            return mqtt_client
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ 重新連接失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                time.sleep(2)
            else:
                print(f"❌ MQTT 重新連接失敗 (已重試 {max_retries} 次): {e}")
    return None
def main():
    """主程式"""
    print("=" * 50)
    print(" Raspberry Pi Pico 2 溫度 MQTT 發布程式")
    print("=" * 50)
   
    # 連接 WiFi
    if not connect_wifi():
        print("無法連接 WiFi，程式結束")
        return
   
    # 連接 MQTT Broker
    print(f"\n正在連接 MQTT Broker: {MQTT_BROKER}...")
    mqtt_client = None
    try:
        # 創建 MQTT 客戶端
        mqtt_client = create_mqtt_client()
        # umqtt.simple 的 connect() 方法不接受參數
        mqtt_client.connect()
        print(f"✅ MQTT 連接成功！")
        print(f" 客戶端 ID: {MQTT_CLIENT_ID}")
        print(f" 主題: {MQTT_TOPIC}")
        print(f" Broker: {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"❌ MQTT 連接失敗: {e}")
        print(f" 請確認：")
        print(f" 1. 樹莓派 IP 地址是否正確: {MQTT_BROKER}")
        print(f" 2. MQTT Broker (mosquitto) 是否正在運行")
        print(f" 3. 防火牆是否允許 1883 端口")
        print(f" 4. Pico 和樹莓派是否在同一個網路")
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
    print("使用 Pico 2 內建溫度感應器")
    print("=" * 50)
   
    # 先測試一次感測器讀取
    print("測試溫度感應器讀取...")
    test_temp = read_temperature()
    if test_temp is not None:
        print(f"✅ 溫度感應器測試成功: {test_temp}°C")
    else:
        print("⚠️ 溫度感應器測試失敗")
        print(" 程式將繼續運行，但可能無法讀取數據...")
   
    # 主循環
    publish_count = 0
    consecutive_failures = 0 # 連續失敗計數
    max_consecutive_failures = 3 # 連續失敗 3 次後強制重連
   
    while True:
        try:
           
            # 讀取溫度
            temperature = read_temperature()
            print(f"🔍 讀取到的溫度: {temperature}°C" if temperature is not None else "⚠️ 溫度讀取失敗")
           
            if temperature is not None:
                # 如果啟用了"發布後斷開"策略，需要先連接
                if USE_DISCONNECT_AFTER_PUBLISH:
                    try:
                        # 檢查是否已連接
                        mqtt_client.check_msg()
                    except:
                        # 未連接，重新連接
                        print("重新連接 MQTT（發布前）...")
                        new_client = reconnect_mqtt()
                        if new_client:
                            mqtt_client = new_client
                        else:
                            print("❌ 無法連接，跳過本次發布")
                            time.sleep(2)
                            continue
               
                # 在發布前確保連接有效
                # 由於連接不穩定，我們採用"發布前檢查，失敗即重連"的策略
                publish_success = False
                max_publish_attempts = 2
               
                for publish_attempt in range(max_publish_attempts):
                    # 嘗試發布
                    if publish_data(mqtt_client, temperature):
                        publish_count += 1
                        consecutive_failures = 0 # 重置失敗計數
                        print(f"📊 總共已發布 {publish_count} 次")
                        publish_success = True
                       
                        # LED 快速閃爍表示成功
                        if led:
                            led.on()
                            time.sleep(0.1)
                            led.off()
                        break
                    else:
                        # 發布失敗，立即重連
                        if publish_attempt < max_publish_attempts - 1:
                            print(f"⚠️ 發布失敗，嘗試重新連接 (嘗試 {publish_attempt + 1}/{max_publish_attempts})...")
                            try:
                                mqtt_client.disconnect()
                            except:
                                pass
                            time.sleep(0.5) # 短暫等待後重連
                           
                            new_client = reconnect_mqtt()
                            if new_client:
                                mqtt_client = new_client
                            else:
                                print("❌ 無法重新連接，等待後重試...")
                                time.sleep(2)
                                break
               
                if not publish_success:
                    consecutive_failures += 1
                    print(f"⚠️ 發布最終失敗 (連續失敗 {consecutive_failures} 次)")
                    # 等待一段時間後再繼續
                    time.sleep(2)
               
                # 如果啟用了"發布後斷開"策略，現在斷開連接
                if USE_DISCONNECT_AFTER_PUBLISH and publish_success:
                    try:
                        mqtt_client.disconnect()
                    except:
                        pass
            else:
                print("⚠️ 溫度讀取失敗，跳過本次發布")
           
            # 等待下次發布
            time.sleep(PUBLISH_INTERVAL)
           
        except KeyboardInterrupt:
            print("\n\n程式被中斷")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")
            # 嘗試重新連接
            try:
                mqtt_client.disconnect()
            except:
                pass
            time.sleep(2)
            new_client = reconnect_mqtt()
            if new_client:
                mqtt_client = new_client
                consecutive_failures = 0 # 重置失敗計數
            else:
                time.sleep(5) # 發生錯誤時等待 5 秒再繼續
   
    # 清理
    try:
        mqtt_client.disconnect()
        print("✅ MQTT 已斷開連接")
    except:
        pass
if __name__ == "__main__":
    main()
