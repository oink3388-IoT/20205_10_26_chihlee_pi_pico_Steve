"""
MQTT 監控應用程式配置檔案
"""
import os

# MQTT Broker 設定
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "streamlit_subscriber_001")
MQTT_KEEPALIVE = 60

# MQTT 訂閱主題
MQTT_TOPIC_TEMPERATURE = os.getenv("MQTT_TOPIC_TEMPERATURE", "home/living_room/temperature")
MQTT_TOPIC_HUMIDITY = os.getenv("MQTT_TOPIC_HUMIDITY", "home/living_room/humidity")
MQTT_TOPIC_LIGHT = os.getenv("MQTT_TOPIC_LIGHT", "home/living_room/light")
MQTT_TOPIC_ALL = os.getenv("MQTT_TOPIC_ALL", "home/living_room/#")  # 訂閱所有客廳相關主題

# 數據儲存設定
DATA_DIR = os.getenv("DATA_DIR", "data")
EXCEL_FILENAME_PREFIX = "mqtt_data"
EXCEL_SAVE_INTERVAL = 10  # 每收到 N 筆資料後儲存一次（0 表示即時儲存）

# Streamlit 設定
STREAMLIT_PAGE_TITLE = "MQTT 監控儀表板"
STREAMLIT_PAGE_ICON = "📊"
STREAMLIT_LAYOUT = "wide"

