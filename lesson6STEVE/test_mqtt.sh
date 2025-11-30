#!/bin/bash
# MQTT 測試發布腳本（自動使用虛擬環境）

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 啟動虛擬環境
source "$PROJECT_ROOT/.venv/bin/activate"

# 切換到 lesson6 目錄
cd "$SCRIPT_DIR"

# 執行 Python 測試腳本
if [ "$1" == "continuous" ]; then
    # 預設：每 1 秒一次，共 100 次
    python test_mqtt_publish.py continuous "${2:-1}" "${3:-100}"
else
    python test_mqtt_publish.py
fi

