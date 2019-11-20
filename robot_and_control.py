import map_data
import numpy as np
from queue import PriorityQueue

class SIM:
    def __init__(self):
        self.direction=0
        #self.position=map_data.MapData.getStartSpot()
        self.position=[1, 2] #temp
        self.moveDirection = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def moveForward(self):
        print(self.position)
        malFunctionProp=np.random.rand()
        print(malFunctionProp)
        if malFunctionProp>0.7:
            if malFunctionProp>0.85:
                self.position += 2*np.array(self.moveDirection[self.direction])
            else:
                pass
        else:
            self.position+=np.array(self.moveDirection[self.direction])
        self.position=list(self.position)
        print(self.position)

    def turnCw(self):
        self.direction=self.direction%4

    def positioningSensor(self):
        return self.position, self.direction

    def colorBlobSensor(self):
        #cbList=map_data.MapData.getCbH()
        cbList=[(4, 4), (2, 3)]
        checkSpot=[self.position]*4 + np.array(self.moveDirection)


class ControlRobot:
    def __init__(self):
        self.path=[]
        self.foundHazardSpot=[]
        self.sz=map_data.MapData.getMapSize()

    def getPath(self):
        return self.path

    def createPath(self, start): # 목표지점에 도달했을 때 해당 지점을 배제하고 경로를 만들어야 한다.
        self.avoidSpot=map_data.MapData.getHazardSpot()+self.foundHazardSpot #these spots are excluded when system makes path.
        objectSpot=map_data.MapData.getObjectSpot()
        objNum=len(objectSpot)
        checkList=[0]*objNum
        chk=objNum

        self.path.append(start)
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

    def g(self, oldSpot, newSpot):
        self.arrayG[newSpot[0]][newSpot[1]]=self.arrayG[oldSpot[0]][oldSpot[1]]+1

    def h(self, spot, obj):
        self.arrayH[spot[0]][spot[1]]=abs(spot[0]-obj[0])+abs(spot[1]-obj[1])

    def f(self, spot):
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
            self.g(start, point)
            self.h(point, end)
            que.put((self.f(point), point))

        nextPoint=que.get()[1]
        self.openList.remove(nextPoint)
        self.closeList.append(nextPoint)
        self.cal(nextPoint, end)

    def isHazard(self, x, y):
        hList=map_data.MapData.getHazardSpot()
        if (x, y) in hList:
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
        while tmp!=start:
            pathList.append(tmp)
            tmp=self.parent[tmp[0]][tmp[1]]
        pathList.reverse()
        self.path+=pathList