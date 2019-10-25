import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_socket import *

LINK_CP_ROUNDNESS = 100

class QDMGraphicsLink(QGraphicsPathItem):
  def __init__(self,link,parent=None):
    super().__init__(parent)

    self.link = link

    self._color = QColor('#001000')
    self._color_selected = QColor('#00ff00')
    self._pen = QPen(self._color)
    self._pen_selected = QPen(self._color_selected)
    self._pen_dragging = QPen(self._color)
    self._pen_dragging.setStyle(Qt.DashLine)
    self._pen.setWidthF(2.0)
    self._pen_selected.setWidthF(2.0)
    self._pen_dragging.setWidthF(2.0)

    self.setFlag(QGraphicsItem.ItemIsSelectable)

    self.posStart = [0,0]
    self.posEnd = [200,100]

    self.setZValue(-1)

  def setStartSocket(self,x,y):
    self.posStart = [x,y]

  def setEndSocket(self,x,y):
    self.posEnd = [x,y]  

  def boundingRect(self):
    return self.shape().boundingRect()  

  def shape(self):
    return self.calcPath()  

  def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
    self.setPath(self.calcPath())

    if self.link.end_socket is None :
      painter.setPen(self._pen_dragging)
    else:  
      painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
    painter.setBrush(Qt.NoBrush)
    painter.drawPath(self.path())

  def intersectsWith(self,p1,p2): 
    cutpath = QPainterPath(p1)
    cutpath.lineTo(p2)
    path = self.calcPath() 
    return cutpath.intersects(path)

  def calcPath(self):
    raise NotImplemented('This method has to be overridden in a child class')  

class QDMGraphicsLinkDirect(QDMGraphicsLink):
  """docstring for QDMGraphicLinkDirect"""
  def calcPath(self):
    path = QPainterPath(QPointF(self.posStart[0],self.posStart[1]))
    path.lineTo(self.posEnd[0],self.posEnd[1])
    return path
    # self.setPath(path)

class QDMGraphicsLinkBezier(QDMGraphicsLink):
  """docstring for QDMGraphicLinkCubic"""

  def calcPath(self):
    s = self.posStart
    e = self.posEnd

    dist = (e[0]-s[0]) * 0.5
    
    cpx_s = +dist
    cpx_e = -dist
    cpy_s = 0
    cpy_e = 0

    if self.link.start_socket is not None:
      sspos = self.link.start_socket.position

      if (s[0]>e[0] and sspos in (RIGHT_TOP,RIGHT_BOTTOM) or (s[0]<e[0] and sspos in (LEFT_TOP,LEFT_BOTTOM))):
        cpx_e *= -1
        cpx_s *= -1

        cpy_e = (
          (s[1]-e[1])/math.fabs(
            (s[1]-e[1]) if (s[1]-e[1]) != 0 else 0.00001 
            )
        ) * LINK_CP_ROUNDNESS

        cpy_s = (
          (e[1]-s[1])/math.fabs(
            (e[1]-s[1]) if (e[1]-s[1]) != 0 else 0.00001 
            )
        ) * LINK_CP_ROUNDNESS

    path = QPainterPath(QPointF(self.posStart[0],self.posStart[1]))
    path.cubicTo(s[0] + cpx_s, s[1] + cpy_s, e[0] + cpx_e, e[1] + cpy_e, self.posEnd[0], self.posEnd[1])
    # self.setPath(path)
    return path










            
