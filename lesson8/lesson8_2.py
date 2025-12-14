from machine import Pin
from time import sleep

led_pin = 15
btn_pin = 14

# 設定 LED 為輸出
led = Pin(led_pin, Pin.OUT)

# 設定按鈕為輸入，並啟用內部上拉電阻
button = Pin(btn_pin, Pin.IN, Pin.PULL_UP)

# 用來記錄 LED 目前狀態：True 表示亮，False 表示熄滅
led_state = False

# 用來偵測按鈕是否剛剛被按下（避免連續觸發）
last_button_state = 1  # 初始為 1（沒按下，因為有上拉）

print("按鈕切換 LED 程式啟動")

while True:
    current_button_state = button.value()  # 讀取目前按鈕狀態
    
    # 偵測到按鈕從「沒按」變成「按下」（下降沿）
    if last_button_state == 1 and current_button_state == 0:
        print("按鈕被按下，切換 LED 狀態")
        
        # 切換 LED 狀態
        led_state = not led_state
        
        if led_state:
            led.on()    # 改成亮
            print("LED 開啟")
        else:
            led.off()   # 改成熄滅
            print("LED 關閉")
        
        # 加入短暫延遲，避免按鈕彈跳（debounce）
        sleep(0.02)  # 20ms 去彈跳
    
    # 更新上次狀態
    last_button_state = current_button_state
    
    # 主迴圈延遲，降低 CPU 負擔
    sleep(0.01)