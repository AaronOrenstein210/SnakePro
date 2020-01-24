# Created on 14 January 2020

from math import ceil
from random import randint
import pygame as pg
import constants as c
from items import CARCASS


class Snake:
    def __init__(self, num, keys):
        self.surface = None
        self.num = num
        self.snake = []
        self.items = []
        self.keys = keys
        self.v = self.next_v = [0, 0]
        self.time = 0
        self.dead = False
        self.add = self.pop = 0
        self.growing = False
        self.spd_mult = 1
        self.zoom = 1
        self.trail = [i // 3 for i in c.COLORS[num]]
        self.spawn()

    @property
    def speed(self):
        return 250 * pow(.9, len(self.snake) - 1) * self.spd_mult

    def draw_snake(self, dt):
        if dt == 0 or self.v == [0, 0]:
            return
        end, front = self.snake[0], self.snake[-1]
        off_i = self.time * c.SQUARE_W // self.speed
        off_f = (self.time + dt) * c.SQUARE_W // self.speed
        if len(self.snake) == 1:
            v_back = self.v
        else:
            end2 = self.snake[1]
            v_back = [end2[0] - end[0], end2[1] - end[1]]
        # Update end if not growing
        if not self.growing:
            if v_back[0] != 0:
                rect = pg.Rect(0, end[1] * c.SQUARE_W, off_f - off_i, c.SQUARE_W)
                if v_back[0] == -1:
                    rect.x = end[0] * c.SQUARE_W + c.SQUARE_W - off_f - 1
                else:
                    rect.x = end[0] * c.SQUARE_W + off_i + 1
            else:
                rect = pg.Rect(end[0] * c.SQUARE_W, 0, c.SQUARE_W, off_f - off_i)
                if v_back[1] == -1:
                    rect.y = end[1] * c.SQUARE_W + c.SQUARE_W - off_f - 1
                else:
                    rect.y = end[1] * c.SQUARE_W + off_i + 1
            pg.draw.rect(c.surface, self.trail, rect)
        # Update front
        if self.v[0] != 0:
            rect = pg.Rect(0, front[1] * c.SQUARE_W, off_f - off_i, c.SQUARE_W)
            if self.v[0] == -1:
                rect.x = front[0] * c.SQUARE_W - off_f
            else:
                rect.x = front[0] * c.SQUARE_W + c.SQUARE_W + off_i
        else:
            rect = pg.Rect(front[0] * c.SQUARE_W, 0, c.SQUARE_W, off_f - off_i)
            if self.v[1] == -1:
                rect.y = front[1] * c.SQUARE_W - off_f
            else:
                rect.y = front[1] * c.SQUARE_W + c.SQUARE_W + off_i
        pg.draw.rect(c.surface, c.COLORS[self.num], rect)

    def tick(self, dt, keys):
        # Zoom minimap
        if keys[self.keys["Out"]]:
            self.zoom -= .5 * dt / 200
            if self.zoom < 1:
                self.zoom = 1
        elif keys[self.keys["In"]]:
            self.zoom += .5 * dt / 200
            if self.zoom > 5:
                self.zoom = 5

        # Move
        if not self.dead:
            # Update velocity
            if self.v[0] == 0:
                if keys[self.keys["Left"]]:
                    self.next_v = [-1, 0]
                elif keys[self.keys["Right"]]:
                    self.next_v = [1, 0]
            if self.v[1] == 0:
                if keys[self.keys["Up"]]:
                    self.next_v = [0, -1]
                elif keys[self.keys["Down"]]:
                    self.next_v = [0, 1]

            for item in self.items:
                item.on_tick(self, dt)

            while dt > 0:
                dt_ = min(dt, self.speed - self.time)
                self.draw_snake(dt_)
                dt -= dt_
                self.time = (self.time + dt_) % self.speed
                if self.time == 0:
                    if self.v != [0, 0]:
                        # Get current front and back and the new front
                        front, back = self.snake[-1], self.snake[0]
                        new = [front[0] + self.v[0], front[1] + self.v[1]]
                        # Check for death
                        if new[0] < 0 or new[1] < 0 or new[0] >= c.BOARD_W or new[1] >= c.BOARD_H:
                            self.die()
                        else:
                            val = c.board[new[1]][new[0]]
                            if val > 0:
                                s2 = c.snakes[val - 1]
                                if new == s2.snake[-1]:
                                    if len(s2.snake) > len(self.snake):
                                        self.die()
                                    elif len(s2.snake) < len(self.snake):
                                        s2.die()
                                    elif randint(1, 2) == 1:
                                        self.die()
                                    else:
                                        s2.die()
                                else:
                                    self.die()
                            else:
                                # If we aren't growing, remove end
                                if not self.growing:
                                    self.snake.pop(0)
                                    c.set_trail(*back, self.trail)
                                # Otherwise we finished growing
                                else:
                                    self.growing = False
                                # If we can add another segment, set growing to true
                                if self.add > 0:
                                    self.add -= 1
                                    self.growing = True
                                if self.pop == 0:
                                    self.snake.append(new)
                                    c.set_at(*new, self.num)
                                elif len(self.snake) == 0:
                                    self.snake.append(new)
                                    self.die()
                                else:
                                    self.pop -= 1
                                if val < 0:
                                    item = c.items[val]
                                    if val not in self.items:
                                        self.items.append(item)
                                    item.on_activate()
                    self.v = self.next_v
        # Try to respawn
        else:
            self.time += dt
            if self.time >= 1000:
                for name in ["Left", "Right", "Down", "Up"]:
                    if keys[self.keys[name]]:
                        self.spawn()
                        break

        self.draw_ui()

    def draw_ui(self):
        # Draw screen
        d = pg.display.get_surface()
        dim = d.get_size()
        margin = 5
        center = [self.snake[-1][0] + .5, self.snake[-1][1] + .5]
        if not self.dead:
            off = self.time / self.speed
            if self.v[0] == -1:
                center[0] -= off
            elif self.v[0] == 1:
                center[0] += off
            elif self.v[1] == -1:
                center[1] -= off
            elif self.v[1] == 1:
                center[1] += off
        x = (1 - self.num % 2) * dim[0] // 2
        y = (1 if self.num > 2 else 0) * dim[1] // 2
        w = dim[0] // 2 if c.num_snakes > 1 else dim[0]
        w_ = w - margin - margin
        h = dim[1] // 2 if c.num_snakes > 2 else dim[1]
        h_ = h - margin - margin
        left = (center[0] * c.SQUARE_W) - (w_ / 2)
        top = (center[1] * c.SQUARE_W) - (h_ / 2)
        d.fill(c.COLORS[self.num], (x, y, w, h))
        d.blit(c.surface, (x + margin, y + margin), area=(int(left), int(top), w_, h_))
        # Draw minimap
        map_w, map_h = w // 5, h // 5
        map_rect = pg.Rect(x + w - margin - map_w, y + h - margin - map_h, map_w, map_h)
        b_w, b_h = map_w / self.zoom, map_h / self.zoom
        left = center[0] - (b_w / 2)
        top = center[1] - (b_h / 2)
        right, bot = ceil(left + b_w), ceil(top + b_h)
        m_w, m_h = right - int(left), bot - int(top)
        s = pg.Surface((m_w, m_h))
        s.fill((128, 128, 128))
        s.blit(c.map_s, (0, 0), area=(int(left), int(top), m_w, m_h))
        off_x, off_y = int((left % 1) * self.zoom), int((top % 1) * self.zoom)
        s = pg.transform.scale(s, (int(m_w * self.zoom), int(m_h * self.zoom)))
        d.blit(s, map_rect.topleft, area=(off_x, off_y, map_w, map_h))
        if self.dead:
            s = pg.Surface((w, h))
            s.set_alpha(128)
            d.blit(s, (x, y))
            text_rect = c.restart_text.get_rect(center=(x + w // 2, y + h // 2))
            d.blit(c.restart_text, text_rect)

    def spawn(self):
        self.snake = [c.add_random(self.num)]
        c.set_at(*self.snake[0], self.num)
        # Reset variables
        self.dead = self.growing = False
        self.add = self.pop = self.time = 0
        self.v = self.next_v = [0, 0]
        self.spd_mult = 1
        self.items.clear()

    def die(self):
        for point in self.snake:
            c.set_trail(*point, self.trail)
            c.add_random(CARCASS)
        self.snake = self.snake[-1:]
        self.dead = True
