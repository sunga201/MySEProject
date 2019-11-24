

class MapData: #static class
    def __init__(self, mapSize=(4, 5), startSpot=(1, 2), objectSpot=[(4, 2), (1, 5)], hazardSpot=[(1, 0), (3, 2)]): #revise (initial data remove)
        MapData.mapSize=mapSize
        MapData.startSpot=startSpot
        MapData.objectSpot=objectSpot
        MapData.hazardSpot=hazardSpot
        MapData.hazardSpotH=[]
        MapData.colorBlobH=[]

    def setHiddenData(hazard, cb):
        MapData.hazardSpotH.append(hazard)
        MapData.colorBlobH.append(cb)

    def getHazardH():
        return MapData.hazardSpotH

    def getCbH():
        return MapData.colorBlobH

    def getMapSize():
        return MapData.mapSize

    def getStartSpot():
        return MapData.startSpot

    def getObjectSpot():
        return MapData.objectSpot

    def getHazardSpot():
        return MapData.hazardSpot

    def removeHiddenSpot(point):
        for h in MapData.hazardSpotH:
            if point==h:
                MapData.hazardSpotH.remove(h)
