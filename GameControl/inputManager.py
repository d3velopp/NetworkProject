from __future__ import annotations
from typing import TYPE_CHECKING
import pygame as pg
from pygame.locals import *
    
# from GameControl.game import Game

def loadGameByIndex(index: 'int'):
    screen = pg.display.set_mode((1920,1080), HWSURFACE | DOUBLEBUF)
    clock = pg.time.Clock()
    from GameControl.game import Game
    game = Game.getInstance(screen, clock) 
    game.loadGame(index)

def save