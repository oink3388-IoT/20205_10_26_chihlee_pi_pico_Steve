<<<<<<< HEAD
<<<<<<< HEAD:lesson6STEVE/app.py
"""
Streamlit MQTT 監控應用程式
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import sys
import os

# 添加當前目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import STREAMLIT_PAGE_TITLE, STREAMLIT_PAGE_ICON, STREAMLIT_LAYOUT
from mqtt_subscriber import MQTTSubscriber
from data_storage import DataStorage

# 設定頁面配置
st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_PAGE_ICON,
    layout=STREAMLIT_LAYOUT
)

# 初始化 Session State
if 'mqtt_subscriber' not in st.session_state:
    st.session_state.mqtt_subscriber = None
if 'data_storage' not in st.session_state:
    st.session_state.data_storage = DataStorage()
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'mqtt_initialized' not in st.session_state:
    st.session_state.mqtt_initialized = False


def init_mqtt():
    """初始化 MQTT 訂閱者"""
    if st.session_state.mqtt_subscriber is None:
        st.session_state.mqtt_subscriber = MQTTSubscriber(
            data_storage=st.session_state.data_storage
        )
        if st.session_state.mqtt_subscriber.connect():
            st.session_state.mqtt_initialized = True
            st.success("✓ MQTT 連線成功！")
            return True
        else:
            st.session_state.mqtt_initialized = False
            st.error("✗ MQTT 連線失敗，請檢查 Broker 設定")
            return False
    # 如果已經存在，檢查連線狀態
    elif not st.session_state.mqtt_subscriber.is_connected:
        # 嘗試重新連線
        if st.session_state.mqtt_subscriber.connect():
            st.session_state.mqtt_initialized = True
            return True
        else:
            st.session_state.mqtt_initialized = False
            return False
    return st.session_state.mqtt_subscriber.is_connected


def get_light_status_display(status):
    """取得電燈狀態的顯示"""
    status_lower = str(status).lower()
    if "on" in status_lower or status_lower == "1" or status_lower == "true":
        return "🟢 開啟", "success"
    elif "off" in status_lower or status_lower == "0" or status_lower == "false":
        return "⚫ 關閉", "secondary"
    else:
        return "❓ 未知", "warning"


def create_temperature_humidity_chart(history_data):
    """建立溫濕度歷史圖表"""
    if not history_data:
        return None
    
    # 轉換為 DataFrame
    df = pd.DataFrame(history_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 建立子圖（雙 Y 軸）
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],
        subplot_titles=("溫濕度歷史趨勢")
    )
    
    # 添加溫度線
    if df['temperature'].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                name='溫度 (°C)',
                line=dict(color='#FF6B6B', width=2),
                mode='lines+markers'
            ),
            secondary_y=False,
        )
    
    # 添加濕度線
    if df['humidity'].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['humidity'],
                name='濕度 (%)',
                line=dict(color='#4ECDC4', width=2),
                mode='lines+markers'
            ),
            secondary_y=True,
        )
    
    # 設定 X 軸標題
    fig.update_xaxes(title_text="時間")
    
    # 設定 Y 軸標題
    fig.update_yaxes(title_text="溫度 (°C)", secondary_y=False)
    fig.update_yaxes(title_text="濕度 (%)", secondary_y=True)
    
    # 更新佈局
    fig.update_layout(
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


# 主標題
st.title("🏠 MQTT 監控儀表板")
st.markdown("---")

# 側邊欄 - 連線控制
with st.sidebar:
    st.header("⚙️ 設定")
    
    # MQTT 連線狀態
    # 檢查連線狀態（但不觸發重新連線，除非用戶點擊按鈕）
    mqtt_connected = (
        st.session_state.mqtt_subscriber is not None and 
        st.session_state.mqtt_subscriber.is_connected
    )
    
    if mqtt_connected:
        st.success("🟢 MQTT 已連線")
        if st.button("🔌 斷開連線", key="disconnect_btn"):
            st.session_state.mqtt_subscriber.disconnect()
            st.session_state.mqtt_subscriber = None
            st.session_state.mqtt_initialized = False
            st.rerun()
    else:
        st.warning("🔴 MQTT 未連線")
        if st.button("🔗 連線 MQTT", key="connect_btn"):
            init_mqtt()
            time.sleep(0.5)  # 減少等待時間
            st.rerun()
    
    st.markdown("---")
    
    # 自動刷新設定
    st.session_state.auto_refresh = st.checkbox(
        "🔄 自動刷新",
        value=st.session_state.auto_refresh
    )
    
    if st.button("💾 手動儲存數據", key="save_btn"):
        if st.session_state.data_storage:
            st.session_state.data_storage.force_save()
            st.success("✓ 數據已儲存")
        else:
            st.warning("數據儲存模組未初始化")
    
    st.markdown("---")
    st.info("📊 此應用程式會自動將接收到的數據儲存到 Excel 檔案")

# 主內容區域
# 安全地檢查 MQTT 連線狀態
mqtt_connected = (
    st.session_state.mqtt_subscriber is not None and 
    hasattr(st.session_state.mqtt_subscriber, 'is_connected') and
    st.session_state.mqtt_subscriber.is_connected
)

if mqtt_connected:
    # 取得當前數據
    current_data = st.session_state.mqtt_subscriber.get_current_data()
    
    # 建立三欄顯示
    col1, col2, col3 = st.columns(3)
    
    # 電燈狀態
    with col1:
        st.subheader("💡 電燈狀態")
        light_display, light_color = get_light_status_display(current_data["light_status"])
        st.markdown(f"### {light_display}")
        if current_data["last_update"]:
            st.caption(f"最後更新: {current_data['last_update'].strftime('%H:%M:%S')}")
    
    # 溫度顯示
    with col2:
        st.subheader("🌡️ 客廳溫度")
        if current_data["temperature"] is not None:
            st.markdown(f"### {current_data['temperature']:.1f} °C")
        else:
            st.markdown("### -- °C")
        if current_data["last_update"]:
            st.caption(f"最後更新: {current_data['last_update'].strftime('%H:%M:%S')}")
    
    # 濕度顯示
    with col3:
        st.subheader("💧 客廳濕度")
        if current_data["humidity"] is not None:
            st.markdown(f"### {current_data['humidity']:.1f} %")
        else:
            st.markdown("### -- %")
        if current_data["last_update"]:
            st.caption(f"最後更新: {current_data['last_update'].strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # 溫濕度歷史圖表
    st.subheader("📈 溫濕度歷史趨勢")
    history_data = st.session_state.mqtt_subscriber.get_history_data()
    
    if history_data:
        fig = create_temperature_humidity_chart(history_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("等待數據中...")
    else:
        st.info("📊 尚未收到數據，請確認 MQTT 主題設定正確")
    
    # 數據表格
    with st.expander("📋 查看歷史數據表格"):
        if history_data:
            df = pd.DataFrame(history_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("尚無歷史數據")
    
    # 自動刷新（使用更安全的方式，避免中斷 MQTT 連線）
    if st.session_state.auto_refresh:
        # 使用 time.sleep 和 rerun，但確保 MQTT 連線不會被中斷
        # 因為 MQTT 客戶端保存在 session_state 中，應該不會被重置
        time.sleep(2)  # 每 2 秒刷新一次
        # 在重新執行前，確保 MQTT 連線狀態正確
        if st.session_state.mqtt_subscriber and not st.session_state.mqtt_subscriber.is_connected:
            # 如果連線中斷，嘗試重新連線（但不顯示訊息，避免干擾）
            try:
                st.session_state.mqtt_subscriber.connect()
            except:
                pass
        st.rerun()
    
else:
    # 未連線時的提示
    st.info("👆 請在左側側邊欄點擊「連線 MQTT」來開始監控")
    
    # 顯示說明
    with st.expander("ℹ️ 使用說明"):
        st.markdown("""
        ### 使用步驟：
        1. 確保 MQTT Broker 正在運行（例如：Mosquitto）
        2. 點擊側邊欄的「連線 MQTT」按鈕
        3. 確認連線成功後，應用程式會自動訂閱主題並接收數據
        
        ### MQTT 主題設定：
        - 溫度主題：`home/living_room/temperature`
        - 濕度主題：`home/living_room/humidity`
        - 電燈主題：`home/living_room/light`
        - 或使用萬用字元：`home/living_room/#`
        
        ### 數據儲存：
        - 所有接收到的數據會自動儲存到 `data/` 目錄下的 Excel 檔案
        - 檔案名稱格式：`mqtt_data_YYYYMMDD_HHMMSS.xlsx`
        """)

=======
=======
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

>>>>>>> b4cf2463aad741e65cb85e2e4cb424284ebb2d9b
import streamlit as st

st.title("我的第一個Streamlit 應用程式")
st.write("歡迎使用Streamlit!")
<<<<<<< HEAD
>>>>>>> 539fd07ba8979941328249a8a325875e75f76a1c:lesson6/app.py
=======
>>>>>>> b4cf2463aad741e65cb85e2e4cb424284ebb2d9b
