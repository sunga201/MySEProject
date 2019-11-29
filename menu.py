import robot_and_control
import map_data
import sys
import random
import copy
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

#Use to determine behavior after press 'OK' button on message box.
CLOSE=1
NOT_CLOSE=0

class MessageController: #static class
    def showMessage(object, head, message, toggle): #static method, show message to operator.
        msg = QMessageBox.question(object, head, message, QMessageBox.Ok)
        if toggle: object.close()

class SaveData(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Save data")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.move(500, 200)  # horizontal, vertical
        self.resize(500, 500)  # width, height
        
        mapLabel = QLabel("Map : ")
        startLabel = QLabel("Start : ")
        spotLabel = QLabel("Object : ")
        hazardLabel = QLabel("Hazard : ")
        self.mapLine = QLineEdit("")
        self.startLine = QLineEdit("")
        self.spotLine = QLineEdit("")
        self.hazardLine = QLineEdit("")

        saveButton = QPushButton('Save', self)
        saveButton.clicked.connect(self.saveInputData)
        cancelButton = QPushButton('cancel', self)
        cancelButton.clicked.connect(self.close)

        layout1 = QGridLayout()
        layout1.addWidget(mapLabel, 0, 0)
        layout1.addWidget(self.mapLine, 0, 1)
        layout1.addWidget(startLabel, 1, 0)
        layout1.addWidget(self.startLine, 1, 1)
        layout1.addWidget(spotLabel, 2, 0)
        layout1.addWidget(self.spotLine, 2, 1)
        layout1.addWidget(hazardLabel, 3, 0)
        layout1.addWidget(self.hazardLine, 3, 1)
        layout1.addWidget(saveButton, 4, 0)
        layout1.addWidget(cancelButton, 4, 1)

        self.setLayout(layout1)
        self.show()

    def saveInputData(self):
        mapSize=self.mapLine.text()
        start=self.startLine.text()
        spot=self.spotLine.text()
        hazard=self.hazardLine.text()

        if mapSize=='' or start=='' or spot=='' or hazard=='':
            MessageController.showMessage(self, 'error', 'Please check map data again.', NOT_CLOSE)
            return
        try:
            mapSize=mapSize.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            start = start.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            spot = spot.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            hazard = hazard.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
        except:
            MessageController.showMessage(self, 'error', 'Please check map data again.', NOT_CLOSE)
            return

        mapSize=tuple(map(int, mapSize))
        start=tuple(map(int, start))
        spot=list(map(int, spot))
        hazard=list(map(int, hazard))
        objectSpot=[]
        for i in range(0, len(spot), 2):
            objectSpot.append(tuple(spot[i:i+2]))

        hazardSpot=[]
        for i in range(0, len(hazard), 2):
            hazardSpot.append(tuple(hazard[i:i+2]))
        map_data.MapData(mapSize, start, objectSpot, hazardSpot)
        MessageController.showMessage(self, 'notice', 'Save Completed.', CLOSE)
    
class ShowMapData(QWidget):
    def __init__(self):
        super().__init__()
        self.mapSize=map_data.MapData.getMapSize()
        self.startSpot=map_data.MapData.getStartSpot()
        self.objectSpot=map_data.MapData.getObjectSpot()
        self.hazardSpot=map_data.MapData.getHazardSpot()

        self.setWindowTitle("Show map data")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.move(500, 200)  # horizontal, vertical
        self.resize(500, 500)  # width, height

        subLayout=QGridLayout()

        mapSizeLabel=QLabel('Map size : ')
        mapSizeText=QLineEdit(str(self.mapSize))
        mapSizeText.setReadOnly(True)
        mapSizeText.setStyleSheet('background:rgb(176, 191, 197)') # qLineEdit 색 변경. 참조 사이트 : http://blog.naver.com/PostView.nhn?blogId=bringblingme&logNo=221544905595&redirect=Dlog&widgetTypeCall=true&directAccess=false

        startSpotLabel=QLabel('start spot : ')
        startSpotText=QLineEdit(str(self.startSpot))
        startSpotText.setReadOnly(True)
        startSpotText.setStyleSheet('background:rgb(176, 191, 197)')

        objectSpotLabel=QLabel('object spot : ')
        objectSpotText=QLineEdit(str(self.objectSpot))
        objectSpotText.setReadOnly(True)
        objectSpotText.setStyleSheet('background:rgb(176, 191, 197)')

        hazardSpotLabel=QLabel('hazard spot : ')
        hazardSpotText=QLineEdit(str(self.hazardSpot))
        hazardSpotText.setReadOnly(True)
        hazardSpotText.setStyleSheet('background:rgb(176, 191, 197)')

        subLayout.addWidget(mapSizeLabel, 0, 0)
        subLayout.addWidget(mapSizeText, 0, 1)
        subLayout.addWidget(startSpotLabel, 1, 0)
        subLayout.addWidget(startSpotText, 1, 1)
        subLayout.addWidget(objectSpotLabel, 2, 0)
        subLayout.addWidget(objectSpotText, 2, 1)
        subLayout.addWidget(hazardSpotLabel, 3, 0)
        subLayout.addWidget(hazardSpotText, 3, 1)

        groupbox=QGroupBox('information')
        groupbox.setStyleSheet('QGroupBox:title {'
                 'subcontrol-origin: margin;'
                 'subcontrol-position: top center;'
                 'padding-left: 10px;'
                 'padding-right: 10px;'
                 'font-size: 16pt;}')
        groupbox.setLayout(subLayout)

        mainLayout=QVBoxLayout()
        mainLayout.addWidget(groupbox)
        self.setLayout(mainLayout)
        self.show()

class ShowResult(QWidget):
    def __init__(self):
        super().__init__()
        self.init()
        np.random.seed(int(time.time()))
        self.generateRandomSpot()
        self.showMap()

    def init(self): # 메뉴로 돌아갔다가 다시 show result를 누를 때 정보를 초기화하기 위해 사용
        self.mapSize = map_data.MapData.getMapSize()
        self.curPosition = copy.deepcopy(map_data.MapData.getStartSpot())
        self.hazardSpot = map_data.MapData.getHazardSpot()
        self.originalObjectSpot = copy.deepcopy(map_data.MapData.getObjectSpot())
        self.objectSpot = map_data.MapData.getObjectSpot()
        self.objCnt=len(self.objectSpot)
        self.drawedLines = []
        self.enlarge = False  # 맵의 가로, 세로 길이가 모두 10을 넘으면 맵을 확대해서 보여준다.

    def showMap(self):
        self.arrowDirection=[(0, 0.7), (0.4, 0), (0, -0.7), (-0.4, 0)]
        self.curDirection=-1
        self.arrowFileName=['up.png', 'right.png', 'down.png', 'left.png']

        self.ctrlPath = robot_and_control.ControlPath()  # 경로를 컨트롤하는 클래스 ControlPath의 인스턴스 생성
        self.ctrlPath.createPath(self.curPosition)  # 경로 생성
        self.path = self.ctrlPath.getPath()  # 생성한 경로 불러오기

        initialDirection=self.path[1][0]-self.path[0][0], self.path[1][1]-self.path[0][1] # 0 : up 1 : right 2 : down 3 : left
        if initialDirection[0]==0:
            if initialDirection[1]>0:
                self.curDirection=0
            else: self.curDirection=2
        else:
            if initialDirection[0]>0:
                self.curDirection=1
            else: self.curDirection=3

        assert(self.curDirection!=-1) #로봇의 방향이 제대로 배정되었는지 확인

        self.ctrlRobot = robot_and_control.ControlRobot(self.curDirection) #로봇을 컨트롤하는 클래스 ControlRobot의 인스턴스 생성
        self.setWindowTitle("Result")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.resize(1900, 1000)  # width, height
        self.fig=plt.figure()
        self.canvas=FigureCanvas(self.fig)
        self.mapScreen = self.fig.add_subplot(1, 1, 1)
        self.mapScreen.grid()
        self.robotImage=None
        self.arrowImage=None
        self.drawRobot(self.curPosition)
        self.objectSpotInstance=[] # Object spot을 그릴 때 나오는 리턴값을 저장한다. 방문한 objec spot을 맵 상에서 지울 때 사용

        for hazardSpot in self.hazardSpot:
            self.imageScatter(hazardSpot[0], hazardSpot[1], 'skull.png', zoom=0.1, ax=self.mapScreen)

        for objSpot in self.objectSpot:
            self.objectSpotInstance.append((objSpot, self.imageScatter(objSpot[0], objSpot[1], 'star.png', zoom=0.1, ax=self.mapScreen)))

        if self.mapSize[0]>10 and self.mapSize[1]>10:
            self.enlarge=True

        if self.enlarge: # 맵 가로, 세로 길이 둘 다 10 초과
            print('check!')
            plt.xlim(-3+self.curPosition[0], 4+self.curPosition[0])
            plt.xticks(np.arange(-3+self.curPosition[0], 4+self.curPosition[0], step=1))
        else:
            plt.xlim(-1, self.mapSize[0]+1)
            plt.xticks(np.arange(-1, self.mapSize[0]+1, step=1))

        if self.enlarge: # 맵 가로, 세로 길이 둘 다 10 초과
            plt.ylim(-3 + self.curPosition[1], 4 + self.curPosition[1])
            plt.yticks(np.arange(-3 + self.curPosition[1], 4 + self.curPosition[1], step=1))
        else:
            plt.ylim(-1, self.mapSize[1]+1)
            plt.yticks(np.arange(-1, self.mapSize[1]+1, step=1))

        #맵의 외곽선을 그린다.
        self.drawBorder()
        
        leftLayout=QVBoxLayout()
        leftLayout.addWidget(self.canvas)

        rightSubLayout=QVBoxLayout()
        currentPosLabel=QLabel('로봇 좌표')
        self.currentPosText=QLineEdit(str(self.curPosition))
        self.currentPosText.setReadOnly(True)
        self.currentPosText.setStyleSheet('background:rgb(176, 191, 197)')

        RobotMovementLabel=QLabel('로봇 동작')
        self.RobotMovementText=QLineEdit()
        self.RobotMovementText.setReadOnly(True)
        self.RobotMovementText.setStyleSheet('background:rgb(176, 191, 197)')

        remainObjectLabel=QLabel('남아있는 목표 지점 갯수')
        self.remainObjectText=QLineEdit(str(self.objCnt))
        self.remainObjectText.setReadOnly(True)
        self.remainObjectText.setStyleSheet('background:rgb(176, 191, 197)')

        rightSubLayout.addWidget(currentPosLabel)
        rightSubLayout.addWidget(self.currentPosText)
        rightSubLayout.addStretch(5)

        rightSubLayout.addWidget(RobotMovementLabel)
        rightSubLayout.addWidget(self.RobotMovementText)
        rightSubLayout.addStretch(5)

        rightSubLayout.addWidget(remainObjectLabel)
        rightSubLayout.addWidget(self.remainObjectText)
        rightSubLayout.addStretch(5)

        groupbox=QGroupBox('information')
        groupbox.setLayout(rightSubLayout)

        rightLayout=QVBoxLayout()
        rightLayout.addStretch(3)
        rightLayout.addWidget(groupbox)

        rightLayout.addStretch(3)

        startButton = QPushButton('start', self)
        startButton.clicked.connect(self.showRobotMovement)
        returnButton = QPushButton('return to menu', self)
        returnButton.clicked.connect(self.close)

        topLayout=QHBoxLayout()
        topLayout.addLayout(leftLayout, 4)
        topLayout.addLayout(rightLayout, 1)

        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(startButton)
        bottomLayout.addWidget(returnButton)

        mainLayout=QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(bottomLayout)
        self.setLayout(mainLayout)
        self.show()
        self.drawPath()

    def drawBorder(self): #맵의 경계를 그린다.
        plt.plot([self.mapSize[1]] * (self.mapSize[0] + 1), 'k', lineWidth=5)  # 위
        plt.plot([0] * (self.mapSize[0] + 1), 'k', lineWidth=5)  # 아래
        plt.plot([0] * (self.mapSize[1] + 1), range(self.mapSize[1] + 1), 'k', lineWidth=5)  # 왼쪽
        plt.plot([self.mapSize[0]] * (self.mapSize[1] + 1), range(self.mapSize[1] + 1), 'k', lineWidth=5)  # 오른쪽

    def imageScatter(self, x, y, image, zoom=1, ax=None):
        if ax is None:
            ax = plt.gca()
        try:
            image = plt.imread(image)
        except TypeError:
            return
        im = OffsetImage(image, zoom=zoom)
        artist = AnnotationBbox(im, (x, y), frameon=False)
        return ax.add_artist(artist)

    def changePath(self):
        print('create start!')
        start1=time.time()
        self.ctrlPath.createPath(self.curPosition)
        print('create end! time : ', time.time()-start1)
        self.path=self.ctrlPath.getPath()
        print('draw start!')
        start2 = time.time()
        self.drawPath()
        print('draw end! time : ', time.time()-start2)

    def showRobotMovement(self):
        while self.objCnt!=0:
            hazardFound=False
            hiddenCbList, hiddenHSpot=self.ctrlRobot.getSensorInfo()

            '''인근 지역에 숨겨진 color spot을 맵에 표시한다.'''
            if len(hiddenCbList)!=0: #현재 위치 근처에 hidden cb가 존재한다.
                for pos in hiddenCbList: #리스트에는 color blob의 좌표가 들어있다.
                    self.imageScatter(pos[0], pos[1], 'splash.png', zoom=0.5, ax=self.mapScreen)
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()

            '''로봇이 보고있는 방향 바로 앞에 숨겨진 hazard spot을 맵에 표시한다.'''
            if self.ctrlRobot.checkDirection() and hiddenHSpot[0]!=-1:
                MessageController.showMessage(self, 'notice', 'Robot found Hazard spot!', NOT_CLOSE)
                self.imageScatter(hiddenHSpot[0], hiddenHSpot[1], 'skull.png', zoom=0.1, ax=self.mapScreen)
                self.changePath()
                hazardFound=True
                map_data.MapData.removeHiddenSpot(hiddenHSpot)
                continue

            self.commandMovementAndChangePosInfo(hazardFound)
            if tuple(self.curPosition) in self.objectSpot:
                for spot, objectImageInstance in self.objectSpotInstance:
                    if spot==tuple(self.curPosition):
                        objectImageInstance.remove()
                        self.fig.canvas.draw()
                        self.fig.canvas.flush_events()
                self.objectSpot.remove(tuple(self.curPosition)) # 방문한 object spot을 MapData의 objectSpot 리스트에서 뺀다.
                self.objCnt-=1
                self.remainObjectText.setText(str(self.objCnt))

        MessageController.showMessage(self, 'notice', 'robot found all object spot!', NOT_CLOSE)
        map_data.MapData.getBackObjectSpot(self.originalObjectSpot)  # objectSpot 리스트를 처음 입력했던 상태로 돌려놓는다.
        robot_and_control.PathInfo.delInstance()
        robot_and_control.SIM.delInstance()

    #commandMovementAndChangePosInfo() : 로봇의 움직임을 지시하고 움직임이 끝난 뒤 현재 로봇의 위치 정보, 방향 정보를 받아 curPosition, curDirection을 수정한다.
    #                                    기존에 맵에 있던 로봇을 지우고 움직인 위치에 로봇을 다시 그린다.
    
    def commandMovementAndChangePosInfo(self, hazardFound):
        beforePosition=(self.curPosition[0], self.curPosition[1])
        changedPosition, changedDirection = self.ctrlRobot.commandMovement()
        isTwoStep=False
        if changedDirection!=self.curDirection :
            print('dir check!!!!!')
            self.RobotMovementText.setText('회전')
            
        if changedDirection==self.curDirection and abs(beforePosition[0]-changedPosition[0]+beforePosition[1]-changedPosition[1])==0:
            self.RobotMovementText.setText('정지')
        self.curPosition = changedPosition
        self.curDirection = changedDirection
        self.currentPosText.setText(str(self.curPosition))
        print('before : ', beforePosition, ', cur : ', self.curPosition, 'dis : ', abs(beforePosition[0]-self.curPosition[0]+beforePosition[1]-self.curPosition[1]))

        if abs(beforePosition[0]-self.curPosition[0]+beforePosition[1]-self.curPosition[1])==1:
            print('one step!!!')
            self.ctrlRobot.upPathNum()
            self.RobotMovementText.setText('앞으로 한 칸 이동')
            
        elif abs(beforePosition[0]-self.curPosition[0]+beforePosition[1]-self.curPosition[1])==2:
            isTwoStep=True
            self.RobotMovementText.setText('앞으로 두 칸 이동')

        isChangePath=hazardFound+isTwoStep
        self.drawRobot(self.curPosition, changePath=isChangePath)
        

    def drawRobot(self, test, changePath=False): # changePath
        moveDirection = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        if test==self.curPosition: #처음 시작할 때
            x = test[0] - self.curPosition[0]
            y = test[1] - self.curPosition[1]

        else: #이외의 경우
            x=test[0][0]-self.curPosition[0]
            y=test[0][1]-self.curPosition[1]

        if self.robotImage:
            self.robotImage.remove()
            self.arrowImage.remove()

        self.robotImage = self.imageScatter(self.curPosition[0] + x, self.curPosition[1] + y, 'robot.png', zoom=0.3,
                                            ax=self.mapScreen)
        self.arrowImage = self.imageScatter(self.curPosition[0] + x + self.arrowDirection[self.curDirection][0],
                                            self.curPosition[1] + y + self.arrowDirection[self.curDirection][1], self.arrowFileName[self.curDirection],
                                            zoom=0.6, ax=self.mapScreen)

        if self.enlarge:# 맵 가로, 세로 길이 둘 다 10 초과
            plt.xlim(-3+self.curPosition[0], 4+self.curPosition[0])
            plt.xticks(np.arange(-3+self.curPosition[0], 4+self.curPosition[0], step=1))

            plt.ylim(-3 + self.curPosition[1], 4 + self.curPosition[1])
            plt.yticks(np.arange(-3 + self.curPosition[1], 4 + self.curPosition[1], step=1))
        if not changePath or self.mapSize[0]+self.mapSize[1]<300 : time.sleep(0.7) # 0.7초 간격으로 로봇의 움직임 표현.
                                                                                   # 맵의 가로, 세로 합이 300 이상이고 경로를 다시 그렸을 때는
                                                                                   # 경로를 다시 그리는게 오래 걸리므로 딜레이를 없앤다.
        if changePath:
            self.changePath()


        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def generateRandomSpot(self):
        visibleHazardSpot=map_data.MapData.getHazardSpot() # 맵 상에 보이는 위험 지역 좌표
        objectSpot=map_data.MapData.getObjectSpot() # 목표 지역 좌표
        startSpot=map_data.MapData.getStartSpot() #시작 지역 좌표
        hazardNum=np.random.randint(0, min((self.mapSize[0]+self.mapSize[1])/2, 100)) #보이지 않는 위험 지역의 수를 0 ~ (맵의 가로 길이 + 세로 길이) (최대 100) 사이의 수로 정한다.
        cbNum=np.random.randint(0, min((self.mapSize[0]+self.mapSize[1])/2, 100)) #color blob spot의 수를 0 ~ (맵의 가로 길이 + 세로 길이) (최대 100) 사이의 수로 정한다.
        mapWidth = self.mapSize[0]
        mapHeight = self.mapSize[1]
        tmpHazard=[]
        tmpCb=[]

        usedSpot = visibleHazardSpot+objectSpot # 이 지역은 hidden hazard spot이나 color blob spot을 만들 수 없다.
        usedSpot.append(startSpot)

        usableSpot=[]
        for i in range(mapWidth+1):
            for j in range(mapHeight+1):
                usableSpot.append((i, j)) # 맵 상의 모든 좌표를 usableSpot 리스트에 넣는다.

        print('used spot : ', usedSpot)
        for point in usedSpot:
            usableSpot.remove(point)
        hiddenCbSpot=random.sample(usableSpot, cbNum) # usableSpot 리스트 내부에서 위에서 정한 갯수민큼 color blob spot을 뽑고, 그 지역을 usableSpot 리스트에서 삭제한다.
        for cbSpot in hiddenCbSpot:
            usableSpot.remove(cbSpot)

        hiddenHazardSpot=random.sample(usableSpot, hazardNum) # hidden hazard spot도 뽑는다.
        for hazardSpot in hiddenHazardSpot:
            usableSpot.remove(hazardSpot)

        totalHazardSpot=hiddenHazardSpot+visibleHazardSpot
        totalHazardSpot=list(set(totalHazardSpot))
        for obj in objectSpot:
            x=obj[0]
            y=obj[1]
            hsNum=4 # 위험 지역이 목표 지역을 감쌀 수 있는 최대 갯수를 지정한다. 맵의 모서리에서는 3개, 꼭짓점에서는 2개
            checkSpot=[(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
            tobeRemovedSpot=(x, y-1)
            if (x==0 and y==0) or (x==0 and y==mapHeight) or (x==mapWidth and y==0) or (x==mapWidth and y==mapHeight):
                if x==0 and y==0:
                    checkSpot=[(x+1, y), (x, y+1)]

                elif x==0 and y==mapHeight:
                    checkSpot=[(x+1, y), (x, y-1)]

                elif x == mapWidth and y == 0:
                    checkSpot = [(x-1, y), (x, y+1)]

                else:
                    checkSpot = [(x - 1, y), (x, y - 1)]

                # 목표 지역을 둘러싸고 있는 위험 지점들 중 목표 지점에 도달하지 못하도록 배치되었을 때 지워질 후보 점을 뽑는다.
                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum=2

            elif x==0 or x==mapWidth:
                if x==0:
                    checkSpot=[(x+1, y), (x, y-1), (x, y+1)]

                else:
                    checkSpot=[(x-1, y), (x, y-1), (x, y+1)]

                # 목표 지역을 둘러싸고 있는 위험 지점들 중 목표 지점에 도달하지 못하도록 배치되었을 때 지워질 후보 점을 뽑는다.
                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum=3

            elif y==0 or y==mapHeight:
                if y==0:
                    checkSpot = [(x, y+1), (x-1, y), (x+1, y)]

                else:
                    checkSpot = [(x, y - 1), (x - 1, y), (x + 1, y)]

                # 목표 지역을 둘러싸고 있는 위험 지점들 중 목표 지점에 도달하지 못하도록 배치되었을 때 지워질 후보 점을 뽑는다.
                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum=3

            if (len(totalHazardSpot)-len([item for item in totalHazardSpot if item not in checkSpot]))==hsNum:
                hiddenHazardSpot.remove(tobeRemovedSpot)
                
        # 무작위로 생성한 color blob spot과 hidden hazard spot이 겹치지는 않는지 확인한다.
        assert len([item for item in hiddenHazardSpot if item in hiddenCbSpot])==0
        map_data.MapData.setHiddenData(hiddenHazardSpot, hiddenCbSpot)

    def drawPath(self):
        if len(self.drawedLines)!=0:
            self.removePath()
        print('len : ', len(self.path))
        print('change path : ', self.path)
        dist=(0, 0)
        i=1
        while True:
            print('i : ', i)
            if i==len(self.path) : break
            prev=self.path[i-1]
            next=self.path[i]
            dist = (next[0]-prev[0], next[1]-prev[1])
            print('dist : ', dist)
            while i<len(self.path)-1 and dist==(self.path[i+1][0]-self.path[i][0], self.path[i+1][1]-self.path[i][1]):
                i+=1
                next = self.path[i]

            x=next[0]-prev[0]
            y=next[1]-prev[1]
            print('prev : ', prev, 'next : ', next)
            print('x : ', x, ' y : ', y)
            if(x==0) :
                if(prev[1]<next[1]) :
                    lines=self.mapScreen.plot([prev[0]]*(y+1), np.linspace(prev[1], next[1], y+1), 'r', linewidth=5)
                else :
                    lines=self.mapScreen.plot([prev[0]]*(-(y-1)), np.linspace(next[1], prev[1], -(y-1)), 'r', linewidth=5)
            else :
                if (prev[0] < next[0]):
                    lines=self.mapScreen.plot(np.linspace(prev[0], next[0], x + 1), [prev[1]] * (x + 1), 'r',
                             linewidth=5)

                else:
                    lines=self.mapScreen.plot(np.linspace(next[0], prev[0], -(x - 1)), [self.path[i][1]] * -(x - 1), 'r',
                             linewidth=5)
            self.drawedLines+=lines #Memorize current path plot object.
            prev=self.path[i]
            i+=1

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def removePath(self):
        for i in range(0, len(self.mapScreen.lines)):
            self.mapScreen.lines[0].remove()
        self.drawBorder()
    
class ShowMenu(QWidget):
    def __init__(self):
        super().__init__()
        map_data.MapData()  # temp
        self.setWindowTitle("ADD-ON System")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.move(500, 200)  # horizontal, vertical
        self.resize(500, 500)  # width, height

        titleLabel = QLabel('------ADD-ON System------')
        titleLabel.setAlignment(Qt.AlignCenter)
        font = titleLabel.font()
        font.setPointSize(15)
        titleLabel.setFont(font)

        saveButton = QPushButton('Save data', self)
        saveButton.clicked.connect(self.saveData)

        showResultButton = QPushButton('Show result', self)
        showResultButton.clicked.connect(self.showResult)
        showDataButton = QPushButton('Show map data', self)
        showDataButton.clicked.connect(self.showMapData)

        quitButton = QPushButton('Quit', self)
        quitButton.clicked.connect(QCoreApplication.instance().quit)

        buttonList = [saveButton, showResultButton, showDataButton, quitButton]
        for bt in buttonList:
            bt.setMinimumHeight(70)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(titleLabel)

        mainLayout.addWidget(saveButton)
        mainLayout.addStretch(3)
        mainLayout.addWidget(showResultButton)
        mainLayout.addStretch(3)
        mainLayout.addWidget(showDataButton)
        mainLayout.addStretch(3)
        mainLayout.addWidget(quitButton)
        mainLayout.addStretch(3)
        self.setLayout(mainLayout)
        self.show()

    def saveData(self):
        print('in')
        self.sd=SaveData()

    def showMapData(self):
        try:
            testAtt=map_data.MapData.getMapSize() #저장된 맵 데이터가 있는지 확인한다.
        except AttributeError:
            MessageController.showMessage(self, 'error', 'map data doesn\'t exist.', NOT_CLOSE)
            return

        self.smd=ShowMapData()

    def showResult(self):
        try:
            testAtt=map_data.MapData.getMapSize() #저장된 맵 데이터가 있는지 확인한다.
        except AttributeError:
            MessageController.showMessage(self, 'error', 'map data doesn\'t exist.', NOT_CLOSE)
            return

        self.sr=ShowResult()