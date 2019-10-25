from collections import OrderedDict
from node_serialize import Serializable
from node_graphic_link import *

LINK_TYPE_DIRECT = 1
LINK_TYPE_BEIZER = 2

DEBUG = False

class Link(Serializable):
  def __init__(self,scene, start_socket=None, end_socket=None, link_type=LINK_TYPE_DIRECT):
    '''
    start/end socket : socket id or socket obj ?
    '''
    super().__init__()
    self.scene = scene

    self.start_socket = start_socket
    self.end_socket = end_socket
    self.link_type = link_type
    self._link_type = link_type

    self.scene.addLink(self)

  def __str__(self):
    return '<Link id: {}>'.format(id(self))

  @property
  def start_socket(self):
    return self._start_socket
  
  @start_socket.setter
  def start_socket(self, value):
    self._start_socket = value
    if self.start_socket is not None:
      self.start_socket.link = self 

  @property
  def end_socket(self):
    return self._end_socket
  
  @end_socket.setter
  def end_socket(self, value):
    self._end_socket = value
    if self.end_socket is not None:
      self.end_socket.link = self  

  @property
  def link_type(self):
    return self._link_type

  @link_type.setter
  def link_type(self, value):
    if hasattr(self,'grLink') and (self.grLink is not None):
      self.scene.grScene.removeItem(self.grLink)  

    self._link_type = value

    if self.link_type == LINK_TYPE_DIRECT:
      self.grLink = QDMGraphicsLinkDirect(self)

    elif self.link_type == LINK_TYPE_BEIZER:
      self.grLink = QDMGraphicsLinkBezier(self)

    else: 
      self.grLink = QDMGraphicsLinkBezier(self)

    self.scene.grScene.addItem(self.grLink)

    if self.start_socket is not None:
      self.updateLinkPositions()

  def updateLinkPositions(self):

    start_pos = self.start_socket.getSocketPosition() 
    start_x = self.start_socket.node.grNode.pos().x() # -250
    start_y = self.start_socket.node.grNode.pos().y() # -250
    start_pos_s = (start_pos[0] + start_x, start_pos[1] + start_y)
    self.grLink.setStartSocket(*start_pos_s)

    # print("Start Socket:",start_pos_s)
    
    if self.end_socket is not None:
      end_pos = self.end_socket.getSocketPosition()
      end_x = self.end_socket.node.grNode.pos().x() # 0
      end_y = self.end_socket.node.grNode.pos().y() # 0
      end_pos_s = (end_pos[0] + end_x, end_pos[1] + end_y)
      self.grLink.setEndSocket(*end_pos_s)
      # print("End Socket:",end_pos_s) 
    else:
      self.grLink.setEndSocket(*start_pos_s)  

    self.grLink.update()  

  def removeFromSocket(self):
    if self.start_socket is not None:
      self.start_socket.link = None

    if self.end_socket is not None:
      self.end_socket.link = None

    self.end_socket = None  
    self.start_socket = None 

  def remove(self):
    if DEBUG: print("node_link :: Remove Link",self)
    if DEBUG: print("node_link :: remove link from all socket")
    self.removeFromSocket()
    if DEBUG: print("node_link :: remove grLink")
    self.scene.grScene.removeItem(self.grLink)
    self.grLink = None
    if DEBUG: print("node_link :: remove link from scene")
    try:
      self.scene.removeLink(self)
    except ValueError: # error thrown when delete both node and link at the same time
      print('node_link :: Notice: Remove multiple elements')
      pass # ignore error when could not find link to delete when delete both node and link   
    if DEBUG: print("node_link :: remove link done")

  def serialize(self):
    return OrderedDict([
        ('id',self.id),
        ('link_type',self.link_type),
        ('start',self.start_socket.id),
        ('end',self.end_socket.id)
      ])
  

  def deserialize(self, data, hashmap={},restore_id=True):
    if restore_id: self.id = data['id']
    self.start_socket = hashmap[data['start']]
    if DEBUG: print('node_link :: self.start_socket',self.start_socket)
    self.end_socket = hashmap[data['end']]
    self.link_type = data['link_type']

    return True
     

