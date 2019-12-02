import map_data
import numpy as np
import time
from abc import *
from queue import PriorityQueue

moveDirection = [(0, 1), (1, 0), (0, -1), (-1, 0)]

class SIM:
    def __init__(self, dir):
        self.direction=dir # 0 : up 1 : right 2 : down 3 : left
        self.position=map_data.MapData.getStartSpot()
        self.foundHazardSpot=[]

    def _checkError(self, checkSpotList): # 바로 앞이나 두 칸 앞에 hazard spot이 있을 때, 또는 앞으로 두칸 움직이면 맵 밖으로 나가버릴 때
                                         # 앞으로 두 칸 움직이는 오동작을 배제하기 위해 사용한다.
        mapSize=map_data.MapData.getMapSize()
        hazardSpot=map_data.MapData.getHazardSpot() + map_data.MapData.getHazardH()

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
        hiddenCB=map_data.MapData.getCbH()
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
        hiddenHazard=map_data.MapData.getHazardH()
        checkSpot=(self.position[0]+moveDirection[self.direction][0], self.position[1]+moveDirection[self.direction][1])
        if checkSpot in hiddenHazard:
            self.foundHazardSpot.append(checkSpot)
            self.isHazard=True
            return True
        return False

    #지금까지 로봇이 발견한 hazard spot들의 리스트를 반환한다.
    def getFoundHazardSpot(self):
        return self.foundHazardSpot

#이 클래스의 메소드는 ControlPath 클래스를 통해서만 참조할 수 있다.
class PathInfo:
    def __init__(self):
        self.path=[]

    def _getPathInfo(self):
        return self.path

    def _setPath(self, newPath):
        self.path=newPath

class ControlPath:
    def __init__(self, dir=-1):
        self.pathInfo =PathInfo()
        self.sz = map_data.MapData.getMapSize()

    #경로정보 반환
    def getPath(self):
        return self.pathInfo._getPathInfo()

    def createPath(self, start, foundHazardSpot=[]):  # 목표지점에 도달했을 때 해당 지점을 배제하고 경로를 만들어야 한다.
        self.path = []
        self.avoidSpot = map_data.MapData.getHazardSpot() + foundHazardSpot  # 이 지점들은 경로를 만들 때 피해가야 한다.
        objectSpot = map_data.MapData.getObjectSpot() # 아직 로봇이 방문하지 않은 object spot들이 들어있다.
        objNum = len(objectSpot) # 아직 방문하지 않은 object spot의 수
        checkList = [0] * objNum # a* 알고리즘을 통해 경로를 만든 목표지점들을 체크한다.
        chk = objNum # a* 알고리즘을 수행하여 목표지점까지의 경로를 구할 때마다 1씩 뺀다.

        self.path.append(tuple(start))  # start를 tuple형으로 만들어서 경로에 넣는다.

        """
        경로 제작 과정
        
        1. 현재 로봇과 가장 가까이 있고, 아직 발견하지 않은 목표 지점을 찾는다. 이 지점을 첫 번째 도착 지점으로 설정한다.

        2. 현재 로봇이 있는 지점을 출발 지점으로 하여 도착 지점까지의 경로를 a* 알고리즘을 통해 구한다.

        3. 구한 경로를 클래스 변수 path에 넣는다.

        4. 출발 지점을 목표로 삼았던 도착 지점으로 바꾸고, 이 지점에서 가장 가깝고 아직 방문하지 않은 다른 목표 지점을 찾아 그 지점을 도착 지점으로 하여 a* 알고리즘을 수행한다.

        5. 모든 목표지점까지의 경로가 만들어질 때까지 반복

        """
        while chk != 0:
            min = 99999999;  # 최소 거리를 저장하기 위해 사용
            startSpot = self.path[-1]  # 이전 경로의 목표 지점, 즉 현재 경로의 시작 지점이 된다.
            for i in range(objNum):
                if checkList[i] == 1:
                    continue
                distance = abs(startSpot[0] - objectSpot[i][0]) + abs(startSpot[1] - objectSpot[i][1])
                if min > distance:
                    minIdx = i  # minIdx : 최소 거리를 가지는 목표 지점의 인덱스
                    min = distance
            checkList[minIdx] = 1
            destSpot = objectSpot[minIdx]  # 현재 경로의 목표 지점
            self._aStar(startSpot, destSpot)
            chk -= 1
        self.pathInfo._setPath(self.path)

    #경로 출발지점에서 후보 지점까지의 실제 이동 거리를 구하여 리스트 arrayG에 저장한다.
    def _g(self, oldSpot, candidateSpot):
        self.arrayG[candidateSpot[0]][candidateSpot[1]] = self.arrayG[oldSpot[0]][oldSpot[1]] + 1

    #후보 지점에서 목표 지점까지의 대략적인 거리를 구하여 리스트 arrayH에 저장한다.
    def _h(self, candidateSpot, objSpot):
        self.arrayH[candidateSpot[0]][candidateSpot[1]] = abs(candidateSpot[0] - objSpot[0]) + abs(candidateSpot[1] - objSpot[1])

    # 후보 지점의 g값과 h값을 더한다. 이 값이 가장 작은 지점을 다음 경로로 채택한다.
    def _f(self, candidateSpot):
        return self.arrayG[candidateSpot[0]][candidateSpot[1]] + self.arrayH[candidateSpot[0]][candidateSpot[1]]

    def _setParentAndOpenList(self, x, y, mod):
        row = x + mod[0]
        col = y + mod[1]
        if (row, col) in self.openList:
            if self.arrayG[x][y] + 1 < self.arrayG[row][col]:
                self.parent[row][col] = (x, y)

        else:
            self.openList.append((row, col))
            self.parent[row][col] = (x, y)

    def _cal(self, current, end):
        if self.completed == True: return
        if current == end:
            self.completed = True
            return

        if current[0] + 1 <= self.sz[0] and (current[0] + 1, current[1]) not in self.closeList and not self._isHazardSpot(
                current[0] + 1, current[1]):
            self._setParentAndOpenList(current[0], current[1], (1, 0))

        if current[0] - 1 >= 0 and (current[0] - 1, current[1]) not in self.closeList and not self._isHazardSpot(current[0] - 1,
                                                                                                      current[1]):
            self._setParentAndOpenList(current[0], current[1], (-1, 0))

        if current[1] + 1 <= self.sz[1] and (current[0], current[1] + 1) not in self.closeList and not self._isHazardSpot(current[0],
                                                                                                               current[
                                                                                                                   1] + 1):
            self._setParentAndOpenList(current[0], current[1], (0, 1))

        if current[1] - 1 >= 0 and (current[0], current[1] - 1) not in self.closeList and not self._isHazardSpot(current[0],
                                                                                                      current[1] - 1):
            self._setParentAndOpenList(current[0], current[1], (0, -1))

        que = PriorityQueue()
        min = 99999999
        for point in self.openList:
            self._g(current, point)
            self._h(point, end)
            que.put((self._f(point), point))

        nextPoint = que.get()[1]
        self.openList.remove(nextPoint)
        self.closeList.append(nextPoint)
        self._cal(nextPoint, end)

    def _isHazardSpot(self, x, y):
        if (x, y) in self.avoidSpot:
            return True
        return False

    def _aStar(self, start, end):  # a* 알고리즘
        self.completed = False
        self.arrayF = np.zeros((self.sz[0] + 1, self.sz[1] + 1))
        self.arrayG = np.zeros((self.sz[0] + 1, self.sz[1] + 1))
        self.arrayH = np.zeros((self.sz[0] + 1, self.sz[1] + 1))
        self.parent = [[-1] * (self.sz[1] + 1) for i in range(self.sz[0] + 1)]
        self.openList = []
        self.closeList = [start]
        self._cal(start, end)

        tmp = end
        pathList = []

        while tmp != tuple(start):
            pathList.append(tmp)
            tmp = self.parent[tmp[0]][tmp[1]]
        pathList.reverse()
        self.path += pathList

class ControlRobot:
    def __init__(self, dir, pathController):
        self.pathCtrl=pathController
        self.robot=SIM(dir)
        self.path=[] # ControlPath에서 만든 path 정보를 저장할 리스트
        self.sz=map_data.MapData.getMapSize()
        self.pathNum = 0  # 현재 로봇이 self.path 리스트 상의 몇 번째 좌표에 있는지를 기록한다. 로봇이 맞는 방향으로 서있는지 확인할 때 사용
        self.pointToDirection={(0, 1) : 0, (1, 0) : 1, (0, -1) : 2, (-1, 0) : 3} # 현재 지점과 다음 지점의 좌표 차이를 보고 로봇이 어느 방향을 봐야하는지 확인한다.

    def turnCW(self): # 로봇을 시계 방향으로 90도 돌린다.
        self.robot.turnCW()

    def getSensorInfo(self): #로봇의 color blob sensor, hazard sensor값을 받아오고 그것들을 묶어서 리턴한다.
        cbList=[]
        hPoint=(-1, -1)
        cbDirection = self.robot.colorBlobSensor()
        curPosition, curDirection= self.robot.positioningSensor()
        if len(cbDirection) != 0:  # 현재 위치 근처에 hidden color blob spot이 존재한다. 리턴값을 보고 hidden color blob spot의 좌표를 계산해서 리스트에 저장한다.
            for dir in cbDirection:
                cbList.append((curPosition[0]+moveDirection[dir][0], curPosition[1]+moveDirection[dir][1]))
                
        isHazard=False
        if self.checkDirection()==True : # 만약 로봇이 경로상의 다음 지점을 향하고 있다면 로봇의 hazard sensor 값을 받아온다.
            isHazard=self.robot.hazardSensor()
        if isHazard == True: # 현재 로봇이 보고있는 방향 바로 앞에 hidden hazard spot이 존재한다.
            hPoint=(curPosition[0]+moveDirection[curDirection][0], curPosition[1]+moveDirection[curDirection][1])
            
        return cbList, hPoint

    def checkDirection(self): # 현재 로봇이 다음 가야할 곳을 향하고 있는지 확인한다.
                              # 방향이 맞지 않으면 turnCW() 메소드를 통해서 로봇의 방향을 바꿔준다.
        _, curDirection=self.robot.positioningSensor()
        tmp=self.pathCtrl.getPath() # 방향을 확인하기 위해 경로 정보를 받아온다.
        if self.path!=tmp: #경로가 바뀌었을 경우
            self.pathNum=0 #pathNum 값을 초기화한다.
            self.path=tmp #경로 정보를 새 경로로 바꿔준다.

        pointSum = (self.path[self.pathNum+1][0] - self.path[self.pathNum][0],
                    self.path[self.pathNum+1][1] - self.path[self.pathNum][1])

        if self.pointToDirection[pointSum] != curDirection:
            return False
        return True
        
    def commandMovement(self):
        curPosition, curDirection=self.robot.positioningSensor()
        if self.checkDirection()==False:
            self.robot.turnCW()

        else:
            self.robot.moveForward()
        return self.robot.positioningSensor()

    def incPathNum(self):
        self.pathNum += 1

    def getFoundHazardSpot(self):
        return self.robot.getFoundHazardSpot()
