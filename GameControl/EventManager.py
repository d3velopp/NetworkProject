import pygame as pg
import sys
import time
pg.init()
pg.mixer.init()

selected_value_index = None
from GameControl.setting import Setting
import GameControl.game as Game
from GameControl.gameControl import GameControl
from view.world import *
from view.utils import *
from Tiles.Bob import *
from Tiles.tiles import *
from GameControl.saveAndLoad import *
from GameControl.valueEvaluator import *
from network.network import *

# Couleurs  
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PATH = "assets/menu/"

################ Game instance ################
setting = Setting.getSettings()
gameController = GameControl.getInstance()

settings_open = False
load_open = False
return_to_menu = False




##################### État du jeu #####################
class EtatJeu:
    instance = None
    def __init__(self):
        self.running = True
        self.playing = False
        self.game_instance = 0
        self.create_room = False
        self.open_menu = True
        self.online_menu = False
        self.waiting_room = False
        self.online_game = False
    def kill(self):
        self.running = False
        self.playing = False
        self.game_instance = 0
        self.open_menu = False
        self.online_menu = False

    @staticmethod
    def getEtatJeuInstance():
        if EtatJeu.instance == None:
            EtatJeu.instance = EtatJeu()
        return EtatJeu.instance 
        


# Création de la fenêtre en plein écran
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
pg.display.set_caption("Game Menu")


#################################### Theme, musique et police ####################################
# Charger l'image de fond, plusieurs images disponibles dans le dossier (à en choisir une)
background_image = pg.image.load(PATH + "back2.png")
background_image = pg.transform.scale(background_image, screen.get_size())

background_image1 = pg.image.load(PATH + "back4.jpg")
background_image1 = pg.transform.scale(background_image1, screen.get_size())

background_image2 = pg.image.load(PATH + "back3.jpg")
background_image2 = pg.transform.scale(background_image2, screen.get_size())

# Charger la musique de fond
pg.mixer.music.load( PATH + "song.mp3")
pg.mixer.music.set_volume(0.5)  # Le volume de 0.0 à 1.0
pg.mixer.music.play(-1)  # -1 pour jouer en boucle
# Initialiser la luminosité à 1.0 (valeur normale)
luminosite = 1.0

def augmenter_luminosite():
    global luminosite
    luminosite += 0.1
    pg.display.set_gamma(luminosite)


def diminuer_luminosite():
    global luminosite
    luminosite -= 0.1
    pg.display.set_gamma(luminosite)

def play_music():
    pg.mixer.music.play(-1)

def stop_music():
    pg.mixer.music.stop()

# Police pour les boutons
font = pg.font.Font(None, 40)
####################################### ############################################################\

############################ Gestion des boutons ####################################################
# Déclaration des rectangles des boutons de base
button_width, button_height = 300, 50
big_button_width, big_button_height = 400, 400
play_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 200, button_width, button_height)
settings_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 300, button_width, button_height)
quit_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 400, button_width, button_height)
back_button_rect = pg.Rect(20, 20, button_width, button_height)
stop_music_button_rect = pg.Rect(back_button_rect.right + 10, 20, button_width, button_height)
play_music_button_rect = pg.Rect(stop_music_button_rect.right + 10, 20, button_width, button_height)
increase_brightness_button_rect = pg.Rect(play_music_button_rect.right + 10, 20, button_width, button_height)
decrease_brightness_button_rect = pg.Rect(increase_brightness_button_rect.right + 10, 20, button_width, button_height)

grid_value_rects = dict()  # Réinitialise la liste des rectangles
grid_dict = { "FPS": setting.getFps() ,"GRID LENGTH": setting.getGridLength(),
               "NUMBER BOB": setting.getNbBob(), "NUMBER SPAWNED FOOD": setting.getNbSpawnFood(),  "FOOD ENERGY": setting.getFoodEnergy(),
               "BOB SPAWN ENERGY": setting.getBobSpawnEnergy(), "BOB MAX ENERGY": setting.getBobMaxEnergy() ,"BOB NEWBORN ENERGY": setting.getBobNewbornEnergy(), "SEXUAL BORN ENERGY": setting.getSexualBornEnergy(), 
               "BOB STATIONARY ENERGY LOSS": setting.getBobStationaryEnergyLoss(), "BOB SELF REPRODUCTION ENERGY LOSS": setting.getBobSelfReproductionEnergyLoss(), "BOB SEXUAL REPRODUCTION LOSS": setting.getBobSexualReproductionLoss(), "BOB SEXUAL REPRODUCTION LEVEL": setting.getBobSexualReproductionLevel(),
                "PERCEPTION FLAT PENALTY": setting.getPerceptionFlatPenalty(), "MEMORY FLAT PENALTY": setting.getMemoryFlatPenalty(),
                "DEFAULT VELOCITY": setting.getDefaultVelocity(), "DEFAULT MASS": setting.getDefaultMass(), "DEFAULT VISION": setting.getDefaultVision(), "DEFAULT MEMORY POINT": setting.getDefaultMemoryPoint(),
                "MASS VARIATION": setting.getMassVariation(), "VELOCITY VARIATION": setting.getVelocityVariation(), "VISION VARIATION": setting.getVelocityVariation() , "MEMORY VARIATION": setting.getMemoryVariation(),
                "SELF REPRODUCTION": setting.getSelfReproduction(),"SEXUAL REPRODUCTION": setting.getSexualReproduction()
               }

ingameparam = [ "FPS", "NUMBER SPAWNED FOOD" ,  "FOOD ENERGY", "BOB MAX ENERGY", "BOB NEWBORN ENERGY", "SEXUAL BORN ENERGY", "BOB STATIONARY ENERGY LOSS", "BOB SELF REPRODUCTION ENERGY LOSS", 
               "BOB SEXUAL REPRODUCTION LOSS", "BOB SEXUAL REPRODUCTION LEVEL", "PERCEPTION FLAT PENALTY", "MEMORY FLAT PENALTY"
               , "MASS VARIATION", "VELOCITY VARIATION", "VISION VARIATION" , "MEMORY VARIATION", "SELF REPRODUCTION", "SEXUAL REPRODUCTION" ]



grid_x = (screen.get_width() - len(max(grid_dict.keys(), key=len)) * 10) // 2
grid_y = (screen.get_height() - len(grid_dict.keys()) * 50) // 2


# Fonction pour dessiner du texte sur l'écran
def drawText(text, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Fonction pour dessiner les boutons avec transparence 
def draw_transparent_button(text, rect, transparency):
    button_surface = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
    button_surface.fill((WHITE[0], WHITE[1], WHITE[2], transparency))
    screen.blit(button_surface, (rect.x, rect.y))
    drawText(text, BLACK, rect.x + rect.width // 2, rect.y + rect.height // 2)

# Fonction pour dessiner les grilles avec transparence (la transparence des grilles des settings à revoir)
def draw_transparent_grids(labels, values, x, y, transparency):
    # global grid_value_rects
    # grid_value_rects = dict()  # Réinitialise la liste des rectangles
    cliquer = dict()
    for i, (label, value) in enumerate(zip(labels, values)):
        drawText(label, WHITE, x, y + 20 + i * 50) # Vẽ label thông số
        value_rect = pg.Rect(x + 320, y + i * 50, 200, 40) # Tạo hình chữ nhật thông số
        pg.draw.rect(screen, (WHITE[0], WHITE[1], WHITE[2], transparency), value_rect) # Vẽ hình chữ nhật thông số
        drawText(str(value), BLACK, x + 420, y + 20 + i * 50) # Vẽ giá trị thông số
        # grid_value_rects[label] = value_rect #  Pour cliquer 
        cliquer[label] = value_rect
    return cliquer

##############################################################################################################


# Dans la fonction open_settings
def open_settings():
    global selected_value_index, grid_value_rects, grid_dict, input_text, settings_open, ingameparam, input_active
    input_active = False
    input_text = ""
    back_button_rect = pg.Rect(20, 20, button_width, button_height)
    stop_music_button_rect = pg.Rect(back_button_rect.right + 10, 20, button_width, button_height)
    play_music_button_rect = pg.Rect(stop_music_button_rect.right + 10, 20, button_width, button_height)
    increase_brightness_button_rect = pg.Rect(play_music_button_rect.right + 10, 20, button_width, button_height)
    decrease_brightness_button_rect = pg.Rect(increase_brightness_button_rect.right + 10, 20, button_width, button_height)

    while True:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    # save_settings()
                    settings_open = False
                    return  # Retourner au menu principal
                
                if stop_music_button_rect.collidepoint(event.pos):
                    stop_music()
                
                if play_music_button_rect.collidepoint(event.pos):
                    play_music()

                if increase_brightness_button_rect.collidepoint(event.pos):
                    augmenter_luminosite()

                if decrease_brightness_button_rect.collidepoint(event.pos):
                    diminuer_luminosite()
                
                # Vérifie si la souris a cliqué sur une valeur spécifique

                for key,value in grid_value_rects.items() :
                    if value.collidepoint(event.pos):
                        selected_value_index = key
                        input_active = True
                        print("input_active")
                        # input_text = str(grid_dict[selected_value_index])  # Utiliser la valeur actuelle pour l'affichage initial
                        input_text = ""  # Utiliser la valeur actuelle pour l'affichage initial

            elif event.type == pg.KEYDOWN:
                if input_active:
                    valueEvaluator(event)
                
 

                            
        screen.blit(background_image, (0, 0))
        labels = list(grid_dict.keys())
        values = list(grid_dict.values())
        # Dessiner les grilles avec transparence
        grid_value_rects.update(draw_transparent_grids(labels[:len(labels)//2], values[:len(values)//2], 400, 300, 50))
        grid_value_rects.update(draw_transparent_grids(labels[len(labels)//2:], values[len(values)//2:], 1300, 300, 50))
   
        # draw_transparent_grids(grid_labels[len(grid_labels)//2:], grid_dict[len(grid_dict)//2:], 1100, 100, 50)
        # Dessiner le bouton de retour avec transparence
        draw_transparent_button("BACK", back_button_rect, 128)
        draw_transparent_button("Stop Music", stop_music_button_rect, 128)
        draw_transparent_button("Play Music", play_music_button_rect, 128)
        draw_transparent_button("Increase Brightness", increase_brightness_button_rect, 128)
        draw_transparent_button("Decrease Brightness", decrease_brightness_button_rect, 128)


        # Si une valeur est sélectionnée, dessine un contour autour de cette valeur
        if selected_value_index is not None:
            pg.draw.rect(screen, WHITE, grid_value_rects[selected_value_index], 2)

        # Si l'entrée est active, affiche le texte saisi
        if input_active:
            # Effacer l'ancien texte avec un rectangle blanc
            pg.draw.rect(screen, WHITE, (grid_value_rects[selected_value_index].x, grid_value_rects[selected_value_index].y, 200, 40))
            input_surface = font.render(input_text, True, BLACK)  # Couleur de la police en noir
            input_rect = input_surface.get_rect(center=(grid_value_rects[selected_value_index].centerx, grid_value_rects[selected_value_index].centery))
            # pg.draw.rect(screen, WHITE, (input_rect.x - 5, input_rect.y - 5, input_rect.width + 10, input_rect.height + 10), border_radius=5)  # Couleur de fond du rectangle en blanc
            screen.blit(input_surface, input_rect)

        pg.display.flip()











########################################## openIngamesetting  ##########################################
def openIngamesetting():
    global selected_value_index, grid_value_rects, grid_dict, input_text, settings_open, ingameparam, input_active
    input_active = False
    input_text = ""
    back_button_rect = pg.Rect(20, 20, button_width, button_height)
    stop_music_button_rect = pg.Rect(back_button_rect.right + 10, 20, button_width, button_height)
    play_music_button_rect = pg.Rect(stop_music_button_rect.right + 10, 20, button_width, button_height)
    increase_brightness_button_rect = pg.Rect(play_music_button_rect.right + 10, 20, button_width, button_height)
    decrease_brightness_button_rect = pg.Rect(increase_brightness_button_rect.right + 10, 20, button_width, button_height)
    

    while True:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    # save_settings()
                    settings_open = False
                    return  # Retourner au menu principal
                if stop_music_button_rect.collidepoint(event.pos):
                    stop_music()
                
                if play_music_button_rect.collidepoint(event.pos):
                    play_music()
                
                if increase_brightness_button_rect.collidepoint(event.pos):
                    augmenter_luminosite()

                if decrease_brightness_button_rect.collidepoint(event.pos):
                    diminuer_luminosite()
                
    
                # Vérifie si la souris a cliqué sur une valeur spécifique
                for key,value in grid_value_rects.items():
                    if value.collidepoint(event.pos):
                        selected_value_index = key
                        input_active = True
                        print("input_active")
                        # input_text = str(grid_dict[selected_value_index])  # Utiliser la valeur actuelle pour l'affichage initial
                        input_text = ""  # Utiliser la valeur actuelle pour l'affichage initial

            elif event.type == pg.KEYDOWN:
                if input_active:
                    valueEvaluator(event)
                            
        screen.blit(background_image, (0, 0))
        new = [(key,value) for key, value in grid_dict.items() if key in ingameparam]
        new1 = dict(new)
        labels = list(new1.keys())
        values = list(new1.values())
        # Dessiner les grilles avec transparence
        grid_value_rects.update(draw_transparent_grids(labels[:len(labels)//2], values[:len(values)//2], 400, 300, 50))
        grid_value_rects.update(draw_transparent_grids(labels[len(labels)//2:], values[len(values)//2:], 1300, 300, 50))
   


        # Dessiner le bouton de retour avec transparence  
        draw_transparent_button("BACK", back_button_rect, 128)
        draw_transparent_button("Stop Music", stop_music_button_rect, 128)
        draw_transparent_button("Play Music", play_music_button_rect, 128)
        draw_transparent_button("Increase Brightness", increase_brightness_button_rect, 128)
        draw_transparent_button("Decrease Brightness", decrease_brightness_button_rect, 128)


        # Si une valeur est sélectionnée, dessine un contour autour de cette valeur
        if selected_value_index is not None:
            pg.draw.rect(screen, WHITE, grid_value_rects[selected_value_index], 2)

        # Si l'entrée est active, affiche le texte saisi
        if input_active:
            # Effacer l'ancien texte avec un rectangle blanc
            pg.draw.rect(screen, WHITE, (grid_value_rects[selected_value_index].x, grid_value_rects[selected_value_index].y, 200, 40))
            input_surface = font.render(input_text, True, BLACK)  # Couleur de la police en noir
            input_rect = input_surface.get_rect(center=(grid_value_rects[selected_value_index].centerx, grid_value_rects[selected_value_index].centery))
            # pg.draw.rect(screen, WHITE, (input_rect.x - 5, input_rect.y - 5, input_rect.width + 10, input_rect.height + 10), border_radius=5)  # Couleur de fond du rectangle en blanc
            screen.blit(input_surface, input_rect)

        pg.display.flip()








####################################### Load Menu ############################################
def open_load(screen, clock):
    global return_to_menu, load_open
    etat = EtatJeu.getEtatJeuInstance()

    # Déclaration des rectangles des boutons de chargement
    button_width, button_height = 300, 50
    load1_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 200, button_width, button_height)
    load2_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 300, button_width, button_height)
    load3_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 400, button_width, button_height)
    load4_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 500, button_width, button_height)
    load5_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 600, button_width, button_height)
    back_button_rect = pg.Rect(20, 20, button_width, button_height)
    # Ajoutez d'autres boutons de chargement ici pour chaque sauvegarde

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if load1_button_rect.collidepoint(event.pos):
                    # load_game('save1.pkl')  # Remplacez par le nom de fichier approprié
                    load_open = False
                    return_to_menu = False  # Réinitialiser la variable
                    etat.game_instance = 1
                    return 1  # Retourner au menu principal
                elif load2_button_rect.collidepoint(event.pos):
                    load_open = False
                    return_to_menu = False  # Réinitialiser la variable
                    etat.game_instance = 2
                    return 2  # Retourner au menu principal
                elif load3_button_rect.collidepoint(event.pos):
                    load_open = False
                    return_to_menu = False  # Réinitialiser la variable
                    etat.game_instance = 3
                    return 3  # Retourner au menu principal
                elif load4_button_rect.collidepoint(event.pos):
                    load_open = False
                    return_to_menu = False  # Réinitialiser la variable
                    etat.game_instance = 4
                    return 4  # Retourner au menu principal
                elif load5_button_rect.collidepoint(event.pos):
                    load_open = False
                    return_to_menu = False  # Réinitialiser la variable
                    etat.game_instance = 5
                    return 5  # Retourner au menu principal
                elif back_button_rect.collidepoint(event.pos):
                    load_open = False
                    return_to_menu = True
                    return None

                # Ajoutez des conditions pour d'autres boutons de chargement ici

        screen.blit(background_image, (0, 0))

        # Center the load buttons horizontally and vertically
        draw_transparent_button("Load Save 1", load1_button_rect, 128)
        draw_transparent_button("Load Save 2", load2_button_rect, 128)
        draw_transparent_button("Load Save 3", load3_button_rect, 128)
        draw_transparent_button("Load Save 4", load4_button_rect, 128)
        draw_transparent_button("Load Save 5", load5_button_rect, 128)
        draw_transparent_button("BACK", back_button_rect, 128)
        # Ajoutez d'autres boutons de chargement ici

        pg.display.flip()


###################################### Show menu ############################################
# Dans la fonction show_menu
def show_menu(screen, clock):
    global selected_value_index, grid_value_rects, grid_dict, settings_open, return_to_menu, load_open
    etat = EtatJeu.getEtatJeuInstance()

    # Déclaration des rectangles des boutons de base
    button_width, button_height = 300, 50
    play_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 200, button_width, button_height)
    online_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 300, button_width, button_height)
    load_game_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 400, button_width, button_height)
    settings_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 500, button_width, button_height)
    quit_button_rect = pg.Rect((screen.get_width() - button_width) // 2, 600, button_width, button_height)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if settings_open:
                    if back_button_rect.collidepoint(event.pos):
                        settings_open = False
                        return_to_menu = True
                    if stop_music_button_rect.collidepoint(event.pos):
                        stop_music()
                    if play_music_button_rect.collidepoint(event.pos):
                        play_music()
                    if increase_brightness_button_rect.collidepoint(event.pos):
                        augmenter_luminosite()
                    if decrease_brightness_button_rect.collidepoint(event.pos):
                        diminuer_luminosite()
                if load_open:
                    if back_button_rect.collidepoint(event.pos):
                        load_open = False
                        return_to_menu = True
                else:
                    if play_button_rect.collidepoint(event.pos):
                        return_to_menu = False  # Réinitialiser la variable
                        etat.playing = True
                        print(etat.playing)
                        etat.open_menu = False
                        etat.game_instance = 0
                        return 0  # Retourner au menu principal
                    if online_button_rect.collidepoint(event.pos):
                        return_to_menu = False
                        etat.open_menu = False
                        etat.online_menu = True
                        return 0
                    elif settings_button_rect.collidepoint(event.pos):
                        return_to_menu = False
                        settings_open = True
                        open_settings() 
                    elif quit_button_rect.collidepoint(event.pos):
                        pg.quit()
                        sys.exit()
                    elif load_game_button_rect.collidepoint(event.pos):
                        return_to_menu = False
                        load_open = True
                        i = open_load(screen, clock)
                        if i == None:
                            pass
                        else:
                            load_open = False
                            etat.open_menu = False
                            etat.playing = True
                            return i
                        
        screen.blit(background_image, (0, 0))

        if settings_open:
            open_settings()
            # Center the buttons horizontally and vertically
        elif load_open:
            open_load(screen, clock)
        else:
            draw_transparent_button("NEW GAME", play_button_rect, 128)
            draw_transparent_button("ONLINE", online_button_rect, 128)
            draw_transparent_button("LOAD GAME", load_game_button_rect, 128)
            draw_transparent_button("SETTINGS", settings_button_rect, 128)
            draw_transparent_button("QUIT", quit_button_rect, 128)

        pg.display.flip()


################################## Pause Mode ############################################

def pause( screen, camera ):
    # Declaration des rectangles des map:
    #screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    from GameControl.game import Game

    clock = pg.time.Clock()
    game = Game.getInstance(screen,clock)
    pauseSurface = pg.Surface((setting.getSurfaceWidth(), setting.getSurfaceHeight())).convert_alpha()
    print(setting.getSurfaceWidth(), setting.getSurfaceHeight())
    while True:
        ########################## Draw map #######################################################
        screen.fill((137, 207, 240))
        pauseSurface.fill((195, 177, 225))
        # surface.blit(loadMap(), (0,0))
        textureImg = loadGrassImage()
        flowImg = loadFlowerImage()
        darkGrass = loadDarkGrassImage()
        darkFlower = loadDarkFlowerImage()
        for row in gameController.getMap(): # x is a list of a double list Map
            for tile in row: # tile is an object in list
                (x, y) = tile.getRenderCoord()
                offset = (x + setting.getSurfaceWidth()/2 , y + setting.getTileSize())
                a,b = offset
                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                    if tile.seen:
                        if tile.flower:
                            pauseSurface.blit(flowImg, offset)
                        else:
                            pauseSurface.blit(textureImg, offset)
                    else:
                        if tile.flower:
                            pauseSurface.blit(darkFlower, offset)
                        else:
                            pauseSurface.blit(darkGrass, offset)
                else: pass
        

        ########################## Draw Bob #######################################################
        greenLeft = loadGreenLeft()
        blueLeft = loadBlueLeft()
        purpleLeft = loadPurpleLeft()
        for bob in gameController.listBobs:
            (destX, destY) = bob.getCurrentTile().getRenderCoord()
            (desX, desY) = (destX + setting.getSurfaceWidth()//2 , destY - ( + 50 - setting.getTileSize() ) )
            finish = (desX, desY + setting.getTileSize())
            a,b = finish
            # bar_width = int((bob.energy / bob.energyMax) * 50)
            # pg.draw.rect(surface, (255, 0, 0), (finish[0], finish[1] - 5, bar_width, 5))
            if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                if bob.isHunting:
                    pauseSurface.blit(purpleLeft, finish)
                else: pauseSurface.blit(greenLeft, finish)
        ########################## Draw Food #######################################################
        foodTexture = loadFoodImage()
        for food in gameController.getFoodTiles():
            (x, y) = food.getRenderCoord()
            (X, Y) = (x + setting.getSurfaceWidth()//2  , y - (foodTexture.get_height() - setting.getTileSize() ) )
            position = (X , Y + setting.getTileSize() )
            a,b = position
            # bar_width = int((food.foodEnergy / setting.getFoodEnergy()) * 50)
            # pg.draw.rect(surface, (0, 0, 255), (position[0] + 5, position[1]+ 20, bar_width, 5))
            pauseSurface.blit(foodTexture, position)
        listRect = []
        camera.update()
        for row in gameController.getMap():
            for tile in row:
                (x,y) = tile.getRenderCoord()
                offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                a, b = offset
                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                    listRect.append((tile,(a + camera.scroll.x, b + camera.scroll.y)))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    return
                game.saveGameByInput(event)
                if event.key == pg.K_m:
                    return 'Menu'
                if event.key == pg.K_BACKSPACE:
                    return 'InGameSetting'
        mouse_x, mouse_y = pg.mouse.get_pos()
        for coord in listRect:
            if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                print(coord[0].gridX, coord[0].gridY)
                if len(coord[0].getBobs()) != 0:
                    nb = len(coord[0].getBobs())
                # for bob in coord[0].getBobs():
                    if ( mouse_y - 150 >= 0 ):
                        if ( mouse_x - 50*nb < 0 ):
                            pg.draw.rect(pauseSurface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x +50 , mouse_y - camera.scroll.y -50 , 100 * nb, 100))
                            i = 0
                            for bob in coord[0].getBobs():
                                draw_text(pauseSurface, f"ID: {bob.id}", 15,(0,0,0),(mouse_x - camera.scroll.x +50 + 100*i + 5 , mouse_y - camera.scroll.y -50 + 5))
                                draw_text(pauseSurface, f"Energy: {bob.energy:.3f}", 15,(0,0,0),(mouse_x - camera.scroll.x +50+ 100*i + 5 , mouse_y - camera.scroll.y -50 + 15))
                                draw_text(pauseSurface, f"Mass: {bob.mass:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x +50+ 100*i + 5 , mouse_y - camera.scroll.y -50 + 25)))
                                draw_text(pauseSurface, f"Vision: {bob.vision:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x +50+ 100*i + 5 , mouse_y - camera.scroll.y -50 + 35)))
                                draw_text(pauseSurface, f"Velocity: {bob.velocity:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x +50+ 100*i + 5 , mouse_y - camera.scroll.y -50 + 45)))
                                draw_text(pauseSurface, f"Memory: {bob.memoryPoint:.3f}",15,(0,0,0) , ((mouse_x - camera.scroll.x +50+ 100*i + 5 , mouse_y - camera.scroll.y -50 + 55)))
                                # draw_text(pauseSurface, f"-------------------------------------------------------------",15,(0,0,0) , ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 65)))
                                i += 1


                        elif( mouse_x + 50*nb > 1920  ):
                            pg.draw.rect(pauseSurface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x - 50 - 100*nb , mouse_y - camera.scroll.y - 50 , 100 * nb, 100))
                            i = 0
                            for bob in coord[0].getBobs():
                                draw_text(pauseSurface, f"ID: {bob.id}", 15,(0,0,0),(mouse_x - camera.scroll.x - 50 -100*nb + 100*i + 5 , mouse_y - camera.scroll.y -50 + 5))
                                draw_text(pauseSurface, f"Energy: {bob.energy:.3f}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 -100*nb + 100*i + 5 , mouse_y - camera.scroll.y -50 + 15))
                                draw_text(pauseSurface, f"Mass: {bob.mass:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb + 100*i + 5 , mouse_y - camera.scroll.y -50 + 25)))
                                draw_text(pauseSurface, f"Vision: {bob.vision:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb + 100*i + 5 , mouse_y - camera.scroll.y -50 + 35)))
                                draw_text(pauseSurface, f"Velocity: {bob.velocity:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb + 100*i + 5 , mouse_y - camera.scroll.y -50 + 45)))
                                draw_text(pauseSurface, f"Memory: {bob.memoryPoint:.3f}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 -100*nb + 100*i + 5 , mouse_y - camera.scroll.y -50 + 55)))
                                # draw_text(pauseSurface, f"-------------------------------------------------------------",15,(0,0,0) , ((mouse_x - camera.scroll.x -250 + 5 , mouse_y - camera.scroll.y -50 + 65)))
                                i += 1


                        else:
                            pg.draw.rect(pauseSurface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x -50 * nb , mouse_y - camera.scroll.y - 150 , 100 * nb, 100))
                            i = 0
                            for bob in coord[0].getBobs():
                                draw_text(pauseSurface, f"ID: {bob.id}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y -150 + 5))
                                draw_text(pauseSurface, f"Energy: {bob.energy:.3f}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y -150 + 15))
                                draw_text(pauseSurface, f"Mass: {bob.mass:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y -150 + 25)))
                                draw_text(pauseSurface, f"Vision: {bob.vision:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y -150 + 35)))
                                draw_text(pauseSurface, f"Velocity: {bob.velocity:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y -150 + 45)))
                                draw_text(pauseSurface, f"Memory: {bob.memoryPoint:.3f}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y -150 + 55)))
                                # draw_text(pauseSurface, f"-------------------------------------------------------------",15,(0,0,0) , ((mouse_x - camera.scroll.x -100 + 5 , mouse_y - camera.scroll.y -150 + 65)))
                                i += 1

                    else:
                        pg.draw.rect(pauseSurface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x -50 * nb , mouse_y - camera.scroll.y + 50 , 100 * nb, 100))
                        i = 0
                        for bob in coord[0].getBobs():
                            draw_text(pauseSurface, f"ID: {bob.id}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y + 50 + 5))
                            draw_text(pauseSurface, f"Energy: {bob.energy:.3f}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y + 50 + 15))
                            draw_text(pauseSurface, f"Mass: {bob.mass:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y + 50 + 25)))
                            draw_text(pauseSurface, f"Vision: {bob.vision:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y + 50 + 35)))
                            draw_text(pauseSurface, f"Velocity: {bob.velocity:.3f}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y + 50 + 45)))
                            draw_text(pauseSurface, f"Memory: {bob.memoryPoint:.3f}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 * nb + 100*i + 5 , mouse_y - camera.scroll.y + 50 + 55)))
                            # draw_text(pauseSurface, f"-------------------------------------------------------------",15,(0,0,0) , ((mouse_x - camera.scroll.x -100 + 5 , mouse_y - camera.scroll.y + 50 + 65)))
                            i += 1

        screen.blit(pauseSurface, (camera.scroll.x, camera.scroll.y))    
        draw_text(screen, f"Paused", 40, (0,0,0), (screen.get_width()//2 - 50, 10))
        drawIndex ( screen)
        pg.display.flip()

def drawIndex( surface):

    draw_text(
        surface,
        'Tick: {}'.format(round(gameController.getTick())),
        25,
        (0,0,0),
        (10, 30)
    )  
    draw_text(
        surface,
        'Day: {}'.format(round(gameController.getDay())),
        25,
        (0,0,0),
        (10, 50)
    )  
    draw_text(
        surface,
        'Number of bobs: {}'.format(gameController.getNbBobs()) ,
        25,
        (0,0,0),
        (10, 70)
    )
    draw_text(
        surface,
        'Number of bob spawned: {}'.format(gameController.getNbBobsSpawned()) ,
        25,
        (0,0,0),
        (10, 90)
    )

# def modifiableMode( screen, clock):

def valueEvaluator(event):
    global selected_value_index, grid_value_rects, grid_dict, input_text, settings_open, ingameparam, input_active
    match selected_value_index:
        case None:
            pass
        case "FPS":
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 4:
                                match new_value:
                                    case 1:
                                        setting.setFps(32)
                                        grid_dict[selected_value_index] = 32
                                        input_active = False
                                        input_text = ""
                                        selected_value_index = None
                                    case 2:
                                        setting.setFps(24)
                                        grid_dict[selected_value_index] = 24
                                        input_active = False
                                        input_text = ""
                                        selected_value_index = None
                                    case 3:
                                        setting.setFps(16)
                                        grid_dict[selected_value_index] = 16
                                        input_active = False
                                        input_text = ""
                                        selected_value_index = None
                                    case 4:
                                        setting.setFps(8)
                                        grid_dict[selected_value_index] = 8
                                        input_active = False
                                        input_text = ""
                                        selected_value_index = None
                                    
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 1:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 3 caractère.")
        case "GRID LENGTH": # GridLength
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 200:
                                setting.setGridLength(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 3:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 3 caractère.")
        case "NUMBER BOB": # nbBobs                            
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 200:
                                setting.setNbBob(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 3:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 3 caractère.")
        case "NUMBER SPAWNED FOOD": # Nb Spawned Food
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 1000:
                                setting.setNbSpawnFood(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")
        case "FOOD ENERGY": # Food Energy
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 2000:
                                setting.setFoodEnergy(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")
        case "BOB SPAWN ENERGY": # Bob Spawned Energy
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 1000:
                                setting.setBobSpawnEnergy(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")
        case "BOB MAX ENERGY": # Bob Max Energy
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 1000:
                                setting.setBobMaxEnergy(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")

        case "BOB NEWBORN ENERGY": # New Born Energy
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 1000:
                                setting.setBobNewbornEnergy(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")

        case "SEXUAL BORN ENERGY": # SEXUAL BORN ENERGY
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 1000:
                                setting.setSexualBornEnergy(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")                            
        case "BOB STATIONARY ENERGY LOSS": # Stationary energy loss
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                setting.setBobStationaryEnergyLoss(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")

        case "BOB SELF REPRODUCTION ENERGY LOSS": # Self Reproduction energy loss
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 1000:
                                setting.setBobSelfReproductionEnergyLoss(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")   

        case "BOB SEXUAL REPRODUCTION LOSS": # Sexual reproduction energy loss
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 1000:
                                setting.setBobSexualReproductionLoss(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")   

        case "BOB SEXUAL REPRODUCTION LEVEL": # Sexual reproduction level
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 1000:
                                setting.setBobSexualReproductionLevel(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")                                                          

        case "PERCEPTION FLAT PENALTY": # Perception Flat Penalty
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 1:
                                setting.setPerceptionFlatPenalty(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")   
        case "MEMORY FLAT PENALTY": # Memory Flat Penalty
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 1:
                                setting.setMemoryFlatPenalty(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")   
        case "DEFAULT VELOCITY": # Default velocity
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 10:
                                setting.setDefaultVelocity(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 5 caractère.")   
        case "DEFAULT MASS": # Default mass
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 10:
                                setting.setDefaultMass(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 5 caractère.")   
        case "DEFAULT VISION": # Default Vision
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                setting.setDefaultVision(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 5 caractère.")   
        case "DEFAULT MEMORY POINT": # Default Memory point
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                setting.setDefaultMemoryPoint(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 5 caractère.")  
        case "MASS VARIATION": # Mass Variation
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                setting.setMassVariation(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")           
        case "VELOCITY VARIATION": # Velocity variation
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                setting.setVelocityVariation(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")   
        case "VISION VARIATION": #Vision Variation
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                setting.setVisionVariation(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 2:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 2 caractère.")
        case "MEMORY VARIATION": # Memory point variation
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                setting.setMemoryVariation(new_value)
                                grid_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 2:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 2 caractère.")
        case "SELF REPRODUCTION": # Self Reproduction
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        grid_dict[selected_value_index] = ""
                        if input_text == "":
                            pass
                        else:
                            if input_text == "0":
                                setting.setSelfReproduction(False)
                                grid_dict[selected_value_index] = False
                            else: 
                                setting.setSelfReproduction(True)
                                grid_dict[selected_value_index] = True
                            input_active = False
                            input_text = ""
                            selected_value_index = None
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 1:
                    if event.unicode == "0":
                        input_text += event.unicode
                    elif event.unicode == "1":
                        input_text += event.unicode
                    else:
                        print("La valeur doit être 0 ou 1.")
                else:
                    print("La valeur ne doit pas dépasser 1 caractère.")    
        case "SEXUAL REPRODUCTION": # Sexual reproduction
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        grid_dict[selected_value_index] = ""
                        if input_text == "":
                            pass
                        else:
                            if input_text == "0":
                                setting.setSexualReproduction(False)
                                grid_dict[selected_value_index] = False
                            else: 
                                setting.setSexualReproduction(True)
                                grid_dict[selected_value_index] = True
                            input_active = False
                            input_text = ""
                            selected_value_index = None
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 1:
                    if event.unicode == "0":
                        input_text += event.unicode
                    elif event.unicode == "1":
                        input_text += event.unicode
                    else:
                        print("La valeur doit être 0 ou 1.")
                else:
                    print("La valeur ne doit pas dépasser 1 caractère.")


new_object_dict = { "Bob Energy": setting.getBobSpawnEnergy(), 
                "Bob Mass": setting.getDefaultMass(), 
                "Bob Vision": setting.getDefaultVision(), 
                "Bob Velocity": setting.getDefaultVelocity(),
                "Bob Memory Point": setting.getDefaultMemoryPoint(), 
                "Food Energy": setting.getFoodEnergy() }

allow_mod = False
modding = False
mod_food = False
mod_bob = False

def newObjectMenu (screen, clock , camera ):
    global allow_mod, modding
    modding = True
    while True:
        print("New Object Menu: ", allow_mod, modding)
        if allow_mod == False and modding == False:
            print("Returning")
            return
        elif allow_mod == True and modding == False:
            modifiableMode(screen, clock, camera)
        elif allow_mod == False and modding == True:
            moddingFunc( screen, clock, camera)


def modifiableMode(screen, clock, camera):

    global allow_mod, modding, mod_food, mod_bob, new_object_dict

    while True: 
        print("Modifiable Mode")
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    allow_mod = False
                    modding = True
                    return
                elif event.key == pg.K_SPACE:
                    modifiableModePause(screen, clock, camera)
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pg.mouse.get_pos()
                listRect = []
                for row in gameController.getMap():
                    for tile in row:
                        (x,y) = tile.getRenderCoord()
                        offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                        a, b = offset
                        if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                            listRect.append((tile,(a + camera.scroll.x, b + camera.scroll.y)))

                for coord in listRect:
                    if mod_bob:
                        if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                            createBob(coord[0])
                    if mod_food:
                        if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                            createFood(coord[0])


        gameController.updateRenderTick()
        screen.fill((137, 207, 240))
        surface = pg.Surface((setting.getSurfaceWidth(), setting.getSurfaceHeight())).convert_alpha()
        surface.fill((195, 177, 225))
        drawModifiable(surface, camera)
        screen.blit(surface, (camera.scroll.x, camera.scroll.y))    
        drawIndex ( screen)
        pg.display.flip()

def createFood(tile):
    tile.foodEnergy += new_object_dict["Food Energy"]
    

def createBob(tile):
    global new_object_dict
    bob = Bob()
    bob.setCurrentTile(tile)
    bob.PreviousTiles.append(tile)
    bob.CurrentTile.addBob(bob)
    bob.setEnergy(new_object_dict["Bob Energy"])
    bob.setMass(new_object_dict["Bob Mass"])
    bob.setVision(new_object_dict["Bob Vision"])
    bob.setVelocity(new_object_dict["Bob Velocity"])
    bob.setMemoryPoint(new_object_dict["Bob Memory Point"])
    bob.determineNextTile()
    gameController.getListBobs().append(bob)
    gameController.setNbBobs(gameController.getNbBobs() + 1)
    gameController.setNbBobsSpawned(gameController.getNbBobsSpawned() + 1)

        
def drawModifiable(surface, camera):
    etat = EtatJeu.getEtatJeuInstance()
    net = Network.getNetworkInstance()

    
    global mod_food, mod_bob, new_object_dict
    textureImg = loadGrassImage()
    flowImg = loadFlowerImage()
    darkGrass = loadDarkGrassImage()
    darkFlower = loadDarkFlowerImage()
    brightGrass = loadGrassBrightImage()
    brightFlower = loadFlowerBrightImage()
    
    net =Network.getNetworkInstance()
    etat=EtatJeu.getEtatJeuInstance()
    for row in gameController.getMap(): # x is a list of a double list Map
        for tile in row: # tile is an object in list
            territoire_true = net.this_client.color == 1 and tile.gridX < setting.gridLength//2 and tile.gridY < setting.gridLength//2 or\
                        net.this_client.color == 2 and tile.gridX < setting.gridLength//2 and setting.gridLength//2 <= tile.gridY or\
                        net.this_client.color == 3 and setting.gridLength//2 <= tile.gridX and setting.gridLength//2 <= tile.gridY or \
                        net.this_client.color == 4 and setting.gridLength//2 <= tile.gridX and tile.gridY < setting.gridLength//2 
    
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
                    if not etat.online_game or territoire_true:
                        if tile.flower:
                            surface.blit(brightFlower, offset)
                        else:
                            surface.blit(brightGrass, offset)
                        tile.hover = False
            else: pass

    greenLeft = loadGreenLeft()
    blueLeft = loadBlueLeft()
    purpleLeft = loadPurpleLeft()

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

    for bob in gameController.listBobs:
        if (bob not in gameController.diedQueue) and (bob not in gameController.newBornQueue):
            # if(gameController.getTick() % 2 == 0 ):
                nbInteval = len(bob.getPreviousTiles()) - 1
                if ( gameController.renderTick < setting.getFps()/2):
                    if nbInteval == 0:
                        (destX, destY) = bob.getCurrentTile().getRenderCoord()
                        (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
                        finish = (desX, desY + setting.getTileSize())
                        a,b = finish
                        if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                            bar_width = int((bob.energy / bob.energyMax) * 50)
                            pg.draw.rect(surface, (255, 0, 0), (finish[0], finish[1] - 5, bar_width, 5))
                            if bob.isHunting:
                                surface.blit(purpleLeft, finish)
                            else: surface.blit(greenLeft, finish)
                        else: pass
                    else:
                        for i in range( nbInteval):
                            if ( i*setting.getFps()) / (nbInteval * 2) <= gameController.renderTick < (i+1)*setting.getFps() / (nbInteval * 2):
                                (x, y) = bob.getPreviousTiles()[i].getRenderCoord()
                                (X, Y) = (x + surface.get_width()/2 , y - (50 - setting.getTileSize() ) )
                                (destX, destY) = bob.getPreviousTiles()[i+1].getRenderCoord()
                                (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
                                pos = (X + (desX - X) * (gameController.renderTick - (i*setting.getFps())/(2 * nbInteval)) * (2 * nbInteval) / setting.getFps() , Y + (desY - Y) * (gameController.renderTick - (i*setting.getFps())/(2 * nbInteval) ) * (2 * nbInteval) / setting.getFps()  + setting.getTileSize()  )
                                a,b = pos
                                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                                    bar_width = int((bob.energy / bob.energyMax) * 50)
                                    pg.draw.rect(surface, (255, 0, 0), (pos[0], pos[1] - 5, bar_width, 5))
                                    if bob.isHunting:
                                        surface.blit(purpleLeft, pos)
                                    else: surface.blit(greenLeft, pos)
                                else: pass
                            else: pass
                else:
                    (destX, destY) = bob.getCurrentTile().getRenderCoord()
                    (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
                    finish = (desX, desY + setting.getTileSize())
                    a,b = finish
                    if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                        bar_width = int((bob.energy / bob.energyMax) * 50)
                        pg.draw.rect(surface, (255, 0, 0), (finish[0], finish[1] - 5, bar_width, 5))
                        if bob.isHunting:
                            surface.blit(purpleLeft, finish)
                        else: surface.blit(greenLeft, finish)
                    else: pass
    for bob in gameController.diedQueue:
        (x, y) = bob.getPreviousTile().getRenderCoord()
        (X, Y) = (x + surface.get_width()/2 , y - (50 - setting.getTileSize() ) )
        position = (X, Y)
        # print(bob.getNextTile())
        (destX, destY) = bob.getCurrentTile().getRenderCoord()
        (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
        start = (X + (desX - X) * (2 *gameController.renderTick/setting.getFps()), Y + (desY - Y) * (2* gameController.renderTick/setting.getFps()) + setting.getTileSize())
        finish = (desX, desY + setting.getTileSize())
        a , b = finish
        if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
            if (gameController.renderTick < setting.getFps()/2):
                surface.blit(greenLeft, start)
            elif setting.getFps()/2 <= gameController.renderTick < setting.getFps()/2 + setting.getFps()/16:
                surface.blit(explode1, finish)
            elif setting.getFps()/2 + setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 2*setting.getFps()/16:
                surface.blit(explode2, finish)
            elif setting.getFps()/2 + 2*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 3*setting.getFps()/16:
                surface.blit(explode3, finish)
            elif setting.getFps()/2 + 3*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 4*setting.getFps()/16:
                surface.blit(explode4, finish)
            elif setting.getFps()/2 + 4*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 5*setting.getFps()/16:
                surface.blit(explode5, finish)
            elif setting.getFps()/2 + 5*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 6*setting.getFps()/16:
                surface.blit(explode6, finish)
            elif setting.getFps()/2 + 6*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 7*setting.getFps()/16:
                surface.blit(explode7, finish)
            else:
                surface.blit(explode8, finish)
        else: pass

    for bob in gameController.newBornQueue:
        if bob not in gameController.diedQueue:
            # (x, y) = bob.getPreviousTile().getRenderCoord()
            # (X, Y) = (x + surface.get_width()/2 , y - (greenLeftt_height() - setting.getTileSize() ) )
            (destX, destY) = bob.getCurrentTile().getRenderCoord()
            (desX, desY) = (destX + surface.get_width()/2 , destY - ( + 50 - setting.getTileSize() ) )
            # position = (X, Y + setting.getTileSize())
            # start = (X + (desX - X) * (2 *gameController.renderTick/setting.getFps()), Y + (desY - Y) * (2* gameController.renderTick/setting.getFps()) + setting.getTileSize())
            finish = (desX, desY + setting.getTileSize())
            a,b = finish
            if -64 <= (a  + camera.scroll.x) <= 1920 and -64 <= (b  + camera.scroll.y)  <= 1080:
                if gameController.renderTick < setting.getFps()/2:
                    # screen.blit(greenLefttart) # need to change to newborn bob texture later
                    # pg.draw.rect(screen, (255, 0, 0), (start[0], start[1] - 5, bar_width, 5))
                    pass
                # else:
                #     screen.blit(greenLeftinish)
                #     pg.draw.rect(screen, (255, 0, 0), (finish[0], finish[1] - 5, bar_width, 5))
                elif setting.getFps()/2 <= gameController.renderTick < setting.getFps()/2 + setting.getFps()/16:
                    surface.blit(spawn1, finish)
                elif setting.getFps()/2 + setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 2*setting.getFps()/16:
                    surface.blit(spawn2, finish)
                elif setting.getFps()/2 + 2*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 3*setting.getFps()/16:
                    surface.blit(spawn3, finish)
                elif setting.getFps()/2 + 3*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 4*setting.getFps()/16:
                    surface.blit(spawn4, finish)
                elif setting.getFps()/2 + 4*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 5*setting.getFps()/16:
                    surface.blit(spawn5, finish)
                elif setting.getFps()/2 + 5*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 6*setting.getFps()/16:
                    surface.blit(spawn6, finish)
                elif setting.getFps()/2 + 6*setting.getFps()/16 <= gameController.renderTick < setting.getFps()/2 + 7*setting.getFps()/16:
                    surface.blit(spawn7, finish)
                else:
                    surface.blit(spawn8, finish)
            else: pass
    
    foodTexture = loadFoodImage()
    for food in gameController.getFoodTiles():
        (x, y) = food.getRenderCoord()
        (X, Y) = (x + surface.get_width()/2  , y - ( 50 - setting.getTileSize() ) )
        position = (X , Y + setting.getTileSize() )
        a,b = position
        if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
            
            bar_width = int((food.foodEnergy / setting.getFoodEnergy()) * 50)
            pg.draw.rect(surface, (0, 0, 255), (position[0] + 5, position[1] - 5, bar_width, 5))
            surface.blit(foodTexture, position)
        else: pass
    mouse_x, mouse_y = pg.mouse.get_pos()
    camera.update()
    if mod_bob:
        surface.blit(greenLeft, (mouse_x - greenLeft.get_width()//2 - camera.scroll.x, mouse_y - greenLeft.get_height()//2 - camera.scroll.y))
        listRect = []
        for row in gameController.getMap():
            for tile in row:
                 
                territoire_true = net.this_client.color == 1 and tile.gridX < setting.gridLength//2 and tile.gridY < setting.gridLength//2 or\
                        net.this_client.color == 2 and tile.gridX < setting.gridLength//2 and setting.gridLength//2 <= tile.gridY or\
                        net.this_client.color == 3 and setting.gridLength//2 <= tile.gridX and setting.gridLength//2 <= tile.gridY or \
                        net.this_client.color == 4 and setting.gridLength//2 <= tile.gridX and tile.gridY < setting.gridLength//2 
    
                (x,y) = tile.getRenderCoord()
                offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                a, b = offset
                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                    if not etat.online_game or territoire_true: 
                        listRect.append((tile,(a + camera.scroll.x, b + camera.scroll.y)))

        for coord in listRect:
            if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                print(coord[0].gridX, coord[0].gridY)
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
    if mod_food:
        surface.blit(foodTexture, (mouse_x - foodTexture.get_width()//2 - camera.scroll.x, mouse_y - foodTexture.get_height()//2 - camera.scroll.y))
        listRect = []
        for row in gameController.getMap():
            for tile in row: 
                territoire_true = net.this_client.color == 1 and tile.gridX < setting.gridLength//2 and tile.gridY < setting.gridLength//2 or\
                        net.this_client.color == 2 and tile.gridX < setting.gridLength//2 and setting.gridLength//2 <= tile.gridY or\
                        net.this_client.color == 3 and setting.gridLength//2 <= tile.gridX and setting.gridLength//2 <= tile.gridY or \
                        net.this_client.color == 4 and setting.gridLength//2 <= tile.gridX and tile.gridY < setting.gridLength//2 

                (x,y) = tile.getRenderCoord()
                offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                a, b = offset
                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                    if not etat.online_game or territoire_true:
                        listRect.append((tile,(a + camera.scroll.x, b + camera.scroll.y)))
        for coord in listRect:
            if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                print(coord[0].gridX, coord[0].gridY)
                coord[0].hover = True


def modifiableModePause(screen, clock, camera):
    global gameController, mod_bob, mod_food, new_object_dict
    pauseSurface = pg.Surface((setting.getSurfaceWidth(), setting.getSurfaceHeight())).convert_alpha()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    return
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pg.mouse.get_pos()
                listRect = []
                for row in gameController.getMap():
                    for tile in row:
                        (x,y) = tile.getRenderCoord()
                        offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                        a, b = offset
                        if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                            listRect.append((tile,(a + camera.scroll.x, b + camera.scroll.y)))
                if mod_bob:
                    for coord in listRect:
                        if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                            createBob(coord[0])
                if mod_food:
                    for coord in listRect:
                        if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                            createFood(coord[0])
        screen.fill((137, 207, 240))
        pauseSurface.fill((195, 177, 225))

        drawPauseModifiable(pauseSurface, camera)
        screen.blit(pauseSurface, (camera.scroll.x, camera.scroll.y))    
        draw_text(screen, f"Paused", 40, (0,0,0), (screen.get_width()//2 - 50, 10))
        drawIndex ( screen)
        pg.display.flip()

def drawPauseModifiable(pauseSurface, camera):
        global mod_bob, mod_food, new_object_dict
        textureImg = loadGrassImage()
        flowImg = loadFlowerImage()
        darkGrass = loadDarkGrassImage()
        darkFlower = loadDarkFlowerImage()
        brightGrass = loadGrassBrightImage()
        brightFlower = loadFlowerBrightImage()
        for row in gameController.getMap(): # x is a list of a double list Map
            for tile in row: # tile is an object in list
                (x, y) = tile.getRenderCoord()
                offset = (x + setting.getSurfaceWidth()/2 , y + setting.getTileSize())
                a,b = offset
                if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                    if tile.seen and not tile.hover:
                        if tile.flower:
                            pauseSurface.blit(flowImg, offset)
                        else:
                            pauseSurface.blit(textureImg, offset)
                    else:
                        if tile.flower:
                            pauseSurface.blit(darkFlower, offset)
                        else:
                            pauseSurface.blit(darkGrass, offset)
                    if tile.hover:
                        if tile.flower:
                            pauseSurface.blit(brightFlower, offset)
                        else:
                            pauseSurface.blit(brightGrass, offset)
                        tile.hover = False
                else: pass
########################## Draw Bob #######################################################
        greenLeft = loadGreenLeft()
        blueLeft = loadBlueLeft()
        purpleLeft = loadPurpleLeft()
        for bob in gameController.listBobs:
            (destX, destY) = bob.getCurrentTile().getRenderCoord()
            (desX, desY) = (destX + setting.getSurfaceWidth()//2 , destY - ( + 50 - setting.getTileSize() ) )
            finish = (desX, desY + setting.getTileSize())
            a,b = finish
            # bar_width = int((bob.energy / bob.energyMax) * 50)
            # pg.draw.rect(surface, (255, 0, 0), (finish[0], finish[1] - 5, bar_width, 5))
            if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                if bob.isHunting:
                    pauseSurface.blit(purpleLeft, finish)
                else: pauseSurface.blit(greenLeft, finish)
        ########################## Draw Food #######################################################
        foodTexture = loadFoodImage()
        for food in gameController.getFoodTiles():
            (x, y) = food.getRenderCoord()
            (X, Y) = (x + setting.getSurfaceWidth()//2  , y - (foodTexture.get_height() - setting.getTileSize() ) )
            position = (X , Y + setting.getTileSize() )
            a,b = position
            # bar_width = int((food.foodEnergy / setting.getFoodEnergy()) * 50)
            # pg.draw.rect(surface, (0, 0, 255), (position[0] + 5, position[1]+ 20, bar_width, 5))
            pauseSurface.blit(foodTexture, position)
        mouse_x, mouse_y = pg.mouse.get_pos()

        
        camera.update()
        if mod_bob:
            pauseSurface.blit(greenLeft, (mouse_x - greenLeft.get_width()//2 - camera.scroll.x, mouse_y - greenLeft.get_height()//2 - camera.scroll.y))
            listRect = []
            for row in gameController.getMap():
                for tile in row:
                    (x,y) = tile.getRenderCoord()
                    offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                    a, b = offset
                    if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                        listRect.append((tile,(a + camera.scroll.x, b + camera.scroll.y)))

            for coord in listRect:
                if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                    print(coord[0].gridX, coord[0].gridY)
                    coord[0].hover = True
                    nb = 1
                    # for bob in coord[0].getBobs():
                    if ( mouse_y - 150 >= 0 ):
                        if ( mouse_x - 50*nb < 0 ):
                            pg.draw.rect(pauseSurface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x +50 , mouse_y - camera.scroll.y -50 , 100 * nb, 100))

                            draw_text(pauseSurface, f"Energy: {new_object_dict['Bob Energy']}", 15,(0,0,0),(mouse_x - camera.scroll.x +50  + 5 , mouse_y - camera.scroll.y -50 + 5))
                            draw_text(pauseSurface, f"Mass {new_object_dict['Bob Mass']}", 15,(0,0,0),(mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 15))
                            draw_text(pauseSurface, f"Vision {new_object_dict['Bob Vision']}",15,(0,0,0), ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 25)))
                            draw_text(pauseSurface, f"Velocity: {new_object_dict['Bob Velocity']}",15,(0,0,0), ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 35)))
                            draw_text(pauseSurface, f"Memory: {new_object_dict['Bob Memory Point']}",15,(0,0,0), ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 45)))
                            draw_text(pauseSurface, f"Food {new_object_dict['Food Energy']}",15,(0,0,0) , ((mouse_x - camera.scroll.x +50 + 5 , mouse_y - camera.scroll.y -50 + 55)))

                        elif( mouse_x + 50*nb > 1920  ):
                            pg.draw.rect(pauseSurface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x - 50 - 100*nb , mouse_y - camera.scroll.y - 50 , 100 * nb, 100))

                            draw_text(pauseSurface, f"Energy: {new_object_dict['Bob Energy']}", 15,(0,0,0),(mouse_x - camera.scroll.x - 50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 5))
                            draw_text(pauseSurface, f"Mass {new_object_dict['Bob Mass']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 15))
                            draw_text(pauseSurface, f"Vision {new_object_dict['Bob Vision']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 25)))
                            draw_text(pauseSurface, f"Velocity: {new_object_dict['Bob Velocity']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 35)))
                            draw_text(pauseSurface, f"Memory: {new_object_dict['Bob Memory Point']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 45)))
                            draw_text(pauseSurface, f"Food {new_object_dict['Food Energy']}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 -100*nb  + 5 , mouse_y - camera.scroll.y -50 + 55)))



                        else:
                            pg.draw.rect(pauseSurface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x -50 * nb , mouse_y - camera.scroll.y - 150 , 100 * nb, 100))
                            draw_text(pauseSurface, f"Energy: {new_object_dict['Bob Energy']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 5))
                            draw_text(pauseSurface, f"Mass {new_object_dict['Bob Mass']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 15))
                            draw_text(pauseSurface, f"Vision {new_object_dict['Bob Vision']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 25)))
                            draw_text(pauseSurface, f"Velocity: {new_object_dict['Bob Velocity']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 35)))
                            draw_text(pauseSurface, f"Memory: {new_object_dict['Bob Memory Point']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 45)))
                            draw_text(pauseSurface, f"Food {new_object_dict['Food Energy']}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y -150 + 55)))

                    else:
                        pg.draw.rect(pauseSurface, (225, 255, 123), pg.Rect( mouse_x - camera.scroll.x -50 * nb , mouse_y - camera.scroll.y + 50 , 100 * nb, 100))
                        draw_text(pauseSurface, f"Energy: {new_object_dict['Bob Energy']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 5))
                        draw_text(pauseSurface, f"Mass {new_object_dict['Bob Mass']}", 15,(0,0,0),(mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 15))
                        draw_text(pauseSurface, f"Vision {new_object_dict['Bob Vision']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 25)))
                        draw_text(pauseSurface, f"Velocity: {new_object_dict['Bob Velocity']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 35)))
                        draw_text(pauseSurface, f"Memory: {new_object_dict['Bob Memory Point']}",15,(0,0,0), ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 45)))
                        draw_text(pauseSurface, f"Food {new_object_dict['Food Energy']}",15,(0,0,0) , ((mouse_x - camera.scroll.x -50 * nb  + 5 , mouse_y - camera.scroll.y + 50 + 55)))
        if mod_food:
            pauseSurface.blit(foodTexture, (mouse_x - foodTexture.get_width()//2 - camera.scroll.x, mouse_y - foodTexture.get_height()//2 - camera.scroll.y))
            listRect = []
            for row in gameController.getMap():
                for tile in row:
                    (x,y) = tile.getRenderCoord()
                    offset = ( x + setting.getSurfaceWidth()//2 , y + setting.getTileSize()  ) 
                    a, b = offset
                    if -64 <= (a + camera.scroll.x) <= 1920 and -64 <= (b + camera.scroll.y)  <= 1080:
                        listRect.append((tile,(a + camera.scroll.x, b + camera.scroll.y)))
            for coord in listRect:
                if coord[1][0] <= mouse_x <= coord[1][0] + 64 and coord[1][1] + 8 <= mouse_y <= coord[1][1] + 24:
                    print(coord[0].gridX, coord[0].gridY)
                    coord[0].hover = True


def moddingFunc(screen, clock, camera ):
    global allow_mod, modding, new_object_dict, input_active, input_text, selected_value_index,gameController, mod_food, mod_bob
    input_active = False
    input_text = ""

    back_button_rect = pg.Rect(20, 20, button_width, button_height)
    add_food_button_rect = pg.Rect(20, 100, button_width, button_height)
    add_bob_button_rect = pg.Rect(20, 180, button_width, button_height)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    allow_mod = False
                    modding = False
                    return
                elif add_food_button_rect.collidepoint(event.pos):
                    mod_food = True
                    mod_bob = False
                    allow_mod = True
                    modding = False
                    return
                elif add_bob_button_rect.collidepoint(event.pos):
                    mod_food = False
                    mod_bob = True
                    allow_mod = True
                    modding = False
                    return

                for key, value in grid_value_rects.items():
                    if value.collidepoint(event.pos):
                        selected_value_index = key
                        input_active = True
            elif event.type == pg.KEYDOWN:
                if input_active:
                    NewObjectValueEvaluator(event)
        
        gameController.updateRenderTick()
        screen.blit(background_image, (0, 0))
        new = [(key,value) for key, value in new_object_dict.items()]
        new1 = dict(new)
        labels = list(new1.keys())
        values = list(new1.values())
        grid_value_rects.update(draw_transparent_grids(labels[:len(labels)//2], values[:len(values)//2], 400, 300, 50))
        grid_value_rects.update(draw_transparent_grids(labels[len(labels)//2:], values[len(values)//2:], 1300, 300, 50))

        draw_transparent_button("BACK", back_button_rect, 128)
        draw_transparent_button("ADD FOOD", add_food_button_rect, 128)
        draw_transparent_button("ADD BOB", add_bob_button_rect, 128)

        if input_active:
            # Effacer l'ancien texte avec un rectangle blanc
            pg.draw.rect(screen, WHITE, (grid_value_rects[selected_value_index].x, grid_value_rects[selected_value_index].y, 200, 40))
            input_surface = font.render(input_text, True, BLACK)  # Couleur de la police en noir
            input_rect = input_surface.get_rect(center=(grid_value_rects[selected_value_index].centerx, grid_value_rects[selected_value_index].centery))
            # pg.draw.rect(screen, WHITE, (input_rect.x - 5, input_rect.y - 5, input_rect.width + 10, input_rect.height + 10), border_radius=5)  # Couleur de fond du rectangle en blanc
            screen.blit(input_surface, input_rect)

        pg.display.flip()

        

def NewObjectValueEvaluator(event):
    global selected_value_index, new_object_dict, input_text, input_active
    match selected_value_index:
        case None:
            pass
        case "Food Energy": # Food Energy
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 2000:
                                new_object_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")
        case "Bob Energy": # Bob Spawned Energy
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 1000:
                                new_object_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 4:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    else:
                        print("La valeur doit être un entier.")
                else:
                    print("La valeur ne doit pas dépasser 4 caractère.")
        case "Bob Velocity": # Default velocity
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 10:
                                new_object_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 5 caractère.")   
        case "Bob Mass": # Default mass
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = float(input_text)
                        if not isinstance(new_value, float):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 < new_value <= 10:
                                new_object_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 5 caractère.")   
        case "Bob Vision": # Default Vision
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                new_object_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 5 caractère.")   

        case "Bob Memory Point": # Default Memory point
            if event.key == pg.K_RETURN:
                    if input_text == "":
                            input_active = False
                            input_text = ""
                            selected_value_index = None
                    else:                                
                        new_value = int(input_text)
                        if not isinstance(new_value, int):
                            # print("La valeur doit être un entier.")
                            input_text = ""
                            input_active = False
                        else:
                            if 0 <= new_value <= 10:
                                new_object_dict[selected_value_index] = new_value
                                input_active = False
                                input_text = ""
                                selected_value_index = None
                            else: 
                                input_text = ""
                                input_active = False
            elif event.key == pg.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(input_text) < 5:
                    if event.unicode.isdigit():
                        input_text += event.unicode
                    elif event.unicode == ".":
                        if "." in input_text:
                            print("La valeur doit être just 1 point.")
                        else:
                            input_text += event.unicode
                    else:
                        print("La valeur doit être un float.")
                else:
                    print("La valeur ne doit pas dépasser 5 caractère.")  




def open_network_setting(screen, clock):
    global selected_value_index, grid_value_rects, input_text, input_active
    back_button_rect = pg.Rect(20, 20, button_width, button_height)
    create_room_rect = pg.Rect( (screen.get_width() - big_button_width ) // 2 - 500, 200, big_button_width, big_button_height)
    join_room_rect = pg.Rect( (screen.get_width() - big_button_width ) // 2 + 500, 200, big_button_width, big_button_height)
    etat = EtatJeu.getEtatJeuInstance()
    while etat.online_menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    etat.open_menu = True
                    etat.online_menu = False
                if create_room_rect.collidepoint(event.pos):
                    etat.open_menu = False
                    etat.online_menu = False
                    etat.waiting_room = True
                    etat.create_room = True
                if join_room_rect.collidepoint(event.pos):
                    join_room(screen, clock)


        screen.blit(background_image2, (0, 0))
        
        draw_transparent_button("BACK", back_button_rect, 128)
        draw_transparent_button("CREATE ROOM", create_room_rect, 128)
        draw_transparent_button("JOIN ROOM", join_room_rect, 128)
    
        pg.display.flip()
    return

def waiting_room( screen, clock):
    global selected_value_index, grid_value_rects, input_text, input_active
    input_active = False
    input_text = ""
    etat = EtatJeu.getEtatJeuInstance()
    net = Network.getNetworkInstance()
    back_button_rect = pg.Rect(20, 20, button_width, button_height)
    start_button_rect = pg.Rect((screen.get_width() - button_width) // 2, (screen.get_height() - button_height) //2 + 250,button_width, button_height)

    green = loadGreenLeft()
    blue = loadBlueLeft()
    purple = loadPurpleLeft()
    red = loadRedLeft()

    greenblack = loadGreenRight()
    blueblack = loadBlueRight()
    purpleblack = loadPurpleRight()
    redblack = loadRedRight()

    net.init_listen()
    if etat.create_room:
        packet = Package(PYMSG_CREATE_ROOM)
        net.send_package(packet)
    else:
        pkg = Package(PYMSG_JOIN_ROOM)
        pkg.packData()
        pkg.concatData(net.pack_ip_port(ip_port_dict["IP"], ip_port_dict["PORT"]))
        net.send_package(pkg)
    start_time = time.time()
    while etat.waiting_room:
        connected_players = [player for player in net.clientList.values() if player is not None]
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    print(net.port)
                    net.close_socket()
                    etat.waiting_room = False
                    etat.online_menu = True
                    return
                if start_button_rect.collidepoint(event.pos):
                    pkg = Package(PYMSG_GAME_READY)
                    pkg.packData()
                    net.send_package(pkg)
                    net.this_client.ready = True
                    etat.waiting_room = False
                    etat.online_game = True
        #timer:
        
        # Vérifiez si le nombre de joueurs est suffisant pour jouer
        
        
        screen.blit(background_image2, (0, 0))
        draw_transparent_button("BACK", back_button_rect, 128)
        draw_transparent_button("PLAY", start_button_rect, 128)
        if net.clientList["Green"]:
            if net.clientList["Green"].ready:
                screen.blit(green, (screen.get_width() // 2 - 100, 300))
            else:
                screen.blit(greenblack, (screen.get_width() // 2 - 100, 300))
        if net.clientList["Blue"]:
            if net.clientList["Blue"].ready:
                screen.blit(blue, (screen.get_width() // 2 - 100, 400))
            else:
                screen.blit(blueblack, (screen.get_width() // 2 - 100, 400))
        if net.clientList["Purple"]:
            if net.clientList["Purple"].ready:
                screen.blit(purple, (screen.get_width() // 2 - 100, 500))
            else:
                screen.blit(purpleblack, (screen.get_width() // 2 - 100, 500))
        if net.clientList["Red"]:
            if net.clientList["Red"].ready:
                screen.blit(red, (screen.get_width() // 2 - 100, 600))
            else:
                screen.blit(redblack, (screen.get_width() // 2 - 100, 600))


        net.listen()
        pg.display.flip()

ip_port_dict = { "IP": "", "PORT": 0 }

def join_room(screen, clock ):
    global selected_value_index, grid_value_rects, input_text, input_active, ip_port_dict
    input_active = False
    input_text = ""
    back_button_rect = pg.Rect(20, 20, button_width, button_height)
    join_button_rect = pg.Rect( (screen.get_width() - button_width ) - 20, (screen.get_height() - button_height) - 20, button_width, button_height)
    etat = EtatJeu.getEtatJeuInstance()
    while etat.online_menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    return
                if ip_port_dict["IP"] != "" and ip_port_dict["PORT"] != 0:
                    if join_button_rect.collidepoint(event.pos):
                        etat.open_menu = False
                        etat.online_menu = False
                        etat.waiting_room = True
                        etat.create_room = False
                        return
                for key, value in grid_value_rects.items():
                    if value.collidepoint(event.pos):
                        selected_value_index = key
                        input_active = True
                        print("input_active")
                        # input_text = str(grid_dict[selected_value_index])  # Utiliser la valeur actuelle pour l'affichage initial
                        input_text = ""  # Utiliser la valeur actuelle pour l'affichage initial
            elif event.type == pg.KEYDOWN:
                if input_active:
                    match selected_value_index:
                        case "IP":
                            if event.key == pg.K_RETURN:
                                if input_text == "":
                                    input_active = False
                                    input_text = ""
                                    selected_value_index = None
                                else:
                                    ip_port_dict["IP"] = input_text
                                    input_active = False
                                    input_text = ""
                                    selected_value_index = None
                            elif event.key == pg.K_BACKSPACE:
                                input_text = input_text[:-1]
                            else:
                                if len(input_text) < 15:
                                    input_text += event.unicode
                        case "PORT":
                            if event.key == pg.K_RETURN:
                                if input_text == "":
                                    input_active = False
                                    input_text = ""
                                    selected_value_index = None
                                else:
                                    ip_port_dict["PORT"] = int(input_text)
                                    input_active = False
                                    input_text = ""
                                    selected_value_index = None
                            elif event.key == pg.K_BACKSPACE:
                                input_text = input_text[:-1]
                            else:
                                if len(input_text) < 5:
                                    if event.unicode.isdigit():
                                        input_text += event.unicode
                                    else:
                                        print("La valeur doit être un entier.")
                                else:
                                    print("La valeur ne doit pas dépasser 5 caractère.")

        screen.blit(background_image2, (0, 0))
        new = [(key,value) for key, value in ip_port_dict.items()]
        new1 = dict(new)
        labels = list(new1.keys())
        values = list(new1.values())
        grid_value_rects.update(draw_transparent_grids(labels[:len(labels)//2], values[:len(values)//2], 400, 300, 50))
        grid_value_rects.update(draw_transparent_grids(labels[len(labels)//2:], values[len(values)//2:], 1300, 300, 50))



        draw_transparent_button("BACK", back_button_rect, 128)

        if ip_port_dict["IP"] != "" and ip_port_dict["PORT"] != 0:
            draw_transparent_button("JOIN", join_button_rect, 128)

        if selected_value_index is not None:
            pg.draw.rect(screen, WHITE, grid_value_rects[selected_value_index], 2)
        
        if input_active:
            pg.draw.rect(screen, WHITE, (grid_value_rects[selected_value_index].x, grid_value_rects[selected_value_index].y, 200, 40))
            input_surface = font.render(input_text, True, BLACK)  # Couleur de la police en noir
            input_rect = input_surface.get_rect(center=(grid_value_rects[selected_value_index].centerx, grid_value_rects[selected_value_index].centery))
            # pg.draw.rect(screen, WHITE, (input_rect.x - 5, input_rect.y - 5, input_rect.width + 10, input_rect.height + 10), border_radius=5)  # Couleur de fond du rectangle en blanc
            screen.blit(input_surface, input_rect)


        pg.display.flip()