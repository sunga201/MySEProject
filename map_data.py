import copy

class MapData: #static class
    def __init__(self, mapSize=(20, 20), startSpot=(7, 9), objectSpot=[(17, 13), (14, 18), (10, 7), (16, 12), (19, 3), (5, 16), (15, 18), (8, 3), (0, 9), (7, 7), (5, 1), (8, 0), (3, 2), (3, 4), (1, 1), (0, 0)], hazardSpot=[(5, 18), (16, 7), (12, 8), (11, 17), (11, 9), (13, 5), (8, 1), (7, 5), (6, 9), (9, 9), (2, 3), (5, 4), (4, 4), (1, 0), (2, 4), (3, 1), (2, 0)]): #revise (Should remove initial data)
    #def __init__(self, mapSize=(4, 5), startSpot=(1, 2), objectSpot=[(4, 2), (1, 5)], hazardSpot=([(1, 0), (3, 2)])):
        MapData.mapSize=mapSize
        MapData.startSpot=startSpot
        MapData.objectSpot=objectSpot
        MapData.hazardSpot=hazardSpot
        MapData.hazardSpotH=[]
        MapData.colorBlobH=[]

    def setHiddenData(hazard, cb):
        MapData.hazardSpotH=hazard
        MapData.colorBlobH=cb

    def getHazardH():
        return MapData.hazardSpotH

    def getCbH():
        return MapData.colorBlobH

    def getMapSize():
        return MapData.mapSize

    def getStartSpot():
        return MapData.startSpot

    def getBackObjectSpot(list):
        MapData.objectSpot=copy.deepcopy(list)
        print('restore : ', MapData.objectSpot)
        
    def getObjectSpot():
        return MapData.objectSpot

    def getHazardSpot():
        return MapData.hazardSpot

    def removeHiddenSpot(point):
        MapData.hazardSpotH.remove(point)
