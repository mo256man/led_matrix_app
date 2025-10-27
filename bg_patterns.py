import random
from config import SIZE

# --- HSV to RGB ---
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

class BG:
    def __init__(self, size=SIZE):
        self.SIZE = size
        self.bg_type = None
        self.params = None

    # --- linear ---
    def linear_gradient(self):
        vertical, forward, offset, _ = self.params
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        k = 1 if forward else -1
        if vertical:
            for y in range(self.SIZE):
                hue = ((y + offset*k) * 360 / self.SIZE) % 360
                color = hsv2rgb(hue,1,1)
                for x in range(self.SIZE):
                    mat[y][x] = color
        else:
            for x in range(self.SIZE):
                hue = ((x + offset*k) * 360 / self.SIZE) % 360
                color = hsv2rgb(hue,1,1)
                for y in range(self.SIZE):
                    mat[y][x] = color
        # offset更新
        self.params = (vertical, forward, (offset+self.params[3]) % self.SIZE, self.params[3])
        return mat

    def init_linear(self):
        vertical = random.choice([True, False])
        forward = random.choice([True, False])
        offset = random.randint(0, self.SIZE-1)
        speed = random.randint(1,5)
        return vertical, forward, offset, speed

    # --- diamond ---
    def diamond_gradient(self):
        inward, offset, speed = self.params
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        cx = cy = (self.SIZE-1)//2
        max_layer = self.SIZE-1
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                layer = abs(x-cx) + abs(y-cy)
                if inward: layer = max_layer - layer
                hue = ((layer + offset) * 360 / (max_layer+1)) % 360
                mat[y][x] = hsv2rgb(hue,1,1)
        # offset更新
        self.params = (inward, (offset+speed)%360, speed)
        return mat

    def init_diamond(self):
        inward = random.choice([True, False])
        offset = random.randint(0,360)
        speed = random.randint(1,5)
        return inward, offset, speed

    # --- radial ---
    def radial_gradient(self):
        inward, offset, speed = self.params
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        cx = cy = (self.SIZE-1)/2
        max_dist = (cx**2 + cy**2)**0.5
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                dx = x - cx
                dy = y - cy
                dist = (dx*dx + dy*dy)**0.5
                t = dist / max_dist
                if inward: t = 1 - t
                hue = (t*360 + offset)%360
                mat[y][x] = hsv2rgb(hue,1,1)
        self.params = (inward, (offset+speed)%360, speed)
        return mat

    def init_radial(self):
        inward = random.choice([True, False])
        offset = random.randint(0,360)
        speed = random.randint(1,5)
        return inward, offset, speed

    # --- split linear ---
    def split_linear_gradient(self):
        vertical, offset, speed = self.params
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                idx = y if vertical else x
                if vertical and y >= self.SIZE//2: idx = self.SIZE-1 - y
                if not vertical and x >= self.SIZE//2: idx = self.SIZE-1 - x
                hue = ((idx + offset) * 360 / self.SIZE) % 360
                mat[y][x] = hsv2rgb(hue,1,1)
        self.params = (vertical, (offset+speed)%self.SIZE, speed)
        return mat

    def init_split_linear(self):
        vertical = random.choice([True, False])
        offset = random.randint(0,self.SIZE-1)
        speed = random.randint(1,5)
        return vertical, offset, speed

    # --- checkerboard ---
    def checkerboard_pattern(self):
        block_size, color1, color2, direction, scroll = self.params
        mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                if ((x//block_size)+(y//block_size))%2==0:
                    mat[y][x] = color1.copy()
                else:
                    mat[y][x] = color2.copy()
        # スクロール
        dx=dy=0
        if direction==0: dy=-scroll
        elif direction==1: dx=scroll; dy=-scroll
        elif direction==2: dx=scroll
        elif direction==3: dx=scroll; dy=scroll
        elif direction==4: dy=scroll
        elif direction==5: dx=-scroll; dy=scroll
        elif direction==6: dx=-scroll
        elif direction==7: dx=-scroll; dy=-scroll
        new_mat = [[[0,0,0] for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        for y in range(self.SIZE):
            for x in range(self.SIZE):
                nx = (x+dx)%self.SIZE
                ny = (y+dy)%self.SIZE
                new_mat[y][x] = mat[ny][nx]
        scroll = (scroll+1)%self.SIZE
        self.params = (block_size,color1,color2,direction,scroll)
        return new_mat

    def init_checkerboard(self):
        block_size = random.choice([2,4,8])
        color1 = [random.randint(0,255) for _ in range(3)]
        color2 = [random.randint(0,255) for _ in range(3)]
        direction = random.randint(0,7)
        offset = random.randint(1,3)
        return block_size, color1, color2, direction, offset

    # --- unified init ---
    def init_bg(self, bg_type=None):
        use_bg_list = ["linear", "diamond", "radial", "split", "checker"]
        if bg_type is None:
            bg_type = random.choice(use_bg_list)
        self.bg_type = bg_type
        if bg_type=="linear": self.params = self.init_linear()
        elif bg_type=="diamond": self.params = self.init_diamond()
        elif bg_type=="radial": self.params = self.init_radial()
        elif bg_type=="split": self.params = self.init_split_linear()
        elif bg_type=="checker": self.params = self.init_checkerboard()
        else: raise ValueError("Unknown bg_type")
        return self.bg_type

    def draw(self):
        if self.bg_type=="linear": return self.linear_gradient()
        elif self.bg_type=="diamond": return self.diamond_gradient()
        elif self.bg_type=="radial": return self.radial_gradient()
        elif self.bg_type=="split": return self.split_linear_gradient()
        elif self.bg_type=="checker": return self.checkerboard_pattern()

