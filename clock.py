import cv2
import time

WIDTH, HEIGHT = 16, 16

def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    hi = int(h / 60) % 6
    f = (h / 60) - hi
    p = int(v * (1 - s) * 255)
    q = int(v * (1 - f * s) * 255)
    t = int(v * (1 - (1 - f) * s) * 255)
    v = int(v * 255)
    if hi == 0:
        return [v, t, p]
    elif hi == 1:
        return [q, v, p]
    elif hi == 2:
        return [p, v, t]
    elif hi == 3:
        return [p, q, v]
    elif hi == 4:
        return [t, p, v]
    else:
        return [v, p, q]

def moving_gradient(vertical=True, forward=True, offset=0):
    mat = [[[0,0,0] for _ in range(WIDTH)] for _ in range(HEIGHT)]
    if vertical:
        for y in range(HEIGHT):
            hue = ((y + (offset if forward else -offset)) * 360 / HEIGHT) % 360
            color = hsv2rgb(hue, 1, 1)
            for x in range(WIDTH):
                mat[y][x] = color
    else:
        for x in range(WIDTH):
            hue = ((x + (offset if forward else -offset)) * 360 / WIDTH) % 360
            color = hsv2rgb(hue, 1, 1)
            for y in range(HEIGHT):
                mat[y][x] = color
    return mat

def radial_gradient(offset=0, inward=True):
    mat = [[[0,0,0] for _ in range(WIDTH)] for _ in range(HEIGHT)]
    cx, cy = (WIDTH-1)/2, (HEIGHT-1)/2
    max_dist = (cx**2 + cy**2) ** 0.5
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx = x - cx
            dy = y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            t = dist / max_dist
            if inward:
                t = 1 - t
            hue = (t * 360 + offset) % 360
            mat[y][x] = hsv2rgb(hue, 1, 1)
    return mat

def show_matrix(led_matrix, prev_time=None, scale=20):
    import numpy as np
    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = led_matrix[y][x]
            img[y, x] = [b, g, r]
    img = cv2.resize(img, (WIDTH*scale, HEIGHT*scale), interpolation=cv2.INTER_NEAREST)
    cv2.imshow("LED Matrix", img)

    target_frame_time = 0.05
    now = time.time()
    if prev_time is None:
        wait_ms = int(target_frame_time * 1000)
    else:
        elapsed = now - prev_time
        wait_ms = max(1, int((target_frame_time - elapsed) * 1000))
    key = cv2.waitKey(wait_ms) & 0xFF
    quit_flag = key == 27
    return time.time(), quit_flag

def main():
    offset = 0
    forward = True
    prev_time = None
    while True:
        # ここで表示するグラデーションを選択
        led_matrix = moving_gradient(vertical=True, forward=forward, offset=offset)
        # led_matrix = radial_gradient(offset=offset, inward=True)

        prev_time, quit_flag = show_matrix(led_matrix, prev_time)
        if quit_flag:
            break

        offset += 1
        if vertical:
            if offset >= HEIGHT:
                offset = 0
        else:
            if offset >= WIDTH:
                offset = 0

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
