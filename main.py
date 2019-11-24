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