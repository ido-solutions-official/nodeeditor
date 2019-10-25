import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QDMGraphicScene(QGraphicsScene):
  def __init__(self,scene, parent=None):
    super().__init__(parent)

    self.scene = scene

    # settings
    self.gridSize = 20
    self.gridSquare = 5

    self._color_background = QColor('#393939')
    self._color_light = QColor('#2f2f2f')
    self._color_dark = QColor('#292929')

    self._pen_light = QPen(self._color_light)
    self._pen_light.setWidth(1)

    self._pen_dark = QPen(self._color_dark)
    self._pen_dark.setWidth(2)

    self.scene_width,self.scene_height = 64000,64000


    self.setBackgroundBrush(self._color_background)
    # self.selectionChanged.connect(self.onSelectionChanged)

  def onSelectionChanged(self):
    view = self.views()[0]
    print('Selection Chaned')

  def setGrScene(self,w ,h):
    self.setSceneRect(-w/2,-h/2,w,h)
    

  def drawBackground(self,painter,rect):
    super().drawBackground(painter,rect)

    # grid settings
    left = int(math.floor(rect.left()))
    right = int(math.ceil(rect.right()))
    top = int(math.floor(rect.top()))
    bottom = int(math.ceil(rect.bottom()))

    first_left = left - (left % self.gridSize)
    # print(first_left)
    first_top = top - (top % self.gridSize)
    # print(first_top)
    lines_light, lines_dark= [],[]
    for x in range(first_left,right,self.gridSize):
      if (x % (self.gridSize*self.gridSquare) != 0): lines_light.append(QLineF(x, top, x, bottom));
      else : lines_dark.append(QLineF(x, top, x, bottom));

    for y in range(first_top,bottom,self.gridSize):
      if (y % (self.gridSize*self.gridSquare) != 0): lines_light.append(QLineF(left, y, right, y)) ;
      else : lines_dark.append(QLineF(left, y, right, y)); 

    # draw the line
    painter.setPen(self._pen_light)
    painter.drawLines(lines_light)

    painter.setPen(self._pen_dark)
    painter.drawLines(lines_dark)
    