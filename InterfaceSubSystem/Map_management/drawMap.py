import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import time
import numpy as np
from abc import *

class IDrawMap(metaclass=ABCMeta):
    def drawInitialMap(self, curPosition, curDirection, path):
        pass

    def eraseAndDrawImage(self, spot, imageInstanceList, imagePath):
        pass

    def getCanvas(self):
        pass

    def getHiddenSpotInstance(self):
        pass

    def drawRobot(self):
        pass

    def drawPath(self):
        pass

class DrawMap(IDrawMap):
    '''
        robotImage : 맵에 로봇의 이미지를 그리는 AnnotationBBox 객체 저장. 움직임을 표현할 때 이전 위치의 이미지를 지우기 위해 사용
        arrowImage : 맵에 화살표를 그리는 AnnotationBBox 객체 저장. 움직임을 표현할 때 이전 위치의 이미지를 지우기 위해 사용
        drawedLines : 기존에 그려 놓은 경로 객체를 저장하는 리스트
        enlarge : 맵의 가로, 세로 길이가 모두 10을 넘으면 맵을 확대해서 보여준다.
    '''

    def __init__(self, mapSize, curPosition, curDirection, hazardSpot, objectSpot, hiddenHazardSpot,
                 hiddenColorBlobSpot, path):
        self.mapSize = mapSize
        self.hazardSpot = hazardSpot
        self.objectSpot = objectSpot
        self.hiddenHazardSpot = hiddenHazardSpot
        self.hiddenColorBlobSpot = hiddenColorBlobSpot

        self.robotImage = None
        self.arrowImage = None
        self.drawedLines = []
        self.enlarge = False
        if self.mapSize[0] > 10 and self.mapSize[1] > 10: self.enlarge = True
        self.drawInitialMap(curPosition, curDirection,
                            path)  # 창에 넣을 맵을 matplotlib을 이용해 만들고 로봇, 초기 경로, hazard spot, object spot을 그린다. 만든 맵은 canvas에 담아 PyQt5로 만든 창에 넣는다.

    '''
        --drawInitialMapIcon()에 선언된 클래스 변수 설명--
        
        objectSpotInstance : Object spot을 그릴 때 나오는 AnnotationBBox 객체를 저장한다. 방문한 object spot을 맵 상에서 지울 때 사용
        hiddenHazardSpotInstance : 숨겨진 hazard spot을 투명하게 그릴 때 나오는 AnnotationBBox 객체를 저장한다. 발견했을 때 지우고 투명하지 않은 그림으로 대체하기 위해 사용
        hiddenColorBlobSpotInstance : 숨겨진 color blob spot을 투명하게 그릴 때 나오는 AnnotationBBox 객체를 저장한다. 발견했을 때 지우고 투명하지 않은 그림으로 대체하기 위해 사용
    '''

    def _drawInitialMapIcon(self):
        self.objectSpotInstance = []
        self.hiddenHazardSpotInstance = []
        self.hiddenColorBlobSpotInstance = []

        for hazardSpot in self.hazardSpot:  # 맵 정보로 주어진 hazard spot을 맵에 표시한다.
            self._drawImage(hazardSpot[0], hazardSpot[1], 'image/skull.png')

        for objSpot in self.objectSpot:  # 맵 정보로 주어진 object spot을 맵에 표시한다.
            self.objectSpotInstance.append((objSpot, self._drawImage(objSpot[0], objSpot[1], 'image/star.png')))

        for hiddenHSpot in self.hiddenHazardSpot:  # 무작위로 생성된 hidden hazard spot을 맵에 흐리게 표시한다.
            self.hiddenHazardSpotInstance.append(
                (hiddenHSpot, self._drawImage(hiddenHSpot[0], hiddenHSpot[1], 'image/skull_dim.png')))

        for hiddenCBSpot in self.hiddenColorBlobSpot:  # 무작위로 생성된 color blob spot을 맵에 흐리게 표시한다.
            self.hiddenColorBlobSpotInstance.append(
                (hiddenCBSpot, self._drawImage(hiddenCBSpot[0], hiddenCBSpot[1], 'image/splash_dim.png')))

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
        self._drawBorder()  # 맵 외곽선을 그린다.
        self.drawRobot(curPosition, curDirection)  # 맵 상에 로봇을 그린다.
        self._drawInitialMapIcon()
        self.drawPath(path)  # MapData 클래스에 저장된 경로 정보를 바탕으로 맵 상에 경로를 그린다.

        if self.enlarge:  # 맵 가로, 세로 길이 둘 다 10 초과
            plt.xlim(-3 + curPosition[0], 4 + curPosition[0])
            plt.xticks(np.arange(-3 + curPosition[0], 4 + curPosition[0], step=1))
            plt.ylim(-3 + curPosition[1], 4 + curPosition[1])
            plt.yticks(np.arange(-3 + curPosition[1], 4 + curPosition[1], step=1))

        else:
            plt.xlim(-1, self.mapSize[0] + 1)
            plt.xticks(np.arange(-1, self.mapSize[0] + 1, step=1))
            plt.ylim(-1, self.mapSize[1] + 1)
            plt.yticks(np.arange(-1, self.mapSize[1] + 1, step=1))

    def _drawBorder(self):  # 맵의 외곽선을 그린다.
        plt.plot([self.mapSize[1]] * (self.mapSize[0] + 1), 'k', lineWidth=5)  # 위
        plt.plot([0] * (self.mapSize[0] + 1), 'k', lineWidth=5)  # 아래
        plt.plot([0] * (self.mapSize[1] + 1), range(self.mapSize[1] + 1), 'k', lineWidth=5)  # 왼쪽
        plt.plot([self.mapSize[0]] * (self.mapSize[1] + 1), range(self.mapSize[1] + 1), 'k', lineWidth=5)  # 오른쪽

    # imageScatter : 맵 상의 좌표 (x, y)에 경로 image에 있는 이미지 파일을 그린다.
    def _imageScatter(self, x, y, image, zoom=1, ax=None):
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
    def _drawImage(self, x, y, imagePath):
        return self._imageScatter(x, y, imagePath, zoom=0.1, ax=self.mapScreen)

    # eraseAndDrawImage(self, spot, imageInstanceList, imagePath) : 기존에 spot 위치에 있던 이미지를 지우고 imagePath에 있는 이미지로 대체한다.
    def eraseAndDrawImage(self, spot, imageInstanceList, imagePath):
        for imageSpot, imageInstance in imageInstanceList:
            if tuple(spot) == imageSpot:
                imageInstance.remove()
                self._drawImage(spot[0], spot[1], imagePath)
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                return

    #drawRobot : 로봇의 위치를 바탕으로 로봇을 맵에 그린다. enlarge 값이 True일 경우 맵을 확대해서 표시한다.
    def drawRobot(self, position, direction):
        arrowDirection = [(0, 0.7), (0.4, 0), (0, -0.7), (-0.4, 0)]
        arrowFileName = ['image/up.png', 'image/right.png', 'image/down.png', 'image/left.png']

        if self.robotImage:
            self.robotImage.remove()
            self.arrowImage.remove()

        self.robotImage = self._drawImage(position[0], position[1], 'image/robot.png')
        self.arrowImage = self._drawImage(position[0] + arrowDirection[direction][0],
                                         position[1] + arrowDirection[direction][1],
                                         arrowFileName[direction])

        if self.enlarge:  # 맵 가로, 세로 길이 둘 다 10 초과
            plt.xlim(-3 + position[0], 4 + position[0])
            plt.xticks(np.arange(-3 + position[0], 4 + position[0], step=1))

            plt.ylim(-3 + position[1], 4 + position[1])
            plt.yticks(np.arange(-3 + position[1], 4 + position[1], step=1))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    # drawPath(self, path) : 로봇이 지나갈 경로를 맵 상에 그린다.
    def drawPath(self, path):
        if len(self.drawedLines) != 0:
            self._removePath()
        dist = (0, 0)
        i = 1
        while True:
            if i == len(path): break
            prev = path[i - 1]
            next = path[i]
            dist = (next[0] - prev[0], next[1] - prev[1])
            while i < len(path) - 1 and dist == (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]):
                i += 1
                next = path[i]

            x = next[0] - prev[0]
            y = next[1] - prev[1]
            if (x == 0):
                if (prev[1] < next[1]):
                    lines = self.mapScreen.plot([prev[0]] * (y + 1), np.linspace(prev[1], next[1], y + 1), 'r',
                                                linewidth=5)
                else:
                    lines = self.mapScreen.plot([prev[0]] * (-(y - 1)), np.linspace(next[1], prev[1], -(y - 1)), 'r',
                                                linewidth=5)
            else:
                if (prev[0] < next[0]):
                    lines = self.mapScreen.plot(np.linspace(prev[0], next[0], x + 1), [prev[1]] * (x + 1), 'r',
                                                linewidth=5)

                else:
                    lines = self.mapScreen.plot(np.linspace(next[0], prev[0], -(x - 1)), [path[i][1]] * -(x - 1), 'r',
                                                linewidth=5)
            self.drawedLines += lines  # Memorize current path plot object.
            prev = path[i]
            i += 1

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def _removePath(self):
        for i in range(0, len(self.mapScreen.lines)):
            self.mapScreen.lines[0].remove()
        self._drawBorder()

    # PyQt5의 창에 맵을 추가하기 위해 canvas 객체를 리턴한다.
    def getCanvas(self):
        return self.canvas

    def getHiddenSpotInstance(self):
        return self.hiddenHazardSpotInstance, self.hiddenColorBlobSpotInstance, self.objectSpotInstance

