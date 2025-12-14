from machine import Pin, ADC
from time import sleep

led_pin = 15
pot_pin = 28                    # GPIO 28 作為 ADC 輸入

led = Pin(led_pin, Pin.OUT)
pot = ADC(Pin(pot_pin))         # 建立 ADC 物件

# 設定閾值（約 0~65535 範圍的中間）
# 轉到底最小 ≈ 0，最大 ≈ 65535
threshold = 30000               # 大於此值算「轉到底」開啟 LED

print("可變電阻控制 LED 啟動")

while True:
    value = pot.read_u16()      # 讀取 16-bit 值 (0~65535)
    
    if value > threshold:
        led.on()                # 轉到高電位 → 亮
        print("LED: 開 (值:", value, ")")
    else:
        led.off()               # 轉到低電位 → 熄
        print("LED: 關 (值:", value, ")")
    
    sleep(0.2)                  # 每 0.2 秒檢查一次，避免序列埠刷太快