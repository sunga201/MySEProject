import map_data
import numpy as np
import time
from abc import *
from queue import PriorityQueue

moveDirection = [(0, 1), (1, 0), (0, -1), (-1, 0)]

class SIM:
    sim=None

    def __init__(self, dir):
        self.direction=dir # 0 : up 1 : right 2 : down 3 : left
        self.position=map_data.MapData.getStartSpot()
        self.foundHazardSpot=[]

    def getInstance(dir):
        if SIM.sim==None:
            SIM.sim=SIM(dir)
        if SIM.sim.direction==-1:
            SIM.sim.direction=dir
        return SIM.sim

    def delInstance():
        SIM.sim=None

    def moveForward(self):
        inPlaceProp=0.8
        twoStepProp=0.9
        if self.hazardSensor : inPlaceProp=1 #바로 앞에 위험 지역이 있을 경우에는 오작동 배제

        bugProp=np.random.rand()
        if bugProp>inPlaceProp:
            if bugProp>twoStepProp:
                print('two step !!!')
                self.position += 2*np.array(moveDirection[self.direction])

            print('no move!!!')
        else:
            self.position+=np.array(moveDirection[self.direction])

        self.position=list(self.position)
        if inPlaceProp==1: inPlaceProp=0.8

    def turnCW(self):
        self.direction=(self.direction+1)%4

    def positioningSensor(self):
        return self.position, self.direction

    def colorBlobSensor(self):
        hiddenCB=map_data.MapData.getCbH()
        checkSpot=[self.position]*4 + np.array(moveDirection)
        cbList=[]

        for spot in hiddenCB:
            for i in range(0, 4):
                if spot[0] == checkSpot[i][0] and spot[1]==checkSpot[i][1]:
                    cbList.append(i)

        return cbList

    def hazardSensor(self): #위험지역을 발견하고 이를 foundHazardSpot 배열에 추가한다.
        hiddenHazard=map_data.MapData.getHazardH()
        checkSpot=(self.position[0]+moveDirection[self.direction][0], self.position[1]+moveDirection[self.direction][1])
        if checkSpot in hiddenHazard:
            self.foundHazardSpot.append(checkSpot)
            return True
        return False

    def getFoundHazardSpot(self):
        return self.foundHazardSpot;

class PathInfo:
    pathClass=None
    def __init__(self, path):
        self.path=path

    def getInstance(path=[]):
        if PathInfo.pathClass == None: PathInfo.pathClass = PathInfo(path)
        return PathInfo.pathClass

    def delInstance():
        PathInfo.pathClass=None

    def getPathInfo(self):
        return self.path

    def setPath(self, path):
        self.path=path


class ControlRobot:
    def __init__(self, direction):
        self.robot=SIM.getInstance(direction) # 여기서 SIM 클래스 처음 생성함.
        self.pathInfo=PathInfo.getInstance()
        self.path=[] # ControlPath에서 만든 path 정보를 저장할 리스트
        self.sz=map_data.MapData.getMapSize()
        self.pathNum = 0  # 현재 로봇이 self.path 리스트 상의 몇 번째 좌표에 있는지를 기록한다. 로봇이 맞는 방향으로 서있는지 확인할 때 사용
        self.pointToDirection={(0, 1) : 0, (1, 0) : 1, (0, -1) : 2, (-1, 0) : 3} # 현재 지점과 다음 지점의 좌표 차이를 보고 로봇이 어느 방향을 봐야하는지 확인한다.

    def turnCW(self):
        self.robot.turnCW()

    def getSensorInfo(self): #SIM의 color blob sensor, hazard sensor를 실행시키고 그 결과를 묶어서 리턴한다.
        cbList=[]
        hPoint=(-1, -1)
        cbDirection = self.robot.colorBlobSensor()
        curPosition, curDirection= self.robot.positioningSensor()
        if len(cbDirection) != 0:  # 현재 위치 근처에 hidden cb가 존재한다.
            for d in cbDirection:
                cbList.append((curPosition[0]+moveDirection[d][0], curPosition[1]+moveDirection[d][1]))
                
        isHazard=False
        if self.checkDirection()==True :
            isHazard=self.robot.hazardSensor()
        if isHazard == True: # 현재 로봇이 보고있는 방향 바로 앞에 hidden hazard가 존재한다.
            hPoint=(curPosition[0]+moveDirection[curDirection][0], curPosition[1]+moveDirection[curDirection][1])
            
        return cbList, hPoint

    def checkDirection(self): # 현재 로봇이 다음 가야할 곳을 향하고 있는지 확인한다.
        '''경로와 방향이 맞지 않으면 방향을 돌린다.'''
        _, curDirection=self.robot.positioningSensor()
        tmp=self.pathInfo.getPathInfo() # 방향을 확인하기 위해 경로 정보를 받아온다.
        if self.path!=tmp:
            self.pathNum=0
            self.path=tmp

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
            self.pathNum+=1
            nextPosition=self.robot.positioningSensor()
        return self.robot.positioningSensor()


class ControlPath:
    def __init__(self, dir=-1):
        self.pathInfo=PathInfo.getInstance()
        self.robot=SIM.getInstance(dir)
        self.sz=map_data.MapData.getMapSize()
        
    def getPath(self):
        return self.pathInfo.getPathInfo()

    def createPath(self, start): # 목표지점에 도달했을 때 해당 지점을 배제하고 경로를 만들어야 한다.
        self.path=[]
        self.avoidSpot=map_data.MapData.getHazardSpot()+self.robot.getFoundHazardSpot() #these spots are excluded when system makes path.
        objectSpot=map_data.MapData.getObjectSpot()
        objNum=len(objectSpot)
        checkList=[0]*objNum
        chk=objNum
        
        self.path.append(tuple(start)) # start를 tuple형으로 만들어서 경로에 넣는다.
        distanceList=[]
        while chk!=0:
            min = 99999999;  # 최소 거리를 저장하기 위해 사용
            prevSpot = self.path[-1]  # 이전 경로의 도착점
            for i in range(objNum):
                if checkList[i]==1:
                    continue
                distance=abs(prevSpot[0]-objectSpot[i][0])+abs(prevSpot[1]-objectSpot[i][1])
                if min>distance:
                    minIdx=i # minIdx : 최소 거리를 가지는 목표 점의 인덱스
                    min=distance
            checkList[minIdx]=1
            nextSpot = objectSpot[minIdx]  # 현재 경로의 목표 지점
            self.aStar(prevSpot, nextSpot)
            chk-=1

        self.pathInfo.setPath(self.path)


    def _g(self, oldSpot, newSpot):
        self.arrayG[newSpot[0]][newSpot[1]]=self.arrayG[oldSpot[0]][oldSpot[1]]+1

    def _h(self, spot, obj):
        self.arrayH[spot[0]][spot[1]]=abs(spot[0]-obj[0])+abs(spot[1]-obj[1])

    def _f(self, spot):
        return self.arrayG[spot[0]][spot[1]]+self.arrayH[spot[0]][spot[1]]

    def setParentAndOpenList(self, x, y, mod):
        row=x+mod[0]
        col=y+mod[1]
        if (row, col) in self.openList:
            if self.arrayG[x][y] + 1 < self.arrayG[row][col]:
                self.parent[row][col] = (x, y)

        else:
            self.openList.append((row, col))
            self.parent[row][col] = (x, y)

    def cal(self, start, end):
        if self.completed==True: return
        if start==end:
            self.completed=True
            return

        if start[0] + 1 <= self.sz[0] and (start[0] + 1, start[1]) not in self.closeList and not self.isHazard(start[0] + 1, start[1]):
            self.setParentAndOpenList(start[0], start[1], (1, 0))

        if start[0] - 1 >= 0 and (start[0] - 1, start[1]) not in self.closeList and not self.isHazard(start[0] - 1, start[1]):
            self.setParentAndOpenList(start[0], start[1], (-1, 0))

        if start[1] + 1 <= self.sz[1] and (start[0], start[1] + 1) not in self.closeList and not self.isHazard(start[0], start[1] + 1):
            self.setParentAndOpenList(start[0], start[1], (0, 1))

        if start[1] - 1 >= 0 and (start[0], start[1] - 1) not in self.closeList and not self.isHazard(start[0], start[1] - 1):
            self.setParentAndOpenList(start[0], start[1], (0, -1))

        que=PriorityQueue()
        min=99999999
        for point in self.openList:
            self._g(start, point)
            self._h(point, end)
            que.put((self._f(point), point))

        nextPoint=que.get()[1]
        self.openList.remove(nextPoint)
        self.closeList.append(nextPoint)
        self.cal(nextPoint, end)

    def isHazard(self, x, y):
        if (x, y) in self.avoidSpot:
            return True
        return False

    def aStar(self, start, end): #a* 알고리즘
        self.completed=False
        self.arrayF = np.zeros((self.sz[0]+1, self.sz[1]+1))
        self.arrayG = np.zeros((self.sz[0]+1, self.sz[1]+1))
        self.arrayH = np.zeros((self.sz[0]+1, self.sz[1]+1))
        self.parent=[[-1]*(self.sz[1]+1) for i in range(self.sz[0]+1)]
        self.openList=[]
        self.closeList=[start]
        self.cal(start, end)

        tmp=end
        pathList=[]

        while tmp!=tuple(start):
            pathList.append(tmp)
            tmp=self.parent[tmp[0]][tmp[1]]
        pathList.reverse()
        self.path+=pathList