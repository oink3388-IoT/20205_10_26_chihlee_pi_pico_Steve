#!/bin/bash
# 簡單的 MQTT 測試腳本（使用 mosquitto_pub）

BROKER="localhost"
TOPIC_TEMP="home/living_room/temperature"
TOPIC_HUM="home/living_room/humidity"
TOPIC_LIGHT="home/living_room/light"

echo "=========================================="
echo "MQTT 測試發布腳本"
echo "=========================================="
echo ""

# 測試 1: 發布電燈狀態
echo "[測試 1] 發布電燈狀態: ON"
mosquitto_pub -h $BROKER -t $TOPIC_LIGHT -m "on" -q 1
sleep 1

# 測試 2: 發布溫度
echo "[測試 2] 發布溫度: 25.5°C"
mosquitto_pub -h $BROKER -t $TOPIC_TEMP -m "25.5" -q 1
sleep 1

# 測試 3: 發布濕度
echo "[測試 3] 發布濕度: 60.0%"
mosquitto_pub -h $BROKER -t $TOPIC_HUM -m "60.0" -q 1
sleep 1

# 測試 4: 發布 JSON 格式
echo "[測試 4] 發布 JSON 格式數據"
mosquitto_pub -h $BROKER -t "home/living_room/data" -m '{"temperature":25.5,"humidity":60.0,"light":"on"}' -q 1
sleep 1

echo ""
echo "=========================================="
echo "✓ 測試完成！"
echo "=========================================="

