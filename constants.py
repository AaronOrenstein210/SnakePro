# Created on 14 January 2020

import pygame as pg
from random import randint
from numpy import full, int8

MIN_W, MIN_H = 500, 500
SQUARE_W = 25
BOARD_W, BOARD_H = 100, 100
COLORS = {
    0: (0, 0, 0),
    1: (255, 0, 0),
    2: (255, 255, 0),
    3: (0, 255, 0),
    4: (0, 0, 255)
}

num_snakes = 0
snakes = []
board = full((BOARD_H, BOARD_W), 0, dtype=int8)
surface = pg.Surface((BOARD_W * SQUARE_W, BOARD_H * SQUARE_W))
map_s = pg.Surface((BOARD_W, BOARD_H))

items = {}


# Resizes surface to fit within desired dimensions, keeping surface's w:h ratio
def scale_to_fit(s, w=-1, h=-1):
    import pygame as pg
    if w == -1 and h == -1:
        return s
    dim = s.get_size()
    if w == -1:
        frac = h / dim[1]
    elif h == -1:
        frac = w / dim[0]
    else:
        frac = min(w / dim[0], h / dim[1])
    return pg.transform.scale(s, (int(frac * dim[0]), int(frac * dim[1])))


# Gets the biggest font that fits the text within max_w and max_h
def get_scaled_font(max_w, max_h, text, font_name):
    font_size = 0
    font = pg.font.SysFont(font_name, font_size)
    w, h = font.size(text)
    while (max_w == -1 or w < max_w) and (max_h == -1 or h < max_h):
        font_size += 1
        font = pg.font.SysFont(font_name, font_size)
        w, h = font.size(text)
    return pg.font.SysFont(font_name, font_size - 1)


pg.init()
restart_font = get_scaled_font(MIN_W // 2 - 10, MIN_H // 4, "Move to Restart", "Times New Roman")
restart_text = restart_font.render("Move to Restart", 1, (255, 255, 255))
del restart_font
pg.quit()


# Sets the value at that point and redraws
def set_at(x, y, val):
    board[y][x] = val
    update(x, y)


# Update board for snake trail
def set_trail(x, y, color):
    board[y][x] = 0
    pg.draw.rect(surface, color, (x * SQUARE_W, y * SQUARE_W, SQUARE_W, SQUARE_W))
    map_s.set_at((x, y), color)


# Redraws a point
def update(x, y):
    val = board[y][x]
    if val < 0:
        item = items[val]
        pg.draw.rect(surface, (128, 128, 128), (x * SQUARE_W + 1, y * SQUARE_W + 1, SQUARE_W - 2, SQUARE_W - 2))
        surface.blit(item.img, (x * SQUARE_W + 1, y * SQUARE_W + 1, SQUARE_W - 2, SQUARE_W - 2))
        map_s.set_at((x, y), item.color)
    else:
        pg.draw.rect(surface, COLORS[val], (x * SQUARE_W + 1, y * SQUARE_W + 1, SQUARE_W - 2, SQUARE_W - 2))
        if val == 0:
            map_s.set_at((x, y), (128, 128, 128))
        else:
            map_s.set_at((x, y), COLORS[val])


def add_random(val):
    pos = [randint(0, BOARD_W - 1), randint(0, BOARD_H - 1)]
    while board[pos[1]][pos[0]] != 0:
        pos = [randint(0, BOARD_W - 1), randint(0, BOARD_H - 1)]
    set_at(*pos, val)
    return pos
