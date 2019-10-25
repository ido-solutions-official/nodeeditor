from collections import OrderedDict
from node_graphic_socket import QDMGraphicsSocket
from node_serialize import Serializable

LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4

DEBUG = True


class Socket(Serializable):
  def __init__(self,node , index=0, position=LEFT_TOP, socket_type=1):
    super().__init__()
    
    self.node = node

    self.index = index

    self.position = position

    self.socket_type = socket_type

    self.grSocket = QDMGraphicsSocket(self, self.socket_type)

    self.grSocket.setPos(*self.node.translateIndexPosition(index,position))

    self.link = None

  def __str__(self):
    return "<Socket id: {}_{}>".format(id(self),hex(id(self)))

  def getSocketPosition(self):
    if DEBUG: print('get socket index/posisiton: ',self.index, self.position, "node:",self.node)
    res = self.node.translateIndexPosition(self.index, self.position)
    if DEBUG: print('get abs socket index/posisiton CO: ',res)
    return res

  def setConnectedLink(self, link=None):
    '''
    use when drag
    '''
    self.link = link

  def hasLink(self): 
    return self.link is not None  

  def serialize(self):
    return OrderedDict([
        ('id', self.id),
        ('index', self.index),
        ('position', self.position),
        ('socket_type', self.socket_type)

      ])   

  def deserialize(self, data, hashmap={},restore_id=True):
    if restore_id: self.id = data['id']
    hashmap[data['id']] = self

    return True  
    