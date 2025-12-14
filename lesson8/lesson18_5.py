from machine import ADC, Pin, PWM
from time import sleep

# 初始化 ADC（GPIO 28）和 PWM LED（GPIO 15）
potentiometer = ADC(Pin(28))
led = PWM(Pin(15))
led.freq(1000)  # 設定 PWM 頻率為 1000Hz

# 全局變數：記錄目前為止讀到的最小 raw 值
min_value = 65535  # 一開始設為最大可能值

# 緩衝值：避免雜訊導致閃爍（可調整，建議 200~500）
BUFFER = 300

while True:
    # 讀取 ADC 值（0 ~ 65535）
    raw_value = potentiometer.read_u16()
    
    # 自動更新歷史最低值
    if raw_value < min_value:
        min_value = raw_value
        print(f"*** 更新最低值: {min_value} ***")
    
    # 計算電壓與百分比（僅用來顯示）
    voltage = raw_value * 3.3 / 65535
    percentage = raw_value * 100 / 65535
    
    print(f"原始值: {raw_value}, 最低記錄: {min_value}, 電壓: {voltage:.2f}V, 百分比: {percentage:.1f}%")
    
    # 自動校正邏輯：
    # 如果目前值很接近歷史最低值（在 BUFFER 範圍內），就強制關閉 LED
    if raw_value <= min_value + BUFFER:
        led.duty_u16(0)  # 完全熄滅
    else:
        # 將剩餘範圍映射到 0~65535
        # 輸入範圍：(min_value + BUFFER) ~ 65535
        # 輸出範圍：0 ~ 65535
        mapped_value = int((raw_value - (min_value + BUFFER)) * 65535 / (65535 - (min_value + BUFFER)))
        # 限制在 0~65535 之間（避免邊界誤差）
        mapped_value = max(0, min(65535, mapped_value))
        led.duty_u16(mapped_value)
    
    sleep(0.5)  # 每 0.5 秒更新一次