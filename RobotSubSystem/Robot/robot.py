import numpy as np
import time
from Database.mapAndPathData import MapData
from abc import *

moveDirection = [(0, 1), (1, 0), (0, -1), (-1, 0)]

class IRobotInterface(metaclass=ABCMeta):
    @abstractmethod
    def positioningSensor(self):
        pass

    @abstractmethod
    def colorBlobSensor(self):
        pass

    @abstractmethod
    def hazardSensor(self):
        pass

    @abstractmethod
    def getFoundHazardSpot(self):
        pass

    @abstractmethod
    def moveForward(self):
        pass

    @abstractmethod
    def turnCW(self):
        pass



class SIM(IRobotInterface):
    def __init__(self, dir):
        self.direction=dir # 0 : up 1 : right 2 : down 3 : left
        self.position=MapData.getStartSpot()
        self.foundHazardSpot=[]

    def _checkError(self, checkSpotList): # 바로 앞이나 두 칸 앞에 hazard spot이 있을 때, 또는 앞으로 두칸 움직이면 맵 밖으로 나가버릴 때
                                         # 앞으로 두 칸 움직이는 오동작을 배제하기 위해 사용한다.
        mapSize=MapData.getMapSize()
        hazardSpot=MapData.getHazardSpot() + MapData.getHazardH()

        for checkSpot in checkSpotList:
            if checkSpot in hazardSpot or checkSpot[0]<0 or checkSpot[0]>mapSize[0] or checkSpot[1]<0 or checkSpot[1]>mapSize[1]:
                return True
        return False

    #로봇을 앞으로 한 칸 이동시킨다. 로봇이 움직이지 않거나, 앞으로 두 칸 움직일 가능성이 있다.
    def moveForward(self):
        inPlaceProp=0.8
        twoStepProp=0.9

        dir=moveDirection[self.direction]
        checkSpotList=[(self.position[0]+dir[0], self.position[1]+dir[1]), (self.position[0]+2*dir[0], self.position[1]+2*dir[1])]
        checkE=self._checkError(checkSpotList)

        if checkE==True:
            twoStepProp=1 #바로 앞이나 두칸 앞에 위험 지역이 있을 경우에는 앞으로 두 칸 가는 오작동을 배제한다.

        bugProp=np.random.rand()
        if bugProp>inPlaceProp:
            if bugProp>twoStepProp:
                self.position += 2*np.array(moveDirection[self.direction])

        else:
            self.position+=np.array(moveDirection[self.direction])

        self.position=list(self.position)
        if inPlaceProp==1: inPlaceProp=0.8

    #로봇을 시계방향으로 90도 회전시킨다.
    def turnCW(self):
        self.direction=(self.direction+1)%4

    #현재 로봇의 위치와 방향을 리턴한다.
    def positioningSensor(self):
        return self.position, self.direction

    #현재 로봇 인근 지점에 hidden color blob spot이 있는지 확인하고 있으면 해당 지점들의 뱡향을 리스트에 넣어서 리턴한다.
    def colorBlobSensor(self):
        hiddenCB=MapData.getCbH()
        checkSpot=[self.position]*4 + np.array(moveDirection)
        cbList=[]

        for spot in hiddenCB:
            for i in range(0, 4):
                if spot[0] == checkSpot[i][0] and spot[1]==checkSpot[i][1]:
                    cbList.append(i)
        return cbList

    # 현재 로봇 전방 한 칸 앞에 있는 위험지역을 발견하고 이를 foundHazardSpot 배열에 추가한다.
    def hazardSensor(self):
        self.isHazard=False # moveForward에 사용. 이 값이 True이면 오동작은 배제한다.
        hiddenHazard=MapData.getHazardH()
        checkSpot=(self.position[0]+moveDirection[self.direction][0], self.position[1]+moveDirection[self.direction][1])
        if checkSpot in hiddenHazard:
            self.foundHazardSpot.append(checkSpot)
            self.isHazard=True
            return True
        return False

    #지금까지 로봇이 발견한 hazard spot들의 리스트를 반환한다.
    def getFoundHazardSpot(self):
        return self.foundHazardSpot