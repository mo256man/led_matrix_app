import cv2
import time
import numpy as np
from config import SIZE
from bg_patterns import BG, SIZE
from digital_clock import DigitalClock


# --- LEDマトリックス表示 ---
def show_matrix(led_matrix, prev_time=None, scale=20):
    img = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    for y in range(SIZE):
        for x in range(SIZE):
            r, g, b = led_matrix[y][x]
            img[y, x] = [b, g, r]
    img = cv2.resize(img, (SIZE*scale, SIZE*scale), interpolation=cv2.INTER_NEAREST)
    cv2.imshow("LED Clock", img)

    target_frame_time = 0.05
    now = time.time()
    if prev_time is None:
        wait_ms = int(target_frame_time*1000)
    else:
        elapsed = now - prev_time
        wait_ms = max(1, int((target_frame_time - elapsed)*1000))
    key = cv2.waitKey(wait_ms) & 0xFF
    quit_flag = key == 27
    return time.time(), quit_flag

# --- main ---
def main():
    bg = BG(SIZE)
    bg.init_bg()  # 初期背景
    clock = DigitalClock()
    prev_time = time.localtime()

    while True:
        t = time.localtime()
        # 秒0で背景切替
        if t.tm_sec == 0 and prev_time.tm_sec != 0:
            bg.init_bg()

        # 背景描画
        led_matrix = bg.draw()

        # 時計描画
        hh = f"{t.tm_hour:02d}"
        mm = f"{t.tm_min:02d}"
        ss = f"{t.tm_sec:02d}"
        clock.draw(led_matrix, hh, mm, ss, [255,255,255])

        # 表示
        prev_time_now, quit_flag = show_matrix(led_matrix, None)
        if quit_flag:
            break
        prev_time = t

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
