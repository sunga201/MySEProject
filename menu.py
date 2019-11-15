#import control_robot
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import tkinter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

class Map_data: #static class
    def __init__(self, map_size, start_spot, object_spot, hazard_spot):
        Map_data.map_size=map_size
        Map_data.start_spot=start_spot
        Map_data.object_spot=object_spot
        Map_data.hazard_spot=hazard_spot
        Map_data.hazard_spot_h=[]
        Map_data.color_blob_h=[]

    def set_hidden_data(hazard, cb):
        Map_data.hazard_spot_h.append(hazard)
        Map_data.color_blob_h.append(cb)

    def get_hazard_h():
        return Map_data.hazard_spot_h

    def get_cb_h():
        return Map_data.color_blob_h

    def get_map_size():
        return Map_data.map_size

    def get_start_spot():
        return Map_data.start_spot

    def get_object_spot():
        return Map_data.object_spot

    def get_hazard_spot():
        return Map_data.hazard_spot

    def remove_hidden_spot(point):
        for h in Map_data.hazard_spot_h:
            if point==h:
                Map_data.hazard_spot_h.remove(h)


class Save_data(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Save data")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.move(500, 200)  # horizontal, vertical
        self.resize(500, 500)  # width, height

        map_label = QLabel("Map : ")
        start_label = QLabel("Start : ")
        spot_label = QLabel("Object : ")
        hazard_label = QLabel("Hazard : ")
        self.map_line = QLineEdit("")
        self.start_line = QLineEdit("")
        self.spot_line = QLineEdit("")
        self.hazard_line = QLineEdit("")

        ok_button = QPushButton('Save', self)
        ok_button.clicked.connect(self.map_data_save)
        cancel_button = QPushButton('cancel', self)
        cancel_button.clicked.connect(self.close)

        layout1 = QGridLayout()
        layout1.addWidget(map_label, 0, 0)
        layout1.addWidget(self.map_line, 0, 1)
        layout1.addWidget(start_label, 1, 0)
        layout1.addWidget(self.start_line, 1, 1)
        layout1.addWidget(spot_label, 2, 0)
        layout1.addWidget(self.spot_line, 2, 1)
        layout1.addWidget(hazard_label, 3, 0)
        layout1.addWidget(self.hazard_line, 3, 1)
        layout1.addWidget(ok_button, 4, 0)
        layout1.addWidget(cancel_button, 4, 1)

        self.setLayout(layout1)
        self.show()

    def map_data_save(self):
        map_size=self.map_line.text()
        start=self.start_line.text()
        spot=self.spot_line.text()
        hazard=self.hazard_line.text()

        if map_size=='' or start=='' or spot=='' or hazard=='':
            self.show_message('Please check map data again.', False)
            return

        map_size=map_size.replace('(', ' ').replace(')', ' ').split()
        start = start.replace('(', ' ').replace(')', ' ').split()
        spot = spot.replace('(', ' ').replace(')', ' ').split()
        hazard = hazard.replace('(', ' ').replace(')', ' ').split()

        map_size=tuple(map(int, map_size))
        start=tuple(map(int, start))
        spot=list(map(int, spot))
        hazard=list(map(int, hazard))
        object_spot=[]
        for i in range(0, len(spot), 2):
            print(i)
            object_spot.append(tuple(spot[i:i+2]))

        hazard_spot=[]
        for i in range(0, len(hazard), 2):
            hazard_spot.append(tuple(hazard[i:i+2]))
        Map_data(map_size, start, object_spot, hazard_spot)
        self.show_message('Save Completed.', True)

    def show_message(self, message, toggle):
        msg = QMessageBox.question(self, 'error', message, QMessageBox.Ok)
        if toggle: self.close()

class Show_map_data(QWidget):
    def __init__(self):
        super().__init__()
        map_size=Map_data.get_map_size()
        start_spot=Map_data.get_start_spot()
        object_spot=Map_data.get_object_spot()
        hazard_spot=Map_data.get_hazard_spot()
        print(map_size, start_spot, object_spot, hazard_spot)

        self.setWindowTitle("Show map data")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.move(500, 200)  # horizontal, vertical
        self.resize(500, 500)  # width, height
        self.show()


class Show_result(QWidget):
    def __init__(self):
        super().__init__()
        np.random.seed(int(time.time()))
        #self.prev_position=Map_data.get_start_spot()
        self.map_size=(4, 5) # temp
        self.prev_position=(1, 2)# temp
        self.hazard_spot=[(1, 0), (3, 2)] # temp
        self.object_spot=[(4, 2), (1, 5)] # temp
        self.generate_random_spot()
        #self.add_on=comtrol_robot.Add_on();
        self.show_map()

    def show_map(self):
        #self.path=self.add_on.get_path()
        self.path=[(1, 2), (2, 2), (2, 3), (4, 3), (4, 2), (4, 5), (1, 5)]
        self.prev_direction=-1
        second_minus_first=self.path[1][0]-self.path[0][0], self.path[1][1]-self.path[0][1]
        if second_minus_first[0]==0:
            if second_minus_first[1]>0:
                self.direction=1
            else: self.direction=3
        else:
            if second_minus_first[0]>0:
                self.direction=2
            else: self.direction=4

        print(self.direction)
        self.setWindowTitle("Result")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.move(500, 100)  # horizontal, vertical
        self.resize(1000, 700)  # width, height

        self.fig=plt.figure()
        self.canvas=FigureCanvas(self.fig)
        plt.grid(True)
        plt.xlim(0, self.map_size[0]+1)
        plt.xticks(np.arange(0, self.map_size[0]+1, step=1), color='w')
        plt.ylim(0, self.map_size[1]+1)
        plt.yticks(np.arange(0, self.map_size[1]+1, step=1), color='w')

        plt.scatter(self.prev_position[0], self.prev_position[1], c='r', linewidths=5)
        for h in self.hazard_spot:
            plt.scatter(h[0], h[1], c='b')

        for o in self.object_spot:
            plt.scatter(o[0], o[1], c='y')

        self.path = [(1, 2), (2, 2), (2, 3), (4, 3), (4, 2), (4, 5), (3, 5), (3, 4), (1, 4), (1, 5)]
        self.draw_path()

        sub_layout1=QVBoxLayout()
        sub_layout1.addWidget(self.canvas)

        start_button = QPushButton('start', self)
        #start_button.clicked.connect(self.)
        return_button = QPushButton('return to menu', self)
        return_button.clicked.connect(self.close)

        sub_layout2 = QHBoxLayout()
        sub_layout2.addWidget(start_button)
        sub_layout2.addWidget(return_button)

        main_layout=QVBoxLayout()
        main_layout.addLayout(sub_layout1)
        main_layout.addLayout(sub_layout2)
        self.setLayout(main_layout)
        self.show()

    def generate_random_spot(self):
        '''hazard_num=np.random.randint(0, min((self.map_size[0]+self.map_size[1])/2, 100))
        cb_num=np.random.randint(0, min((self.map_size[0]+self.map_size[1])/2, 100))
        map_width = self.map_size[0]
        map_height=self.map_size[1]
        tmp_hazard=[]
        tmp_cb=[]

        already_used_point = self.hazard_spot + self.object_spot
        already_used_point.append(self.prev_position)

        hidden_point=[]
        for i in range(map_height):
            for j in range(map_width):
                hidden_point.append((i, j))

        for _ in range(hazard_num):
            tmp_hazard.append((np.random.randint(0, map_width), np.random.randint(0, map_height)));

        for _ in range(cb_num):
            tmp_cb.append((np.random.randint(0, map_width), np.random.randint(0, map_height)));

        print(already_used_point)

        for aup in already_used_point:
            for hp in tmp_hazard:
                if(aup==hp):
                    print("catched!!", aup, hp)
        print(hazard_num, cb_num)
        print(tmp_hazard, tmp_cb)'''

    def draw_path(self):
        for i in range(len(self.path)-1):
            print(self.path[i], self.path[i+1])
            x=self.path[i+1][0]-self.path[i][0]
            y=self.path[i+1][1]-self.path[i][1]

            if(x==0) :
                if(self.path[i][1]<self.path[i+1][1]) : plt.plot([self.path[i][0]]*(y+1), np.linspace(self.path[i][1], self.path[i+1][1], y+1), 'r', linewidth=5)
                else : plt.plot([self.path[i][0]]*(-(y-1)), np.linspace(self.path[i+1][1], self.path[i][1], -(y-1)), 'r', linewidth=5)
            else :
                print(x, y)
                if (self.path[i][0] < self.path[i + 1][0]):
                    plt.plot(np.linspace(self.path[i][0], self.path[i + 1][0], x + 1), [self.path[i][1]] * (x + 1), 'r',
                             linewidth=5)

                else:
                    print("i+1 : ", self.path[i+1][0], "i : ", self.path[i][0])
                    plt.plot(np.linspace(self.path[i+1][0], self.path[i][0], -(x - 1)), [self.path[i][1]] * -(x - 1), 'r',
                             linewidth=5)


class Show_menu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADD-ON System")
        self.setWindowIcon(QIcon('titleIcon.png'))
        self.move(500, 200)  # horizontal, vertical
        self.resize(500, 500)  # width, height

        title_label = QLabel('------ADD-ON System------')
        title_label.setAlignment(Qt.AlignCenter)
        font = title_label.font()
        font.setPointSize(15)
        title_label.setFont(font)

        save_button = QPushButton('Save data', self)
        save_button.clicked.connect(self.save_data)

        show_result_button = QPushButton('Show result', self)
        show_result_button.clicked.connect(self.show_result)
        show_data_button = QPushButton('Show map data', self)
        show_data_button.clicked.connect(self.show_map_data)

        quit_button = QPushButton('Quit', self)
        quit_button.clicked.connect(QCoreApplication.instance().quit)

        button_list = [save_button, show_result_button, show_data_button, quit_button]
        for bt in button_list:
            bt.setMinimumHeight(70)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)

        main_layout.addWidget(save_button)
        main_layout.addStretch(3)
        main_layout.addWidget(show_result_button)
        main_layout.addStretch(3)
        main_layout.addWidget(show_data_button)
        main_layout.addStretch(3)
        main_layout.addWidget(quit_button)
        main_layout.addStretch(3)
        self.setLayout(main_layout)
        self.show()

    def save_data(self):
        self.sd=Save_data()

    def show_map_data(self):
        try:
            test_att=Map_data.get_map_size()
        except AttributeError:
            self.show_message('map data doesn\'t exist.')
            return

        self.smd=Show_map_data()

    def show_result(self):
        '''try:
            test_att=Map_data.get_map_size()
        except AttributeError:
            self.show_message('map data doesn\'t exist.')
            return'''

        self.sr=Show_result()

    def show_message(self, message):
        msg = QMessageBox.question(self, 'error', message, QMessageBox.Ok)

    #def initUI(self):
        '''mapLabel=QLabel("Map Size    ")
        startLabel=QLabel("Start Point   ")
        spotLabel=QLabel("Object Spot ")
        hazardLabel=QLabel("Hazard Spot")
        mapLine=QLineEdit("")
        startLine=QLineEdit("")
        spotLine=QLineEdit("")
        hazardLine=QLineEdit("")
        layout1=QGridLayout()
        layout1.addWidget(mapLabel, 0, 0)
        layout1.addWidget(mapLine, 0, 1)
        layout1.addWidget(startLabel, 1, 0)
        layout1.addWidget(startLine, 1, 1)
        layout1.addWidget(spotLabel, 2, 0)
        layout1.addWidget(spotLine, 2, 1)
        layout1.addWidget(hazardLabel, 3, 0)
        layout1.addWidget(hazardLine, 3, 1)'''
        '''
        subLayout1=QHBoxLayout()
        subLayout1.addWidget(mapLabel)
        subLayout1.addWidget(mapLine)

        subLayout2 = QHBoxLayout()
        subLayout2.addWidget(startLabel)
        subLayout2.addWidget(startLine)

        subLayout3 = QHBoxLayout()
        subLayout3.addWidget(spotLabel)
        subLayout3.addWidget(spotLine)

        subLayout4 = QHBoxLayout()
        subLayout4.addWidget(hazardLabel)
        subLayout4.addWidget(hazardLine)

        layout1.addLayout(subLayout1)
        layout1.addLayout(subLayout2)
        layout1.addLayout(subLayout3)
        layout1.addLayout(subLayout4)
        '''
        '''gBox1=QGroupBox('input')
        #layout1.addWidget(gBox1)
        #self.lineEdit=QLineEdit("", self)
        #self.lineEdit.move(80, 20)
        #self.lineEdit.textChanged.connect(self.lineEditChanged)

        gBox1.setLayout(layout1)
        gBox2=QGroupBox('select')
        start_button=QPushButton('start')
        quit_button=QPushButton('Quit')
        start_button.clicked.connect(self.showGraph)
        quit_button.clicked.connect(QCoreApplication.instance().quit)
        layout2=QHBoxLayout()
        layout2.addWidget(start_button)
        layout2.addWidget(quit_button)

        layout=QVBoxLayout()
        layout.addWidget(gBox1)
        layout.addLayout(layout2)
        self.setLayout(layout)

        self.show()

    def showGraph(self):
        ax = plt.subplot()
        plt.subplot()
        ax.set_xlim([0, 7])
        ax.set_ylim([0, 9])
        # ax.plot([0,1], [0,0], color='red', linewidth=2) add path
        # plt.scatter(0,0, c='red', s=500) add dot
        ax.set_yticks([1, 2, 3, 4, 5], minor=True)
        ax.set_yticks([1, 2, 3, 4, 5], minor=True)
        ax.yaxis.grid(True, which='major')
        ax.xaxis.grid(True, which='major')

        plt.show()'''
