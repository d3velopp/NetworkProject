import os
import sys
from GameControl.gameControl import GameControl
from GameControl.EventManager import *
from GameControl.setting import Setting
from Tiles.Bob.bob import *
from Tiles.tiles import *

setting = Setting.getSettings()
gameController = GameControl.getInstance()

def saveGame( option):
    file = open(f"save/save{option}.txt", "w")
    file.write( f"SETTING GRID_LENGTH {setting.getGridLength()}\n")
    file.write( f"SETTING NB_SPAWN_FOOD {setting.getNbSpawnFood()}\n")
    file.write( f"SETTING FOOD_ENERGY {setting.getFoodEnergy()}\n")
    file.write( f"SETTING BOB_SPAWN_ENERGY {setting.getBobSpawnEnergy()}\n")
    file.write( f"SETTING BOB_MAX_ENERGY {setting.getBobMaxEnergy()}\n")
    file.write( f"SETTING BOB_NEWBORN_ENERGY {setting.getBobNewbornEnergy()}\n")
    file.write( f"SETTING SEXUAL_BORN_ENERGY {setting.getSexualBornEnergy()}\n")
    file.write( f"SETTING BOB_STATIONARY_ENERGY_LOSS {setting.getBobStationaryEnergyLoss()}\n")
    file.write( f"SETTING BOB_SELF_REPRODUCTION_ENERGY_LOSS {setting.getBobSelfReproductionEnergyLoss()}\n")
    file.write( f"SETTING BOB_SEXUAL_REPRODUCTION_LOSS {setting.getBobSexualReproductionLoss()}\n")
    file.write( f"SETTING BOB_SEXUAL_REPRODUCTION_LEVEL {setting.getBobSexualReproductionLevel()}\n")
    file.write( f"SETTING PERCEPTION_FLAT_PENALTY {setting.getPerceptionFlatPenalty()}\n")
    file.write( f"SETTING MEMORY_FLAT_PENALTY {setting.getMemoryFlatPenalty()}\n")
    file.write( f"SETTING DEFAULT_VELOCITY {setting.getDefaultVelocity()}\n")
    file.write( f"SETTING DEFAULT_MASS {setting.getDefaultMass()}\n")
    file.write( f"SETTING DEFAULT_VISION {setting.getDefaultVision()}\n")
    file.write( f"SETTING DEFAULT_MEMORY_POINT {setting.getDefaultMemoryPoint()}\n")
    file.write( f"SETTING MASS_VARIATION {setting.getMassVariation()}\n")
    file.write( f"SETTING VELOCITY_VARIATION {setting.getVelocityVariation()}\n")
    file.write( f"SETTING VISION_VARIATION {setting.getVisionVariation()}\n")
    file.write( f"SETTING MEMORY_POINT_VARIATION {setting.getMemoryVariation()}\n")
    file.write( f"SETTING SELF_REPRODUCTION {setting.getSelfReproduction()}\n")
    file.write( f"SETTING SEXUAL_REPRODUCTION {setting.getSexualReproduction()}\n")
    file.write( f"SETTING TICK_PER_DAY {setting.getTicksPerDay()}\n")
    file.write( f"GAME NB_BOB {gameController.getNbBobs()}\n")
    file.write( f"GAME NB_BOB_SPAWNED {gameController.getNbBobsSpawned()}\n")
    file.write( f"GAME CURRENT_TICK {gameController.getTick()}\n")
    file.write( f"GAME CURRENT_DAY {gameController.getDay()}\n")
    for bob in gameController.getListBobs():
        file.write(f"BOB {bob.getId()} {bob.getCurrentTile().gridX} {bob.getCurrentTile().gridY} {bob.getEnergy()} {bob.getMass()} {bob.getVelocity()} {bob.getVision()} {bob.getMemoryPoint()}\n")
    for bob in gameController.getNewBornQueue():
        file.write(f"NEW_BORN {bob.getId()} {bob.getCurrentTile().gridX} {bob.getCurrentTile().gridY} {bob.getEnergy()} {bob.getMass()} {bob.getVelocity()} {bob.getVision()} {bob.getMemoryPoint()}\n")
    try:
        for tile in gameController.getFoodTiles():
            file.write(f"FOOD {tile.gridX} {tile.gridY} {tile.getEnergy()}\n")
    except TypeError:
        pass
    
    file.close()

def loadSetting(option):
    # gameController = GameControl.getInstance()

    print("Loading setting")
    try:
        file = open(f"save/save{option}.txt", 'r')
    except FileNotFoundError:
        saveGame(option)
    
    print("File opened")
    for line in file.readlines():
        word = line.split()
        if word[0] == "SETTING":
            match word[1]:
                case "GRID_LENGTH":
                    setting.setGridLength(int(word[2]))
                case "NB_SPAWN_FOOD":
                    setting.setNbSpawnFood(int(word[2]))
                case "FOOD_ENERGY":
                    setting.setFoodEnergy(int(word[2]))
                case "BOB_SPAWN_ENERGY":
                    setting.setBobSpawnEnergy(int(word[2]))
                case "BOB_MAX_ENERGY":
                    setting.setBobMaxEnergy(int(word[2]))
                case "BOB_NEWBORN_ENERGY":
                    setting.setBobNewbornEnergy(int(word[2]))
                case "SEXUAL_BORN_ENERGY":
                    setting.setSexualBornEnergy(int(word[2]))
                case "BOB_STATIONARY_ENERGY_LOSS":
                    setting.setBobStationaryEnergyLoss(float(word[2]))
                case "BOB_SELF_REPRODUCTION_ENERGY_LOSS":
                    setting.setBobSelfReproductionEnergyLoss(int(word[2]))
                case "BOB_SEXUAL_REPRODUCTION_LOSS":
                    setting.setBobSexualReproductionLoss(int(word[2]))
                case "BOB_SEXUAL_REPRODUCTION_LEVEL":
                    setting.setBobSexualReproductionLevel(int(word[2]))
                case "PERCEPTION_FLAT_PENALTY":
                    setting.setPerceptionFlatPenalty(float(word[2]))
                case "MEMORY_FLAT_PENALTY":
                    setting.setMemoryFlatPenalty(float(word[2]))
                case "DEFAULT_VELOCITY":
                    setting.setDefaultVelocity(float(word[2]))
                case "DEFAULT_MASS":
                    setting.setDefaultMass(float(word[2]))
                case "DEFAULT_VISION":
                    setting.setDefaultVision(int(word[2]))
                case "DEFAULT_MEMORY_POINT":
                    setting.setDefaultMemoryPoint(int(word[2]))
                case "MASS_VARIATION":
                    setting.setMassVariation(float(word[2]))
                case "VELOCITY_VARIATION":
                    setting.setVelocityVariation(float(word[2]))
                case "VISION_VARIATION":
                    setting.setVisionVariation(int(word[2]))
                case "MEMORY_POINT_VARIATION":
                    setting.setMemoryVariation(int(word[2]))
                case "SELF_REPRODUCTION":
                    if word[2] == "True":
                        setting.setSelfReproduction(True)
                    else:
                        setting.setSelfReproduction(False)
                case "SEXUAL_REPRODUCTION":
                    if word[2] == "True":
                        setting.setSexualReproduction(True)
                    else:
                        setting.setSexualReproduction(False)
                case "TICK_PER_DAY":
                    setting.setTicksPerDay(int(word[2]))
    file.close()
    
def loadGameController(option):
    # gameController = GameControl.getInstance()
    try:
        file = open(f"save/save{option}.txt", 'r')
    except FileNotFoundError:
        saveGame(option)
    for line in file.readlines():
        word = line.split()
        if word[0] == "GAME":
            match word[1]:
                case "NB_BOB":
                    gameController.setNbBobs(int(word[2]))
                case "NB_BOB_SPAWNED":
                    gameController.setNbBobsSpawned(int(word[2]))
                case "CURRENT_TICK":
                    gameController.setTick(int(word[2]))
                case "CURRENT_DAY":
                    gameController.setDay(int(word[2]))
    file.close()

def loadBob(option):
    # gameController = GameControl.getInstance()
    try:
        file = open(f"save/save{option}.txt", 'r')
    except FileNotFoundError:
        saveGame(option)
    for line in file.readlines():
        word = line.split()
        if word[0] == "BOB":
            bob = Bob()
            bob.setId(int(word[1]))
            bob.setCurrentTile(gameController.getMap()[int(word[2])][int(word[3])])
            bob.PreviousTiles.append(bob.CurrentTile)
            bob.CurrentTile.addBob(bob)
            bob.setEnergy(float(word[4]))
            bob.setMass(float(word[5]))
            bob.setVelocity(float(word[6]))
            bob.setVision(float(word[7]))
            bob.setMemoryPoint(float(word[8]))
            bob.determineNextTile()
            gameController.getListBobs().append(bob)
            gameController.setNbBobs(gameController.getNbBobs() + 1)
            gameController.setNbBobsSpawned(gameController.getNbBobsSpawned() + 1)
        if word[0] == "NEW_BORN":
            bob = Bob()
            bob.setId(int(word[1]))
            bob.setCurrentTile(gameController.getMap()[int(word[2])][int(word[3])])
            bob.setPreviousTile(bob.CurrentTile)
            bob.PreviousTiles.append(bob.CurrentTile)
            bob.CurrentTile.addBob(bob)
            bob.setEnergy(float(word[4]))
            bob.setMass(float(word[5]))
            bob.setVelocity(float(word[6]))
            bob.setVision(float(word[7]))
            bob.setMemoryPoint(float(word[8]))
            bob.determineNextTile()
            gameController.addToNewBornQueue(bob)
    file.close()

def loadFood(option):
    # gameController = GameControl.getInstance()
    try:
        file = open(f"save/save{option}.txt", 'r')
    except FileNotFoundError:
        saveGame(option)
    for line in file.readlines():
        word = line.split()
        if word[0] == "FOOD":
            tile = gameController.getMap()[int(word[1])][int(word[2])]
            tile.foodEnergy = float(word[3])
    file.close()