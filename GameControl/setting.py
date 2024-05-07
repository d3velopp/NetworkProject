class Setting:
    instance = None
    
    def __init__ (self):
        self.tileSize = 32
        self.simuMode = False
        self.resolutionX = 1920
        self.resolutionY = 1080
        self.fps = 16
        self.gridLength = 30
        self.nbBob = 10
        self.nbSpawnFood = 20
        self.foodEnergy = 100
        self.bobSpawnEnergy = 100
        self.bobMaxEnergy = 200
        self.bobNewbornEnergy = 50
        self.sexualBornEnergy = 100
        self.bobStationaryEnergyLoss = 0.5
        self.bobSelfReproductionEnergyLoss = 150
        self.bobSexualReproductionLoss = 100
        self.bobSexualReproductionLevel = 150
        self.perceptionFlatPenalty = 0.2
        self.memoryFlatPenalty = 0.2
        self.defaultVelocity = 1
        self.defaultMass = 1
        self.defaultVision = 0
        self.defaultMemoryPoint = 0
        self.massVariation = 0.1
        self.velocityVariation = 0.1
        self.visionVariation = 1
        self.memoryVariation = 1
        self.selfReproduction = True
        self.sexualReproduction = True
        self.surfaceWidth = self.tileSize * self.gridLength * 2
        self.surfaceHeight = self.tileSize * self.gridLength + self.tileSize * 2
        self.ticksPerDay = 50
        self.imagePath = 'assets/graphics/'
        # self.zoom

    # def getZoom(self):
    #     return self.zoom

    def getTileSize(self):
        return self.tileSize
    
    def getResolutionX(self):
        return self.resolutionX
    
    def getResolutionY(self):
        return self.resolutionY
    
    def getFps(self):
        return self.fps
    
    def getGridLength(self):
        return self.gridLength
    
    def getNbBob(self):
        return self.nbBob
    
    def getNbSpawnFood(self):
        return self.nbSpawnFood
    
    def getFoodEnergy(self):
        return self.foodEnergy
    
    def getBobSpawnEnergy(self):
        return self.bobSpawnEnergy
    
    def getBobMaxEnergy(self):
        return self.bobMaxEnergy
    
    def getBobNewbornEnergy(self):
        return self.bobNewbornEnergy
    
    def getSexualBornEnergy(self):
        return self.sexualBornEnergy
    
    def getBobStationaryEnergyLoss(self):
        return self.bobStationaryEnergyLoss
    
    def getBobSelfReproductionEnergyLoss(self):
        return self.bobSelfReproductionEnergyLoss
    
    def getBobSexualReproductionLoss(self):
        return self.bobSexualReproductionLoss
    
    def getBobSexualReproductionLevel(self):
        return self.bobSexualReproductionLevel
    
    def getPerceptionFlatPenalty(self):
        return self.perceptionFlatPenalty
    
    def getMemoryFlatPenalty(self):
        return self.memoryFlatPenalty
    
    def getDefaultVelocity(self):
        return self.defaultVelocity
    
    def getDefaultMass(self):
        return self.defaultMass
    
    def getDefaultVision(self):
        return self.defaultVision
    
    def getDefaultMemoryPoint(self):
        return self.defaultMemoryPoint
    
    def getMassVariation(self):
        return self.massVariation
    
    def getVelocityVariation(self):
        return self.velocityVariation
    
    def getVisionVariation(self):
        return self.visionVariation
    
    def getMemoryVariation(self):
        return self.memoryVariation
    
    def getSelfReproduction(self):
        return self.selfReproduction
    
    def getSexualReproduction(self):
        return self.sexualReproduction
    
    def getSurfaceWidth(self):
        return self.surfaceWidth
    
    def getSurfaceHeight(self):
        return self.surfaceHeight
    
    def getTicksPerDay(self):
        return self.ticksPerDay
    def setTicksPerDay(self, ticksPerDay):
        self.ticksPerDay = ticksPerDay
    
    def getImagePath(self):
        return self.imagePath
    
    # def setTileSize(self, tileSize):
    #     self.tileSize = tileSize

    def setFps(self, fps):
        self.fps = fps

    def setGridLength(self, gridLength):
        self.gridLength = gridLength
        self.surfaceWidth = self.tileSize * self.gridLength * 2
        self.surfaceHeight = self.tileSize * self.gridLength + self.tileSize * 2

    def setNbBob(self, nbBob):
        self.nbBob = nbBob
    

    def setResolutionX(self, resolutionX):
        self.resolutionX = resolutionX
    
    def setResolutionY(self, resolutionY):
        self.resolutionY = resolutionY
    
    def setNbSpawnFood(self, nbSpawnFood):
        self.nbSpawnFood = nbSpawnFood

    def setFoodEnergy(self, foodEnergy):
        self.foodEnergy = foodEnergy

    def setBobSpawnEnergy(self, bobSpawnEnergy):
        self.bobSpawnEnergy = bobSpawnEnergy

    def setBobMaxEnergy(self, bobMaxEnergy):
        self.bobMaxEnergy = bobMaxEnergy

    def setBobNewbornEnergy(self, bobNewbornEnergy):
        self.bobNewbornEnergy = bobNewbornEnergy

    def setSexualBornEnergy(self, sexualBornEnergy):
        self.sexualBornEnergy = sexualBornEnergy

    def setBobStationaryEnergyLoss(self, bobStationaryEnergyLoss):
        self.bobStationaryEnergyLoss = bobStationaryEnergyLoss

    def setBobSelfReproductionEnergyLoss(self, bobSelfReproductionEnergyLoss):
        self.bobSelfReproductionEnergyLoss = bobSelfReproductionEnergyLoss

    def setBobSexualReproductionLoss(self, bobSexualReproductionLoss):
        self.bobSexualReproductionLoss = bobSexualReproductionLoss

    def setBobSexualReproductionLevel(self, bobSexualReproductionLevel):
        self.bobSexualReproductionLevel = bobSexualReproductionLevel

    def setPerceptionFlatPenalty(self, perceptionFlatPenalty):
        self.perceptionFlatPenalty = perceptionFlatPenalty

    def setMemoryFlatPenalty(self, memoryFlatPenalty):
        self.memoryFlatPenalty = memoryFlatPenalty

    def setDefaultVelocity(self, defaultVelocity):
        self.defaultVelocity = defaultVelocity

    def setDefaultMass(self, defaultMass):
        self.defaultMass = defaultMass

    def setDefaultVision(self, defaultVision):
        self.defaultVision = defaultVision

    def setDefaultMemoryPoint(self, defaultMemoryPoint):
        self.defaultMemoryPoint = defaultMemoryPoint

    def setMassVariation(self, massVariation):
        self.massVariation = massVariation

    def setVelocityVariation(self, velocityVariation):
        self.velocityVariation = velocityVariation

    def setVisionVariation(self, visionVariation):
        self.visionVariation = visionVariation

    def setMemoryVariation(self, memoryVariation):
        self.memoryVariation = memoryVariation

    def setSelfReproduction(self, selfReproduction):
        self.selfReproduction = selfReproduction

    def setSexualReproduction(self, sexualReproduction):
        self.sexualReproduction = sexualReproduction

    def setSurfaceWidth(self, surfaceWidth):
        self.surfaceWidth = surfaceWidth

    def setSurfaceHeight(self, surfaceHeight):
        self.surfaceHeight = surfaceHeight

    def setTicksPerDay(self, ticksPerDay):
        self.ticksPerDay = ticksPerDay

    def setImagePath(self, imagePath):
        self.imagePath = imagePath

    @staticmethod
    def getSettings():
        if Setting.instance is None:
            if (Setting.instance is not None):
                raise Exception("This class is a singleton!")
            Setting.instance = Setting()
            print("Created new setting")
        return Setting.instance

