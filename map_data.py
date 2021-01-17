import copy

class MapData: #static class
    # 맵 데이터 기본값
    # size : 4 X 5
    # 시작지점 : (1, 2)
    # 목표지점 : (4, 2), (1, 5)
    # 위험지점 : (1, 0), (3, 2)
    def __init__(self, mapSize=(4, 5), startSpot=(1, 2), objectSpot=[(4, 2), (1, 5)], hazardSpot=([(1, 0), (3, 2)])):
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
