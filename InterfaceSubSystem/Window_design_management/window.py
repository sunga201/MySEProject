from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QCoreApplication, Qt, QRect, QAbstractAnimation
from abc import *

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

class IDesign(metaclass=ABCMeta):
    def setWindowDesign(self, title, image, width, height, xPos=0, yPos=0):
        pass

    def makeLabel(self, labelNameList):
        pass

    def makeTextLine(self, num, isEditable, baseText=['']):
        pass

    def setLayoutOnGroupBox(self, title, customLayout):
        pass

    def makeButton(self, name, clickFunction):
        pass

    def setCustomStyleSheet(self, widget, styleSheet):
        pass

    def addWidgetOnLayout(self, layout, widget, *x):
        pass

    def addLayoutOnLayout(self, baseLayout, addLayout, ratio=1):
        pass

    def showMessage(self, head, message, toggle):
        pass

    def design(self):
        pass

class FinalMeta(type(QWidget), type(IDesign)):
    pass

class WindowDesign(QWidget, IDesign, metaclass=FinalMeta): # 새 창을 띄우는 클래스들은 전부 이 클래스를 상속받아서 사용한다.
    def __init__(self):
        super().__init__()

    def setWindowDesign(self, title, image, width, height, xPos=0, yPos=0):
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(image))
        self.move(xPos, yPos)  # 창이 화면 왼쪽 위에서 xPos만큼 아래에, yPos만큼 오른쪽에 위치해 있다.
        self.resize(height, width)  # 창의 세로, 가로 길이

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

    def _makeGroupBox(self, title): # 이 클래스 안에서만 사용된다.
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

    def showMessage(self, head, message, toggle): #정적 메소드, 객체 object에 제목이 head이고 message로 이루어진 메시지 박스를 띄운다.
                                                    # toggle은 메시지 박스를 띄운 창을 닫을지, 닫지 않을 지를 결정함.
        msg = QMessageBox.question(self, head, message, QMessageBox.Ok)
        if toggle: self.close()

    @abstractmethod
    def design(self):
        pass