from math import radians

import pygame as pg

import prepare
from state_engine import GameState
from labels import Label
from animation import Task
from world import World
from clay_pigeon import ClayPigeon


class Crosshair(pg.sprite.Sprite):
    def __init__(self):
        super(Crosshair, self).__init__()
        self.image = prepare.GFX["crosshair"]
        self.rect = self.image.get_rect()


class Shooting(GameState):
    """Main gameplay state."""
    colors = {
            "day": {
                    "sky": pg.Color("skyblue"),
                    "grass": pg.Color(125, 183, 100)},
            "night": {
                    "sky": pg.Color(1, 2, 7),
                    "grass":  pg.Color(11, 15, 8)}}

    def __init__(self):
        super(Shooting, self).__init__()
        self.animations = pg.sprite.Group()
        self.crosshair = Crosshair()      
        self.world = World(True)
        self.cooldown = 0
        self.cooldown_duration = 250
 
    def startup(self, persistent):
        self.persist = persistent
        pg.mouse.set_visible(False)
        self.score = 0
        self.score_label = Label("{}".format(self.score),
                                           {"topleft": (5, 5)}, font_size=64)
        self.world.reset()
        
    def get_event(self, event):
        if event.type == pg.QUIT:
            pg.mouse.set_visible(True)
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            
            self.shoot()
        
    def update(self, dt):
        self.cooldown += dt
        self.animations.update(dt)
        self.world.update(dt)
        self.crosshair.rect.center = pg.mouse.get_pos()
        for sprite in self.world.all_sprites:
            self.world.all_sprites.change_layer(sprite, sprite.z * -1)
        self.score_label.set_text("{}".format(int(self.score)))
        if self.world.done:
            self.done = True
            self.persist["score"] = int(self.score)
            self.next_state = "HIGHSCORES"
            
    def shoot(self):
        if self.cooldown < self.cooldown_duration:
            return
        else:
            prepare.SFX["gunshot"].play()
            self.cooldown = 0
        for clay in [x for x in self.world.clays if not x.shattered]:
            if clay.rect.collidepoint(self.crosshair.rect.center):
                clay.shatter()
                self.add_points(clay)

    def add_points(self, clay):
        modifier = clay.z / 50.
        score = modifier * (100. / clay.speed)
        self.score += score

    def draw(self, surface):
        surface.fill(self.world.sky)
        surface.fill(self.world.grass, self.world.ground_rect)
        self.world.all_sprites.draw(surface)
        surface.blit(self.crosshair.image, self.crosshair.rect)
        surface.set_at(self.crosshair.rect.center, pg.Color("white"))
        self.score_label.draw(surface)