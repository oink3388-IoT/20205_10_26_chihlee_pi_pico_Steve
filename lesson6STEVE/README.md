# Streamlit MQTT 監控應用程式

這是一個基於 Streamlit 的 MQTT 監控儀表板，用於即時監控和顯示物聯網設備的狀態與感測器數據。

## 功能特色

- ✅ 即時顯示電燈開/關狀態
- ✅ 即時顯示客廳溫度和濕度
- ✅ 溫濕度歷史趨勢圖表（使用 Plotly）
- ✅ 自動將數據儲存為 Excel 檔案
- ✅ 自動刷新顯示
- ✅ 響應式設計，支援寬屏顯示

## 安裝步驟

### 1. 安裝依賴套件

```bash
cd /home/pi/Documents/GitHub/20205_10_26_chihlee_pi_pico_Steve
uv sync
```

或使用 pip：

```bash
pip install streamlit pandas openpyxl plotly paho-mqtt
```

### 2. 確保 MQTT Broker 正在運行

如果使用本地 Mosquitto：

```bash
# 檢查 Mosquitto 是否運行
sudo systemctl status mosquitto

# 如果未運行，啟動它
sudo systemctl start mosquitto
```

### 3. 執行應用程式

```bash
cd lesson6
streamlit run app.py
```

應用程式會在瀏覽器中自動開啟，預設網址：`http://localhost:8501`

## 配置說明

所有配置都在 `config.py` 檔案中，可以修改以下設定：

- **MQTT_BROKER_HOST**: MQTT Broker 位址（預設：localhost）
- **MQTT_BROKER_PORT**: MQTT Broker 埠號（預設：1883）
- **MQTT_TOPIC_***: MQTT 訂閱主題
- **DATA_DIR**: 數據儲存目錄（預設：data）
- **EXCEL_SAVE_INTERVAL**: Excel 儲存間隔（0 表示即時儲存）

## MQTT 主題格式

應用程式預設訂閱以下主題：

- `home/living_room/temperature` - 溫度數據
- `home/living_room/humidity` - 濕度數據
- `home/living_room/light` - 電燈狀態
- `home/living_room/#` - 所有客廳相關主題（萬用字元）

### 訊息格式

**溫度/濕度（數值）**：
```
25.5
```

**電燈狀態（文字）**：
```
on
```
或
```
off
```

**完整 JSON 格式**：
```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "light": "on"
}
```

## 測試 MQTT 發布

可以使用 `mosquitto_pub` 命令來測試：

```bash
# 發布溫度
mosquitto_pub -h localhost -t "home/living_room/temperature" -m "25.5"

# 發布濕度
mosquitto_pub -h localhost -t "home/living_room/humidity" -m "60.0"

# 發布電燈狀態
mosquitto_pub -h localhost -t "home/living_room/light" -m "on"

# 發布 JSON 格式
mosquitto_pub -h localhost -t "home/living_room/data" -m '{"temperature":25.5,"humidity":60.0,"light":"on"}'
```

## 檔案結構

```
lesson6/
├── app.py              # Streamlit 主應用程式
├── config.py           # 配置檔案
├── mqtt_subscriber.py  # MQTT 訂閱者模組
├── data_storage.py    # 數據儲存模組
├── PRD.md             # 產品需求文件
├── README.md          # 本檔案
└── data/              # 數據儲存目錄（自動建立）
    └── mqtt_data_*.xlsx
```

## 使用說明

1. **啟動應用程式**：執行 `streamlit run app.py`
2. **連線 MQTT**：在側邊欄點擊「連線 MQTT」按鈕
3. **查看數據**：連線成功後，數據會自動顯示在儀表板上
4. **查看圖表**：溫濕度歷史趨勢圖會自動更新
5. **儲存數據**：數據會自動儲存到 Excel 檔案，也可手動點擊「手動儲存數據」

## 疑難排解

### MQTT 連線失敗

- 確認 MQTT Broker 正在運行
- 檢查 `config.py` 中的 Broker 位址和埠號
- 確認防火牆設定允許連線

### 沒有收到數據

- 確認 MQTT 主題名稱正確
- 使用 `mosquitto_sub` 測試訂閱：
  ```bash
  mosquitto_sub -h localhost -t "home/living_room/#" -v
  ```

### Excel 檔案無法儲存

- 確認 `data/` 目錄有寫入權限
- 檢查磁碟空間是否足夠

## 授權

本專案為課程專案，僅供學習使用。

