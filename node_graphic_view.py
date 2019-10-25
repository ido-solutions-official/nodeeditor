from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_graphic_socket import QDMGraphicsSocket
from node_graphic_link import QDMGraphicsLink
from node_graphic_node import QDMGraphicNode
from node_link import *
from node_graphic_cutline import QDMCutline

DEBUG = True

# define hex key
# Qt.Key_Delete = 0x1000007

# define mode
MODE_NONE = 1
MODE_LINK_DRAG = 2
MODE_LINK_CUT = 3

LINK_DRAG_START_THRES = 10

class QDMGraphicView(QGraphicsView):
  scenePosChanged = pyqtSignal(int,int)

  def __init__(self, grScene, parent=None):
    super().__init__(parent)
    self.grScene = grScene

    self.initUIV()
    
    self.setScene(self.grScene)

    self.mode = MODE_NONE
    self.editingFlag = False
    self.rubberBandFlag = False

    self.zoomClamp = True
    self.zoomInFactor = 1.25
    self.zoom = 10
    self.zoomStep = 1
    self.zoomRange = [0,8]

    # cutline
    self.cutline = QDMCutline()
    self.grScene.addItem(self.cutline)
  
  def initUIV(self):
    self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
    self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
    self.setDragMode(QGraphicsView.RubberBandDrag)

  def mousePressEvent(self,event):
    if event.button() == Qt.MiddleButton:
      self.middleMouseButtonPress(event)
    elif event.button() ==  Qt.LeftButton:
      self.leftMouseButtonPress(event)
    elif event.button() ==  Qt.RightButton:
      self.rightMouseButtonPress(event)
    else :
      super().mousePressEvent(event)

  def mouseReleaseEvent(self,event):
    if event.button() == Qt.MiddleButton:
      self.middleMouseButtonRelease(event)
    elif event.button() == Qt.LeftButton:
      self.leftMouseButtonRelease(event)
    elif event.button() ==  Qt.RightButton:
      self.rightMouseButtonRelease(event)  
    else :
      super().mouseReleaseEvent(event)  

  def middleMouseButtonPress(self,event):
    releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(),event.screenPos(),
                               Qt.LeftButton, Qt.NoButton, event.modifiers())
    super().mouseReleaseEvent(releaseEvent)
    self.setDragMode(QGraphicsView.ScrollHandDrag)

    fakeEvent = QMouseEvent(event.type(),event.localPos(),event.screenPos(),
                            Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
    super().mousePressEvent(fakeEvent)

  def middleMouseButtonRelease(self,event):

    fakeEvent = QMouseEvent(event.type(),event.localPos(),event.screenPos(),
                            Qt.LeftButton, event.buttons() & ~Qt.LeftButton , event.modifiers())
    super().mouseReleaseEvent(fakeEvent)   
    self.setDragMode(QGraphicsView.RubberBandDrag)

  def leftMouseButtonPress(self,event):
    if DEBUG: print('left button click')

    item = self.getItemAtClick(event)

    self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

    # multiple selection
    if hasattr(item,'node') or (item is None) or isinstance(item,QDMGraphicsLink):
      if event.modifiers() & Qt.ShiftModifier:
        print('LMB + Shift on:',item)
        event.ignore()
        fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                               Qt.LeftButton, event.buttons()|Qt.LeftButton,
                               event.modifiers()|Qt.ControlModifier)
        super().mousePressEvent(fakeEvent)
        return

    # drag item
    if type(item) is QDMGraphicsSocket:
      if self.mode == MODE_NONE:
        self.linkDragStart(item)
        self.mode = MODE_LINK_DRAG
        return

    if self.mode == MODE_LINK_DRAG:
      res = self.linkDragEnd(item)
      if res: return

    # click on empty space 
    if item is None:
      # cutline
      if event.modifiers() == Qt.ControlModifier:

        self.mode = MODE_LINK_CUT
        fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        QApplication.setOverrideCursor(Qt.CrossCursor)
        return

      else:
        self.rubberBandFlag = True

    if self.dragMode() == QGraphicsView.RubberBandDrag:
      self.grScene.scene.history.storeHistory('selection changed')  


    super().mousePressEvent(event)    

  def rightMouseButtonPress(self,event):
    if DEBUG: print('right button click')

    item = self.getItemAtClick(event)

    if isinstance(item, QDMGraphicsLink): print('rmb debug:', item.link, 'connecting socket',
                                       item.link.start_socket, '<-->',item.link.end_socket) 
    if type(item) is QDMGraphicsSocket: print('rmb debug:', item.socket, 'has link', item.socket.link)

    if isinstance(item, QDMGraphicNode): print('rmb debug:', item.node)

    if item is None:
      print('Scene:')
      print(' Node:')
      for node in self.grScene.scene.nodes: print('   ',node)
      print(' Link:')
      for link in self.grScene.scene.links: print('   ',link)


    super().mousePressEvent(event)
    
    
  def leftMouseButtonRelease(self,event):

    item = self.getItemAtClick(event)

    if hasattr(item,'node') or (item is None) or isinstance(item,QDMGraphicsLink):
      if event.modifiers() & Qt.ShiftModifier:
        print('LMB release + Shift on:',item)
        event.ignore()
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                               Qt.LeftButton, Qt.NoButton,
                               event.modifiers()|Qt.ControlModifier)
        super().mouseReleaseEvent(fakeEvent)
        return

    if self.mode == MODE_LINK_DRAG:

      if self.distanceClickOff(event): 
        res = self.linkDragEnd(item)
        if res: return

    if self.mode == MODE_LINK_CUT:
    
      self.cutIntersectLink()
      self.cutline.line_points = []     
      self.cutline.update()
      QApplication.setOverrideCursor((Qt.ArrowCursor))
      self.mode = MODE_NONE
      return

    if self.rubberBandFlag:
      self.grScene.scene.history.storeHistory('selection changed')  
      self.rubberBandFlag = False
        

    super().mouseReleaseEvent(event)

  def rightMouseButtonRelease(self,event):
    super().mouseReleaseEvent(event) 

  def mouseMoveEvent(self, event):
    if self.mode == MODE_LINK_DRAG:
      pos = self.mapToScene(event.pos())
      self.dragLink.grLink.setEndSocket(pos.x(), pos.y())
      self.dragLink.grLink.update()

    if self.mode == MODE_LINK_CUT:
      pos = self.mapToScene(event.pos())
      self.cutline.line_points.append(pos)
      self.cutline.update()

    self.last_scene_mouse_position = self.mapToScene(event.pos())  

    self.scenePosChanged.emit(
      int(self.last_scene_mouse_position.x()),int(self.last_scene_mouse_position.y())
    )  
     

    super().mouseMoveEvent(event)

  def keyPressEvent(self, event):
    '''
    some were override in node_editor_window.py
      # if (event.key() == Qt.Key_Delete) or (event.key() == Qt.Key_Backspace): 
      #   if not self.editingFlag:
      #     self.deleteSelected()
      #   else:
      #     super().keyPressEvent(event) 
      # elif (event.key() == Qt.Key_S) and (event.modifiers() & Qt.ControlModifier):
      #   self.grScene.scene.saveToFile('untitled.nd')
      # elif (event.key() == Qt.Key_1):
      #   self.grScene.scene.history.storeHistory("Item A")
      # elif (event.key() == Qt.Key_Z) and (event.modifiers() & Qt.ControlModifier):
      #   self.grScene.scene.history.undo()
      # elif (event.key() == Qt.Key_Y) and (event.modifiers() & Qt.ControlModifier):
      #   self.grScene.scene.history.redo() 
    '''
    if DEBUG:print('grView:: Key Press',event.key())
    if (event.key() == Qt.Key_H):
      print('node_graphic_view :: HS',self.grScene.scene.history.history_stack)
      print('node_graphic_view :: current step',self.grScene.scene.history.history_current_step)
      ix = 0
      for item in self.grScene.scene.history.history_stack:
        print('#',ix, '--', item['description'])
        
    super().keyPressEvent(event)

  def cutIntersectLink(self):

    for ix in range(len(self.cutline.line_points) - 1):
      p1 = self.cutline.line_points[ix] # QPointF
      p2 = self.cutline.line_points[ix + 1]

      for link in self.grScene.scene.links:
        if link.grLink.intersectsWith(p1,p2):
          link.remove()  

    self.grScene.scene.history.storeHistory('Delete cutted links',setModified=True)      

  def deleteSelected(self):
    for item in self.grScene.selectedItems():    
      if isinstance(item, QDMGraphicsLink):
        item.link.remove()
      elif hasattr(item,'node'):
        item.node.remove()  

    self.grScene.scene.history.storeHistory('Deleted selected',setModified=True)    
      

  def debug_modifiers(self, event):
    out = "MODS: "
    if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
    if event.modifiers() & Qt.ControlModifier: out += "CRTL " 
    if event.modifiers() & Qt.AltModifier: out += "ALT "
    # if event.modifiers() & Qt.ShiftModifier: out += "CMD "
    return out       

      

  def getItemAtClick(self, event):
    '''return object when lmb on the target'''
    pos = event.pos()
    obj = self.itemAt(pos)
    return obj  

  def wheelEvent(self, event): 
    '''override wheel event'''
    # calculate zoom factor   
    zoomOutFactor = 1 / self.zoomInFactor

    # store scene position

    # calculate zoom
    if event.angleDelta().y() > 0:
      zoomFactor = self.zoomInFactor
      self.zoom += self.zoomStep
    else:
      zoomFactor = zoomOutFactor
      self.zoom -= self.zoomStep

    clamped = False
    if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
    if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True   

    if not clamped or self.zoomClamp is False:
      self.scale(zoomFactor, zoomFactor)  

  def linkDragStart(self, item):  
    print('Start dragging link')
    print('  assign start socket to:',item.socket)
    self.previousLink = item.socket.link
    self.last_start_socket = item.socket
    self.dragLink = Link(self.grScene.scene, item.socket, None, LINK_TYPE_BEIZER)
    print('  dragLink:',self.dragLink)   

  def linkDragEnd(self, item):  
    self.mode = MODE_NONE
    if type(item) is QDMGraphicsSocket:
      if item.socket != self.last_start_socket:
        print('  previous link', self.previousLink)
        if item.socket.hasLink():
          item.socket.link.remove()
        print('  assign end socket', item.socket)
        if self.previousLink is not None: self.previousLink.remove()
        print('  previous link remove', item.socket)
        self.dragLink.start_socket = self.last_start_socket
        self.dragLink.end_socket = item.socket
        self.dragLink.start_socket.setConnectedLink(self.dragLink)
        self.dragLink.end_socket.setConnectedLink(self.dragLink)
        print('reassign start & end to drag edge')
        self.dragLink.updateLinkPositions()
        self.grScene.scene.history.storeHistory('Create new link(Dragging)',setModified=True)
        return True

    print('End dragging link')
    self.dragLink.remove()
    self.dragLink = None  
    print('about to set socket on previous edge', self.previousLink)
    if self.previousLink is not None:
      self.previousLink.start_socket.link = self.previousLink

    return False       

  def distanceClickOff(self,event):
    '''measure distance between click and release'''
    new_lmb_release_scene_pos = self.mapToScene(event.pos())
    delta = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
    x = delta.x(); y = delta.y(); dist_sq = x*x + y*y
    return dist_sq > LINK_DRAG_START_THRES*LINK_DRAG_START_THRES    





