
import pygame as pg
from GameControl.game import Game
from GameControl.EventManager import show_menu, EtatJeu, open_network_setting, waiting_room
from pygame.locals import *
# from GameControl.inputManager import *
from GameControl.setting import Setting
# from GameControl.gameControl import GameControl
import sys

flags = HWSURFACE | DOUBLEBUF

def main():

    etat = EtatJeu.getEtatJeuInstance()
    pg.init()
    pg.mixer.init()
    # screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    screen = pg.display.set_mode((1920,1080), HWSURFACE | DOUBLEBUF)
    #screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    clock = pg.time.Clock()
    # setting = Setting.getSettings()
    # implement menus
    
    # implement game 

    while etat.running:
        
        # # start menu goes here
        # i = show_menu(screen, clock)
        # game = Game.getInstance(screen, clock)
        # if i == 0:
        #     # print("i = ", i )
        #     # print("new game")
        #     game.createNewGame()

        # else:
        #     game.loadGame(i)
        #     # game loop here
        # game.run()
        if etat.open_menu:
            show_menu(screen, clock)
        elif etat.playing:
            game = Game.getInstance(screen, clock)
            if etat.game_instance == 0:

                game.createNewGame()
            else: 
                game.loadGame(etat.game_instance)
            game.run()
        elif etat.online_menu:
            open_network_setting(screen, clock)
        elif etat.waiting_room:
            waiting_room(screen, clock)
        

            

if __name__ == "__main__":
    main()

