from __future__ import annotations
from typing import TYPE_CHECKING
import pygame as pg
import sys

# from GameControl.gameControl import GameControl
# from GameControl.settings import *
from GameControl.setting import Setting
from view.utils import draw_text
from view.camera import Camera
from view.world import World
# from GameControl.settings import *
# import random
from GameControl.EventManager import *
from GameControl.gameControl import GameControl
from GameControl.saveAndLoad import *
from view.graph import *
# from GameControl.inputManager import *

class Game_Online:
    instance = None
    def __init__(self, screen, clock):
        self.setting = Setting.getSettings()
        self.gameController = GameControl.getInstance()
        self.network = Network.getNetworkInstance()
        self.etat = EtatJeu.getEtatJeuInstance()
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()
        
        self.camera = None

        # self.gameController.initiateBobs(self.setting.getNbBob())
        # # self.gameController.eatingTest()
        # self.gameController.respawnFood()
        # self.createNewGame()
        # print("Game: ", self.setting.getGridLength(), self.setting.getNbBob(), self.setting.getFps(), self.setting.getTileSize()) 
    
    def createNewGame(self):
        self.gameController.initiateGame()
        self.gameController.is_online = True
        self.gameController.createWorld(self.setting.getGridLength(),self.setting.getGridLength()) 
        self.camera = Camera(self.width, self.height) 
        self.gameController.nbBobPut = 5
        self.load_game()
    
    def load_game(self):
        for color, player in self.network.clientList.items():
            if player is not self.network.this_client and player is not None and player.ready:
                if player.ready_rep_pkg == None:
                    raise Exception("Player ready_rep_pkg is None")
                player.ready_rep_pkg.extractData()
                for data in player.ready_rep_pkg.data:
                    if data.type == BOB_STATUS:
                        bob = Bob()
                        bob.id = data.data['id']
                        bob.color = data.data['color']
                        for row in self.gameController.grid:
                            for tile in row:
                                if tile.getGameCoord() == data.data['currentTile']:
                                    bob.CurrentTile = tile
                                    tile.addBob(bob)
                                    break
                        for coord in data.data['previousTiles']:
                            for row in self.gameController.grid:
                                for tile in row:
                                    if tile.getGameCoord() == coord:
                                        bob.PreviousTiles.append(tile)
                        bob.energy = data.data['energy']
                        bob.mass = data.data['mass']
                        bob.velocity = data.data['velocity']
                        bob.speed = data.data['speed']
                        bob.vision = data.data['vision']
                        bob.memoryPoint = data.data['memoryPoint']
                        self.gameController.listBobs.append(bob)
                    elif data.type == FOOD_STATE:
                        for cas in data.data:
                            for row in self.gameController.grid:
                                for tile in row:
                                    if tile.getGameCoord() == cas[0]:
                                        tile.foodEnergy = cas[1]
                                        break
                    elif data.type == BOB_BORN:
                        bob = Bob()
                        bob.id = data.data['id']
                        bob.color = data.data['color']
                        for row in self.gameController.grid:
                            for tile in row:
                                if tile.getGameCoord() == data.data['currentTile']:
                                    bob.CurrentTile = tile
                                    tile.addBob(bob)
                                    break
                        for coord in data.data['previousTiles']:
                            for row in self.gameController.grid:
                                for tile in row:
                                    if tile.getGameCoord() == coord:
                                        bob.PreviousTiles.append(tile)
                        bob.energy = data.data['energy']
                        bob.mass = data.data['mass']
                        bob.velocity = data.data['velocity']
                        bob.speed = data.data['speed']
                        bob.vision = data.data['vision']
                        bob.memoryPoint = data.data['memoryPoint']
                        self.gameController.addToNewBornQueue(bob)

    def loadGame(self, saveNumber):
        loadSetting(saveNumber)
        # self.setting = Setting.getSettings()
        self.gameController.initiateGame()
        self.gameController.createWorld(self.setting.getGridLength(),self.setting.getGridLength()) 
        loadGameController(saveNumber)
        self.world = World(self.width, self.height)
        self.camera = Camera(self.width, self.height) 
        # self.gameController.initiateBobs(self.setting.getNbBob())
        loadBob(saveNumber)
        loadFood(saveNumber) 

    # def saveGameByInput(self, event):
    #     if event.key == pg.K_1:
    #         # print("save")
    #         saveGame(1)
    #     if event.key == pg.K_2:
    #         # print("save")
    #         saveGame(2)
    #     if event.key == pg.K_3:
    #         # print("save")
    #         saveGame(3)
    #     if event.key == pg.K_4:
    #         # print("save")
    #         saveGame(4)
    #     if event.key == pg.K_5:
    #         # print("save")
    #         saveGame(5)

    
    def run(self):
        from network.network import Network
        self.playing = True
        self.gameController.phase = 1
        while self.playing:
            self.clock.tick(5*self.setting.getFps())
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        self.etat.waiting_room = False
                        self.etat.online_menu = True
                        self.etat.online_game = False
                        self.playing = False
                        self.network.close_socket()
                        Network.destroyNetwork()
                        return
                    elif event.key == pg.K_b:
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        listRect = []
                        for row in self.gameController.getMap():
                            for tile in row:
                                (x,y) = tile.getRenderCoord()
                                offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                                a, b = offset
                                if -64 <= (a + self.camera.scroll.x) <= 1920 and -64 <= (b + self.camera.scroll.y)  <= 1080:
                                    listRect.append((tile,(a + self.camera.scroll.x, b + self.camera.scroll.y)))
                        for coord in listRect:
                            if coord[1][0] < mouse_x < coord[1][0] + 64 and coord[1][1] + 8 < mouse_y < coord[1][1] + 24:
                                if coord[0].territoire == self.network.this_client.color:
                                    if self.gameController.nbBobPut > 0:
                                        self.gameController.add_bob_online(coord[0])
                                        self.gameController.nbBobPut -= 1   
                    elif event.key == pg.K_n:
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        listRect = []
                        for row in self.gameController.getMap():
                            for tile in row:
                                (x,y) = tile.getRenderCoord()
                                offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                                a, b = offset
                                if -64 <= (a + self.camera.scroll.x) <= 1920 and -64 <= (b + self.camera.scroll.y)  <= 1080:
                                    listRect.append((tile,(a + self.camera.scroll.x, b + self.camera.scroll.y)))
                        for coord in listRect:
                            if coord[1][0] < mouse_x < coord[1][0] + 64 and coord[1][1] + 8 < mouse_y < coord[1][1] + 24:
                                if self.gameController.nbFoodPut > 0:
                                    self.gameController.add_food_online(coord[0])


            self.gameController.tick_online_update()
            # print(self.gameController.renderTick)
            self.network.listen()

            screen.fill((137, 207, 240))
            surface = pg.Surface((setting.getSurfaceWidth(), setting.getSurfaceHeight())).convert_alpha()
            surface.fill((195, 177, 225))
            self.drawModifiable_Online(surface, self.camera)
            screen.blit(surface, (self.camera.scroll.x, self.camera.scroll.y))    
            self.drawIndex_Online(screen)
            # drawIndex ( screen )
            pg.display.flip()

            # self.update()
            # self.draw()
            # if self.setting.simuMode:
            #     self.gameController.increaseTick()
            #     self.drawSimu()
            # else:
            # self.gameController.updateRenderTick()
            # self.draw()
            # else:
            #     self.clock.tick(5*self.setting.getFps())
            #     self.events()
            #     self.update()
            #     # self.draw()
            #     self.gameController.updateRenderTick()
            #     self.draw()
        if not self.etat.playing:
            return
            

    def drawModifiable_Online(self, surface, camera):
        net = Network.getNetworkInstance()
        textureImg = loadGrassImage()
        flowImg = loadFlowerImage()
        darkGrass = loadDarkGrassImage()
        darkFlower = loadDarkFlowerImage()
        brightGrass = loadGrassBrightImage()
        brightFlower = loadFlowerBrightImage()
        for row in self.gameController.getMap(): # x is a list of a double list Map
            for tile in row: # tile is an object in list
                (x, y) = tile.getRenderCoord()
                offset = (x + setting.getSurfaceWidth()/2 , y + setting.getTileSize())
                a,b = offset
                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                    if tile.seen and not tile.hover:
                        if tile.flower:
                            surface.blit(flowImg, offset)
                        else:
                            surface.blit(textureImg, offset)
                    else:
                        if tile.flower:
                            surface.blit(darkFlower, offset)
                        else:
                            surface.blit(darkGrass, offset)
                    if tile.hover:
                        if tile.flower:
                            surface.blit(brightFlower, offset)
                        else:
                            surface.blit(brightGrass, offset)
                        tile.hover = False
                else: pass

        greenLeft = loadGreenLeft()
        blueLeft = loadBlueLeft()
        purpleLeft = loadPurpleLeft()
        redLeft = loadRedLeft()

        explode1 = loadExplosionImage()[1]
        explode2 = loadExplosionImage()[2]
        explode3 = loadExplosionImage()[3]
        explode4 = loadExplosionImage()[4]
        explode5 = loadExplosionImage()[5]
        explode6 = loadExplosionImage()[6]
        explode7 = loadExplosionImage()[7]
        explode8 = loadExplosionImage()[8]

        spawn1 = loadSpawnImage()[1]
        spawn2 = loadSpawnImage()[2]
        spawn3 = loadSpawnImage()[3]
        spawn4 = loadSpawnImage()[4]
        spawn5 = loadSpawnImage()[5]
        spawn6 = loadSpawnImage()[6]
        spawn7 = loadSpawnImage()[7]
        spawn8 = loadSpawnImage()[8]

        for bob in self.gameController.listBobs:
            if (bob not in self.gameController.diedQueue) and (bob not in self.gameController.newBornQueue):
                # if(self.gameController.getTick() % 2 == 0 ):
                    nbInteval = len(bob.getPreviousTiles()) - 1
                    
                    if ( self.gameController.renderTick < setting.getFps()/2):
                        if ( self.gameController.renderTick == 0 and bob.color != net.this_client.color and self.gameController.phase == 2):
                            (destX, destY) = bob.getCurrentTile().getRenderCoord()
                            (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
                            finish = (desX, desY + setting.getTileSize())
                            a,b = finish
                            if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                                self.afficherText(surface, f"Energy: {bob.energy}", finish[0], finish[1] - 5, 15, (255,0,0))
                                if bob.color == 1:
                                    surface.blit(redLeft, finish)
                                elif bob.color == 2:
                                    surface.blit(blueLeft, finish)
                                elif bob.color == 3:
                                    surface.blit(greenLeft, finish)
                                elif bob.color == 4:
                                    surface.blit(purpleLeft, finish)
                            else: pass
                        else:
                            if nbInteval == 0:
                                (destX, destY) = bob.getCurrentTile().getRenderCoord()
                                (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
                                finish = (desX, desY + setting.getTileSize())
                                a,b = finish
                                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                                    self.afficherText(surface, f"Energy: {bob.energy}", finish[0], finish[1] - 5, 15, (255,0,0))
                                    if bob.color == 1:
                                        surface.blit(redLeft, finish)
                                    elif bob.color == 2:
                                        surface.blit(blueLeft, finish)
                                    elif bob.color == 3:
                                        surface.blit(greenLeft, finish)
                                    elif bob.color == 4:
                                        surface.blit(purpleLeft, finish)
                                else: pass
                            else:
                                for i in range( nbInteval):
                                    if ( i*setting.getFps()) / (nbInteval * 2) <= self.gameController.renderTick < (i+1)*setting.getFps() / (nbInteval * 2):
                                        (x, y) = bob.getPreviousTiles()[i].getRenderCoord()
                                        (X, Y) = (x + surface.get_width()/2 , y - (50 - setting.getTileSize() ) )
                                        (destX, destY) = bob.getPreviousTiles()[i+1].getRenderCoord()
                                        (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
                                        pos = (X + (desX - X) * (self.gameController.renderTick - (i*setting.getFps())/(2 * nbInteval)) * (2 * nbInteval) / setting.getFps() , Y + (desY - Y) * (self.gameController.renderTick - (i*setting.getFps())/(2 * nbInteval) ) * (2 * nbInteval) / setting.getFps()  + setting.getTileSize()  )
                                        a,b = pos
                                        if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                                            self.afficherText(surface, f"Energy: {bob.energy}", pos[0], pos[1] - 5, 15, (255,0,0))
                                            if bob.color == 1:
                                                surface.blit(redLeft, pos)
                                            elif bob.color == 2:
                                                surface.blit(blueLeft, pos)
                                            elif bob.color == 3:
                                                surface.blit(greenLeft, pos)
                                            elif bob.color == 4:
                                                surface.blit(purpleLeft, pos)
                                        else: pass
                                    else: pass
                    else:
                        (destX, destY) = bob.getCurrentTile().getRenderCoord()
                        (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
                        finish = (desX, desY + setting.getTileSize())
                        a,b = finish
                        if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                            self.afficherText(surface, f"Energy: {bob.energy}", finish[0], finish[1] - 5, 15, (255,0,0))
                            if bob.color == 1:
                                surface.blit(redLeft, finish)
                            elif bob.color == 2:
                                surface.blit(blueLeft, finish)
                            elif bob.color == 3:
                                surface.blit(greenLeft, finish)
                            elif bob.color == 4:
                                surface.blit(purpleLeft, finish)
                        else: pass
        for bob in self.gameController.diedQueue:
            (x, y) = bob.getPreviousTile().getRenderCoord()
            (X, Y) = (x + surface.get_width()/2 , y - (50 - setting.getTileSize() ) )
            position = (X, Y)
            # print(bob.getNextTile())
            (destX, destY) = bob.getCurrentTile().getRenderCoord()
            (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
            start = (X + (desX - X) * (2 *self.gameController.renderTick/setting.getFps()), Y + (desY - Y) * (2* self.gameController.renderTick/setting.getFps()) + setting.getTileSize())
            finish = (desX, desY + setting.getTileSize())
            a , b = finish
            if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                if (self.gameController.renderTick < setting.getFps()/2):
                    if bob.color == 1:
                        surface.blit(redLeft, start)
                    elif bob.color == 2:
                        surface.blit(blueLeft, start)
                    elif bob.color == 3:
                        surface.blit(greenLeft, start)
                    elif bob.color == 4:
                        surface.blit(purpleLeft, start)
                elif setting.getFps()/2 <= self.gameController.renderTick < setting.getFps()/2 + setting.getFps()/16:
                    surface.blit(explode1, finish)
                elif setting.getFps()/2 + setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 2*setting.getFps()/16:
                    surface.blit(explode2, finish)
                elif setting.getFps()/2 + 2*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 3*setting.getFps()/16:
                    surface.blit(explode3, finish)
                elif setting.getFps()/2 + 3*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 4*setting.getFps()/16:
                    surface.blit(explode4, finish)
                elif setting.getFps()/2 + 4*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 5*setting.getFps()/16:
                    surface.blit(explode5, finish)
                elif setting.getFps()/2 + 5*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 6*setting.getFps()/16:
                    surface.blit(explode6, finish)
                elif setting.getFps()/2 + 6*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 7*setting.getFps()/16:
                    surface.blit(explode7, finish)
                else:
                    surface.blit(explode8, finish)
            else: pass

        for bob in self.gameController.newBornQueue:
            if bob not in self.gameController.diedQueue:
                # (x, y) = bob.getPreviousTile().getRenderCoord()
                # (X, Y) = (x + surface.get_width()/2 , y - (greenLeftt_height() - setting.getTileSize() ) )
                (destX, destY) = bob.getCurrentTile().getRenderCoord()
                (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
                # position = (X, Y + setting.getTileSize())
                # start = (X + (desX - X) * (2 *self.gameController.renderTick/setting.getFps()), Y + (desY - Y) * (2* self.gameController.renderTick/setting.getFps()) + setting.getTileSize())
                finish = (desX, desY + setting.getTileSize())
                a,b = finish
                if -64 <= (a  + camera.scroll.x) <= 1920 and -64 <= (b  + camera.scroll.y)  <= 1080:
                    if self.gameController.renderTick < setting.getFps()/2:
                        # screen.blit(greenLefttart) # need to change to newborn bob texture later
                        # pg.draw.rect(screen, (255, 0, 0), (start[0], start[1] - 5, bar_width, 5))
                        pass
                    # else:
                    #     screen.blit(greenLeftinish)
                    #     pg.draw.rect(screen, (255, 0, 0), (finish[0], finish[1] - 5, bar_width, 5))
                    elif setting.getFps()/2 <= self.gameController.renderTick < setting.getFps()/2 + setting.getFps()/16:
                        surface.blit(spawn1, finish)
                    elif setting.getFps()/2 + setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 2*setting.getFps()/16:
                        surface.blit(spawn2, finish)
                    elif setting.getFps()/2 + 2*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 3*setting.getFps()/16:
                        surface.blit(spawn3, finish)
                    elif setting.getFps()/2 + 3*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 4*setting.getFps()/16:
                        surface.blit(spawn4, finish)
                    elif setting.getFps()/2 + 4*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 5*setting.getFps()/16:
                        surface.blit(spawn5, finish)
                    elif setting.getFps()/2 + 5*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 6*setting.getFps()/16:
                        surface.blit(spawn6, finish)
                    elif setting.getFps()/2 + 6*setting.getFps()/16 <= self.gameController.renderTick < setting.getFps()/2 + 7*setting.getFps()/16:
                        surface.blit(spawn7, finish)
                    else:
                        surface.blit(spawn8, finish)
                else: pass
        
        foodTexture = loadFoodImage()
        for food in self.gameController.getFoodTiles():
            (x, y) = food.getRenderCoord()
            (X, Y) = (x + surface.get_width()/2  , y - ( 50 - setting.getTileSize() ) )
            position = (X , Y + setting.getTileSize() )
            a,b = position
            if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                self.afficherText(surface, f"Food: {food.foodEnergy}", position[0], position[1] - 5, 15, (0,0,255))
                surface.blit(foodTexture, position)
            else: pass
        mouse_x, mouse_y = pg.mouse.get_pos()
        camera.update()
        ##### Can lam #####
        if net.this_client.color == 1:
            surface.blit(redLeft, (mouse_x - redLeft.get_width()//2 - camera.scroll.x, mouse_y - redLeft.get_height()//2 - camera.scroll.y))
        if net.this_client.color == 2:
            surface.blit(blueLeft, (mouse_x - blueLeft.get_width()//2 - camera.scroll.x, mouse_y - blueLeft.get_height()//2 - camera.scroll.y))
        if net.this_client.color == 3:
            surface.blit(greenLeft, (mouse_x - greenLeft.get_width()//2 - camera.scroll.x, mouse_y - greenLeft.get_height()//2 - camera.scroll.y))
        if net.this_client.color == 4:
            surface.blit(purpleLeft, (mouse_x - purpleLeft.get_width()//2 - camera.scroll.x, mouse_y - purpleLeft.get_height()//2 - camera.scroll.y))
        
        ######################
        
        listRect = []
        for row in self.gameController.getMap():
            for tile in row:
                territoire_true = net.this_client.color == tile.territoire
                (x,y) = tile.getRenderCoord()
                offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                a, b = offset
                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                    if territoire_true: 
                        listRect.append((tile,(a + camera.scroll.x, b + camera.scroll.y)))

        for coord in listRect:
            if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                # print(coord[0].gridX, coord[0].gridY)
                coord[0].hover = True
                nb = 1
                # for bob in coord[0].getBobs():
                if ( mouse_y - 150 >= 0 ):
                    if ( mouse_x - 50*nb < 0 ):
                        pg.draw.rect(surface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x +50 , mouse_y - camera.scroll.y -50 , 100 * nb, 100))

                        draw_text(surface, f"Energy: {new_object_dict['Bob Energy']}", 15,(0,0,0),(mouse_x - camera.scroll.x +50  + 5 , mouse_y - camera.scroll.y -50 + 5))
                        draw_text(surface, f"Mass {new_object_dict['Bob Mass']}", 15,(0,0,0),(mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 15))
                        draw_text(surface, f"Vision {new_object_dict['Bob Vision']}",15,(0,0,0), ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 25)))
                        draw_text(surface, f"Velocity: {new_object_dict['Bob Velocity']}",15,(0,0,0), ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 35)))
                        draw_text(surface, f"Memory: {new_object_dict['Bob Memory Point']}",15,(0,0,0), ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 45)))
                        draw_text(surface, f"Food {new_object_dict['Food Energy']}",15,(0,0,0) , ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 55)))

                    elif( mouse_x + 50*nb > 1920  ):
                        pg.draw.rect(surface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x - 50 - 100*nb , mouse_y - camera.scroll.y - 50 , 100 * nb, 100))

                        draw_text(surface, f"Energy: {new_object_dict['Bob Energy']}", 15,(0,0,0),(mouse_x - camera.scroll.x - 50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 5))
                        draw_text(surface, f"Mass {new_object_dict['Bob Mass']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 15))
                        draw_text(surface, f"Vision {new_object_dict['Bob Vision']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 25)))
                        draw_text(surface, f"Velocity: {new_object_dict['Bob Velocity']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 35)))
                        draw_text(surface, f"Memory: {new_object_dict['Bob Memory Point']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 45)))
                        draw_text(surface, f"Food {new_object_dict['Food Energy']}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 55)))



                    else:
                        pg.draw.rect(surface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x -50 * nb , mouse_y - camera.scroll.y - 150 , 100 * nb, 100))
                        draw_text(surface, f"Energy: {new_object_dict['Bob Energy']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 5))
                        draw_text(surface, f"Mass {new_object_dict['Bob Mass']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 15))
                        draw_text(surface, f"Vision {new_object_dict['Bob Vision']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 25)))
                        draw_text(surface, f"Velocity: {new_object_dict['Bob Velocity']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 35)))
                        draw_text(surface, f"Memory: {new_object_dict['Bob Memory Point']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 45)))
                        draw_text(surface, f"Food {new_object_dict['Food Energy']}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 55)))

                else:
                    pg.draw.rect(surface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x -50 * nb , mouse_y - camera.scroll.y + 50 , 100 * nb, 100))
                    draw_text(surface, f"Energy: {new_object_dict['Bob Energy']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 5))
                    draw_text(surface, f"Mass {new_object_dict['Bob Mass']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 15))
                    draw_text(surface, f"Vision {new_object_dict['Bob Vision']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 25)))
                    draw_text(surface, f"Velocity: {new_object_dict['Bob Velocity']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 35)))
                    draw_text(surface, f"Memory: {new_object_dict['Bob Memory Point']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 45)))
                    draw_text(surface, f"Food {new_object_dict['Food Energy']}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 55)))

    def afficherText(self,surface, text, x, y, size, color):
        font = pg.font.Font(None, size)
        text = font.render(text, 1, color)
        surface.blit(text, (x, y))


    def drawIndex_Online(self, surface):
        
        net=Network.getNetworkInstance()
        connected_players = [player for player in net.clientList.values() if player is not None]
        greenLeft = loadGreenLeft()
        blueLeft = loadBlueLeft()
        purpleLeft = loadPurpleLeft()
        redLeft = loadRedLeft()

        draw_text(
        surface,
        'Tick: {}'.format(round(self.gameController.getTick())),
        25,
        (0,0,0),
        (10, 30)
        )
        draw_text(
        surface,
        'Day: {}'.format(round(self.gameController.getDay())),
        25,
        (0,0,0),
        (10, 50)
        )
        draw_text(
        surface,
        'Number of bobs: {}'.format(self.gameController.getNbBobs()),
        25,
        (0,0,0),
        (10, 70)
        )
        draw_text(
        surface,
        'Number of bob spawned: {}'.format(self.gameController.getNbBobsSpawned()),
        25,
        (0,0,0),
        (10, 90)
        )
        
        draw_text(
        surface,
        'Nombre de joueurs: {}'.format(len(connected_players)),
        25,
        (0,0,0),
        (10, 110) 
        )

        if net.clientList["Red"] and net.clientList["Red"].ready:
            surface.blit(redLeft, (10, 150))
        if net.clientList["Blue"] and net.clientList["Blue"].ready:
            surface.blit(blueLeft, (80, 150))
        if net.clientList["Green"] and net.clientList["Green"].ready:
            surface.blit(greenLeft, (150, 150))
        if net.clientList["Purple"] and net.clientList["Purple"].ready:
            surface.blit(purpleLeft, (220, 150))

    # def events(self):
    #     etat = EtatJeu.getEtatJeuInstance()
    #     for event in pg.event.get():
    #         if event.type == pg.QUIT:
    #             pg.quit()
    #             sys.exit()
    #         if event.type == pg.KEYDOWN:
    #             if event.key == pg.K_g:
    #                 self.self.gameController.renderTick = 0
    #                 #graph methods
    #                 save_graph_data()
    #                 save_born_data()
    #                 save_died_data()
    #                 save_mass_data()
    #                 save_veloce_data()
    #                 save_vision_data()
    #                 save_energy_data()

    #                 show_graph_data()
    #                 show_born_data()
    #                 show_died_data()
    #                 show_mass_data()
    #                 show_veloce_data()
    #                 show_vision_data()
    #                 show_energy_data()
    #                 #graph methods
    #             if event.key == pg.K_m:
    #                 # i = show_menu(self.screen, self.clock)
    #                 # if i == 0:
    #                 #     self.createNewGame()
    #                 # else:
    #                 #     self.loadGame(i)
    #                 self.playing = False
    #                 etat.playing = False
    #                 etat.open_menu = True
    #             # self.saveGameByInput(event)
    #             if event.key == pg.K_ESCAPE:
    #                 pg.quit()
    #                 sys.exit()
    #             if event.key == pg.K_BACKSPACE:
    #                 self.self.gameController.renderTick = 0
    #                 openIngamesetting()
    #             if event.key == pg.K_SPACE:
    #                 self.self.gameController.renderTick = 0
    #                 res = pause(self.screen,self.camera)
    #                 self.setting.simuMode = False
    #                 self.modeTransition(res)
    #             if event.key == pg.K_s:
    #                 self.self.gameController.renderTick = 0
    #                 self.setting.simuMode = not self.setting.simuMode
    #             # if event.key == pg.K_r:
    #             #     self.self.gameController.renderTick = 0
    #             #     newObjectMenu_Online(self.screen, self.clock ,self.camera)

    # def update(self):
    #     self.camera.update()
        
    # def drawSimu(self):
    #     self.screen.fill((137, 207, 240))
    #     self.world.drawSimu(self.screen, self.camera)
    #     self.drawIndex()
    #     pg.display.flip()


    # def draw(self):
    #     self.screen.fill((137, 207, 240))
    #     self.world.draw_online(self.screen, self.camera)
    #     self.drawIndex()
    #     pg.display.flip()

    # def drawIndex( self ):
    #     draw_text(
    #         self.screen,
    #         'FPS: {}'.format(round(self.clock.get_fps())),
    #         25,
    #         (0,0,0),
    #         (10, 10)
    #     )  
    #     draw_text(
    #         self.screen,
    #         'Tick: {}'.format(round(self.gameController.getTick())),
    #         25,
    #         (0,0,0),
    #         (10, 30)
    #     )  
    #     draw_text(
    #         self.screen,
    #         'Day: {}'.format(round(self.gameController.getDay())),
    #         25,
    #         (0,0,0),
    #         (10, 50)
    #     )  
    #     draw_text(
    #         self.screen,
    #         'Number of bobs: {}'.format(self.gameController.getNbBobs()) ,
    #         25,
    #         (0,0,0),
    #         (10, 70)
    #     )
    #     draw_text(
    #         self.screen,
    #         'Number of bob spawned: {}'.format(self.gameController.getNbBobsSpawned()) ,
    #         25,
    #         (0,0,0),
    #         (10, 90)
    #     )

    # def saveGameByInput(self, event):
    #     if event.key == pg.K_1:
    #         # print("save")
    #         saveGame(1)
    #     if event.key == pg.K_2:
    #         # print("save")
    #         saveGame(2)
    #     if event.key == pg.K_3:
    #         # print("save")
    #         saveGame(3)
    #     if event.key == pg.K_4:
    #         # print("save")
    #         saveGame(4)
    #     if event.key == pg.K_5:
    #         # print("save")
    #         saveGame(5)
    
    # def modeTransition(self, mode):
    #     if mode == 'Menu':
    #         i = show_menu(self.screen, self.clock)
    #         if i == 0:
    #             # print("i = ", i )
    #             # print("new game")
    #             self.createNewGame()
    #         else:
    #             self.loadGame(i)
    #     elif mode == 'InGameSetting':
    #         openIngamesetting()
    #     else:
    #         return


    @staticmethod
    def getInstance(screen, clock):
        if Game_Online.instance == None:
            Game_Online.instance = Game_Online(screen, clock)
        return Game_Online.instance