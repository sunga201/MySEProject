import robot_and_control
import map_data
import sys
import random
import copy
import time
from abc import *
from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QCoreApplication, Qt, QRect, QAbstractAnimation
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

#메시지 박스의 OK 버튼을 눌렀을 때 기존 창을 닫을지, 닫지 않을 지를 정할 때 사용한다.
CLOSE=1
NOT_CLOSE=0

class MessageController: #정적 클래스, 메시지 박스를 관리한다.
    def showMessage(object, head, message, toggle): #정적 메소드, 객체 object에 제목이 head이고 message로 이루어진 메시지 박스를 띄운다.
                                                    # toggle은 메시지 박스를 띄운 창을 닫을지, 닫지 않을 지를 결정함.
        msg = QMessageBox.question(object, head, message, QMessageBox.Ok)
        if toggle: object.close()

class CustomButton(QPushButton): # 버튼에 애니메이션을 추가하기 위한 클래스. QPushButton을 상속받는다.
    def __init__(self):
        super().__init__()

        self.setMinimumSize(150, 70) # 버튼의 최소 사이즈 설정 (가로, 세로)

        self.startColor = QtGui.QColor(220, 220, 220) # 버튼 그라데이션을 위한 첫 번째 색
        self.endColor = QtGui.QColor(255, 255, 255) # 두번째 색
        self._animation = QtCore.QVariantAnimation(self,
            valueChanged=self._customAnimate, # 애니메이션에 사용할 stylesheet 정보를 제공한다.
            startValue=0.00001, # 애니메이션 시작 지점 결정
            endValue=0.9999, # 애니메이션 끝 지점 결정
            duration=250 # 애니메이션 재생 속도를 결정한다.
        )

    def _customAnimate(self, value): #value는 마우스가 버튼을 가리킬 때 startValue에서 endValue까지 점차적으로 증가한다.
                               #마우스가 버튼에서 떨어지면 endValue에서 startValue까지 점차적으로 감소한다.

        #qss : 버튼 글자 모양, 버튼 외곽선의 모양을 결정한다.
        qss = """ 
            font: 75 14pt "Bahnschrift SemiLight\";
            border-style : outset;
            border-width : 1px;
            border-color : rgb(200, 200, 200);
            border-radius: 15px;
        """

        #grad : 버튼의 색을 결정한다.
        grad = "background-color:  qlineargradient(spread:repeat, x1:0, y1:0, x2:1, y2:1, stop:0 {startColor}, stop:{value} {endColor}, stop: 1.0 {startColor});".format(
            startColor=self.startColor.name(), endColor=self.endColor.name(), value=value)
        qss += grad
        self.setStyleSheet(qss)

    def enterEvent(self, event): # 마우스가 버튼을 가리킬 때 재생되는 애니메이션
        self._animation.setDirection(QAbstractAnimation.Forward)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event): # 마우스가 버튼에서 떨어질 때 재생되는 애니메이션
        self._animation.setDirection(QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)

class WindowDesign(QWidget): # 새 창을 띄우는 클래스들은 전부 이 클래스를 상속받아서 사용한다.
    def __init__(self):
        super().__init__()

    def setWindowDesign(self, title, image, width, height, xPos=0, yPos=0):
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(image))
        self.move(xPos, yPos)  # horizontal, vertical
        self.resize(height, width)  # width, height

    def makeLabel(self, labelNameList):
        labelList=[]
        for labelName in labelNameList:
            labelList.append(QLabel(labelName))
        return labelList

    def makeTextLine(self, num, isEditable, baseText=['']):
        if len(baseText)==1 : baseText*=num
        textLineList=[]
        for i in range(num):
            textLine=QLineEdit(baseText[i])
            if not isEditable : textLine.setReadOnly(True)
            textLineList.append(textLine)
        return textLineList

    def _makeGroupBox(self, title): # private method
        groupBox=QGroupBox(title)
        groupBox.setAlignment(Qt.AlignCenter)
        return groupBox

    def setLayoutOnGroupBox(self, title, customLayout):
        groupBox=self._makeGroupBox(title)
        groupBox.setLayout(customLayout)
        return groupBox

    def makeButton(self, name, clickFunction):
        button=CustomButton()
        button.setText(name)
        button.clicked.connect(clickFunction)
        return button

    def setCustomStyleSheet(self, widget, styleSheet):
        if type(widget) is not list:
            widget.setStyleSheet(styleSheet)

        else:
            for widgetElement in widget:
                widgetElement.setStyleSheet(styleSheet)

    def addWidgetOnLayout(self, layout, widget, *x): #(파이썬은 메소드 오버로딩 지원 안함)
        if len(x)==2 : layout.addWidget(widget, x[0], x[1])
        elif len(x)==0 : layout.addWidget(widget)
        else :
            print('widget add on layout error!!')
            return

    def addLayoutOnLayout(self, baseLayout, addLayout, ratio=1):
        baseLayout.addLayout(addLayout, ratio)

# 맵 데이터를 저장할수 있는 창을 띄워주는 클래스, QWidget 클래스를 상속받는다.
class SaveData(WindowDesign):
    def __init__(self):
        super().__init__()
        self.design()

    def design(self):
        # 디자인 코드 시작
        self.setWindowDesign('Save data', 'image/titleIcon.png', 500, 500, 500, 200)

        labelNameList = ['Map : ', 'Start : ', 'Object : ', 'Hazard : ']
        widgetStyleSheet = "font: 11pt \"Bahnschrift SemiLight\";"
        labelList = self.makeLabel(labelNameList)
        self.textLineList = self.makeTextLine(4, True)

        saveButton = self.makeButton('save', self.saveInputData)
        cancelButton = self.makeButton('cancel', self.close)
        buttonLayout = QHBoxLayout()
        self.addWidgetOnLayout(buttonLayout, saveButton)
        self.addWidgetOnLayout(buttonLayout, cancelButton)

        gBoxLayout = QGridLayout()
        for i in range(len(labelList)):
            self.addWidgetOnLayout(gBoxLayout, labelList[i], i, 0)
            self.addWidgetOnLayout(gBoxLayout, self.textLineList[i], i, 1)

        gBoxStyleSheet = """
                               font: 18pt \"Bahnschrift SemiLight\";
                               font-weight: bold;
                            """
        widgetStyleSheet = "font: 11pt \"Bahnschrift SemiLight\";"

        groupBox = self.setLayoutOnGroupBox('save map data', gBoxLayout)
        self.setCustomStyleSheet(groupBox, gBoxStyleSheet)
        self.setCustomStyleSheet(labelList, widgetStyleSheet)
        self.setCustomStyleSheet(self.textLineList, widgetStyleSheet)

        mainLayout = QVBoxLayout()
        self.addWidgetOnLayout(mainLayout, groupBox)
        self.addLayoutOnLayout(mainLayout, buttonLayout)
        self.setLayout(mainLayout)
        self.show()
        # 디자인 코드 끝

    def saveInputData(self): # 맵 데이터를 입력하고 save 버튼을 누르면 데이터가 저장된다.
        mapSize=self.textLineList[0].text()
        start=self.textLineList[1].text()
        spot=self.textLineList[2].text()
        hazard=self.textLineList[3].text()

        if mapSize=='' or start=='' or spot=='' or hazard=='': # 4개의 데이터 입력칸 중 하나라도 빈칸이 있는 경우
            MessageController.showMessage(self, 'error', 'Please check map data again.', NOT_CLOSE)
            return
        try: # 입력된 데이터에서 괄호와 쉼표를 분리한다.
            mapSize=mapSize.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            start = start.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            spot = spot.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            hazard = hazard.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
        except: #괄호, 쉼표 외에 다른 문자가 들어있는 경우 에러 발생
            MessageController.showMessage(self, 'error', 'Please check map data again.', NOT_CLOSE)
            return

        #int로 parsing
        mapSize=tuple(map(int, mapSize))
        start=tuple(map(int, start))
        spot=list(map(int, spot))
        hazard=list(map(int, hazard))

        isErr, objectSpot, hazardSpot=self.inputValueCheck(mapSize, start, spot, hazard)

        if isErr: # 입력 오류 발생
            MessageController.showMessage(self, 'error', 'Please check map data again.', NOT_CLOSE)
            return

        map_data.MapData(mapSize, start, objectSpot, hazardSpot)
        MessageController.showMessage(self, 'notice', 'Save Completed.', CLOSE) # 저장 완료 메시지를 띄우고, 메시지의 ok 버튼을 누르면 입력창이 닫힌다.

    def inputValueCheck(self, mapSize, start, spot, hazard):
        isErr = False  # 맵 크기로 음수값이 들어온 경우
        if mapSize[0] < 0 or mapSize[1] < 0:
            isErr = True

        objectSpot = []
        for i in range(0, len(spot), 2):  # 입력 데이터가 하나의 list에 담긴 int형으로 저장되어 있으므로, 2개씩 잘라 목표 좌표로 사용한다.
            if spot[i] < 0 or spot[i] > mapSize[0] or spot[i + 1] < 0 or spot[i + 1] > mapSize[1]:
                isErr = True
                break
            objectSpot.append(tuple(spot[i:i + 2]))

        hazardSpot = []
        for i in range(0, len(hazard), 2):  # 마찬가지로 2개씩 잘라 위험 좌표로 사용한다.
            if hazard[i] < 0 or hazard[i] > mapSize[0] or hazard[i + 1] < 0 or hazard[i + 1] > mapSize[1]:
                isErr = True
                break
            hazardSpot.append(tuple(hazard[i:i + 2]))

        for hazard in hazardSpot:  # hazardSpot list와 objectSpot list 둘 다에 속하는 점이 있으면 입력 오류
            if hazard in objectSpot:
                isErr = True
                break

        # start spot이 map을 넘어가거나 hazard spot 리스트 또는 object spot 리스트에 속하면 입력 오류
        if start in hazardSpot or start in objectSpot or start[0] < 0 or start[0] > mapSize[0] or start[1] < 0 or start[1] > mapSize[1]:
            isErr = True

        return isErr, objectSpot, hazardSpot

# 현재 시스템에 저장중인 맵 데이터를 보여주는 창을 띄워주는 클래스
class ShowMapData(WindowDesign):
    def __init__(self):
        super().__init__()

        self.mapSize=map_data.MapData.getMapSize()
        self.startSpot=map_data.MapData.getStartSpot()
        self.objectSpot=map_data.MapData.getObjectSpot()
        self.hazardSpot=map_data.MapData.getHazardSpot()
        self.design()

    def design(self):
        # 디자인 코드 시작
        self.setWindowDesign("Show map data", 'image/titleIcon.png', 500, 500, 500, 200)

        labelNameList = ['Map size : ', 'start spot : ', 'object spot : ', 'hazard spot : ']
        labelList = self.makeLabel(labelNameList)

        baseTextList = list(map(str, [self.mapSize, self.startSpot, self.objectSpot, self.hazardSpot]))
        textLineList = self.makeTextLine(4, False, baseTextList)

        gBoxLayout = QGridLayout()
        for i in range(len(labelList)):
            self.addWidgetOnLayout(gBoxLayout, labelList[i], i, 0)
            self.addWidgetOnLayout(gBoxLayout, textLineList[i], i, 1)

        groupBox = self.setLayoutOnGroupBox('Information', gBoxLayout)

        for label in labelList:
            self.setCustomStyleSheet(label, "font: 11pt \"Bahnschrift SemiLight\";")

        for textLine in textLineList:
            self.setCustomStyleSheet(textLine, "font: 11pt \"Bahnschrift SemiLight\";"
                                               "background:rgb(196, 211, 217);")

        returnButton = self.makeButton('return to menu', self.close)

        mainLayout = QVBoxLayout()
        self.addWidgetOnLayout(mainLayout, groupBox)
        self.addWidgetOnLayout(mainLayout, returnButton)
        self.setLayout(mainLayout)
        self.show()
        # 디자인 코드 끝

class DrawMap:

    '''
        robotImage : 맵에 로봇의 이미지를 그리는 AnnotationBBox 객체 저장. 움직임을 표현할 때 이전 위치의 이미지를 지우기 위해 사용
        arrowImage : 맵에 화살표를 그리는 AnnotationBBox 객체 저장. 움직임을 표현할 때 이전 위치의 이미지를 지우기 위해 사용
        drawedLines : 기존에 그려 놓은 경로 객체를 저장하는 리스트
        enlarge : 맵의 가로, 세로 길이가 모두 10을 넘으면 맵을 확대해서 보여준다.
        delay : 로봇 동작 표시 주기를 결정한다.
    '''

    def __init__(self, mapSize, curPosition, curDirection, hazardSpot, objectSpot, hiddenHazardSpot, hiddenColorBlobSpot, path):
        self.mapSize=mapSize
        self.hazardSpot=hazardSpot
        self.objectSpot=objectSpot
        self.hiddenHazardSpot=hiddenHazardSpot
        self.hiddenColorBlobSpot=hiddenColorBlobSpot

        self.robotImage=None
        self.arrowImage=None
        self.drawedLines = []
        self.enlarge=False
        if self.mapSize[0]>10 and self.mapSize[1]>10 : self.enlarge=True
        self.delay=0.5
        self.drawInitialMap(curPosition, curDirection, path)  # 창에 넣을 맵을 matplotlib을 이용해 만들고 로봇, 초기 경로, hazard spot, object spot을 그린다. 만든 맵은 canvas에 담아 PyQt5로 만든 창에 넣는다.
    '''
    
        drawInitialMapIcon()에 선언된 클래스 변수 설명
            objectSpotInstance : Object spot을 그릴 때 나오는 AnnotationBBox 객체를 저장한다. 방문한 object spot을 맵 상에서 지울 때 사용
            hiddenHazardSpotInstance : 숨겨진 hazard spot을 투명하게 그릴 때 나오는 AnnotationBBox 객체를 저장한다. 발견했을 때 지우고 투명하지 않은 그림으로 대체하기 위해 사용
            hiddenColorBlobSpotInstance : 숨겨진 color blob spot을 투명하게 그릴 때 나오는 AnnotationBBox 객체를 저장한다. 발견했을 때 지우고 투명하지 않은 그림으로 대체하기 위해 사용
        '''

    def drawInitialMapIcon(self):
        self.objectSpotInstance = []
        self.hiddenHazardSpotInstance = []
        self.hiddenColorBlobSpotInstance = []

        for hazardSpot in self.hazardSpot:  # 맵 정보로 주어진 hazard spot을 맵에 표시한다.
            self.drawImage(hazardSpot[0], hazardSpot[1], 'image/skull.png')

        for objSpot in self.objectSpot:  # 맵 정보로 주어진 object spot을 맵에 표시한다.
            self.objectSpotInstance.append((objSpot, self.drawImage(objSpot[0], objSpot[1], 'image/star.png')))

        for hiddenHSpot in self.hiddenHazardSpot:  # 무작위로 생성된 hidden hazard spot을 맵에 흐리게 표시한다.
            self.hiddenHazardSpotInstance.append(
                (hiddenHSpot, self.drawImage(hiddenHSpot[0], hiddenHSpot[1], 'image/skull_dim.png')))

        for hiddenCBSpot in self.hiddenColorBlobSpot:  # 무작위로 생성된 color blob spot을 맵에 흐리게 표시한다.
            self.hiddenColorBlobSpotInstance.append(
                (hiddenCBSpot, self.drawImage(hiddenCBSpot[0], hiddenCBSpot[1], 'image/splash_dim.png')))

    '''
           drawInitialMap() : matplotlib을 이용해 맵을 만들고 로봇, 초기 경로, hazard spot, object spot을 그린다. 만든 맵은 canvas에 담아 PyQt5로 만든 창에 넣는다.
             - 선언된 클래스 변수 -
               fig : 맵을 표현할 때 사용할 matplotlib의 figure 클래스의 인스턴스를 받아온다.
               canvas : fig를 PyQt5의 윈도우 창에 넣기 위해 사용하는 틀
               mapScreen : fig의 subplot 저장
               hiddenHazardSpot : hidden hazard spot 저장
               hiddenColorBlobSpot : hidden color blob spot 저장
       '''

    def drawInitialMap(self, curPosition, curDirection, path):
        self.fig = plt.figure()  # matplotlib의 figure 객체를 만든다.
        self.canvas = FigureCanvas(self.fig)  # 만든 figure 객체를 PyQt5와 연동시키기 위해 canvas에 담는다.
        self.mapScreen = self.fig.add_subplot(1, 1, 1)  # subplot 생성
        self.mapScreen.grid()
        self.drawBorder() # 맵 외곽선을 그린다.
        self.drawRobot(curPosition, curDirection)  # 맵 상에 로봇을 그린다.
        self.drawInitialMapIcon()
        self.drawPath(path)  # MapData 클래스에 저장된 경로 정보를 바탕으로 맵 상에 경로를 그린다.

    def drawBorder(self):  # 맵의 외곽선을 그린다.
        plt.plot([self.mapSize[1]] * (self.mapSize[0] + 1), 'k', lineWidth=5)  # 위
        plt.plot([0] * (self.mapSize[0] + 1), 'k', lineWidth=5)  # 아래
        plt.plot([0] * (self.mapSize[1] + 1), range(self.mapSize[1] + 1), 'k', lineWidth=5)  # 왼쪽
        plt.plot([self.mapSize[0]] * (self.mapSize[1] + 1), range(self.mapSize[1] + 1), 'k', lineWidth=5)  # 오른쪽

    # imageScatter : 맵 상의 좌표 (x, y)에 경로 image에 있는 이미지 파일을 그린다.
    def imageScatter(self, x, y, image, zoom=1, ax=None):
        """
        :param x: 이미지 x좌표
        :param y: 이미지 y좌표
        :param image: 이미지 파일 경로
        :param zoom: 이미지 크기 배율
        :param ax: 어떤 plot에 이미지를 그릴 지 저장하고 있다.
        """
        if ax is None:
            ax = plt.gca()  # ax로 들어온 값이 없을 경우 새로 plot을 생성한다.
        try:
            image = plt.imread(image)  # 경로 image에 있는 이미지를 불러온다.
        except TypeError:
            return
        im = OffsetImage(image, zoom=zoom)
        artist = AnnotationBbox(im, (x, y), frameon=False)
        return ax.add_artist(artist)

    # drawImage(self, x, y, imagePath) : 맵 상의 좌표 (x, y)에 imagePath에 있는 이미지를 그린다.
    def drawImage(self, x, y, imagePath):
        return self.imageScatter(x, y, imagePath, zoom=0.1, ax=self.mapScreen)

    # eraseAndDrawImage(self, spot, imageInstanceList, imagePath) : 기존에 spot 위치에 있던 이미지를 지우고 imagePath에 있는 이미지로 대체한다.
    def eraseAndDrawImage(self, spot, imageInstanceList, imagePath):
        for imageSpot, imageInstance in imageInstanceList:
             if tuple(spot) == imageSpot:
                imageInstance.remove()
                self.drawImage(spot[0], spot[1], imagePath)
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                return

    def drawRobot(self, position, direction):  # changePath
        arrowDirection = [(0, 0.7), (0.4, 0), (0, -0.7), (-0.4, 0)]
        arrowFileName = ['image/up.png', 'image/right.png', 'image/down.png', 'image/left.png']

        if self.robotImage:
            self.robotImage.remove()
            self.arrowImage.remove()

        self.robotImage = self.drawImage(position[0], position[1], 'image/robot.png')
        self.arrowImage = self.drawImage(position[0] + arrowDirection[direction][0],
                                         position[1] + arrowDirection[direction][1],
                                         arrowFileName[direction])

        if self.enlarge:  # 맵 가로, 세로 길이 둘 다 10 초과
            plt.xlim(-3 + position[0], 4 + position[0])
            plt.xticks(np.arange(-3 + position[0], 4 + position[0], step=1))

            plt.ylim(-3 + position[1], 4 + position[1])
            plt.yticks(np.arange(-3 + position[1], 4 + position[1], step=1))
        if self.mapSize[0] + self.mapSize[1] < 300: time.sleep(self.delay)  # delay초 간격으로 로봇의 움직임 표현.
                                                                            # 맵의 가로, 세로 합이 300 이상이고 경로를 다시 그렸을 때는
                                                                            # 경로를 다시 그리는게 오래 걸리므로 딜레이를 없앤다.

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    #drawPath(self, path) : 로봇이 지나갈 경로를 맵 상에 그린다.
    def drawPath(self, path):
        if len(self.drawedLines)!=0:
            self.removePath()
        dist=(0, 0)
        i=1
        while True:
            if i==len(path) : break
            prev=path[i-1]
            next=path[i]
            dist = (next[0]-prev[0], next[1]-prev[1])
            while i<len(path)-1 and dist==(path[i+1][0]-path[i][0], path[i+1][1]-path[i][1]):
                i+=1
                next = path[i]

            x=next[0]-prev[0]
            y=next[1]-prev[1]
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
                    lines=self.mapScreen.plot(np.linspace(next[0], prev[0], -(x - 1)), [path[i][1]] * -(x - 1), 'r',
                             linewidth=5)
            self.drawedLines+=lines #Memorize current path plot object.
            prev=path[i]
            i+=1

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def removePath(self):
        for i in range(0, len(self.mapScreen.lines)):
            self.mapScreen.lines[0].remove()
        self.drawBorder()

    #PyQt5의 창에 맵을 추가하기 위해 canvas 객체를 리턴한다.
    def getCanvas(self):
        return self.canvas

    def getHiddenSpotInstance(self):
        return self.hiddenHazardSpotInstance, self.hiddenColorBlobSpotInstance, self.objectSpotInstance


#ShowRobotMovement : 로봇의 이동과정을 보여주는 창을 띄우는 클래스.
class ShowRobotMovement(WindowDesign):
    def __init__(self):
        super().__init__()
        np.random.seed(int(time.time()))
        self.setInitialInfo() # 계산에 필요한 여러 가지 변수들을 세팅한다.
        hiddenHazardNum = 3  # 갯수를 랜덤으로 설정하려면 -1 대입
        hiddenCBNum = 3  # 갯수를 랜덤으로 설정하려면 -1 대입
        self.generateRandomSpot(hiddenHazardNum, hiddenCBNum)  # hidden hazard spot과 object spot을 무작위로 생성
        self.drawMap = DrawMap(self.mapSize, self.curPosition, self.curDirection, self.hazardSpot, self.objectSpot,
                               map_data.MapData.getHazardH(), map_data.MapData.getCbH(), self.path)
        self.design()  # 창의 디자인을 담당하는 메소드 호출

    def setInitialDirection(self, secondSpot, firstSpot):
        secondFirstDifference = secondSpot[0] - firstSpot[0], secondSpot[1] - firstSpot[1]  # 0 : 위 1 : 오른쪽 2 : 아래 3 : 왼쪽

        # 초기 로봇 방향 설정
        if secondFirstDifference[0] == 0:
            if secondFirstDifference[1] > 0:
                initialDirection = 0
            else:
                initialDirection = 2
        else:
            if secondFirstDifference[0] > 0:
                initialDirection = 1
            else:
                initialDirection = 3

        assert (initialDirection != -1)  # 로봇의 방향이 제대로 배정되었는지 확인
        return initialDirection
    '''
    setInitialInfo()에 선언된 클래스 변수 설명
        mapSize, curPosition, hazardSpot, objectSpot : 각각 맵 사이즈, 현재 로봇의 위치, hazard spot 리스트, object spot 리스트를 나타낸다.
        originalobjectSpot : objectSpot 리스트는 실행 도중 내부 원소들이 리스트에서 제외된다. 이러면 MapData에 있는 데이터가 손상되므로 미리 
                             MapData에 있는 objectSpot을 깊은 복사를 통해 저장한다. ShowRobotMovement 실행이 끝난 후에 이 값을 MapData의 
                             objectSpot에 덮어씌워 데이터 손상을 복구한다.
        objCnt : 로봇이 아직 방문하지 않은 목표 지점의 갯수를 나타낸다.
        drawedLines :맵 상에 그린 경로 객체들을 저장
        curDirection : 로봇의 현재 방향을 나타낸다.
        ctrlPath : 경로를 컨트롤하는 클래스 ControlPath의 인스턴스 저장
        ctrlRobot : 로봇을 컨트롤하는 클래스 ControlRobot의 인스턴스 저장
        path : ctrlPath의 getPath() 메소드를 통해 클래스 pathInfo에 저장되어 있는 경로 정보를 받아온다.
        enlarge : 맵의 가로, 세로 길이가 모두 10을 넘을 때 맵을 확대해서 그린다.
    '''

    def setInitialInfo(self): # 메뉴로 돌아갔다가 다시 show result를 누를 때 정보를 초기화하기 위해 사용
        self.mapSize = map_data.MapData.getMapSize()
        self.curPosition = copy.deepcopy(map_data.MapData.getStartSpot()) # 현재 로봇 위치 값은 실행 도중 변하므로 동작이 끝난 뒤
                                                                          # 메인 메뉴로 돌아갔을 때 재실행이 가능하게 하기 위해서 깊은 복사를 수행한다.
        self.hazardSpot = map_data.MapData.getHazardSpot()
        self.originalObjectSpot = copy.deepcopy(map_data.MapData.getObjectSpot()) # 실행 도중 방문한 object spot들은 리스트에서 제거되므로 동작이 끝난 뒤
                                                                                  # 메인 메뉴로 돌아갔을 때 재실행 가능하게 하기 위해서 깊은 복사를 수행한다.
        self.objectSpot = map_data.MapData.getObjectSpot()
        self.objCnt=len(self.objectSpot)
        self.ctrlPath = robot_and_control.ControlPath()
        self.ctrlPath.createPath(self.curPosition)  # 경로 생성, 현재 좌표와 로봇이 지금까지 찾은 hidden hazard spot이 저장되어 있는 리스트를 매개변수로 준다.
        self.path = self.ctrlPath.getPath()
        self.curDirection = self.setInitialDirection(self.path[1], self.path[0]) #로봇의 처음 방향 설정
        self.ctrlRobot = robot_and_control.ControlRobot(self.curDirection, self.ctrlPath)
        self.enlarge = False

    def design(self):
        # 디자인 코드 시작
        self.setWindowDesign('Result', 'image/titleIcon.png', 1000, 1920)

        if self.mapSize[0] > 10 and self.mapSize[1] > 10:  # 맵의 가로, 세로 크기가 모두 10을 넘을 경우
            self.enlarge = True

        if self.enlarge:  # 맵 가로, 세로 길이 둘 다 10 초과
            plt.xlim(-3 + self.curPosition[0], 4 + self.curPosition[0])
            plt.xticks(np.arange(-3 + self.curPosition[0], 4 + self.curPosition[0], step=1))
            plt.ylim(-3 + self.curPosition[1], 4 + self.curPosition[1])
            plt.yticks(np.arange(-3 + self.curPosition[1], 4 + self.curPosition[1], step=1))

        else:
            plt.xlim(-1, self.mapSize[0] + 1)
            plt.xticks(np.arange(-1, self.mapSize[0] + 1, step=1))
            plt.ylim(-1, self.mapSize[1] + 1)
            plt.yticks(np.arange(-1, self.mapSize[1] + 1, step=1))

        leftLayout = QVBoxLayout()
        self.addWidgetOnLayout(leftLayout, self.drawMap.getCanvas())

        rightSubLayout = QVBoxLayout()

        labelNameList = ['로봇 좌표', '로봇 동작', '남아있는 object spot 갯수']
        labelList = self.makeLabel(labelNameList)
        self.curPositionText, self.robotMovementText, self.remainObjectText = \
            self.makeTextLine(len(labelNameList), False, [str(list(self.curPosition)), '', str(self.objCnt)])
        textLineList = [self.curPositionText, self.robotMovementText, self.remainObjectText]

        for i in range(len(labelList)):
            rightSubLayout.addWidget(labelList[i])
            rightSubLayout.addWidget(textLineList[i])

        groupBox = self.setLayoutOnGroupBox('Information', rightSubLayout)
        self.setCustomStyleSheet(groupBox, "font: 18pt \"Bahnschrift SemiLight\";\n"
                                           "font-weight: bold;")

        self.setCustomStyleSheet(labelList, "font: 11pt \"나눔고딕\";")
        self.setCustomStyleSheet(textLineList, "font: 11pt \"나눔고딕\";"
                                               "background:rgb(196, 211, 217)")

        rightLayout = QVBoxLayout()
        self.addWidgetOnLayout(rightLayout, groupBox)

        imageLabel = QLabel()
        pixmap = QPixmap('image/description.png')
        imageLabel.setPixmap(pixmap)
        rightLayout.addWidget(imageLabel)

        startButton = self.makeButton('start', self.controlRobotMovement)
        returnButton = self.makeButton('return to menu', self.close)

        topLayout = QHBoxLayout()
        self.addLayoutOnLayout(topLayout, leftLayout, 4)
        self.addLayoutOnLayout(topLayout, rightLayout, 1)

        bottomLayout = QHBoxLayout()
        self.addWidgetOnLayout(bottomLayout, startButton)
        self.addWidgetOnLayout(bottomLayout, returnButton)

        mainLayout = QVBoxLayout()
        self.addLayoutOnLayout(mainLayout, topLayout)
        self.addLayoutOnLayout(mainLayout, bottomLayout)
        self.setLayout(mainLayout)
        self.show()
        # 디자인 코드 끝

    def changePath(self):
        self.ctrlPath.createPath(self.curPosition, self.ctrlRobot.getFoundHazardSpot())
        self.path=self.ctrlPath.getPath()
        self.drawMap.drawPath(self.path)

    def controlRobotMovement(self):
        while self.objCnt!=0:
            hazardFound=False
            hiddenCbList, hiddenHSpot=self.ctrlRobot.getSensorInfo()

            hiddenHazardSpotInstance, hiddenColorBlobSpotInstance, objectSpotInstance=self.drawMap.getHiddenSpotInstance()
            '''인근 지역에 숨겨진 color blob spot을 맵에 표시한다.'''
            if len(hiddenCbList)!=0: #현재 위치 근처에 hidden cb가 존재한다.
                for pos in hiddenCbList: #리스트에는 color blob의 좌표가 들어있다.
                    self.drawMap.eraseAndDrawImage(pos, hiddenColorBlobSpotInstance, 'image/splash.png')
                    map_data.MapData.removeHiddenCBSpot(pos) # 지우지 않으면 로봇이 다른 위치에서 동일한 object spot을 다시 발견할 수 있고, 오류가 발생한다.

            '''로봇이 보고있는 방향 바로 앞에 hidden hazard spot을 맵에 표시한다.'''
            if self.ctrlRobot.checkDirection() and hiddenHSpot[0]!=-1:
                MessageController.showMessage(self, 'notice', 'Robot found Hazard spot!', NOT_CLOSE) #메시지 출력
                self.drawMap.eraseAndDrawImage(hiddenHSpot, hiddenHazardSpotInstance, 'image/skull.png')
                self.changePath()
                hazardFound=True
                map_data.MapData.removeHiddenHSpot(hiddenHSpot) # 지우지 않으면 로봇이 다른 위치에서 동일한 hidden hazard spot을 다시 발견할 수 있고, 오류가 발생한다.
                continue

            self.commandMovementAndChangePosInfo(hazardFound)

            if tuple(self.curPosition) in self.objectSpot:
                self.drawMap.eraseAndDrawImage(self.curPosition, objectSpotInstance, 'image/star_red.png')
                self.objectSpot.remove(tuple(self.curPosition)) # 방문한 object spot을 MapData의 objectSpot 리스트에서 뺀다.
                self.objCnt-=1
                self.remainObjectText.setText(str(self.objCnt))

        MessageController.showMessage(self, 'notice', 'robot found all object spot!', NOT_CLOSE)
        map_data.MapData.getBackObjectSpot(self.originalObjectSpot)  # objectSpot 리스트를 처음 입력했던 상태로 돌려놓는다.

    #commandMovementAndChangePosInfo() : 로봇의 움직임을 지시하고 움직임이 끝난 뒤 현재 로봇의 위치 정보, 방향 정보를 받아 curPosition, curDirection을 수정한다.
    #                                    기존에 맵에 있던 로봇을 지우고 움직인 위치에 로봇을 다시 그린다.
    
    def commandMovementAndChangePosInfo(self, hazardFound):
        beforePosition=(self.curPosition[0], self.curPosition[1])
        changedPosition, changedDirection = self.ctrlRobot.commandMovement()
        isTwoStep=False
        if changedDirection!=self.curDirection :
            self.robotMovementText.setText('회전')
            
        if changedDirection==self.curDirection and abs(beforePosition[0]-changedPosition[0]+beforePosition[1]-changedPosition[1])==0:
            self.robotMovementText.setText('정지')
        self.curPosition = changedPosition
        self.curDirection = changedDirection
        self.curPositionText.setText(str(self.curPosition))

        if abs(beforePosition[0]-self.curPosition[0]+beforePosition[1]-self.curPosition[1])==1:
            self.ctrlRobot.incPathNum()
            self.robotMovementText.setText('앞으로 한 칸 이동')
            
        elif abs(beforePosition[0]-self.curPosition[0]+beforePosition[1]-self.curPosition[1])==2:
            isTwoStep=True
            self.robotMovementText.setText('앞으로 두 칸 이동')

        isChangePath=hazardFound+isTwoStep
        self.drawMap.drawRobot(self.curPosition, self.curDirection)
        if isChangePath : self.changePath()

    #generateRandomSpot(self, hazardNum, cbNum) : 무작위로 hidden hazard spot, hidden color blob spot을 생성한다. hazardNum을 통해
    #                                             hidden hazard spot의 갯수를, cbNum을 통해 hidden color blob spot의 갯수를 설정할
    #                                             수 있다. 설정하지 않으면 두 지점 모두 0에서 (맵의 가로 길이 + 맵의 세로 길이) / 2 개
    #                                             중 무작위 갯수로 생성된다. (최대 100개씩)

    def generateRandomSpot(self, hazardNum=-1, cbNum=-1):
        visibleHazardSpot=map_data.MapData.getHazardSpot() # 맵 상에 보이는 hazard spot 좌표
        objectSpot=map_data.MapData.getObjectSpot() # object spot 좌표
        startSpot=map_data.MapData.getStartSpot() #start spot 좌표
        # 갯수가 주어지지 않은 경우. hidden hazard spot의 수를 0 ~ (맵의 가로 길이 + 세로 길이) (최대 100) 사이의 수로 정한다.
        if hazardNum==-1 : hazardNum=np.random.randint(0, min((self.mapSize[0]+self.mapSize[1])/2, 100))
        # 갯수가 주어지지 않은 경우, color blob spot의 수를 0 ~ (맵의 가로 길이 + 세로 길이) (최대 100) 사이의 수로 정한다.
        if cbNum==-1 : cbNum=np.random.randint(0, min((self.mapSize[0]+self.mapSize[1])/2, 100))

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
            hsNum=4 # hazard spot이 object spot을 감쌀 수 있는 최대 갯수를 지정한다. 맵의 모서리에서는 3개, 꼭짓점에서는 2개
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

                # 로봇이 object spot에 도달하지 못하는 형태로 hidden hazard spot이 생성되었을 때, 지워질 hidden hazard spot을 뽑는다.
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
                hiddenHazardSpot.remove(tobeRemovedSpot)
                
        # 무작위로 생성한 color blob spot과 hidden hazard spot이 겹치지는 않는지 확인한다.
        assert len([item for item in hiddenHazardSpot if item in hiddenCbSpot])==0

        map_data.MapData.setHiddenData(hiddenHazardSpot, hiddenCbSpot)
    
class ShowMenu(WindowDesign):
    def __init__(self):
        super().__init__()
        map_data.MapData() #temp
        self.design()

    def design(self):
        # 디자인 코드 시작
        self.setWindowDesign('ADD-ON System 1.0', 'image/titleIcon.png', 500, 500, 500, 200)

        saveButton = self.makeButton('Save data', self.saveData)
        showRobotMovementButton = self.makeButton('Show robot movement', self.showRobotMovement)
        showDataButton = self.makeButton('Show map data', self.showMapData)
        quitButton = self.makeButton('Quit', QCoreApplication.instance().quit)

        buttonList = [saveButton, showRobotMovementButton, showDataButton, quitButton]
        boxLayout = QVBoxLayout()
        for button in buttonList:
            self.addWidgetOnLayout(boxLayout, button)

        headLabel = self.makeLabel(['ADD-ON system'])
        self.setCustomStyleSheet(headLabel, "font: 26pt \"Bahnschrift SemiBold\";\n"
                                            "font-weight: bold;")
        headLabel[0].setAlignment(Qt.AlignCenter)

        subLabel = self.makeLabel(['version 1.0'])
        self.setCustomStyleSheet(subLabel, "font: 12pt \"Bahnschrift SemiBold\";\n"
                                           "font-weight: bold;")
        subLabel[0].setAlignment(Qt.AlignCenter)

        groupBox = self.setLayoutOnGroupBox('', boxLayout)
        self.setCustomStyleSheet(groupBox, "font: 18pt \"Bahnschrift SemiLight\";\n"
                                           "font-weight: bold;")

        mainLayout = QVBoxLayout()
        self.addWidgetOnLayout(mainLayout, headLabel[0])
        self.addWidgetOnLayout(mainLayout, subLabel[0])
        self.addWidgetOnLayout(mainLayout, groupBox)
        self.setLayout(mainLayout)
        self.show()
        # 디자인 코드 끝

    def saveData(self): #Save data 버튼을 눌렀을 때 SaveData 클래스의 인스턴스를 생성한다.
        self.sd=SaveData()

    def showMapData(self):#Show map data 버튼을 눌렀을 때 ShowMapData 클래스의 인스턴스를 생성한다.
        try:
            testAtt=map_data.MapData.getMapSize() #저장된 맵 데이터가 있는지 확인한다.
        except AttributeError:
            MessageController.showMessage(self, 'error', 'map data doesn\'t exist.', NOT_CLOSE)
            return

        self.smd=ShowMapData()

    def showRobotMovement(self): # Show robot mavement 버튼을 눌렀을 때 ShowRobotMovement 클래스의 인스턴스를 생성한다.
        try:
            testAtt=map_data.MapData.getMapSize() #저장된 맵 데이터가 있는지 확인한다.
        except AttributeError:
            MessageController.showMessage(self, 'error', 'map data doesn\'t exist.', NOT_CLOSE)
            return

        self.sr=ShowRobotMovement()

if __name__=='__main__':
    app=QApplication(sys.argv)
    ex=ShowMenu()
    sys.exit(app.exec_())