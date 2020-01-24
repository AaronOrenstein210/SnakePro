# Created on 14 January 2020

from os.path import isfile
from random import randint, choice
import pygame as pg
import constants as c

FOOD = -1
POISON = -2
CARCASS = -3
GOLD_GRAPE = -4
SPEED_POT = -5
SLOW_POT = -6
INSTA_KILL = -7


class Item:
    def __init__(self, idx, img, color=(0, 0, 0)):
        self.idx = idx
        c.items[idx] = self
        if isfile(img):
            self.img = c.scale_to_fit(pg.image.load(img), c.SQUARE_W - 2, c.SQUARE_W - 2)
        else:
            self.img = pg.Surface((c.SQUARE_W, c.SQUARE_W))
        self.color = color

    def on_tick(self, snake, dt):
        pass

    def on_activate(self):
        pass


class Food(Item):
    def __init__(self):
        Item.__init__(self, FOOD, "res/grape.png", color=(200, 0, 175))

    def on_tick(self, snake, dt):
        snake.add += 1
        snake.items.remove(self)
        if randint(1, 50) == 1:
            c.add_random(GOLD_GRAPE)
        else:
            c.add_random(FOOD)
        if randint(1, 5) == 1:
            c.add_random(choice([POISON, SLOW_POT, SPEED_POT]))


class Poison(Item):
    def __init__(self):
        Item.__init__(self, POISON, "res/poison.png", color=(128, 200, 0))

    def on_tick(self, snake, dt):
        snake.pop += 1
        snake.items.remove(self)


class Carcass(Item):
    def __init__(self):
        Item.__init__(self, CARCASS, "res/carcass.png", color=(200, 150, 0))

    def on_tick(self, snake, dt):
        snake.add += 1
        snake.items.remove(self)
        if randint(1, 3) == 1:
            c.add_random(POISON)


class GoldGrape(Item):
    def __init__(self):
        Item.__init__(self, GOLD_GRAPE, "res/gold_grape.png", color=(180, 160, 80))
        self.time = 0

    def on_activate(self):
        self.time = 3000

    def on_tick(self, snake, dt):
        if self.time % 1000 < dt:
            snake.add += 1
        self.time -= dt
        if self.time <= 0:
            snake.items.remove(self)
            if randint(1, 10) == 1:
                c.add_random(FOOD)
            c.add_random(FOOD)
            c.add_random(choice([SLOW_POT, SPEED_POT, POISON]))
            if randint(1, 2) == 1:
                c.add_random(INSTA_KILL)


class SpeedPot(Item):
    def __init__(self):
        Item.__init__(self, SPEED_POT, "res/speed.png", color=(64, 200, 150))

    def on_tick(self, snake, dt):
        snake.spd_mult /= 1.1
        snake.items.remove(self)


class SlowPot(Item):
    def __init__(self):
        Item.__init__(self, SLOW_POT, "res/slow.png", color=(200, 150, 75))

    def on_tick(self, snake, dt):
        snake.spd_mult *= 1.1
        snake.items.remove(self)


class InstaKill(Item):
    def __init__(self):
        Item.__init__(self, INSTA_KILL, img="res/insta_kill.png", color=(0, 0, 175))

    def on_tick(self, snake, dt):
        snake.die()
        snake.items.remove(self)
