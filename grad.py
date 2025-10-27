import cv2
import time
import random

SIZE = 16  # マトリックスサイズ

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
    if hi == 0: return [v, t, p]
    elif hi == 1: return [q, v, p]
    elif hi == 2: return [p, v, t]
    elif hi == 3: return [p, q, v]
    elif hi == 4: return [t, p, v]
    else: return [v, p, q]

SEGMENTS = {
    "0":[[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
    "1":[[0,0,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
    "2":[[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
    "3":[[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
    "4":[[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
    "5":[[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
    "6":[[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
    "7":[[1,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
    "8":[[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
    "9":[[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]],
}

def draw_digit(mat, digit, x0, y0, color):
    seg = SEGMENTS[digit]
    for dy, row in enumerate(seg):
        for dx, val in enumerate(row):
            if 0 <= x0+dx < SIZE and 0 <= y0+dy < SIZE:
                if val:
                    mat[y0+dy][x0+dx] = color

def draw_number(mat, number, x, y, color=[255,255,255]):
    draw_digit(mat, number[0], x, y, color)
    draw_digit(mat, number[1], x+4, y, color)

def draw_clock(mat, hh, mm, ss, color):
    draw_number(mat, hh, 0, 2, color=color)
    draw_number(mat, mm, 9, 2, color=color)
    draw_number(mat, ss, 9, 9, color=color)

def show_matrix(led_matrix, prev_time=None, scale=20):
    import numpy as np
    img = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    for y in range(SIZE):
        for x in range(SIZE):
            r,g,b = led_matrix[y][x]
            img[y,x] = [b,g,r]
    img = cv2.resize(img,(SIZE*scale, SIZE*scale), interpolation=cv2.INTER_NEAREST)
    cv2.imshow("LED Clock", img)

    target_frame_time = 0.05
    now = time.time()
    if prev_time is None:
        wait_ms = int(target_frame_time*1000)
    else:
        elapsed = now - prev_time
        wait_ms = max(1,int((target_frame_time - elapsed)*1000))
    key = cv2.waitKey(wait_ms) & 0xFF
    quit_flag = key==27
    return time.time(), quit_flag

class BG:
    def __init__(self, size=SIZE):
        self.SIZE = size

    # --- linear ---
    def linear_gradient(self, vertical=True, forward=True, offset=0):
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        k = 1 if forward else -1
        if vertical:
            for y in range(self.SIZE):
                hue = ((y + offset*k) * 360 / self.SIZE) % 360
                color = hsv2rgb(hue, 1, 1)
                for x in range(self.SIZE):
                    mat[y][x] = color
        else:
            for x in range(self.SIZE):
                hue = ((x + offset*k) * 360 / self.SIZE) % 360
                color = hsv2rgb(hue, 1, 1)
                for y in range(self.SIZE):
                    mat[y][x] = color
        return mat

    def init_linear(self):
        vertical = random.choice([True, False])
        forward = random.choice([True, False])
        offset = random.randint(0, self.SIZE-1)
        speed = random.randint(1,5)
        return vertical, forward, offset, speed

    # --- diamond ---
    def diamond_gradient(self, offset=0, inward=True):
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        cx = cy = (self.SIZE-1)//2
        max_layer = self.SIZE-1
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                layer = abs(x-cx) + abs(y-cy)
                if inward: layer = max_layer - layer
                hue = ((layer + offset) * 360 / (max_layer+1)) % 360
                mat[y][x] = hsv2rgb(hue,1,1)
        return mat

    def init_diamond(self):
        inward = random.choice([True, False])
        offset = random.randint(0,360)
        speed = random.randint(1,5)
        return inward, offset, speed

    # --- radial ---
    def radial_gradient(self, offset=0, inward=True):
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        cx = cy = (self.SIZE-1)/2
        max_dist = (cx**2 + cy**2) ** 0.5
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                dx = x - cx
                dy = y - cy
                dist = (dx*dx + dy*dy) ** 0.5
                t = dist / max_dist
                if inward: t = 1 - t
                hue = (t * 360 + offset) % 360
                mat[y][x] = hsv2rgb(hue,1,1)
        return mat

    def init_radial(self):
        inward = random.choice([True, False])
        offset = random.randint(0,360)
        speed = random.randint(1,5)
        return inward, offset, speed

    # --- split linear ---
    def split_linear_gradient(self, vertical=True, offset=0):
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                idx = y if vertical else x
                if vertical and y >= self.SIZE//2: idx = self.SIZE-1 - y
                if not vertical and x >= self.SIZE//2: idx = self.SIZE-1 - x
                hue = ((idx + offset) * 360 / self.SIZE) % 360
                mat[y][x] = hsv2rgb(hue,1,1)
        return mat

    def init_split_linear(self):
        vertical = random.choice([True, False])
        offset = random.randint(0,self.SIZE-1)
        speed = random.randint(1,5)
        return vertical, offset, speed

    # --- checkerboard ---
    def checkerboard_pattern(self, offset_x, offset_y, block_size, color1, color2, direction):
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        # 市松模様生成
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                if ((x//block_size)+(y//block_size)) % 2 == 0:
                    mat[y][x] = color1.copy()
                else:
                    mat[y][x] = color2.copy()
        # スクロール量
        dx = dy = 0
        if direction == 0: dy = -offset_y
        elif direction == 1: dy = offset_y
        elif direction == 2: dx = -offset_x
        elif direction == 3: dx = offset_x
        elif direction == 4: dx, dy = -offset_x, -offset_y
        elif direction == 5: dx, dy = offset_x, -offset_y
        elif direction == 6: dx, dy = -offset_x, offset_y
        elif direction == 7: dx, dy = offset_x, offset_y
        # 手動ロール
        new_mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                new_x = (x + dx) % self.SIZE
                new_y = (y + dy) % self.SIZE
                new_mat[new_y][new_x] = mat[y][x]
        return new_mat

    def init_checkerboard(self):
        block_size = random.choice([2, 4, 8])
        color1 = [random.randint(0,255) for _ in range(3)]
        color2 = [random.randint(0,255) for _ in range(3)]
        direction = random.randint(0,7)
        offset = random.randint(1,3)
        return block_size, color1, color2, direction, offset

# --- main ---
def main():
    bg = BG(SIZE)
    use_bg_list = ["linear", "diamond", "radial", "split", "checker"]

    # 初期背景選択
    bg_type = random.choice(use_bg_list)

    # 初期値保持用
    linear_params = diamond_params = radial_params = split_params = checker_params = None

    prev_time = time.localtime()
    offset = 0

    while True:
        t = time.localtime()
        # 秒0で背景切替
        if t.tm_sec == 0 and prev_time.tm_sec != 0:
            bg_type = random.choice(use_bg_list)
            if bg_type == "linear": linear_params = bg.init_linear()
            elif bg_type == "diamond": diamond_params = bg.init_diamond()
            elif bg_type == "radial": radial_params = bg.init_radial()
            elif bg_type == "split": split_params = bg.init_split_linear()
            elif bg_type == "checker": checker_params = bg.init_checkerboard()

        # 背景描画
        if bg_type == "linear":
            vertical, forward, offset, speed = linear_params
            led_matrix = bg.linear_gradient(vertical, forward, offset)
            offset = (offset + speed) % SIZE
            linear_params = (vertical, forward, offset, speed)
        elif bg_type == "diamond":
            inward, offset, speed = diamond_params
            led_matrix = bg.diamond_gradient(offset, inward)
            offset = (offset + speed) % 360
            diamond_params = (inward, offset, speed)
        elif bg_type == "radial":
            inward, offset, speed = radial_params
            led_matrix = bg.radial_gradient(offset, inward)
            offset = (offset + speed) % 360
            radial_params = (inward, offset, speed)
        elif bg_type == "split":
            vertical, offset, speed = split_params
            led_matrix = bg.split_linear_gradient(vertical, offset)
            offset = (offset + speed) % SIZE
            split_params = (vertical, offset, speed)
        elif bg_type == "checker":
            block_size, color1, color2, direction, scroll = checker_params
            led_matrix = bg.checkerboard_pattern(scroll, scroll, block_size, color1, color2, direction)
            checker_params = (block_size, color1, color2, direction, scroll)  # offset更新はscrollで調整可能

        # 時計描画
        hh = f"{t.tm_hour:02d}"
        mm = f"{t.tm_min:02d}"
        ss = f"{t.tm_sec:02d}"
        draw_clock(led_matrix, hh, mm, ss, [255,255,255])

        prev_time_now, quit_flag = show_matrix(led_matrix, None)
        if quit_flag: break
        prev_time = t

    cv2.destroyAllWindows()

if __name__=="__main__":
    main()

