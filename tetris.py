import cv2
import random
import time

# ==== HSV→RGB ====
def hsv2rgb(h, s, v):
    if s == 0:
        r = g = b = int(v * 255)
        return (r, g, b)
    h = h % 360
    i = int(h // 60)
    f = (h / 60) - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else:        r, g, b = v, p, q
    return (int(r*255), int(g*255), int(b*255))

# ==== 基本設定 ====
W, H = 16, 16
CELL = 28
WIDTH, HEIGHT = W * CELL, H * CELL

PLAY_X0 = 1
PLAY_X1 = 10
WALL_L = 0
WALL_R = 11
NEXT_X0 = 12

# ==== テトリミノ定義 ====
TETROMINOS = {
    'I': [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
    'O': [[0,0,0,0],[0,1,1,0],[0,1,1,0],[0,0,0,0]],
    'T': [[0,0,0,0],[1,1,1,0],[0,1,0,0],[0,0,0,0]],
    'S': [[0,0,0,0],[0,1,1,0],[1,1,0,0],[0,0,0,0]],
    'Z': [[0,0,0,0],[1,1,0,0],[0,1,1,0],[0,0,0,0]],
    'J': [[0,0,0,0],[1,1,1,0],[0,0,1,0],[0,0,0,0]],
    'L': [[0,0,0,0],[1,1,1,0],[1,0,0,0],[0,0,0,0]],
}
COLORS = {
    0:(0,0,0),     # 空
    1:(200,60,60), # 赤
    2:(60,200,60), # 緑
    3:(60,60,200), # 青
    4:(200,200,60),# 黄
    5:(200,60,200),# 紫
    6:(60,200,200),# 水
    7:(200,140,60),# オレンジ
    8:(80,80,80),  # 壁
}
PIECE_COLOR = {'I':6,'O':4,'T':5,'S':2,'Z':1,'J':3,'L':7}

# ==== 基本関数 ====
def new_board():
    board = [[0 for _ in range(W)] for _ in range(H)]
    for y in range(H):
        board[y][WALL_L] = 8
        board[y][WALL_R] = 8
    return board

class Piece:
    def __init__(self, name):
        self.name = name
        self.shape = [row[:] for row in TETROMINOS[name]]
        self.color = PIECE_COLOR[name]
        self.x = PLAY_X0 + 4
        self.y = 0
        for _ in range(random.randint(0,3)):  # ランダム回転
            self.rotate()
    def rotate(self):
        s = [[0]*4 for _ in range(4)]
        for y in range(4):
            for x in range(4):
                s[x][3-y] = self.shape[y][x]
        self.shape = s

def check_collision(board, piece, dx=0, dy=0, shape=None):
    if shape is None:
        shape = piece.shape
    for r in range(4):
        for c in range(4):
            if shape[r][c]:
                x = piece.x + c + dx
                y = piece.y + r + dy
                if x < WALL_L+1 or x > WALL_R-1 or y >= H:
                    return True
                if y >= 0 and board[y][x] not in (0,):
                    return True
    return False

def place_piece(board, piece):
    for r in range(4):
        for c in range(4):
            if piece.shape[r][c]:
                x = piece.x + c
                y = piece.y + r
                if 0 <= x < W and 0 <= y < H:
                    board[y][x] = piece.color

def clear_lines(board):
    lines = []
    for y in range(H):
        if all(board[y][x] != 0 for x in range(PLAY_X0, PLAY_X1+1)):
            lines.append(y)
    return lines

def delete_lines(board, lines):
    for y in sorted(lines):
        del board[y]
        new_line = [0]*W
        new_line[WALL_L] = 8
        new_line[WALL_R] = 8
        board.insert(0, new_line)

# ==== 描画 ====
def draw_board(board, cur=None, nxt=None, hue_shift=0, effect_lines=None):
    import numpy as np
    img = np.zeros((HEIGHT, WIDTH, 3), dtype="uint8")

    for y in range(H):
        for x in range(W):
            val = board[y][x]
            color = COLORS[val]
            if effect_lines and y in effect_lines and PLAY_X0 <= x <= PLAY_X1:
                h = (hue_shift + x * 20) % 360
                color = hsv2rgb(h, 1.0, 1.0)
            cv2.rectangle(img, (x*CELL, y*CELL),
                          (x*CELL+CELL-1, y*CELL+CELL-1),
                          color, -1)

    # 落下中ピース
    if cur:
        for r in range(4):
            for c in range(4):
                if cur.shape[r][c]:
                    x = cur.x + c
                    y = cur.y + r
                    if 0 <= x < W and 0 <= y < H:
                        cv2.rectangle(img, (x*CELL, y*CELL),
                                      (x*CELL+CELL-1, y*CELL+CELL-1),
                                      COLORS[cur.color], -1)

    # 次ピース表示（13〜16列）
    if nxt:
        for r in range(4):
            for c in range(4):
                if nxt.shape[r][c]:
                    x = NEXT_X0 + c
                    y = 2 + r
                    if 0 <= x < W and 0 <= y < H:
                        cv2.rectangle(img, (x*CELL, y*CELL),
                                      (x*CELL+CELL-1, y*CELL+CELL-1),
                                      COLORS[nxt.color], -1)

    return img

# ==== メイン ====
def spawn_piece():
    return Piece(random.choice(list(TETROMINOS.keys())))

def main():
    import numpy as np
    board = new_board()
    cur = spawn_piece()
    nxt = spawn_piece()
    score = 0
    drop_interval = 0.6
    last_drop = time.time()

    effect_lines = None
    pending_clear = None
    hue_shift = 0
    effect_start = 0
    EFFECT_TIME = 0.5

    cv2.namedWindow("TETRIS", cv2.WINDOW_AUTOSIZE)

    while True:
        now = time.time()

        if effect_lines:
            hue_shift = (hue_shift + 15) % 360
            if now - effect_start > EFFECT_TIME:
                delete_lines(board, pending_clear)
                effect_lines = None
                pending_clear = None

        elif now - last_drop > drop_interval:
            last_drop = now
            if not check_collision(board, cur, dy=1):
                cur.y += 1
            else:
                place_piece(board, cur)
                lines = clear_lines(board)
                if lines:
                    effect_lines = lines
                    pending_clear = lines
                    effect_start = time.time()
                    hue_shift = 0
                cur = nxt
                nxt = spawn_piece()
                if check_collision(board, cur):
                    break

        img = draw_board(board, cur, nxt, hue_shift, effect_lines)
        cv2.imshow("TETRIS", img)
        key = cv2.waitKey(30) & 0xFF
        if key in (ord('q'), 27):
            break
        elif key == ord('a'):
            if not check_collision(board, cur, dx=-1):
                cur.x -= 1
        elif key == ord('d'):
            if not check_collision(board, cur, dx=1):
                cur.x += 1
        elif key == ord('s'):
            if not check_collision(board, cur, dy=1):
                cur.y += 1
        elif key == ord('w'):
            new_shape = [[0]*4 for _ in range(4)]
            for y in range(4):
                for x in range(4):
                    new_shape[x][3-y] = cur.shape[y][x]
            if not check_collision(board, cur, shape=new_shape):
                cur.shape = new_shape
        elif key == 32:
            while not check_collision(board, cur, dy=1):
                cur.y += 1
            place_piece(board, cur)
            lines = clear_lines(board)
            if lines:
                effect_lines = lines
                pending_clear = lines
                effect_start = time.time()
                hue_shift = 0
            cur = nxt
            nxt = spawn_piece()
            if check_collision(board, cur):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
