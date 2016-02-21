import sys
import pygame as pg

from state_engine import Game, GameState
import prepare
import splash, shooting, high_score_screen

states = {"SPLASH": splash.Splash(),
               "SHOOTING": shooting.Shooting(),
               "HIGHSCORES": high_score_screen.HighScores()}
game = Game(prepare.SCREEN, states, "SPLASH")
game.run()
pg.quit()
sys.exit()