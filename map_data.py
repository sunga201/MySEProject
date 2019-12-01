import copy
import numpy as np

class MapData: #static class
    #def __init__(self, mapSize=(20, 20), startSpot=(7, 9), objectSpot=[(17, 13), (14, 18), (10, 7), (16, 12), (19, 3), (5, 16), (15, 18), (8, 3), (0, 9), (7, 7), (5, 1), (8, 0), (3, 2), (3, 4), (1, 1), (0, 0)], hazardSpot=[(5, 18), (16, 7), (12, 8), (11, 17), (11, 9), (13, 5), (8, 1), (7, 5), (6, 9), (9, 9), (2, 3), (5, 4), (4, 4), (1, 0), (2, 4), (3, 1), (2, 0)]): #revise (Should remove initial data)
    #def __init__(self, mapSize=(5, 0), startSpt=(3, 0), objectSpot=[(2, 0), (5, 0)], hazardSpot=([])):
    def __init__(self, mapSize=(4, 5), startSpot=(1, 2), objectSpot=[(4, 2), (1, 5)], hazardSpot=([(1, 0), (3, 2)])):
    #def __init__(self, mapSize, startSpot, objectSpot, hazardSpot):
        MapData.mapSize=mapSize
        MapData.startSpot=startSpot
        MapData.objectSpot=objectSpot
        MapData.hazardSpot=hazardSpot
        MapData.hazardSpotH = []
        MapData.colorBlobH=[]
        #MapData.makeTestSet(200, 200) # 테스트용 데이터 만드는 함수. 맵 크기 200X200, 목표 지점 (200+200)/2개, 위험 지점 (200+200)/2개

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
        
    def getObjectSpot():
        return MapData.objectSpot

    def getHazardSpot():
        return MapData.hazardSpot

    def removeHiddenHSpot(point):
        MapData.hazardSpotH.remove(point)

    def removeHiddenCBSpot(point):
        MapData.colorBlobH.remove(point)

    '''def makeTestSet(x, y): # 테스트용 맵 데이터를 만드는 함수. x : 테스트 셋 가로 길이, y : 테스트 셋 세로 길이
        MapData.mapSize=(x, y)
        MapData.startSpot=(np.random.choice(x+1, 1)[0], np.random.choice(y+1, 1)[0])
        xList=list(np.random.choice(x+1, x+1, replace=False))
        yList=list(np.random.choice(y+1, y+1, replace=False))

        xobj=xList[:(x+1)//2]
        yobj=yList[:(y+1)//2]
        xhazard=xList[(x+1)//2:]
        yhazard=yList[(y+1)//2:]
        MapData.objectSpot=list(zip(xobj, yobj))
        MapData.hazardSpot=list(zip(xhazard, yhazard))'''
