from machine import Pin, RTC, PWM
import time
import sys
from app_Wifi import connect_wifi
import app_RTC
from app_load_image import load_images
from app_LED_pico import PicoWS2812Matrix
import app_LED


# 起動時に内蔵LEDを光らせる
print("start")
pico_led =  Pin("LED", Pin.OUT)
pico_led.value(1)


# 章仁さんち
SSID = "ctc-g-23f767"
PASSWD = "55523cdb20ec3"

# 森島さんち
# SSID = "ctc-g-072c7c"
# PASSWD = "6e1fd330fb1cd"

PIN_NUM = 1
ROWS = 16
COLS = 16
leds = PicoWS2812Matrix(pin=PIN_NUM, rows=ROWS, cols=COLS, brightness=0.02)

hex_str = "0000557455445574294400003766455545553755000000000000000000000000"
app_LED.draw_hex(leds, hex_str, color1=(128, 64, 255))
leds.show()

connect_wifi(SSID, PASSWD)

hex_str = "000055745544557429440000376645554555375500001E481250126012501E48"
app_LED.draw_hex(leds, hex_str, color1=(0, 0, 255))
leds.show()

app_RTC.sync_time(tz_offset_hours=9)
print(RTC().datetime() )

images = load_images("anim.txt", ROWS, COLS, 3)

def main():
    # 外周を1周する時間（秒）
    cycle_time = 1
    # フレームごとの目標待機時間（秒）
    frame_delay = 0.1

    # 外周LED数
    rows, cols = leds.rows, leds.cols
    n = 2*(rows + cols) - 4

    # 初期化
    offset_hue = 0.0

    # MicroPython 用の時間計測（ticks_ms を使用）
    last_ticks = time.ticks_ms()

    image_interval = 0.2   # 画像切替間隔（秒）
    last_image_time = time.ticks_ms()
    image_index = 0

    try:
        while True:
            loop_start = time.ticks_ms()
            dt_ms = time.ticks_diff(loop_start, last_ticks)
            last_ticks = loop_start

            current_time = time.localtime()
            minute = current_time[4]
            second = current_time[5]
            mode = (minute // 10) % 3

            if mode == 0:

                # 実際に経過した時間を使って hue を進める
                offset_hue = (offset_hue + 0.360 * dt_ms / cycle_time) % 360.0

                app_LED.draw_clock(leds, current_time)
                app_LED.border_rainbow(leds, offset_hue)
                r, c = leds.outer_coords[second]
                leds.matrix[r][c] = (255,255,255)

            elif mode == 1 or mode == 2:
                if time.ticks_diff(loop_start, last_image_time) > int(image_interval * 1000):
                    image_index = (image_index + 1) % len(images)
                    src = images[image_index]
                    for y in range(leds.rows):
                        for x in range(leds.cols):
                            leds.matrix[y][x] = src[y][x]
                    last_image_time = loop_start

            elif mode == 2:
                pass

            leds.show()

            # 描画にかかった時間を考慮してスリープ（目標 frame_delay を維持）
            elapsed_ms = time.ticks_diff(time.ticks_ms(), loop_start)
            to_sleep_ms = int(frame_delay * 1000 - elapsed_ms)
            if to_sleep_ms > 0:
                time.sleep_ms(to_sleep_ms)
            # 処理が遅ければスリープしない（次ループで dt が大きくなるため速度は補正される）

    except KeyboardInterrupt:
        leds.close()

    finally:
        leds.close()

if __name__ == "__main__":
    main()