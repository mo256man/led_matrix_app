from config import SIZE

class DigitalClock:
    SEGMENTS = {
        "0": [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
        "1": [[0,0,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
        "2": [[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
        "3": [[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
        "4": [[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
        "5": [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
        "6": [[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
        "7": [[1,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
        "8": [[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
        "9": [[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]],
    }

    def __init__(self):
        self.SIZE = SIZE

    def draw_digit(self, mat, digit, x0, y0, color):
        seg = self.SEGMENTS[digit]
        for dy, row in enumerate(seg):
            for dx, val in enumerate(row):
                if 0 <= x0+dx < self.SIZE and 0 <= y0+dy < self.SIZE:
                    if val:
                        mat[y0+dy][x0+dx] = color

    def draw_number(self, mat, number, x, y, color=[255,255,255]):
        self.draw_digit(mat, number[0], x, y, color)
        self.draw_digit(mat, number[1], x+4, y, color)

    def draw(self, mat, hh, mm, ss, color=[255,255,255]):
        self.draw_number(mat, hh, 0, 2, color)
        self.draw_number(mat, mm, 9, 2, color)
        self.draw_number(mat, ss, 9, 9, color)
