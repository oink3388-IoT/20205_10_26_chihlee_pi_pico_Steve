#!/bin/bash
# Streamlit MQTT 監控應用程式啟動腳本

cd "$(dirname "$0")"
cd ..

# 啟動虛擬環境並執行 Streamlit
source .venv/bin/activate
cd lesson6
streamlit run app.py

