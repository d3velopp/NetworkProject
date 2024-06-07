from Tiles.tiles import Tile
from GameControl.gameControl import GameControl
from GameControl.setting import Setting
from network.network import *
from Tiles.directions import directionsDict, directionsList
from view.texture import *
import random
from math import floor

class Bob: 
    id = 0
    def __init__(self):
        self.setting = Setting.getSettings()
        self.color = 0 
        self.id = Bob.id
        Bob.id += 1
        self.age = 0
        self.isHunting = False
        self.alreadyInteracted = False
        self.isReadyForInteraction = False
        self.eat_all = False
        self.CurrentTile : 'Tile' = None

        self.energy: 'float' = self.setting.getBobSpawnEnergy()
        self.energyMax = self.setting.getBobMaxEnergy()

        self.mass: 'float' = self.setting.getDefaultMass()
        self.velocity: 'float' = self.setting.getDefaultVelocity()
        self.speedBuffer = 0
        self.speed = self.velocity 

        self.vision: 'float' = self.setting.getDefaultVision()

        self.NextTile : 'Tile' = None
        # self.predator: 'Bob' = None
        self.predators : list['Bob'] = []
        self.prey : 'Bob' = None
        self.foodTilesInVision : list['Tile'] = []
        self.memoryPoint: 'float' = self.setting.getDefaultMemoryPoint()
        self.memorySpace = 2 * round(self.memoryPoint)
        self.memorySpaceLeft = self.memorySpace
        self.visitedTiles: list['Tile'] = []
        self.foodTilesInMemo: dict('Tile', 'float') = {}

        # for graphic purposes
        self.PreviousTile : 'Tile' = None
        self.PreviousTiles : list['Tile'] = []
################ Die and Born ############################
    def spawn(self, tile: 'Tile'):
        self.CurrentTile = tile
        self.PreviousTile = self.CurrentTile
        self.PreviousTiles.append(self.CurrentTile)
        self.CurrentTile.addBob(self)
        GameControl.getInstance().addToNewBornQueue(self) 

    def die(self):
        self.CurrentTile.removeBob(self)
        GameControl.getInstance().addToDiedQueue(self)
        # self.alive = False
    
    ####################### Reproduction #####################################
    def reproduce(self):
        from network.network import Network
        newBob = Bob()
        newBob.energy = self.setting.getBobNewbornEnergy()
        newBob.mass = round(random.uniform(self.mass - self.setting.getMassVariation(), self.mass + self.setting.getMassVariation()), 2)
        newBob.velocity = round(random.uniform(self.velocity - self.setting.getVelocityVariation(), self.velocity + self.setting.getVelocityVariation()), 2)
        newBob.speed = self.velocity
        newBob.color = Network.getNetworkInstance().this_client.color
        newBob.vision = round(random.choice([max(0, self.vision - self.setting.getVisionVariation()), self.vision, self.vision + self.setting.getVisionVariation()]), 2)  
        newBob.memoryPoint = round(random.choice([max(0, self.memoryPoint - self.setting.getMemoryVariation()), self.memoryPoint, self.memoryPoint + self.setting.getMemoryVariation()]), 2)
        newBob.spawn(self.CurrentTile)
        self.energy = self.energy - self.setting.getBobSelfReproductionEnergyLoss()
        return newBob
        
    def born_new_online_bob(self,  dataPack: 'Data'):
        from GameControl.gameControl import GameControl
        game = GameControl.getInstance()
        data = dataPack.data
        self.id = data['id']
        self.color = data['color']
        self.energy = data['energy']
        self.mass = data['mass']
        self.velocity = data['velocity']
        self.speed = data['speed']
        self.vision = data['vision']
        self.memoryPoint = data['memoryPoint']
        for row in game.grid:
            for tile in row:
                if tile.getGameCoord() == data['currentTile']:
                    self.spawn(tile)

############################ Logic action ##################################

    def bob_info_assignment(self, dataPack: 'Data'):
        from GameControl.gameControl import GameControl
        game = GameControl.getInstance()
        data = dataPack.data
        self.id = data['id']
        self.color = data['color']
        for row in game.grid:
            for tile in row:
                if tile.getGameCoord() == data['currentTile']:
                    self.CurrentTile.removeBob(self)
                    self.CurrentTile = tile
                    tile.addBob(self)
                    break
        for coord in data['previousTiles']:
            for row in game.grid:
                for tile in row:
                    if tile.getGameCoord() == coord:
                        self.PreviousTiles.append(tile)
        # print("Bob ", self.id, " is assigned to tile ", [tile.getGameCoord() for tile in self.PreviousTiles])
        self.energy = data['energy']
        self.mass = data['mass']
        self.velocity = data['velocity']
        self.speed = data['speed']
        self.vision = data['vision']
        self.memoryPoint = data['memoryPoint']

    def interact_online(self, pkg: 'Package'):
        if (self.CurrentTile.getEnergy() != 0):
            # print(len(self.CurrentTile.getCurrentBob()))
            if len(self.CurrentTile.getCurrentBob()) == 1:
                energy = self.CurrentTile.getEnergy()
                if(self.energy < self.setting.getBobMaxEnergy()):
                    if ( self.energy + energy < self.setting.getBobMaxEnergy()):
                        self.eat_all = True
                        self.energy += energy
                        self.CurrentTile.foodEnergy = 0
                        data = Data()
                        data.create_bob_consome(self, energy, 1 )
                        # print("Bob ", self.id, self.color ," eat ", energy, " energy", self.eat_all)
                        pkg.addData(data)
                    else:
                        self.eat_all = False
                        self.CurrentTile.foodEnergy -= (self.setting.getBobMaxEnergy() - self.energy)
                        data = Data()
                        data.create_bob_consome(self, (self.setting.getBobMaxEnergy() - self.energy), 0 )
                        pkg.addData(data)
                        # print("Bob ", self.id, self.color ," eat ", self.setting.getBobMaxEnergy() - self.energy, " energy", self.eat_all)
                        self.energy = self.setting.getBobMaxEnergy()
            elif len(self.CurrentTile.getCurrentBob()) > 1:
                sum = 0
                for bob in self.CurrentTile.getCurrentBob():
                    sum += bob.velocity
                energy = self.CurrentTile.getEnergy()*self.velocity/sum
                if(self.energy < self.setting.getBobMaxEnergy()):
                    if ( self.energy + energy < self.setting.getBobMaxEnergy()):
                        self.eat_all = True
                        self.energy += energy
                        self.CurrentTile.foodEnergy -= energy
                        data = Data()
                        data.create_bob_consome(self, energy, 1 )
                        print("Bob ", self.id, self.color ," eat ", energy, " energy", self.eat_all)
                        pkg.addData(data)
                    else:
                        # print(self.energy)
                        self.eat_all = False
                        print("Bob ", self.id, self.color ," eat ", self.setting.getBobMaxEnergy() - self.energy, " energy", self.eat_all)
                        data = Data()
                        data.create_bob_consome(self, self.setting.getBobMaxEnergy() - self.energy, 0 )
                        pkg.addData(data)
                        self.CurrentTile.foodEnergy -= (self.setting.getBobMaxEnergy() - self.energy)
                        self.energy = self.setting.getBobMaxEnergy()
        elif (len(self.CurrentTile.getBobs()) > 1):
            preys = self.detectPreys(self.CurrentTile.getBobs())
            unluckyBob = self.getSmallestPrey(preys)
            if (unluckyBob is not None):
                self.eat(unluckyBob)
                data = Data()
                data.create_bob_kill(self.id, self.color, unluckyBob.id, unluckyBob.color)
                pkg.addData(data)
            elif (self.setting.getSexualReproduction()):
                partners = self.detectPotentialPartners(self.CurrentTile.getBobs())
                if (partners != []):
                    partner = self.getRandomPartner(partners)
                    childBob = self.mate(partner)
                    print("Mateeeeeeee")
                    if GameControl.getInstance().is_online:
                        data = Data()
                        data.create_bob_mate(self, partner, childBob.id, childBob.color)
                        pkg.addData(data)
                    

    def move_online(self, pkg):
        self.PreviousTile = self.CurrentTile
        self.PreviousTiles.append(self.CurrentTile)
        if (self.energy <= 0): 
            self.die()
            data = Data()
            data.create_bob_die_package(self)
            pkg.addData(data)
            # Send message to all clients
        elif self.energy >= self.setting.getBobMaxEnergy(): 
            data = Data()
            data.create_bob_born_package(self.reproduce())
            pkg.addData(data)
            data2 = Data()
            data2.create_bob_status_package(self)
            pkg.addData(data2)
            # Send message to all clients
        else: # Move
            self.consumePerceptionAndMemoryEnergy()
            if (self.speed < 1 or self.CurrentTile.getEnergy() != 0 or self.detectPreys(self.CurrentTile.getBobs()) != []):
                self.consumeStationaryEnergy()
                data = Data()
                data.create_bob_status_package(self)
                pkg.addData(data)
                # print("Standing still", self.speed , self.velocity, self.CurrentTile.getEnergy(), self.detectPreys(self.CurrentTile.getBobs()))
                # Send message to all clients 
            else:
                self.consumeKinecticEnergy()
                for _ in range(floor(self.speed)):
                    if self in GameControl.getInstance().getDiedQueue():
                        break
                    else:
                        if (self.alreadyInteracted):
                            self.alreadyInteracted = False
                        if (self.isReadyForInteraction):
                            # self.isReadyForInteraction = False
                            break
                        else:
                            if (self.memoryPoint != 0):
                                self.memorizeVisitedTile(self.CurrentTile)
                            if (round(self.vision) != 0):
                                self.scan()
                            self.determineNextTile()
                            self.move()
                            self.PreviousTiles.append(self.CurrentTile)
                            if (self.CurrentTile.getEnergy() > 0):
                                self.isReadyForInteraction = True
                            elif (len(self.CurrentTile.getBobs()) > 1):
                                preys = self.detectPreys(self.CurrentTile.getBobs())
                                unluckyBob = self.getSmallestPrey(preys)
                                if (unluckyBob is not None):
                                    self.isReadyForInteraction = True
                                elif (self.setting.getSexualReproduction()):
                                    partners = self.detectPotentialPartners(self.CurrentTile.getBobs())
                                    if (partners != []):
                                        self.isReadyForInteraction = True
            
                data = Data()
                data.create_bob_status_package(self)
                pkg.addData(data)
                self.isReadyForInteraction = False
            self.updateSpeed()
        for tile in self.CurrentTile.getNearbyTiles(round(self.vision)):
            tile.seen = True
        
            # print("Tile seen", tile.seen)

################## Action ##################################
    def action(self):
        self.PreviousTile = self.CurrentTile
        self.PreviousTiles.append(self.CurrentTile)

        if (self.energy <= 0): 
            self.die()    
        elif (self.setting.getSelfReproduction() and self.energy >= self.setting.getBobMaxEnergy()):
                self.reproduce()
        else:
            self.consumePerceptionAndMemoryEnergy()
            if (self.speed < 1 or self.CurrentTile.getEnergy() != 0 or self.detectPreys(self.CurrentTile.getBobs()) != []):
                self.consumeStationaryEnergy()
                self.interact()
            else:
                # if not then bob will use its speed and consume kinetic energy to move
                self.consumeKinecticEnergy()
                for _ in range(floor(self.speed)):
                    if self in GameControl.getInstance().getDiedQueue():
                        break
                    else:
                        if (self.alreadyInteracted):
                            self.alreadyInteracted = False
                            break
                        else:
                            if (self.memoryPoint != 0):
                                self.memorizeVisitedTile(self.CurrentTile)
                            if (round(self.vision) != 0):
                                self.scan()
                            self.determineNextTile()
                            self.move()
                            self.PreviousTiles.append(self.CurrentTile)
                            self.interact()
            self.updateSpeed()  
        for tile in self.CurrentTile.getNearbyTiles(round(self.vision)):
            tile.seen = True
    


    def move(self):
        self.CurrentTile.removeBob(self)
        self.NextTile.addBob(self)
        self.CurrentTile = self.NextTile

    def updateSpeed(self):
        self.speedBuffer = round(self.speed - floor(self.speed), 2)
        self.speed = self.velocity + self.speedBuffer

################## Consume Energy ##################################
    def consumeKinecticEnergy(self):
        kinecticEnergy = self.mass * self.velocity**2
        self.energy = max(0, round(self.energy - kinecticEnergy, 2))
    def consumePerceptionAndMemoryEnergy(self):
        perceptionEnergy = self.vision * (self.setting.getPerceptionFlatPenalty())
        memoryEnergy = self.memoryPoint * (self.setting.getMemoryFlatPenalty())
        self.energy = max(0, round(self.energy - perceptionEnergy - memoryEnergy, 2)) 
    def consumeStationaryEnergy(self):
        self.energy = max(0, round(self.energy - self.setting.getBobStationaryEnergyLoss(), 2)) 

##################### Interact in one tick  #############################
    def interact(self):
        if (self.CurrentTile.getEnergy() != 0):
            self.consumeFood()
        elif (len(self.CurrentTile.getBobs()) > 1):
            preys = self.detectPreys(self.CurrentTile.getBobs())
            unluckyBob = self.getSmallestPrey(preys)
            if (unluckyBob is not None):
                self.eat(unluckyBob)
            elif (self.setting.getSexualReproduction()):
                partners = self.detectPotentialPartners(self.CurrentTile.getBobs())
                if (partners != []):
                    partner = self.getRandomPartner(partners)
                    self.mate(partner)

##################### Interact with foods #####################################
    def consumeFood(self):
        energy = self.CurrentTile.getEnergy()
        if(self.energy < self.setting.getBobMaxEnergy()):
            if ( self.energy + energy < self.setting.getBobMaxEnergy()):
                self.energy += energy
                self.CurrentTile.foodEnergy = 0
            else:
                self.CurrentTile.foodEnergy -= (self.setting.getBobMaxEnergy() - self.energy)
                self.energy = self.setting.getBobMaxEnergy()
        self.alreadyInteracted = True

################### Interact with other bobs ###########################
    def canEat(self, bob: 'Bob') -> bool:
        if GameControl.getInstance().is_online:
            return bob.mass * 3 / 2 < self.mass and self.color != bob.color
        else:
            return bob.mass * 3 / 2 < self.mass
    

    def eat(self, bob: 'Bob'):
        ############################ Envoyer message de mort

        ######################################################
        bob.PreviousTile = bob.CurrentTile
        self.energy = min(self.setting.getBobMaxEnergy(), self.energy + 1/2 * bob.energy * (1 - bob.mass / self.mass))
        bob.die()
        self.alreadyInteracted = True

    def canMate(self, bob: 'Bob') -> bool:
        energyCondition = self.energy >= self.setting.getBobSexualReproductionLevel() and bob.energy >= self.setting.getBobSexualReproductionLevel()
        return energyCondition and not self.canEat(bob) and not bob.canEat(self)

    def mate(self, partner: 'Bob'):
        childBob = Bob()
        childBob.color = self.color
        childBob.energy = self.setting.getSexualBornEnergy()
        childBob.mass = round((self.mass + partner.mass) / 2, 2)
        childBob.velocity = round((self.velocity + partner.velocity) / 2)
        childBob.speed = childBob.velocity
        childBob.vision = round((self.vision + partner.vision) / 2, 2)
        childBob.memoryPoint = round((self.memoryPoint + partner.memoryPoint) / 2, 2)
        childBob.spawn(self.CurrentTile)
        self.energy -= self.setting.getBobSexualReproductionLoss()
        partner.energy -= self.setting.getBobSexualReproductionLoss()
        self.alreadyInteracted = True
        partner.alreadyInteracted = True
        return childBob
        print("Bob ", self.id, " and Bob ", partner.id, " have a child Bob ", childBob.id)


####################### Detect Preys, Predators. Partners and Foods #####################################
    def detectPreys(self, listBobs: list['Bob']) -> list['Bob']:
        preys : list['Bob'] = []
        for bob in listBobs:
            if (self.canEat(bob)):
                preys.append(bob)
        return preys
    
    def getSmallestPrey(self, listPreys: list['Bob']) -> 'Bob':
        if (listPreys != []):
            smallestMassBob = min(listPreys, key = lambda bob: bob.mass)
            return smallestMassBob
        else:
            return None
        
    def detectPredators(self, listBobs: list['Bob']) -> list['Bob']:
        predators : list['Bob'] = []
        for bob in listBobs:
            if (bob.canEat(self)):
                predators.append(bob)
        return predators
    
    def getClosestPredator(self, listPredators: list['Bob']) -> 'Bob':  
        if (listPredators != []):
            closestPredator = min(listPredators, 
                                 key = lambda bob: Tile.distanceofTile(self.getCurrentTile(), bob.getCurrentTile()))
            return closestPredator
        else:
            return None
    
    def detectPotentialPartners(self, listBobs: list['Bob']) -> list['Bob']:
        potentialPartners: list['Bob'] = []
        if GameControl.getInstance().is_online:
            for bob in listBobs:
                if (self.canMate(bob) and bob != self and self.color == bob.color):
                    potentialPartners.append(bob)
        else:
            for bob in listBobs:
                if (self.canMate(bob) and bob != self):
                    potentialPartners.append(bob)
        return potentialPartners
    
    def getRandomPartner(self, listPartners: list['Bob']) -> 'Bob':
        return random.choice(listPartners)
    
    def getLargestNearestFoodTile(self, listFoodTiles: list['Tile']) -> Tile:
        if (listFoodTiles == []):
            return None
        else:
            bestFoodTile = min(listFoodTiles, 
                            key = lambda tile: (Tile.distanceofTile(self.CurrentTile, tile), 
                                                 -tile.getEnergy()))
            return bestFoodTile
        
################ Scan ###########################################
    def scan(self):
        tilesInVision = self.CurrentTile.getNearbyTiles(round(self.vision))

        seenBobs: list['Bob'] = []
        newFoodTilesInVision: list['Tile'] = []

        #remove the food in memo if it in vision right now
        for tile in list(self.foodTilesInMemo.keys()):
            if (Tile.distanceofTile(self.CurrentTile, tile) <= round(self.vision)):
                self.removeFoodTileInMemo(tile)

        #detect bobs and food in vision
        for tile in tilesInVision:
            if (tile.getBobs() != []):
                for bob in tile.getBobs():
                    if (bob != self):
                        seenBobs.append(bob)
            else:
                if (tile.getEnergy() != 0):
                    newFoodTilesInVision.append(tile)

        #remember the food in the precendent tick 
        if (self.memoryPoint != 0):
            notChosenFoods = list(set(self.foodTilesInVision) - set(newFoodTilesInVision))
            for tile in notChosenFoods:
                self.memorizeFoodTile(tile)
        
        #update the food in vision
        self.foodTilesInVision = newFoodTilesInVision.copy()
        
        #detect predators and preys
        # predatorInVision = self.detectPredators(seenBobs)
        # self.predator = self.getClosestPredator(predatorInVision)
        self.predators = self.detectPredators(seenBobs)
        
        preysInVision = self.detectPreys(seenBobs)
        self.prey = self.getSmallestPrey(preysInVision)


################ Use memory #####################################
    def memorizeVisitedTile(self, tile: 'Tile'):
        if (tile not in self.visitedTiles):
            if (self.memorySpaceLeft >= 1):
                self.visitedTiles.append(tile)
            else:
                if (self.visitedTiles != []):
                    self.visitedTiles.pop(0)
                self.visitedTiles.append(tile)
        self.updateMemorySpaceLeft()
    
    def memorizeFoodTile(self, tile: 'Tile'):
        if (self.memorySpaceLeft >= 2 ):
            self.foodTilesInMemo[tile] = tile.getEnergy()
        else:
            if (len(self.visitedTiles) >= 2):
                self.visitedTiles.pop(0)
                self.visitedTiles.pop(0)
                self.foodTilesInMemo[tile] = tile.getEnergy()
            else:
                if (self.foodTilesInMemo != {}):
                    smallestFoodtile = min(self.foodTilesInMemo, key = lambda tile: self.foodTilesInMemo[tile])
                    if tile.getEnergy() > self.foodTilesInMemo[smallestFoodtile]:
                        self.foodTilesInMemo.pop(smallestFoodtile)
                self.foodTilesInMemo[tile] = tile.getEnergy()
        self.updateMemorySpaceLeft()

    def updateMemorySpaceLeft(self):
        memorySpaceUsed = len(self.visitedTiles) + 2*len(self.foodTilesInMemo)
        self.memorySpaceLeft = self.memorySpace - memorySpaceUsed
    
    def removeFoodTileInMemo(self, tile: 'Tile'):
        if (tile in self.foodTilesInMemo):
            self.foodTilesInMemo.pop(tile)
            self.updateMemorySpaceLeft()

######################## Find next tile #####################################
    def determineNextTile(self):
        if (self.predators != []):
            self.NextTile = self.runFrom(self.predators)
            self.isHunting = False
        elif (self.foodTilesInVision != []):
            target = self.getLargestNearestFoodTile(self.foodTilesInVision)
            self.NextTile = self.moveToward(target)
            self.isHunting = False
        elif (self.prey is not None):
            target = self.prey.getCurrentTile()
            self.NextTile = self.moveToward(target)
            self.isHunting = True
        elif (self.foodTilesInMemo != {}):
            target = max(self.foodTilesInMemo, key = lambda tile: self.foodTilesInMemo[tile])
            self.NextTile = self.moveToward(target)
            self.isHunting = False
        else:
            # move random but not move to the previous tile
            nearbyTiles = self.CurrentTile.getNearbyTiles(1)
            nearbyTiles.remove(self.CurrentTile)
            nearbyTiles = list(set(nearbyTiles) - set(self.visitedTiles))
            self.NextTile = random.choice(nearbyTiles) if nearbyTiles != [] else self.setRandomTile()
            self.isHunting = False

######################## Move toward food, prey ###############################################
    def moveToward(self, target: 'Tile'):

        (x, y) = Tile.CountofTile(target, self.CurrentTile)

        x_direction = 0 if x == 0 else (1 if x > 0 else -1)
        y_direction = 0 if y == 0 else (1 if y > 0 else -1)

        if (x_direction == 0 and y_direction == 0):
            return self.CurrentTile
        else:
            chosenDirection = random.choice(directionsDict[(x_direction, y_direction)])
            return self.CurrentTile.getDirectionTiles(chosenDirection)
    
############################# Run from predators###########################################
    def runFrom(self, predators: list['Bob']):
        bestDirection = None
        bestDistance = 0

        for direction in directionsList:
            tile = self.CurrentTile.getDirectionTiles(direction)
            if tile is None:
                continue
    
            minDistance = min([Tile.distanceofTile(tile, predator.CurrentTile) for predator in predators])
            # minDistance = Tile.distanceofTile(tile, predator.CurrentTile) 
            if minDistance > bestDistance:
                bestDirection = direction
                bestDistance = minDistance
        
        return self.CurrentTile.getDirectionTiles(bestDirection) if bestDirection is not None else self.CurrentTile
    

    def setRandomTile(self):     
        nearbyTiles = self.CurrentTile.getNearbyTiles(1)
        return random.choice(nearbyTiles)
    def randomAdjacent(self):
        nearbyTiles = self.CurrentTile.getNearbyTiles(1)
        nearbyTiles.remove(self.CurrentTile)
        return random.choice(nearbyTiles)
        
    def getExplodeTexture(self, progression):
        return loadExplosionImage()[progression]
    def getSpawnTexture(self, progression):
        return loadSpawnImage()[progression]
    def getCurrentTile(self) -> Tile:
        return self.CurrentTile
    def getNextTile(self) -> Tile:
        return self.NextTile
    def getPreviousTile(self) -> Tile:
        return self.PreviousTile
    def getPreviousTiles(self) -> list['Tile']:
        return self.PreviousTiles
    def clearPreviousTiles(self):
        self.PreviousTiles.clear()

    def getEnergy(self) -> float:
        return self.energy
    def getMass(self) -> float:
        return self.mass
    def getVelocity(self) -> float:
        return self.velocity
    def getVision(self) -> float:
        return self.vision
    def getMemoryPoint(self) -> float:
        return self.memoryPoint
    def getId(self) -> int:
        return self.id
    
    def setId(self, id: int):
        self.id = id
    def setEnergy(self, energy: float):
        self.energy = energy
    def setMass(self, mass: float):
        self.mass = mass
    def setVelocity(self, velocity: float):
        self.velocity = velocity
    def setVision(self, vision: float):
        self.vision = vision
    def setMemoryPoint(self, memoryPoint: float):
        self.memoryPoint = memoryPoint
    def setCurrentTile(self, tile: Tile):
        self.CurrentTile = tile
    def setPreviousTile(self, tile: Tile):
        self.PreviousTile = tile

    
        



        
        
