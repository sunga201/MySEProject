from Database.mapAndPathData import MapData
from RobotSubSystem.Robot_control import robotAndPathController
from InterfaceSubSystem.Window_design_management.window import WindowDesign
from InterfaceSubSystem.Map_management.drawMap import DrawMap
from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QCoreApplication, Qt, QRect, QAbstractAnimation
import numpy as np
import sys
import random
import copy
import time

#메시지 박스의 OK 버튼을 눌렀을 때 기존 창을 닫을지, 닫지 않을 지를 정할 때 사용한다.
CLOSE=1
NOT_CLOSE=0

# ShowRobotMovement : 로봇의 이동과정을 보여주는 창을 띄우는 클래스.
class ShowRobotMovement(WindowDesign):
    def __init__(self):
        super().__init__()
        np.random.seed(int(time.time()))
        self.setInitialInfo()  # 계산에 필요한 여러 가지 변수들을 세팅한다.
        hiddenHazardNum = 3  # 갯수를 랜덤으로 설정하려면 -1 대입
        hiddenCBNum = 3  # 갯수를 랜덤으로 설정하려면 -1 대입
        self.generateRandomSpot(hiddenHazardNum, hiddenCBNum)  # hidden hazard spot과 object spot을 무작위로 생성
        self.drawMap = DrawMap(self.mapSize, self.curPosition, self.curDirection, self.hazardSpot, self.objectSpot,
                               MapData.getHazardH(), MapData.getCbH(), self.path)
        self.design()  # 창의 디자인을 담당하는 메소드 호출

    def setInitialDirection(self, secondSpot, firstSpot):
        secondFirstDifference = secondSpot[0] - firstSpot[0], secondSpot[1] - firstSpot[
            1]  # 0 : 위 1 : 오른쪽 2 : 아래 3 : 왼쪽

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
    --- setInitialInfo()에 선언된 클래스 변수 설명 ---
        mapSize, curPosition, hazardSpot, objectSpot : 각각 맵 사이즈, 현재 로봇의 위치, hazard spot 리스트, object spot 리스트를 나타낸다.
        originalobjectSpot : objectSpot 리스트는 실행 도중 내부 원소들이 리스트에서 제외된다. 이러면 MapData에 있는 데이터가 손상되므로 미리 
                             MapData에 있는 objectSpot을 깊은 복사를 통해 저장한다. ShowRobotMovement 실행이 끝난 후에 이 값을 MapData의 
                             objectSpot에 덮어씌워 데이터 손상을 복구한다.
        objCnt : 로봇이 아직 방문하지 않은 목표 지점의 갯수를 나타낸다.
        drawedLines :맵 상에 그린 경로 객체들을 저장
        ctrlPath : 경로를 컨트롤하는 클래스 PathController의 인스턴스 저장
        path : ctrlPath의 getPath() 메소드를 통해 클래스 pathInfo에 저장되어 있는 경로 정보를 받아온다.
        curDirection : 로봇의 현재 방향을 나타낸다.
        ctrlRobot : 로봇을 컨트롤하는 클래스 RobotController의 인스턴스 저장
        delay : 로봇 동작 표현 주기를 결정한다.
    '''

    def setInitialInfo(self):  # 메뉴로 돌아갔다가 다시 show result를 누를 때 정보를 초기화하기 위해 사용
        self.mapSize = MapData.getMapSize()
        self.curPosition = copy.deepcopy(MapData.getStartSpot())  # 현재 로봇 위치 값은 실행 도중 변하므로 동작이 끝난 뒤
        # 메인 메뉴로 돌아갔을 때 재실행이 가능하게 하기 위해서 깊은 복사를 수행한다.
        self.hazardSpot = MapData.getHazardSpot()
        self.originalObjectSpot = copy.deepcopy(MapData.getObjectSpot())  # 실행 도중 방문한 object spot들은 리스트에서 제거되므로 동작이 끝난 뒤
        # 메인 메뉴로 돌아갔을 때 재실행 가능하게 하기 위해서 깊은 복사를 수행한다.
        self.objectSpot = MapData.getObjectSpot()
        self.objCnt = len(self.objectSpot)
        self.ctrlPath = robotAndPathController.PathController()
        self.ctrlPath.createPath(self.curPosition)  # 경로 생성, 현재 좌표와 로봇이 지금까지 찾은 hidden hazard spot이 저장되어 있는 리스트를 매개변수로 준다.
        self.path = self.ctrlPath.getPath()
        self.curDirection = self.setInitialDirection(self.path[1], self.path[0])  # 로봇의 처음 방향 설정
        self.ctrlRobot = robotAndPathController.RobotController(self.curDirection, self.ctrlPath, self.mapSize)
        self.delay = 0.5

    def design(self):
        # 디자인 코드 시작
        self.setWindowDesign('Result', 'image/titleIcon.png', 1000, 1920)

        leftLayout = QVBoxLayout()
        self.addWidgetOnLayout(leftLayout, self.drawMap.getCanvas()) # Show robot movement 창의 왼쪽 편에 맵 추가

        rightSubLayout = QVBoxLayout()

        labelNameList = ['로봇 좌표', '로봇 동작', '남아있는 object spot 갯수']
        labelList = self.makeLabel(labelNameList)
        self.curPositionText, self.robotMovementText, self.remainObjectText = \
            self.makeTextLine(len(labelNameList), False, [str(list(self.curPosition)), '', str(self.objCnt)])
        textLineList = [self.curPositionText, self.robotMovementText, self.remainObjectText]

        for i in range(len(labelList)):
            self.addWidgetOnLayout(rightSubLayout, labelList[i])
            self.addWidgetOnLayout(rightSubLayout, textLineList[i])

        groupBox = self.setLayoutOnGroupBox('Information', rightSubLayout) # 로봇의 현재 위치, 방향, 남은 object spot 갯수를 표현할 groupbox를 만든다.
        self.setCustomStyleSheet(groupBox, "font: 18pt \"Bahnschrift SemiLight\";\n"
                                           "font-weight: bold;")

        self.setCustomStyleSheet(labelList, "font: 11pt \"나눔고딕\";")
        self.setCustomStyleSheet(textLineList, "font: 11pt \"나눔고딕\";"
                                               "background:rgb(196, 211, 217)")

        rightLayout = QVBoxLayout()
        self.addWidgetOnLayout(rightLayout, groupBox) # 위에서 만든 groupbox를 show robot movement 창의 오른쪽 편에 배치한다.

        imageLabel = QLabel()
        pixmap = QPixmap('image/description.png')
        imageLabel.setPixmap(pixmap)
        rightLayout.addWidget(imageLabel)

        startButton = self.makeButton('start', self.showMovingProcess)
        returnButton = self.makeButton('return to menu', self.close)

        topLayout = QHBoxLayout()
        self.addLayoutOnLayout(topLayout, leftLayout, 4)
        self.addLayoutOnLayout(topLayout, rightLayout, 1)

        bottomLayout = QHBoxLayout()
        self.addWidgetOnLayout(bottomLayout, startButton)
        self.addWidgetOnLayout(bottomLayout, returnButton) #show robot movement 창의 아래쪽에는 버튼들을 배치한다.

        mainLayout = QVBoxLayout()
        self.addLayoutOnLayout(mainLayout, topLayout)
        self.addLayoutOnLayout(mainLayout, bottomLayout)
        self.setLayout(mainLayout)
        self.show()
        # 디자인 코드 끝

    def changePath(self):
        self.ctrlPath.createPath(self.curPosition, self.ctrlRobot.getFoundHazardSpot())
        self.path = self.ctrlPath.getPath()
        self.drawMap.drawPath(self.path)

    def showMovingProcess(self):
        while self.objCnt != 0:
            hiddenCbList, hiddenHSpot = self.ctrlRobot.getSensorInfo()
            hiddenHazardSpotInstance, hiddenColorBlobSpotInstance, objectSpotInstance = self.drawMap.getHiddenSpotInstance()
            '''인근 지역에 숨겨진 color blob spot을 맵에 표시한다.'''
            if len(hiddenCbList) != 0:  # 현재 위치 근처에 hidden cb가 존재한다.
                for pos in hiddenCbList:  # 리스트에는 color blob의 좌표가 들어있다.
                    self.drawMap.eraseAndDrawImage(pos, hiddenColorBlobSpotInstance, 'image/splash.png')
                    MapData.removeHiddenCBSpot(pos)  # 지우지 않으면 로봇이 다른 위치에서 동일한 object spot을 다시 발견할 수 있고, 오류가 발생한다.

            '''로봇이 보고있는 방향 바로 앞에 hidden hazard spot을 맵에 표시한다.'''
            if self.ctrlRobot.checkDirection() and hiddenHSpot[0] != -1:
                self.showMessage('notice', 'Robot found Hazard spot!', NOT_CLOSE)  # 메시지 출력
                self.drawMap.eraseAndDrawImage(hiddenHSpot, hiddenHazardSpotInstance, 'image/skull.png')
                self.changePath()
                MapData.removeHiddenHSpot(hiddenHSpot)  # 지우지 않으면 로봇이 다른 위치에서 동일한 hidden hazard spot을 다시 발견할 수 있고, 오류가 발생한다.
                if self.mapSize[0] + self.mapSize[1] < 300: time.sleep(self.delay)
                continue

            self.commandMovementAndChangePosInfo()

            if tuple(self.curPosition) in self.objectSpot:
                self.drawMap.eraseAndDrawImage(self.curPosition, objectSpotInstance, 'image/star_red.png')
                self.objectSpot.remove(tuple(self.curPosition))  # 방문한 object spot을 MapData의 objectSpot 리스트에서 뺀다.
                self.objCnt -= 1
                self.remainObjectText.setText(str(self.objCnt))

            if self.mapSize[0] + self.mapSize[1] < 300: time.sleep(self.delay)  # delay초 간격으로 로봇의 움직임 표현.
                                                                                # 맵의 가로, 세로 합이 300 이상이고 경로를 다시 그렸을 때는
                                                                                # 경로를 다시 그리는게 오래 걸리므로 딜레이를 없앤다.

        self.showMessage('notice', 'robot found all object spot!', NOT_CLOSE)
        MapData.getBackObjectSpot(self.originalObjectSpot)  # objectSpot 리스트를 처음 입력했던 상태로 돌려놓는다.

    # commandMovementAndChangePosInfo() : 로봇의 움직임을 지시하고 움직임이 끝난 뒤 현재 로봇의 위치 정보, 방향 정보를 받아 curPosition, curDirection을 수정한다.
    #                                    기존에 맵에 있던 로봇을 지우고 움직인 위치에 로봇을 다시 그린다.

    def commandMovementAndChangePosInfo(self):
        beforePosition = (self.curPosition[0], self.curPosition[1])
        changePosition, changeDirection = self.ctrlRobot.commandMovement()
        isTwoStep = False
        if changeDirection != self.curDirection:
            self.robotMovementText.setText('회전')

        if changeDirection == self.curDirection and abs(
                beforePosition[0] - changePosition[0] + beforePosition[1] - changePosition[1]) == 0:
            self.robotMovementText.setText('정지')
        self.curPosition = changePosition
        self.curDirection = changeDirection
        self.curPositionText.setText(str(self.curPosition))

        if abs(beforePosition[0] - self.curPosition[0] + beforePosition[1] - self.curPosition[1]) == 1:
            self.ctrlRobot.incPathNum()
            self.robotMovementText.setText('앞으로 한 칸 이동')

        elif abs(beforePosition[0] - self.curPosition[0] + beforePosition[1] - self.curPosition[1]) == 2:
            isTwoStep = True
            self.robotMovementText.setText('앞으로 두 칸 이동')

        self.drawMap.drawRobot(self.curPosition, self.curDirection)
        if isTwoStep : self.changePath()

    # generateRandomSpot(self, hazardNum, cbNum) : 무작위로 hidden hazard spot, hidden color blob spot을 생성한다. hazardNum을 통해
    #                                             hidden hazard spot의 갯수를, cbNum을 통해 hidden color blob spot의 갯수를 설정할
    #                                             수 있다. 설정하지 않으면 두 지점 모두 0에서 (맵의 가로 길이 + 맵의 세로 길이) / 2 개
    #                                             중 무작위 갯수로 생성된다. (최대 100개씩)

    def generateRandomSpot(self, hazardNum=-1, cbNum=-1):
        visibleHazardSpot = MapData.getHazardSpot()  # 맵 상에 보이는 hazard spot 좌표
        objectSpot = MapData.getObjectSpot()  # object spot 좌표
        startSpot = MapData.getStartSpot()  # start spot 좌표
        # 갯수가 주어지지 않은 경우. hidden hazard spot의 수를 0 ~ (맵의 가로 길이 + 세로 길이) (최대 100) 사이의 수로 정한다.
        if hazardNum == -1: hazardNum = np.random.randint(0, min((self.mapSize[0] + self.mapSize[1]) / 2, 100))
        # 갯수가 주어지지 않은 경우, color blob spot의 수를 0 ~ (맵의 가로 길이 + 세로 길이) (최대 100) 사이의 수로 정한다.
        if cbNum == -1: cbNum = np.random.randint(0, min((self.mapSize[0] + self.mapSize[1]) / 2, 100))

        mapWidth = self.mapSize[0]
        mapHeight = self.mapSize[1]
        tmpHazard = []
        tmpCb = []

        usedSpot = visibleHazardSpot + objectSpot  # 이 지역은 hidden hazard spot이나 color blob spot을 만들 수 없다.
        usedSpot.append(startSpot)

        usableSpot = []
        for i in range(mapWidth + 1):
            for j in range(mapHeight + 1):
                usableSpot.append((i, j))  # 맵 상의 모든 좌표를 usableSpot 리스트에 넣는다.

        for point in usedSpot:
            usableSpot.remove(point)
        hiddenCbSpot = random.sample(usableSpot,
                                     cbNum)  # usableSpot 리스트 내부에서 위에서 정한 갯수민큼 color blob spot을 뽑고, 그 지역을 usableSpot 리스트에서 삭제한다.
        for cbSpot in hiddenCbSpot:
            usableSpot.remove(cbSpot)

        hiddenHazardSpot = random.sample(usableSpot, hazardNum)  # hidden hazard spot도 뽑는다.
        for hazardSpot in hiddenHazardSpot:
            usableSpot.remove(hazardSpot)

        totalHazardSpot = hiddenHazardSpot + visibleHazardSpot
        totalHazardSpot = list(set(totalHazardSpot))
        for obj in objectSpot:
            x = obj[0]
            y = obj[1]
            hsNum = 4  # hazard spot이 object spot을 감쌀 수 있는 최대 갯수를 지정한다. 맵의 모서리에서는 3개, 꼭짓점에서는 2개
            checkSpot = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            tobeRemovedSpot = (x, y - 1)
            if (x == 0 and y == 0) or (x == 0 and y == mapHeight) or (x == mapWidth and y == 0) or (
                    x == mapWidth and y == mapHeight):
                if x == 0 and y == 0:
                    checkSpot = [(x + 1, y), (x, y + 1)]

                elif x == 0 and y == mapHeight:
                    checkSpot = [(x + 1, y), (x, y - 1)]

                elif x == mapWidth and y == 0:
                    checkSpot = [(x - 1, y), (x, y + 1)]

                else:
                    checkSpot = [(x - 1, y), (x, y - 1)]

                # 로봇이 object spot에 도달하지 못하는 형태로 hidden hazard spot이 생성되었을 때, 지워질 hidden hazard spot을 뽑는다.
                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum = 2

            elif x == 0 or x == mapWidth:
                if x == 0:
                    checkSpot = [(x + 1, y), (x, y - 1), (x, y + 1)]

                else:
                    checkSpot = [(x - 1, y), (x, y - 1), (x, y + 1)]

                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum = 3

            elif y == 0 or y == mapHeight:
                if y == 0:
                    checkSpot = [(x, y + 1), (x - 1, y), (x + 1, y)]

                else:
                    checkSpot = [(x, y - 1), (x - 1, y), (x + 1, y)]

                tobeRemovedSpot = random.sample([item for item in checkSpot if item not in visibleHazardSpot], 1)[0]
                hsNum = 3

            if (len(totalHazardSpot) - len([item for item in totalHazardSpot if item not in checkSpot])) == hsNum:
                hiddenHazardSpot.remove(tobeRemovedSpot)

        # 무작위로 생성한 color blob spot과 hidden hazard spot이 겹치지는 않는지 확인한다.
        assert len([item for item in hiddenHazardSpot if item in hiddenCbSpot]) == 0

        MapData.setHiddenData(hiddenHazardSpot, hiddenCbSpot)