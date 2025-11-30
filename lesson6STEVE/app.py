"""
Streamlit 應用程式

⚠️ 重要：這個檔案不能直接用 python 執行！
請使用以下命令來執行：

方法 1（推薦）：
    .venv/bin/streamlit run lesson6/app.py

方法 2：
    source .venv/bin/activate
    streamlit run lesson6/app.py

方法 3：
    ./lesson6/run_app.sh
"""

import sys

# 檢查是否直接用 python 執行（錯誤的方式）
if __name__ == "__main__" and "streamlit" not in sys.modules:
    print("=" * 60)
    print("❌ 錯誤：Streamlit 應用程式不能直接用 python 執行！")
    print("=" * 60)
    print("\n✅ 請使用以下命令執行：")
    print("\n   方法 1: .venv/bin/streamlit run lesson6/app.py")
    print("   方法 2: ./lesson6/run_app.sh")
    print("\n   或先啟動虛擬環境：")
    print("   source .venv/bin/activate")
    print("   streamlit run lesson6/app.py")
    print("\n" + "=" * 60)
    sys.exit(1)

import streamlit as st

st.title("我的第一個Streamlit 應用程式")
st.write("歡迎使用Streamlit!")
