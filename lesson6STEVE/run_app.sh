#!/bin/bash
# Streamlit 應用程式啟動腳本
# 使用虛擬環境中的 Python 和 Streamlit

cd "$(dirname "$0")/.."
.venv/bin/streamlit run lesson6/app.py

