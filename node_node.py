from collections import OrderedDict
from node_serialize import Serializable
from node_graphic_node import QDMGraphicNode
from node_content_widget import QDMNodeContentWidget
from node_socket import *

DEBUG = False

class Node(Serializable):
  """docstring for Node"""
  def __init__(self, scene, title="Untitled Node",inpts=[],outpts=[]):
    super().__init__()
    self._title = title
    self.scene = scene

    self.content = QDMNodeContentWidget(self)
    self.grNode = QDMGraphicNode(self)
    self.title = title

    self.scene.addNode(self)
    self.scene.grScene.addItem(self.grNode)

    self.socket_spacing = 30

    
    self.inputs = []
    self.outputs = []


    # create I/O socket
    if len(inpts) > 0:

      counter = 0
      for item in inpts:
        socket = Socket(node=self,index=counter,position=LEFT_TOP, socket_type=item)
        counter += 1
        self.inputs.append(socket)

    if len(outpts) > 0: 

      counter = 0
      for item in outpts:
        socket = Socket(node=self,index=counter,position=RIGHT_BOTTOM, socket_type=item) 
        counter += 1
        self.outputs.append(socket) 

  def __str__(self):
    return "<Node id_hex: {}_{}>".format(id(self),hex(id(self)))

  @property
  def pos(self):
    return self.grNode.pos()  # QPointF --> pos.x()

  @property
  def title(self):
    return self._title

  @title.setter
  def title(self,value):
    self._title = value
    self.grNode.title = self._title
  
  def setNodePos(self,x,y):    
    self.grNode.setPos(x,y)

  def translateIndexPosition(self, index, position):
    '''position translate from index and position array
    will return (x,y) on grNode

    '''
    x_gr = 0 if (position in (LEFT_TOP, LEFT_BOTTOM)) else self.grNode.width

    if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
      # start from bottom
      y_gr = self.grNode.height - self.grNode.edge_size - index * self.socket_spacing
    else:  
      # start from top
      y_gr = self.grNode.title_height + self.grNode.edge_size +  index * self.socket_spacing

    return x_gr, y_gr

  def updatedConnectedLinks(self):
    for _socket in (self.inputs + self.outputs):
      if _socket.hasLink():
        _socket.link.updateLinkPositions()

  def remove(self):
    if DEBUG: print("node_node :: Remove Node",self)
    if DEBUG: print("node_node :: remove all link from socket")  
    # cause ValueError: list.remove(x): x not in list     
    for socket in (self.inputs+self.outputs):
      if socket.hasLink():
        if DEBUG: print("node_node :: remove from socket",socket,'link:',socket.link)
        socket.link.remove()        
    if DEBUG: print("node_node :: Remove grNode")
    self.scene.grScene.removeItem(self.grNode)
    self.grNode = None
    if DEBUG: print("node_node :: Remove node from the scene")
    self.scene.removeNode(self)
    if DEBUG: print("node_node :: Remove Node Done")
      

  def serialize(self):
    _inputs,_outputs = [],[]
    _inputs = [socket.serialize() for socket in self.inputs]
    _outputs = [socket.serialize() for socket in self.outputs]
    return OrderedDict([
        ('id', self.id),
        ('title', self.title),
        ('pos_x',self.grNode.scenePos().x()),
        ('pos_y',self.grNode.scenePos().y()),
        ('inputs',_inputs),
        ('outputs',_outputs),
        ('content',self.content.serialize())
      ])   

  def deserialize(self, data, hashmap={},restore_id=True):
    '''
    why after deserialize id does not change ?
    '''
    if restore_id: self.id = data['id']

    hashmap[data['id']] = self


    self.setNodePos(data['pos_x'],data['pos_y'])
    self.title = data['title']

    data['inputs'].sort(key = lambda socket:socket['index']+ socket['position'] * 10000)
    data['outputs'].sort(key = lambda socket:socket['index']+ socket['position'] * 10000)

    self.inputs = []
    for socket_data in data['inputs']:
      new_socket = Socket(node=self,index=socket_data['index'],position=socket_data['position'],
                          socket_type=socket_data['socket_type']) 
      new_socket.deserialize(socket_data, hashmap,restore_id)
      self.inputs.append(new_socket)

    self.outputs = []
    for socket_data in data['outputs']:
      new_socket = Socket(node=self,index=socket_data['index'],position=socket_data['position'],
                          socket_type=socket_data['socket_type']) 
      new_socket.deserialize(socket_data, hashmap,restore_id)
      self.outputs.append(new_socket)  

    return True  

