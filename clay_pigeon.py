from __future__ import division

from math import radians, sqrt, sin, cos

from random import randint, uniform
from itertools import cycle

import pygame as pg

import prepare
from animation import Animation, Task
from angles import project


GRAVITY = -.25


class ClayPigeon(pg.sprite.Sprite):
    broken_images = [prepare.GFX["broken{}".format(x)]
                                 for x in range(1, 20)]
    broken_glow_images = [prepare.GFX["broken-glow{}".format(x)]
                                          for x in range(1, 25)]

    def __init__(self, pos, pitch, yaw, speed, nighttime, *groups):
        super(ClayPigeon, self).__init__(*groups)
        self.x, self.y = pos
        self.z = 0
        self.start_x, self.start_y = self.x, self.y
        self.speed = speed #70 #speed of time elapsed for trajectory, lower means faster clays
        self.glow = nighttime
        if self.glow:
            self.base_image = prepare.GFX["glow-clay"]
        else:
            self.base_image = prepare.GFX["clay"]
        self.width, self.height = self.base_image.get_size()
        self.original_width, self.original_height = self.width, self.height
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(self.x, self.y))

        firing_speed = fs = 105
        pitch = radians(pitch)
        y = project((0, 0), pitch, 1)[1]
        x, z = project((0, 0), yaw, 1)
        z *= -1
        magnitude = sqrt(x**2 + y**2 + z**2)
        self.z_velocity = (z / magnitude) * firing_speed
        self.y_velocity = (y / magnitude) * firing_speed
        self.x_velocity = (x / magnitude) * firing_speed
        dist = ((fs**2)*sin(2*pitch)) / -GRAVITY 
        self.flight_time = (dist / (fs*cos(pitch))) * .85
        
        self.animations = pg.sprite.Group()
        self.timer = 0
        self.alpha = 255
        self.shattered = False

    def shatter(self):
        if self.shattered:
            return
        if self.glow:
            broken_images = self.broken_glow_images
        else:
            broken_images = self.broken_images
        self.animations.empty()
        size = self.width * 4
        images = [pg.transform.smoothscale(img, (size, size)) for img in broken_images]
        self.images = cycle(images)
        self.next_image()
        self.rect = self.image.get_rect(center=self.rect.center)

        frame_time = 15
        duration = frame_time * (len(images) - 1)
        task = Task(self.next_image, frame_time, -1)
        finish = Task(self.kill, duration)
        self.animations.add(task, finish)
        self.shattered = True

    def next_image(self):
        self.image = next(self.images)

    def update(self, dt):
        self.timer += dt
        elapsed = self.timer / self.speed
        if elapsed > self.flight_time:
            self.kill()
        
        self.animations.update(dt)

        dy = (self.y_velocity * elapsed) - (.5 * GRAVITY * elapsed**2)
        self.y = self.start_y + dy
        self.x = self.start_x + (self.x_velocity * elapsed)
        self.z = self.z_velocity * elapsed
        self.width = int(self.original_width * (.5**(self.z/3500.)))
        self.height = int(self.original_height * (.5**(self.z/3500.)))
        if self.width < 3:
            self.kill()
        if not self.shattered:
            self.image = pg.transform.smoothscale(self.base_image, (self.width, self.height))
            self.rect = self.image.get_rect(center=(self.x, self.y))

