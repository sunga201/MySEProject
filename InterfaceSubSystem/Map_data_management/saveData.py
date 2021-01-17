from Database.mapAndPathData import MapData
from InterfaceSubSystem.Window_design_management.window import WindowDesign
from PyQt5.QtWidgets import *

CLOSE=1
NOT_CLOSE=0

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
            self.showMessage('error', 'Please check map data again.', NOT_CLOSE)
            return
        try: # 입력된 데이터에서 괄호와 쉼표를 분리한다.
            mapSize=mapSize.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            start = start.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            spot = spot.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
            hazard = hazard.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
        except: #괄호, 쉼표 외에 다른 문자가 들어있는 경우 에러 발생
            self.showMessage('error', 'Please check map data again.', NOT_CLOSE)
            return

        #int로 parsing
        mapSize=tuple(map(int, mapSize))
        start=tuple(map(int, start))
        spot=list(map(int, spot))
        hazard=list(map(int, hazard))

        isErr, objectSpot, hazardSpot=self.inputValueCheck(mapSize, start, spot, hazard)

        if isErr: # 입력 오류 발생
            self.showMessage('error', 'Please check map data again.', NOT_CLOSE)
            return

        MapData(mapSize, start, objectSpot, hazardSpot)
        self.showMessage('notice', 'Save Completed.', CLOSE) # 저장 완료 메시지를 띄우고, 메시지의 ok 버튼을 누르면 입력창이 닫힌다.

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

        # start spot이 map 크기를 넘어가거나 hazard spot 리스트 또는 object spot 리스트에 속하면 입력 오류
        if start in hazardSpot or start in objectSpot or start[0] < 0 or start[0] > mapSize[0] or start[1] < 0 or start[1] > mapSize[1]:
            isErr = True

        return isErr, objectSpot, hazardSpot