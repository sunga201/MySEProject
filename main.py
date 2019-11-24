import menu
import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import numpy as np
import matplotlib.pyplot as plt
import tkinter
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

app=QApplication(sys.argv)
ex=menu.ShowMenu()
sys.exit(app.exec_())

'''class ShowResult:
    def __init__(self):
        np.random.seed(int(time.time()))
        #self.prev_position=Map_data.get_start_spot()
        self.mapSize=(4, 5) # temp
        self.prevPosition=(1, 2)# temp
        self.hazardSpot=[(1, 0), (3, 2)] # temp
        self.objectSpot=[(4, 2), (1, 5)] # temp
        self.drawedLines = []
        #self.add_on=comtrol_robot.Add_on();
        self.showMap()

    def showMap(self):
        #self.path=self.add_on.get_path()
        self.path=[(1, 2), (2, 2), (2, 3), (4, 3), (4, 2), (4, 5), (1, 5)]
        self.prevDirection=-1
        checkDirection=self.path[1][0]-self.path[0][0], self.path[1][1]-self.path[0][1]
        if checkDirection[0]==0:
            if checkDirection[1]>0:
                self.direction=1
            else: self.direction=3
        else:
            if checkDirection[0]>0:
                self.direction=2
            else: self.direction=4

        print(self.direction)

        self.fig=plt.figure()
        self.mapScreen = self.fig.add_subplot(1, 1, 1)
        self.mapScreen.grid()
        self.canvas.draw()
        plt.xlim(0, self.mapSize[0]+1)
        plt.xticks(np.arange(0, self.mapSize[0]+1, step=1), color='w')
        plt.ylim(0, self.mapSize[1]+1)
        plt.yticks(np.arange(0, self.mapSize[1]+1, step=1), color='w')
        plt.ion()

        self.mapScreen.scatter(self.prevPosition[0], self.prevPosition[1], c='r', linewidths=5)
        for h in self.hazardSpot:
            plt.scatter(h[0], h[1], c='b')

        for o in self.objectSpot:
            plt.scatter(o[0], o[1], c='y')

        self.path = [(1, 2), (2, 2), (2, 3), (4, 3), (4, 2), (4, 5), (3, 5), (3, 4), (1, 4), (1, 5)]
        plt.show()
        self.drawPath()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        time.sleep(1)
        self.path = [(1, 2), (2, 2), (2, 3), (4, 3), (4, 2), (4, 5), (1, 5)]
        self.drawPath()
        self.fig.canvas.draw()

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

    def removePath(self):
        for i in range(len(self.mapScreen.lines)):
            self.mapScreen.lines[0].remove()

k=ShowResult()'''