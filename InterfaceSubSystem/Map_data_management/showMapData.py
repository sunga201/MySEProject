from Database.mapAndPathData import MapData
from InterfaceSubSystem.Window_design_management.window import WindowDesign
from PyQt5.QtWidgets import *
# 현재 시스템에 저장중인 맵 데이터를 보여주는 창을 띄워주는 클래스
class ShowMapData(WindowDesign):
    def __init__(self):
        super().__init__()

        self.mapSize=MapData.getMapSize()
        self.startSpot=MapData.getStartSpot()
        self.objectSpot=MapData.getObjectSpot()
        self.hazardSpot=MapData.getHazardSpot()
        self.design()

    def design(self):
        # 디자인 코드 시작
        self.setWindowDesign("Show map data", 'image/titleIcon.png', 500, 500, 500, 200)

        labelNameList = ['Map size : ', 'Start spot : ', 'Object spot : ', 'Hazard spot : ']
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