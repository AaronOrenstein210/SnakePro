import pygame as pg
import constants as c

pg.init()

t = pg.time.get_ticks()
print(t)
c.get_scaled_font(250, 50, "Something", "Times New Roman")
print(pg.time.get_ticks() - t)
