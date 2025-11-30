"""
MQTT 訂閱者模組
"""
import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime
from config import (
    MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENT_ID, MQTT_KEEPALIVE,
    MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_HUMIDITY, MQTT_TOPIC_LIGHT, MQTT_TOPIC_ALL
)


class MQTTSubscriber:
    """MQTT 訂閱者類別"""
    
    def __init__(self, data_storage=None):
        self.client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        self.data_storage = data_storage
        self.is_connected = False
        
        # 數據緩存（用於 Streamlit 顯示）
        self.data_lock = threading.Lock()
        self.current_data = {
            "light_status": "未知",
            "temperature": None,
            "humidity": None,
            "last_update": None
        }
        
        # 歷史數據（用於圖表）
        self.history_data = []
        self.max_history = 1000  # 最多保留 1000 筆歷史數據
        
        # 設定回調函數
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        """連線回調函數"""
        if rc == 0:
            self.is_connected = True
            print(f"✓ 成功連線到 MQTT Broker: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
            
            # 訂閱所有主題
            client.subscribe(MQTT_TOPIC_ALL, qos=1)
            print(f"✓ 已訂閱主題: {MQTT_TOPIC_ALL}")
        else:
            self.is_connected = False
            print(f"✗ 連線失敗，錯誤代碼: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """訊息接收回調函數"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # 嘗試解析 JSON
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                # 如果不是 JSON，當作字串處理
                data = payload
            
            # 根據主題更新數據
            with self.data_lock:
                self.current_data["last_update"] = datetime.now()
                
                if topic == MQTT_TOPIC_LIGHT or "light" in topic.lower():
                    self.current_data["light_status"] = str(data).lower() if isinstance(data, str) else data
                
                elif topic == MQTT_TOPIC_TEMPERATURE or "temperature" in topic.lower():
                    temp_value = float(data) if isinstance(data, (int, float, str)) else None
                    self.current_data["temperature"] = temp_value
                
                elif topic == MQTT_TOPIC_HUMIDITY or "humidity" in topic.lower():
                    hum_value = float(data) if isinstance(data, (int, float, str)) else None
                    self.current_data["humidity"] = hum_value
                
                # 如果是完整的感測器數據（JSON 格式）
                elif isinstance(data, dict):
                    if "temperature" in data:
                        self.current_data["temperature"] = float(data["temperature"])
                    if "humidity" in data:
                        self.current_data["humidity"] = float(data["humidity"])
                    if "light" in data or "light_status" in data:
                        light_val = data.get("light") or data.get("light_status")
                        self.current_data["light_status"] = str(light_val).lower()
                
                # 添加到歷史數據
                if self.current_data["temperature"] is not None or self.current_data["humidity"] is not None:
                    history_entry = {
                        "timestamp": datetime.now(),
                        "temperature": self.current_data["temperature"],
                        "humidity": self.current_data["humidity"],
                        "light_status": self.current_data["light_status"]
                    }
                    self.history_data.append(history_entry)
                    
                    # 限制歷史數據數量
                    if len(self.history_data) > self.max_history:
                        self.history_data.pop(0)
                
                # 儲存到 Excel（如果有 data_storage）
                if self.data_storage:
                    self.data_storage.add_data(
                        timestamp=self.current_data["last_update"],
                        light_status=self.current_data["light_status"],
                        temperature=self.current_data["temperature"],
                        humidity=self.current_data["humidity"]
                    )
        
        except Exception as e:
            print(f"✗ 處理訊息時發生錯誤: {e}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """訂閱回調函數"""
        print(f"✓ 訂閱確認 (Message ID: {mid}, QoS: {granted_qos})")
    
    def _on_disconnect(self, client, userdata, rc):
        """斷線回調函數"""
        self.is_connected = False
        if rc != 0:
            print(f"✗ 意外斷線，錯誤代碼: {rc}")
            # 注意：不在此處自動重連，避免無限循環
            # 重連邏輯由應用程式層控制
        else:
            print("✓ 已正常斷線")
    
    def connect(self):
        """連線到 MQTT Broker"""
        # 如果已經連線，直接返回
        if self.is_connected:
            return True
        
        # 如果 loop 正在運行，先停止
        try:
            if self.client._thread is not None:
                self.client.loop_stop()
        except:
            pass
        
        try:
            self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=MQTT_KEEPALIVE)
            self.client.loop_start()
            time.sleep(1)  # 等待連線建立
            return self.is_connected
        except Exception as e:
            print(f"✗ 連線錯誤: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """斷開 MQTT 連線"""
        self.client.loop_stop()
        self.client.disconnect()
        self.is_connected = False
    
    def get_current_data(self):
        """取得當前數據（執行緒安全）"""
        with self.data_lock:
            return self.current_data.copy()
    
    def get_history_data(self):
        """取得歷史數據（執行緒安全）"""
        with self.data_lock:
            return self.history_data.copy()

