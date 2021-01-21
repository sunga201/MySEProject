from Database.mapAndPathData import MapData
from InterfaceSubSystem.Window_design_management.window import WindowDesign
from InterfaceSubSystem.Map_data_management.saveData import SaveData
from InterfaceSubSystem.Map_data_management.showMapData import ShowMapData
from InterfaceSubSystem.Show_robot_transfer_process.showRobotMovement import ShowRobotMovement
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QCoreApplication, Qt, QRect, QAbstractAnimation
import sys
import numpy as np

CLOSE=1
NOT_CLOSE=0

class ShowMenu(WindowDesign):
    def __init__(self):
        super().__init__()
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

        subLabel = self.makeLabel(['- - - - - version 1.0 - - - - -'])
        self.setCustomStyleSheet(subLabel, "font: 14pt \"Bahnschrift SemiBold\";\n"
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
            testAtt=MapData.getMapSize() #저장된 맵 데이터가 있는지 확인한다.
        except AttributeError:
            self.showMessage('error', 'map data doesn\'t exist.', NOT_CLOSE)
            return

        self.smd=ShowMapData()

    def showRobotMovement(self): # Show robot mavement 버튼을 눌렀을 때 ShowRobotMovement 클래스의 인스턴스를 생성한다.
        try:
            testAtt=MapData.getMapSize() #저장된 맵 데이터가 있는지 확인한다.
        except AttributeError:
            self.showMessage('error', 'map data doesn\'t exist.', NOT_CLOSE)
            return

        self.srm=ShowRobotMovement()

if __name__=='__main__':
    app=QApplication(sys.argv)
    ex=ShowMenu()
    sys.exit(app.exec_())