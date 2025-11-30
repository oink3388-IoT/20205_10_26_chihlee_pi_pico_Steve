"""
數據儲存模組 - 處理 Excel 檔案儲存
"""
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import threading
from config import DATA_DIR, EXCEL_FILENAME_PREFIX, EXCEL_SAVE_INTERVAL


class DataStorage:
    """數據儲存類別，負責將 MQTT 數據儲存到 Excel 檔案"""
    
    def __init__(self):
        self.data_lock = threading.Lock()
        self.data_buffer = []
        self.save_counter = 0
        
        # 建立數據目錄
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    def add_data(self, timestamp, light_status, temperature, humidity):
        """
        添加數據到緩衝區
        
        參數:
            timestamp: 時間戳記
            light_status: 電燈狀態 (on/off)
            temperature: 溫度
            humidity: 濕度
        """
        with self.data_lock:
            self.data_buffer.append({
                "時間戳記": timestamp,
                "電燈狀態": light_status,
                "溫度": temperature,
                "濕度": humidity
            })
            self.save_counter += 1
            
            # 根據設定決定是否儲存
            if EXCEL_SAVE_INTERVAL == 0 or self.save_counter >= EXCEL_SAVE_INTERVAL:
                self._save_to_excel()
                self.save_counter = 0
    
    def _save_to_excel(self):
        """將緩衝區的數據儲存到 Excel 檔案"""
        if not self.data_buffer:
            return
        
        try:
            # 建立檔案名稱（包含日期時間）
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{EXCEL_FILENAME_PREFIX}_{timestamp_str}.xlsx"
            filepath = os.path.join(DATA_DIR, filename)
            
            # 建立 DataFrame
            df = pd.DataFrame(self.data_buffer)
            
            # 儲存到 Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            # 清空緩衝區
            self.data_buffer = []
            
            print(f"✓ 數據已儲存到: {filepath}")
        except Exception as e:
            print(f"✗ 儲存 Excel 檔案時發生錯誤: {e}")
    
    def get_all_data(self):
        """取得所有已儲存的數據（用於圖表顯示）"""
        data_files = sorted(Path(DATA_DIR).glob(f"{EXCEL_FILENAME_PREFIX}_*.xlsx"))
        
        if not data_files:
            return pd.DataFrame()
        
        # 讀取所有 Excel 檔案並合併
        all_data = []
        for file in data_files:
            try:
                df = pd.read_excel(file, engine='openpyxl')
                all_data.append(df)
            except Exception as e:
                print(f"✗ 讀取檔案 {file} 時發生錯誤: {e}")
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    def force_save(self):
        """強制儲存當前緩衝區的數據"""
        with self.data_lock:
            if self.data_buffer:
                self._save_to_excel()

