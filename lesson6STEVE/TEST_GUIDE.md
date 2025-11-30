# MQTT 測試指南

本指南說明如何發送測試 MQTT 訊息來測試 Streamlit 監控應用程式。

## 方法 1: 使用 Shell 腳本（最簡單，推薦）⭐

### 單次測試
```bash
cd /home/pi/Documents/GitHub/20205_10_26_chihlee_pi_pico_Steve/lesson6
./test_mqtt.sh
```

這個腳本會自動啟動虛擬環境並執行測試，無需手動啟動虛擬環境。

### 持續發布模式
```bash
# 使用預設值：每 1 秒發布一次，共 100 次
./test_mqtt.sh continuous

# 自訂頻率和筆數
./test_mqtt.sh continuous 1 100  # 每 1 秒一次，共 100 次
./test_mqtt.sh continuous 0.5 200  # 每 0.5 秒一次，共 200 次
./test_mqtt.sh continuous 2 50    # 每 2 秒一次，共 50 次
```

## 方法 2: 使用 Python 測試腳本（需手動啟動虛擬環境）

### 單次測試
```bash
cd /home/pi/Documents/GitHub/20205_10_26_chihlee_pi_pico_Steve
source .venv/bin/activate
cd lesson6
python test_mqtt_publish.py
```

這會發送：
- 電燈狀態（ON）
- 溫度數據
- 濕度數據
- JSON 格式的完整數據
- **30 筆連續的模擬感測器數據**（每 1 秒一次）

### 持續發布模式
```bash
# 使用預設值：每 1 秒發布一次，共 100 次
python test_mqtt_publish.py continuous

# 自訂頻率和筆數
python test_mqtt_publish.py continuous 1 100  # 每 1 秒一次，共 100 次
python test_mqtt_publish.py continuous 0.5 200  # 每 0.5 秒一次，共 200 次
python test_mqtt_publish.py continuous 2 50    # 每 2 秒一次，共 50 次
```

## 方法 2: 使用 Shell 腳本（快速測試）

```bash
cd /home/pi/Documents/GitHub/20205_10_26_chihlee_pi_pico_Steve/lesson6
./test_mqtt_simple.sh
```

## 方法 3: 使用 mosquitto_pub 命令（手動測試）

### 發布單一訊息

**發布電燈狀態：**
```bash
mosquitto_pub -h localhost -t "home/living_room/light" -m "on" -q 1
mosquitto_pub -h localhost -t "home/living_room/light" -m "off" -q 1
```

**發布溫度：**
```bash
mosquitto_pub -h localhost -t "home/living_room/temperature" -m "25.5" -q 1
```

**發布濕度：**
```bash
mosquitto_pub -h localhost -t "home/living_room/humidity" -m "60.0" -q 1
```

**發布 JSON 格式：**
```bash
mosquitto_pub -h localhost -t "home/living_room/data" -m '{"temperature":25.5,"humidity":60.0,"light":"on"}' -q 1
```

### 連續發布多筆數據

```bash
# 發布 10 筆溫度數據
for i in {1..10}; do
  temp=$(echo "scale=1; 20 + $RANDOM % 100 / 10" | bc)
  mosquitto_pub -h localhost -t "home/living_room/temperature" -m "$temp" -q 1
  sleep 2
done
```

## 方法 4: 使用 Jupyter Notebook

可以使用之前建立的 `lesson6_1.ipynb` notebook 來發布測試數據。

## 測試步驟

1. **啟動 Streamlit 應用程式**
   ```bash
   cd /home/pi/Documents/GitHub/20205_10_26_chihlee_pi_pico_Steve/lesson6
   streamlit run app.py
   ```

2. **在瀏覽器中開啟應用程式**
   - 網址：`http://localhost:8501`
   - 點擊側邊欄的「連線 MQTT」按鈕

3. **在另一個終端機執行測試腳本**
   ```bash
   # 方法 1: Python 腳本
   python test_mqtt_publish.py
   
   # 方法 2: Shell 腳本
   ./test_mqtt_simple.sh
   
   # 方法 3: 手動命令
   mosquitto_pub -h localhost -t "home/living_room/temperature" -m "25.5" -q 1
   ```

4. **觀察 Streamlit 應用程式**
   - 數據應該會即時顯示在儀表板上
   - 圖表會自動更新
   - 數據會自動儲存到 Excel 檔案

## 驗證 MQTT 訂閱

如果想確認 MQTT 訊息是否正確發布，可以在另一個終端機訂閱主題：

```bash
# 訂閱所有客廳相關主題
mosquitto_sub -h localhost -t "home/living_room/#" -v

# 訂閱特定主題
mosquitto_sub -h localhost -t "home/living_room/temperature" -v
```

## 常見問題

### Q: 應用程式沒有收到數據？
- 確認 MQTT Broker 正在運行：`sudo systemctl status mosquitto`
- 確認主題名稱正確（參考 `config.py`）
- 確認應用程式已連線 MQTT（側邊欄顯示「已連線」）

### Q: 如何修改測試數據？
- 編輯 `test_mqtt_publish.py` 來修改測試數據
- 或直接使用 `mosquitto_pub` 命令手動發布

### Q: 如何測試不同的數據值？
```bash
# 發布不同的溫度值
mosquitto_pub -h localhost -t "home/living_room/temperature" -m "30.0" -q 1

# 發布不同的濕度值
mosquitto_pub -h localhost -t "home/living_room/humidity" -m "75.5" -q 1
```

## 測試數據範例

### 正常範圍數據
- 溫度：20-30°C
- 濕度：40-70%
- 電燈：on/off

### 極端值測試
```bash
# 高溫
mosquitto_pub -h localhost -t "home/living_room/temperature" -m "35.0" -q 1

# 低溫
mosquitto_pub -h localhost -t "home/living_room/temperature" -m "15.0" -q 1

# 高濕度
mosquitto_pub -h localhost -t "home/living_room/humidity" -m "90.0" -q 1

# 低濕度
mosquitto_pub -h localhost -t "home/living_room/humidity" -m "20.0" -q 1
```

