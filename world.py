from __future__ import division
from math import pi
from random import randint, uniform, choice
from itertools import cycle

import pygame as pg

import tools
import prepare
from angles import project
from animation import Task, Animation
from clay_pigeon import ClayPigeon

LEVELS = {
    1: {"delay_range": (4000, 6000),
          "pitch_range": (8.0, 8.0),
          "yaw_range": (.495 * pi, .505 * pi),
          "firing_speed": 70},
    2: {"delay_range": (3500, 5500),
          "pitch_range": (7.5, 8.5),
          "yaw_range": (.49 * pi, .51 * pi),
          "firing_speed": 65},
    3: {"delay_range": (3500, 5500),
          "pitch_range": (7.0, 9.0),
          "yaw_range": (.485 * pi, .515 * pi),
          "firing_speed": 60},
    4: {"delay_range": (3000, 5000),
          "pitch_range": (7.0, 9.0),
          "yaw_range": (.485 * pi, .515 * pi),
          "firing_speed": 55},
    5: {"delay_range": (3000, 5000),
          "pitch_range": (7.0, 9.0),
          "yaw_range": (.480 * pi, .52 * pi),
          "firing_speed": 50},
    6: {"delay_range": (2500, 4500),
          "pitch_range": (7.0, 9.0),
          "yaw_range": (.480 * pi, .52 * pi),
          "firing_speed": 45},
    7: {"delay_range": (2500, 4500),
          "pitch_range": (7.0, 9.0),
          "yaw_range": (.475 * pi, .525 * pi),
          "firing_speed": 40}}


class SkeetMachine(object):
    def __init__(self, positions, delay_range, pitch_range,
                         yaw_range, speed, world, active=True):
        self.positions = positions
        self.delay_range = delay_range
        self.pitch_range = pitch_range
        self.yaw_range = yaw_range
        self.speed = speed
        self.animations = pg.sprite.Group()
        self.world = world
        self.active = active
        if active:
            delay = randint(*self.delay_range)
            task = Task(self.shoot, delay)
            self.animations.add(task)
        self.shoot_sound = prepare.SFX["skeet-machine"]

    def shoot(self):
        self.shoot_sound.play()
        pitch = uniform(*self.pitch_range)
        yaw = uniform(*self.yaw_range)
        delay = randint(*self.delay_range)
        pos = choice(self.positions)
        clay = ClayPigeon(pos, pitch, yaw, self.speed, self.world.nighttime)
        task = Task(self.world.all_sprites.add, 550, args=(clay,))
        task2 = Task(self.world.clays.add, 550, args=(clay,))
        task3 = Task(self.shoot, delay)
        self.animations.add(task, task2)
        if self.active:
            self.animations.add(task3)

    def update(self, dt):
        self.animations.update(dt)


class BackgroundElement(pg.sprite.Sprite):
    def __init__(self, topleft, image_name, depth, *groups):
        super(BackgroundElement, self).__init__(*groups)
        self.name = image_name
        self.cover = prepare.GFX[image_name]
        self.cover.set_colorkey((255, 0, 255))
        self.rect = self.cover.get_rect(topleft=topleft)
        self.image = pg.Surface(self.rect.size)
        self.image.set_colorkey((0, 0, 0))
        self.z = depth

    def recolor(self, color):
        self.image.fill(color)
        self.image.blit(self.cover, (0, 0))


class CelestialBody(pg.sprite.Sprite):
    def __init__(self, image_name, pivot, radius, angle,
                         minute_length, *groups):
        super(CelestialBody, self).__init__(*groups)
        self.name = image_name
        self.image = prepare.GFX[image_name]
        self.rect = self.image.get_rect()
        self.timer = 0
        self.pivot = pivot
        self.radius = radius
        self.z = 50000
        self.ends = [project(self.pivot, angle - (x * pi), self.radius)
                           for x in (0, .5, 1, 1.5)]
        self.transitions = cycle([("in_sine", "out_sine"),
                                            ("out_sine", "in_sine")])
        self.ends = cycle(self.ends)
        self.rect.center = next(self.ends)
        self.animations = pg.sprite.Group()
        self.make_ani(minute_length)

    def make_ani(self, minute_length):
        dest = next(self.ends)
        x_trans, y_trans = next(self.transitions)
        duration = minute_length * 60 * 6
        ani = Animation(centerx=dest[0], duration=duration,
                                 transition=x_trans, round_values=True)
        ani2 = Animation(centery=dest[1], duration=duration,
                                  transition=y_trans, round_values=True)
        task = Task(self.make_ani, duration, args=(minute_length,))
        ani.start(self.rect)
        ani2.start(self.rect)
        self.animations.add(ani, ani2, task)

    def set_image(self, image_name):
        self.image = prepare.GFX[image_name]
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, dt, hours, minutes):
        self.animations.update(dt)


class DayNightCycle(object):
    def __init__(self, start_hour, start_minute, minute_length):
        self.minute_length = minute_length
        h, m = start_hour, start_minute
        self.timer = ((h * 60) + m) * self.minute_length

    @property
    def minutes(self):
        return (self.timer // self.minute_length) % (24 * 60)

    @property
    def clock_time(self):
        minutes = self.minutes
        hours, minutes = divmod(minutes, 60)
        return hours, minutes

    def update(self, dt):
        self.timer += dt


class World(object):
    colors = {
            "day": {
                "sky": pg.Color("skyblue"),
                "grass": pg.Color(125, 183, 100),
                "trees1": (95, 137, 75),
                "trees2": (82, 117, 64),
                "trees3": (73, 104, 57)},
            "night": {
                "sky": pg.Color(1, 2, 7),
                "grass":  pg.Color(11, 15, 8),
                "trees1":  (6, 10, 5),
                "trees2": (5, 7, 3),
                "trees3": (3, 5, 2)}}

    def __init__(self, machine_active):
        self.done = False
        self.dawn = 4
        self.noon_start = 10
        self.noon_end = 14
        self.midnight_start = 19
        ground_h = 250
        w, h = prepare.SCREEN_SIZE
        self.ground_rect = pg.Rect(0, h - ground_h, w, ground_h)
        self.active = machine_active
        self.reset()

    def reset(self):
        self.done = False
        minute_length = 60
        self.dn_cycle = DayNightCycle(6, 0, minute_length)
        self.clays = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.trees = pg.sprite.Group()
        BackgroundElement((0, 450), "trees1", 12000, self.trees, self.all_sprites)
        BackgroundElement((0, 431), "trees2", 14000, self.trees, self.all_sprites)
        BackgroundElement((0, 415), "trees3", 16000, self.trees, self.all_sprites)
        self.celestials = [CelestialBody("sun", (640, 900), 900, pi,
                                                      minute_length, self.all_sprites),
                                 CelestialBody("moon", (640, 900), 900, 0,
                                                      minute_length, self.all_sprites)]
        self.level_num = 6
        self.nighttime = False
        self.level_up()

    def level_up(self):
        max_level = max(LEVELS)
        if self.level_num < max_level:
            self.level_num += 1
            level = LEVELS[self.level_num]
            self.skeet_machine = SkeetMachine(
                        [(640, 730), (440, 730), (840, 730)],
                        level["delay_range"],
                        level["pitch_range"],
                        level["yaw_range"],
                        level["firing_speed"],
                        self, self.active)
        else:
            self.done = True

    def recolor(self, hour, minute):
        h, m = hour, minute
        if self.dawn <= h < self.noon_start:
            start = "night"
            finish = "day"
            minutes = ((h - self.dawn) * 60) + m
            lerp_val = (minutes / ((self.noon_start - self.dawn) * 60)) % 1.
        elif self.noon_start <= h < self.noon_end:
            start = "day"
            finish = "day"
            lerp_val = 0
        elif self.noon_end <= h < self.midnight_start:
            start = "day"
            finish = "night"
            minutes = ((h - self.noon_end) * 60) + m
            lerp_val = minutes / ((self.midnight_start - self.noon_end) * 60)
        elif (self.midnight_start <= h <= 24) or (0 <= h < self.dawn):
            start = "night"
            finish = "night"
            lerp_val = 0

        self.sky = tools.lerp(self.colors[start]["sky"],
                                      self.colors[finish]["sky"],
                                      lerp_val)
        self.grass = tools.lerp(self.colors[start]["grass"],
                                      self.colors[finish]["grass"],
                                      lerp_val)
        for tree in self.trees:
            color = tools.lerp(self.colors[start][tree.name],
                                       self.colors[finish][tree.name],
                                       lerp_val)
            tree.recolor(color)

    def update(self, dt):
        self.dn_cycle.update(dt)
        h, m = self.dn_cycle.clock_time
        self.recolor(h, m)
        for c in self.celestials:
            c.update(dt, h, m)
        nighttime = self.nighttime
        if 6 <= h <= 18:
            self.nighttime = False
        else:
            self.nighttime = True
        if nighttime and not self.nighttime:
            self.level_up()
        self.skeet_machine.update(dt)
        self.clays.update(dt)
