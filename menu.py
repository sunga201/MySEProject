import robot_and_control
import map_data
import sys
import random
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
    def showMessage(object, message, toggle): #static method, show message to operator.
        msg = QMessageBox.question(object, 'error', message, QMessageBox.Ok)
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

        okButton = QPushButton('Save', self)
        okButton.clicked.connect(self.saveInputData)
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
        layout1.addWidget(okButton, 4, 0)
        layout1.addWidget(cancelButton, 4, 1)

        self.setLayout(layout1)
        self.show()

    def saveInputData(self):
        mapSize=self.mapLine.text()
        start=self.startLine.text()
        spot=self.spotLine.text()
        hazard=self.hazardLine.text()

        if mapSize=='' or start=='' or spot=='' or hazard=='':
            MessageController.showMessage(self, 'Please check map data again.', NOT_CLOSE)
            return
        try:
            mapSize=mapSize.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            start = start.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            spot = spot.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            hazard = hazard.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
        except:
            print("check!!!")
            MessageController.showMessage(self, 'Please check map data again.', NOT_CLOSE)
            return

        mapSize=tuple(map(int, mapSize))
        start=tuple(map(int, start))
        spot=list(map(int, spot))
        hazard=list(map(int, hazard))
        objectSpot=[]
        for i in range(0, len(spot), 2):
            print(i)
            objectSpot.append(tuple(spot[i:i+2]))

        hazardSpot=[]
        for i in range(0, len(hazard), 2):
            hazardSpot.append(tuple(hazard[i:i+2]))
        map_data.MapData(mapSize, start, objectSpot, hazardSpot)
        MessageController.showMessage(self, 'Save Completed.', CLOSE)

class ShowMapData(QWidget):
    def __init__(self):
        super().__init__()
        mapSize=map_data.MapData.getMapSize()
        startSpot=map_data.MapData.getStartSpot()
        objectSpot=map_data.MapData.getObjectSpot()
        hazardSpot=map_data.MapData.getHazardSpot()
        print(mapSize, startSpot, objectSpot, hazardSpot)

        self.setWindowTitle("Show map data")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.move(500, 200)  # horizontal, vertical
        self.resize(500, 500)  # width, height
        self.show()


class ShowResult(QWidget):
    def __init__(self):
        super().__init__()
        np.random.seed(int(time.time()))
        map_data.MapData()  # temp
        self.mapSize=map_data.MapData.getMapSize()
        self.prevPosition=map_data.MapData.getStartSpot()
        self.hazardSpot=map_data.MapData.getHazardSpot()
        self.objectSpot=map_data.MapData.getObjectSpot()
        self.drawedLines = []
        self.generateRandomSpot()
        self.objCnt=len(self.objectSpot)
        self.ControlRobot=robot_and_control.ControlRobot();
        self.showMap()

    def showMap(self):
        #self.path=self.add_on.get_path()
        self.path=[(1, 2), (2, 2), (2, 3), (4, 3), (4, 2), (4, 5), (1, 5)]
        self.arrowDirection=[(0, 0.4), (0.4, 0), (0, -0.4), (-0.4, 0)]
        self.prevDirection=-1
        self.arrowFileName=['up.png', 'right.png', 'down.png', 'left.png']
        checkDirection=self.path[1][0]-self.path[0][0], self.path[1][1]-self.path[0][1]
        if checkDirection[0]==0:
            if checkDirection[1]>0:
                self.prevDirection=0
            else: self.prevDirection=2
        else:
            if checkDirection[0]>0:
                self.prevDirection=1
            else: self.prevDirection=3
        # 0 : up 1 : right 2 : down 3 : left
        self.setWindowTitle("Result")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.resize(1900, 1000)  # width, height
        self.fig=plt.figure()
        self.canvas=FigureCanvas(self.fig)
        self.mapScreen = self.fig.add_subplot(1, 1, 1)
        self.mapScreen.grid()
        self.robotImage=self.imageScatter(self.prevPosition[0], self.prevPosition[1], 'robot.png', zoom=0.3, ax=self.mapScreen)
        self.arrowImage=self.imageScatter(self.prevPosition[0]+self.arrowDirection[self.prevDirection][0], self.prevPosition[1]+self.arrowDirection[self.prevDirection][1],
                                       self.arrowFileName[self.prevDirection], zoom=0.6, ax=self.mapScreen)

        for hazardSpot in self.hazardSpot:
            self.imageScatter(hazardSpot[0], hazardSpot[1], 'skull.png', zoom=0.1, ax=self.mapScreen)

        for objSpot in self.objectSpot:
            self.imageScatter(objSpot[0], objSpot[1], 'star.png', zoom=0.1, ax=self.mapScreen)

        plt.xlim(0, self.mapSize[0]+1)
        plt.xticks(np.arange(0, self.mapSize[0]+1, step=1), color='w')
        plt.ylim(0, self.mapSize[1]+1)
        plt.yticks(np.arange(0, self.mapSize[1]+1, step=1), color='w')

        for o in self.objectSpot:
            plt.scatter(o[0], o[1], c='y')

        self.path = [(1, 2), (2, 2), (2, 3), (4, 3), (4, 2), (4, 5), (3, 5), (3, 4), (1, 4), (1, 5)]
        subLayout1=QVBoxLayout()
        subLayout1.addWidget(self.canvas)

        startButton = QPushButton('start', self)
        startButton.clicked.connect(self.showRobotMovement)
        returnButton = QPushButton('return to menu', self)
        returnButton.clicked.connect(self.close)

        subLayout2 = QHBoxLayout()
        subLayout2.addWidget(startButton)
        subLayout2.addWidget(returnButton)

        mainLayout=QVBoxLayout()
        mainLayout.addLayout(subLayout1)
        mainLayout.addLayout(subLayout2)
        self.setLayout(mainLayout)
        self.show()
        self.drawPath()


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
        self.path = [(1, 2), (2, 2), (2, 3), (4, 3), (4, 2), (4, 5), (1, 5)]
        self.drawPath()

    def showRobotMovement(self):
        while self.objCnt!=0:
            time.sleep(1)
            if self.robotImage:
                self.robotImage.remove()
                self.arrowImage.remove()
            self.robotImage=self.imageScatter(self.prevPosition[0]+1, self.prevPosition[1], 'robot.png', zoom=0.3, ax=self.mapScreen)
            self.arrowImage=self.imageScatter(self.prevPosition[0] + 1+self.arrowDirection[self.prevDirection][0], self.prevPosition[1], self.arrowFileName[self.prevDirection],
                           zoom=0.6, ax=self.mapScreen)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.objCnt=0

    def generateRandomSpot(self):
        visibleHazardSpot=map_data.MapData.getHazardSpot()
        objectSpot=map_data.MapData.getObjectSpot()
        startSpot=map_data.MapData.getStartSpot()
        hazardNum=np.random.randint(0, min((self.mapSize[0]+self.mapSize[1]), 100))
        cbNum=np.random.randint(0, min((self.mapSize[0]+self.mapSize[1]), 100))
        mapWidth = self.mapSize[0]
        mapHeight = self.mapSize[1]
        tmpHazard=[]
        tmpCb=[]

        usedSpot = visibleHazardSpot+objectSpot
        usedSpot.append(startSpot)

        usableSpot=[]
        for i in range(mapWidth+1):
            for j in range(mapHeight+1):
                usableSpot.append((i, j))

        for point in usedSpot:
            usableSpot.remove(point)

        hiddenCbSpot=random.sample(usableSpot, cbNum) #Pick random color blob spot.
        for cbSpot in hiddenCbSpot:
            usableSpot.remove(cbSpot)

        hiddenHazardSpot=random.sample(usableSpot, hazardNum)
        for hazardSpot in hiddenHazardSpot:
            usableSpot.remove(hazardSpot)

        totalHazardSpot=hiddenHazardSpot+visibleHazardSpot
        totalHazardSpot=list(set(totalHazardSpot))
        for obj in objectSpot:
            x=obj[0]
            y=obj[1]
            hsNum=4 #decide maximum number of hazard spot surrounding each object spot.
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

                # pick random hazard spot that surrounds a object spot from hiddenHazardSpot list.
                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum=2

            elif x==0 or x==mapWidth:
                if x==0:
                    checkSpot=[(x+1, y), (x, y-1), (x, y+1)]

                else:
                    checkSpot=[(x-1, y), (x, y-1), (x, y+1)]

                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum=3

            elif y==0 or y==mapHeight:
                if y==0:
                    checkSpot = [(x, y+1), (x-1, y), (x+1, y)]

                else:
                    checkSpot = [(x, y - 1), (x - 1, y), (x + 1, y)]

                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum=3

            if (len(totalHazardSpot)-len([item for item in totalHazardSpot if item not in checkSpot]))==hsNum:
                print('catch!!, to be removed : ', tobeRemovedSpot)
                hiddenHazardSpot.remove(tobeRemovedSpot)

        print('final hidden hazard spot : ', hiddenHazardSpot)
        print('findl cb spot : ', hiddenCbSpot)

        # check if there is an overlapped point between hidden hazard spot and hidden cb spot.
        assert len([item for item in hiddenHazardSpot if item in hiddenCbSpot])==0
        map_data.MapData.setHiddenData(hiddenHazardSpot, hiddenCbSpot)

    def drawPath(self):
        if len(self.drawedLines)!=0:
            self.removePath()

        for i in range(len(self.path)-1):
            x=self.path[i+1][0]-self.path[i][0]
            y=self.path[i+1][1]-self.path[i][1]

            if(x==0) :
                if(self.path[i][1]<self.path[i+1][1]) :
                    lines=self.mapScreen.plot([self.path[i][0]]*(y+1), np.linspace(self.path[i][1], self.path[i+1][1], y+1), 'r', linewidth=5)
                else :
                    lines=self.mapScreen.plot([self.path[i][0]]*(-(y-1)), np.linspace(self.path[i+1][1], self.path[i][1], -(y-1)), 'r', linewidth=5)
            else :
                if (self.path[i][0] < self.path[i + 1][0]):
                    lines=self.mapScreen.plot(np.linspace(self.path[i][0], self.path[i + 1][0], x + 1), [self.path[i][1]] * (x + 1), 'r',
                             linewidth=5)

                else:
                    lines=self.mapScreen.plot(np.linspace(self.path[i+1][0], self.path[i][0], -(x - 1)), [self.path[i][1]] * -(x - 1), 'r',
                             linewidth=5)
            self.drawedLines+=lines #Memorize current path plot object.

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def removePath(self):
        for i in range(len(self.mapScreen.lines)):
            self.mapScreen.lines[0].remove()

class ShowMenu(QWidget):
    def __init__(self):
        super().__init__()
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
        self.sd=SaveData()

    def showMapData(self):
        try:
            testAtt=map_data.MapData.getMapSize()
        except AttributeError:
            MessageController.showMessage(self, 'map data doesn\'t exist.', NOT_CLOSE)
            return

        self.smd=ShowMapData()

    def showResult(self):
        '''try:
            testAtt=MapData.getMapSize()
        except AttributeError:
            MessageController.showMessage(self, 'map data doesn\'t exist.', NOT_CLOSE)
            return'''

        self.sr=ShowResult()
