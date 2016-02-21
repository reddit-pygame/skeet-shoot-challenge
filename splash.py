import os
import json

import pygame as pg

import prepare
from state_engine import GameState
from animation import Animation, Task
from clay_pigeon import ClayPigeon
from world import World


class Splash(GameState):
    """Splash/Title screen"""
    def __init__(self):
        super(Splash, self).__init__()
        self.next_state = "SHOOTING"
        self.animations = pg.sprite.Group()
        with open(os.path.join("resources", "clay_spots.json"), "r") as f:
            skeet_spots = json.load(f)
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.clays = pg.sprite.OrderedUpdates()
        delay = 0
        duration = 500
        depth = 5000
        for spot in skeet_spots:
            clay = ClayPigeon((640, 750), 7, 0, False, self.clays, self.all_sprites)
            clay.rect.center = 640, 750
            clay.z = depth
            x, y = spot
            ani = Animation(centerx=x, centery=y, duration=duration, delay=delay, round_values=True)
            ani.start(clay.rect)
            self.animations.add(ani)
            
            delay += 15
            depth -= 1
    
        self.world = World(False)
        for s in self.all_sprites:
            self.all_sprites.change_layer(s, -s.z)
        try:
            with open(os.path.join("resources", "high_scores.json"), "r") as f:
                high_scores = json.load(f)
        except IOError:
            with open(os.path.join("resources", "high_scores.json"), "w") as f:
                json.dump([], f)
                
    def startup(self, persistent):
        self.persist = persistent

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.done = True

    def update(self, dt):
        self.animations.update(dt)
        self.world.update(dt)
        
    def draw(self, surface):
        surface.fill(self.world.sky)
        surface.fill(self.world.grass, self.world.ground_rect)
        self.all_sprites.draw(surface)
        
        


