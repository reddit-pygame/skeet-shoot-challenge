import os
from random import choice, sample
import pygame as pg
import tools


SCREEN_SIZE = (1280, 720)
ORIGINAL_CAPTION = "Skeet Shoot"

pg.mixer.pre_init(44100, -16, 1, 512)

pg.init()
os.environ['SDL_VIDEO_CENTERED'] = "TRUE"
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()
pg.mixer.set_num_channels(16)
GFX = tools.load_all_gfx(os.path.join("resources", "graphics"))
SFX = tools.load_all_sfx(os.path.join("resources", "sounds"))
night_colors = [
        ("trees1", {(95, 137, 75): (6, 10, 5)}),
        ("trees2", {(82, 117, 64): (5, 7, 3)}),
        ("trees3", {(73, 104, 57): (3, 5, 2)})]
for name, swaps in night_colors:
    img = GFX[name]
    GFX["night-{}".format(name)] = tools.color_swap(img, swaps)