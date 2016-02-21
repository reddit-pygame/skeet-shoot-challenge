import os
import json

import pygame as pg

import prepare
from state_engine import GameState
from labels import Label


class HighScores(GameState):
    def __init__(self):
        super(HighScores, self).__init__()

    def startup(self, persistent):
        self.persist = persistent
        with open(os.path.join("resources", "high_scores.json"), "r") as f:
            self.high_scores = json.load(f)
        self.new_score = self.persist["score"]
        self.high_scores.append(self.new_score)
        self.high_scores.sort(reverse=True)
        if len(self.high_scores) > 10:
            self.high_scores = self.high_scores[:10]
        with open(os.path.join("resources", "high_scores.json"), "w") as f:
            json.dump(self.high_scores, f)
        self.make_score_labels()
        self.timer = 0

    def make_score_labels(self):
        self.labels = pg.sprite.Group()
        centerx = prepare.SCREEN_RECT.centerx
        title = Label("High Scores", {"midtop": (centerx, 10)}, self.labels, font_size=64, text_color=(225, 111, 4))
        top = 80
        for score in self.high_scores:
            label = Label("{}".format(score), {"midtop": (centerx, top)}, self.labels, font_size=48)
            top += 60

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.timer >= 1000:
                self.done = True
                self.next_state = "SHOOTING"

    def update(self, dt):
        self.timer += dt

    def draw(self, surface):
        surface.fill(pg.Color("skyblue"))
        self.labels.draw(surface)