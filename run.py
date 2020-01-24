# Created on 6 January 2020
from inspect import getmembers, isclass
from random import randint
from sys import byteorder
from numpy import full, int8
import pygame as pg
from pygame.locals import *
import constants as c
from Snake import Snake
import items

# Compile a list of tiles
c.items.clear()
for name, obj in getmembers(items):
    if isclass(obj):
        if "items.Item" not in str(obj):
            # The constructor automatically adds the item to the list
            obj()

pg.init()


def main():
    pg.display.set_mode((c.MIN_W, c.MIN_H), RESIZABLE)
    pg.display.set_caption('Aaron, this is a school')
    new_game()
    pg.display.get_surface().fill((200, 200, 180))
    time = pg.time.get_ticks()
    while True:
        dt = pg.time.get_ticks() - time
        time = pg.time.get_ticks()
        events = pg.event.get()
        for e in events:
            if e.type == QUIT:
                pg.quit()
                exit(0)
            elif e.type == VIDEORESIZE:
                pg.display.set_mode((max(c.MIN_W, e.w), max(c.MIN_H, e.h)), RESIZABLE)
                pg.display.get_surface().fill((200, 200, 180))
        keys = pg.key.get_pressed()
        for player in c.snakes:
            player.tick(dt, keys)
        pg.display.update()


def new_game():
    c.num_snakes = 0
    c.snakes.clear()
    for i in range(choose_num_snakes()):
        c.snakes.append(choose_snake())
    c.board = full((c.BOARD_H, c.BOARD_W), 0, dtype=int8)
    c.surface = pg.Surface((c.BOARD_W * c.SQUARE_W, c.BOARD_H * c.SQUARE_W))
    c.add_random(items.FOOD)
    if c.num_snakes > 2:
        c.add_random(items.FOOD)


def choose_num_snakes():
    num = 1
    rects = {}

    def redraw():
        d = pg.display.get_surface()
        d.fill((0, 0, 0))
        w, h = d.get_size()
        quarter_h = h // 4
        text = "Set Number of Players"
        font = c.get_scaled_font(w, quarter_h, text, "Times New Roman")
        text = font.render(text, 1, (255, 255, 255))
        text_rect = text.get_rect(center=(w // 2, quarter_h // 2))
        d.blit(text, text_rect)

        square_w = min(w, quarter_h)
        rects["Up"] = pg.Rect((w - square_w) // 2, square_w, square_w, square_w)
        rects["Down"] = pg.Rect(rects["Up"].x, square_w * 3, square_w, square_w)
        rects["Num"] = pg.Rect(rects["Up"].x, quarter_h * 2, square_w, square_w)

        font = c.get_scaled_font(square_w, square_w, "0", "Times New Roman")
        text = font.render(str(num), 1, (255, 255, 255))
        text_rect = text.get_rect(center=rects["Num"].center)
        d.blit(text, text_rect)
        arrow = c.scale_to_fit(pg.image.load("res/arrow.png"), square_w, square_w)
        d.blit(arrow, rects["Up"])
        arrow = pg.transform.flip(arrow, False, True)
        d.blit(arrow, rects["Down"])

    def update_num():
        d = pg.display.get_surface()
        d.fill((0, 0, 0), rects["Num"])
        font = c.get_scaled_font(*rects["Num"].size, "0", "Times New Roman")
        text = font.render(str(num), 1, (255, 255, 255))
        text_rect = text.get_rect(center=rects["Num"].center)
        d.blit(text, text_rect)

    redraw()
    while True:
        for e in pg.event.get():
            if e.type == QUIT:
                pg.quit()
                exit(0)
            elif e.type == VIDEORESIZE:
                pg.display.set_mode((e.w, e.h), RESIZABLE)
                redraw()
            elif e.type == KEYUP and e.key == K_RETURN and num > 0:
                return num
            elif e.type == MOUSEBUTTONUP and e.button == BUTTON_LEFT:
                pos = pg.mouse.get_pos()
                if rects["Up"].collidepoint(*pos):
                    num += 1
                    if num > 4:
                        num = 4
                elif rects["Down"].collidepoint(*pos):
                    num -= 1
                    if num < 1:
                        num = 1
                else:
                    break
                update_num()
        pg.display.update()


key_names = ["Left", "Right", "Up", "Down", "Out", "In"]


def choose_snake():
    d = pg.display.get_surface()
    d.fill((0, 0, 0))
    w, h = d.get_size()
    names, keys = [], []
    with open("saves.bin", "rb+") as file:
        data = file.read()
        while len(data) > 0:
            str_len = int.from_bytes([data[0]], byteorder)
            names.append(data[1:str_len + 1].decode(encoding="ascii"))
            data = data[str_len + 1:]
            temp = {}
            for key in key_names:
                temp[key] = int.from_bytes(data[:2], byteorder)
                data = data[2:]
            keys.append(temp)

    def resize():
        item_h = line_h()
        font = c.get_scaled_font(-1, item_h, "|", "Times New Roman")
        temp = pg.Surface((w, item_h * (len(names) + 1)))
        margin = item_h // 10

        # Page title
        string = "Choose a Control Configuration for Snake {}".format(c.num_snakes + 1)
        font1 = c.get_scaled_font(w, item_h - margin, string, "Times New Roman")
        text = font1.render(string, 1, (172, 128, 128))
        text_rect = text.get_rect(top=margin, centerx=w // 2)
        temp.blit(text, text_rect)

        for i, n in enumerate(names):
            i += 1
            img_w = item_h - margin
            if n == "":
                img = pg.transform.scale(pg.image.load("res/add.png"), (img_w, img_w))
                img_rect = img.get_rect(centerx=w // 2, bottom=temp.get_size()[1])
                temp.blit(img, img_rect)
            else:
                pg.draw.rect(temp, (255, 245, 215), (margin, i * item_h + margin, w - margin * 2, item_h - margin))
                if font.size(n)[0] > w:
                    font_ = c.get_scaled_font(w, item_h, n, "Times New Roman")
                else:
                    font_ = font
                text = font_.render(n, 1, (0, 0, 0))
                text_rect = text.get_rect(centerx=w // 2, y=i * item_h + margin)
                temp.blit(text, text_rect)
                # Draw delete button
                img = pg.transform.scale(pg.image.load("res/delete.png"), (img_w, img_w))
                img_rect = img.get_rect(y=i * item_h + margin, right=temp.get_size()[0] - margin)
                temp.blit(img, img_rect)
                # Draw play button
                img = pg.transform.scale(pg.image.load("res/play.png"), (img_w, img_w))
                img_rect = img.get_rect(y=i * item_h + margin, left=margin)
                temp.blit(img, img_rect)
        return temp

    def max_offset():
        return max(0, s.get_size()[1] - d.get_size()[1])

    def line_h():
        return h // 10

    def scroll_amnt():
        return h // 20

    def add_new():
        names.append("")
        keys.append({"Left": K_a,
                     "Right": K_d,
                     "Up": K_w,
                     "Down": K_s,
                     "Out": K_e,
                     "In": K_q})

    add_new()
    s = resize()
    d.blit(s, (0, 0))
    off = 0
    while True:
        for e in pg.event.get():
            if e.type == QUIT:
                save_configs(names, keys)
                pg.quit()
                exit(0)
            elif e.type == VIDEORESIZE:
                dx, dy = abs(w - e.w), abs(h - e.h)
                if dx > dy:
                    h = int(h * e.w / w)
                    w = e.w
                else:
                    w = int(w * e.h / h)
                    h = e.h
                d = pg.display.set_mode((w, h), RESIZABLE)
                s = resize()
                d.blit(s, (0, off))
            elif e.type == MOUSEBUTTONUP:
                if e.button == BUTTON_WHEELUP:
                    off += scroll_amnt()
                    if off > 0:
                        off = 0
                    d.blit(s, (0, off))
                elif e.button == BUTTON_WHEELDOWN:
                    off -= scroll_amnt()
                    max_off = -max_offset()
                    if off < max_off:
                        off = max_off
                    d.blit(s, (0, off))
                elif e.button == BUTTON_LEFT:
                    pos = pg.mouse.get_pos()
                    idx = pos[1] // line_h() - 1
                    if 0 <= idx < len(key_names):
                        # Play
                        if pos[0] < line_h() and idx != len(names) - 1:
                            c.num_snakes += 1
                            return Snake(c.num_snakes, keys[idx])
                        # Remove
                        elif pos[0] >= s.get_size()[0] - line_h() and idx != len(names) - 1:
                            del names[idx]
                            del keys[idx]
                            s = resize()
                            d.fill((0, 0, 0))
                            d.blit(s, (0, off))
                        # Edit
                        else:
                            snake_config(names, keys, idx)
                            if idx == len(names) - 1:
                                add_new()
                            s = resize()
                            off = 0
                            d.fill((0, 0, 0))
                            d.blit(s, (0, off))
        pg.display.update()


def snake_config(names, keys, idx):
    w, h = pg.display.get_surface().get_size()
    if w != h:
        h = w
        pg.display.set_mode((w, h), RESIZABLE)

    rects = {}
    info = keys[idx]
    name = names[idx]
    selected = "Left"

    def resize():
        d = pg.display.get_surface()
        d.fill((0, 0, 0))
        w = d.get_size()[0]
        eighth_w = w // 8
        fourth_w = w // 4
        rects["Left"] = pg.Rect(eighth_w, fourth_w + eighth_w, fourth_w, fourth_w)
        rects["Right"] = pg.Rect(w - eighth_w - fourth_w, fourth_w + eighth_w, fourth_w, fourth_w)
        rects["Up"] = pg.Rect(eighth_w + fourth_w, fourth_w, fourth_w, fourth_w)
        rects["Down"] = pg.Rect(eighth_w + fourth_w, fourth_w * 2, fourth_w, fourth_w)
        rects["Out"] = pg.Rect(fourth_w, fourth_w * 3, fourth_w, fourth_w)
        rects["In"] = pg.Rect(fourth_w * 2, fourth_w * 3, fourth_w, fourth_w)
        rects["Name"] = pg.Rect(eighth_w, eighth_w, fourth_w * 3, eighth_w)
        draw()

    def draw(update_list=()):
        update_list = [i for i in update_list if i in rects.keys()]
        d = pg.display.get_surface()
        angle = {"Left": 90,
                 "Right": -90,
                 "Up": 0,
                 "Down": 180}
        for k_name in (rects.keys() if len(update_list) == 0 else update_list):
            rect = rects[k_name]
            d.fill((0, 0, 0), rect)
            if k_name == "Name":
                string = name
                if string == "":
                    string = "Enter Name"
            else:
                string = pg.key.name(info[k_name])
                if k_name == "Out":
                    img = "res/zoom_out.png"
                elif k_name == "In":
                    img = "res/zoom_in.png"
                else:
                    img = "res/arrow.png"
                arrow = pg.transform.scale(pg.image.load(img), (rect.w - 2, rect.h - 2))
                if k_name in angle.keys():
                    arrow = pg.transform.rotate(arrow, angle[k_name])
                arrow.convert_alpha()
                arrow.fill((255, 255, 255, 175), None, BLEND_RGBA_MULT)
                d.blit(arrow, (rect.x + 1, rect.y + 1))
            font = c.get_scaled_font(rect.w - 2, rect.h - 2, string, "Times New Roman")
            text = font.render(string, 1, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            d.blit(text, text_rect)
            if k_name == selected:
                pg.draw.rect(d, (200, 200, 0), rect, 2)

    resize()

    while True:
        for e in pg.event.get():
            if e.type == QUIT:
                save_configs(names, keys)
                pg.quit()
                exit(0)
            elif e.type == VIDEORESIZE:
                dx, dy = abs(w - e.w), abs(h - e.h)
                if dx > dy:
                    h = int(h * e.w / w)
                    w = e.w
                else:
                    w = int(w * e.h / h)
                    h = e.h
                pg.display.set_mode((w, h), RESIZABLE)
                resize()
            elif e.type == MOUSEBUTTONUP and e.button == BUTTON_LEFT:
                pos = pg.mouse.get_pos()
                for key in rects.keys():
                    if rects[key].collidepoint(*pos):
                        temp = pg.display.get_surface()
                        if selected != "":
                            pg.draw.rect(temp, (0, 0, 0), rects[selected], 2)
                        if selected == key:
                            selected = ""
                        else:
                            selected = key
                            pg.draw.rect(temp, (200, 200, 0), rects[selected], 2)
                        break
            elif e.type == KEYDOWN:
                # Exit
                if e.key == K_ESCAPE:
                    return
                # Done
                elif e.key == K_RETURN and name != "":
                    # Save information
                    names[idx] = name
                    keys[idx] = info
                    save_configs(names, keys)
                    return
                elif selected == "Name":
                    # Delete last character
                    if e.key == K_BACKSPACE:
                        name = name[:-1]
                    elif e.key == K_SPACE:
                        name += " "
                    # Add single character
                    elif len(pg.key.name(e.key)) == 1:
                        name += e.unicode
                elif selected != "":
                    info[selected] = e.key
                draw(update_list=[selected])
        pg.display.update()


def save_configs(names, keys):
    with open("saves.bin", "wb+") as file:
        for n, d in zip(names, keys):
            if n != "":
                file.write(len(n).to_bytes(1, byteorder))
                file.write(n.encode(encoding="ascii"))
                for key in key_names:
                    file.write(d[key].to_bytes(2, byteorder))


main()
