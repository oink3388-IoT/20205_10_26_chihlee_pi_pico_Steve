"""
MQTT 測試發布腳本
用於測試 Streamlit MQTT 監控應用程式

使用方式：
1. 使用 shell 腳本（推薦）：
   ./test_mqtt.sh
   或
   ./test_mqtt.sh continuous 5 10

2. 手動啟動虛擬環境後執行：
   source ../.venv/bin/activate
   python test_mqtt_publish.py
"""
import sys
import os

# 檢查是否在虛擬環境中
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("⚠️  警告：未偵測到虛擬環境！")
    print("請使用以下方式執行：")
    print("  方法 1: ./test_mqtt.sh")
    print("  方法 2: source ../.venv/bin/activate && python test_mqtt_publish.py")
    print("\n或按 Ctrl+C 取消，然後使用正確的方式執行。")
    print("等待 3 秒後繼續...")
    import time
    time.sleep(3)

import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime
from config import (
    MQTT_BROKER_HOST, MQTT_BROKER_PORT,
    MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_HUMIDITY, MQTT_TOPIC_LIGHT
)


def publish_test_data():
    """發布測試數據"""
    client = mqtt.Client(
        client_id="test_publisher",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        client.loop_start()
        time.sleep(1)
        
        print("=" * 50)
        print("開始發布測試數據...")
        print("=" * 50)
        
        # 測試 1: 發布電燈狀態
        print("\n[測試 1] 發布電燈狀態: ON")
        client.publish(MQTT_TOPIC_LIGHT, "on", qos=1)
        time.sleep(1)
        
        # 測試 2: 發布溫度
        temperature = round(random.uniform(20, 30), 1)
        print(f"\n[測試 2] 發布溫度: {temperature}°C")
        client.publish(MQTT_TOPIC_TEMPERATURE, str(temperature), qos=1)
        time.sleep(1)
        
        # 測試 3: 發布濕度
        humidity = round(random.uniform(40, 70), 1)
        print(f"\n[測試 3] 發布濕度: {humidity}%")
        client.publish(MQTT_TOPIC_HUMIDITY, str(humidity), qos=1)
        time.sleep(1)
        
        # 測試 4: 發布 JSON 格式的完整數據
        data = {
            "temperature": round(random.uniform(20, 30), 1),
            "humidity": round(random.uniform(40, 70), 1),
            "light": "on",
            "timestamp": datetime.now().isoformat()
        }
        print(f"\n[測試 4] 發布 JSON 格式數據:")
        print(f"  {json.dumps(data, indent=2, ensure_ascii=False)}")
        client.publish("home/living_room/data", json.dumps(data), qos=1)
        time.sleep(1)
        
        # 測試 5: 連續發布多筆數據（模擬感測器）
        test_count = 30  # 增加到 30 筆
        print(f"\n[測試 5] 連續發布 {test_count} 筆模擬感測器數據（每 1 秒一次）...")
        for i in range(test_count):
            temp = round(random.uniform(20, 30), 1)
            hum = round(random.uniform(40, 70), 1)
            light_state = "on" if i % 2 == 0 else "off"
            
            client.publish(MQTT_TOPIC_TEMPERATURE, str(temp), qos=1)
            client.publish(MQTT_TOPIC_HUMIDITY, str(hum), qos=1)
            client.publish(MQTT_TOPIC_LIGHT, light_state, qos=1)
            
            # 每 5 筆顯示一次，避免輸出太多
            if (i + 1) % 5 == 0 or i == 0:
                print(f"  [{i+1}/{test_count}] 溫度: {temp}°C, 濕度: {hum}%, 電燈: {light_state}")
            time.sleep(1)  # 減少到 1 秒間隔
        
        print("\n" + "=" * 50)
        print("✓ 測試數據發布完成！")
        print("=" * 50)
        
        time.sleep(1)
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"✗ 發布測試數據時發生錯誤: {e}")


def publish_continuous_data(interval=1, count=100):
    """持續發布數據（用於長時間測試）
    
    預設參數：
    - interval: 發布間隔（秒），預設 1 秒
    - count: 發布次數，預設 100 次
    """
    client = mqtt.Client(
        client_id="test_publisher_continuous",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        client.loop_start()
        time.sleep(1)
        
        print(f"開始持續發布數據（每 {interval} 秒一次，共 {count} 次）...")
        print("按 Ctrl+C 可提前停止\n")
        
        for i in range(count):
            temp = round(random.uniform(20, 30), 1)
            hum = round(random.uniform(40, 70), 1)
            light_state = "on" if i % 2 == 0 else "off"
            
            client.publish(MQTT_TOPIC_TEMPERATURE, str(temp), qos=1)
            client.publish(MQTT_TOPIC_HUMIDITY, str(hum), qos=1)
            client.publish(MQTT_TOPIC_LIGHT, light_state, qos=1)
            
            print(f"[{i+1}/{count}] {datetime.now().strftime('%H:%M:%S')} - "
                  f"溫度: {temp}°C, 濕度: {hum}%, 電燈: {light_state}")
            
            time.sleep(interval)
        
        client.loop_stop()
        client.disconnect()
        print("\n✓ 持續發布完成！")
        
    except KeyboardInterrupt:
        print("\n\n停止發布...")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"✗ 發布時發生錯誤: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        # 持續發布模式
        # 預設：每 1 秒一次，共 100 次
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        publish_continuous_data(interval, count)
    else:
        # 單次測試模式
        publish_test_data()

