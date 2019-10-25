import json

from PyQt5.QtWidgets import *

from collections import OrderedDict
from node_serialize import Serializable
from node_graphic_scene import QDMGraphicScene
from node_node import Node 
from node_link import Link
from node_scene_history import SceneHistory
from node_scene_clipboard import SceneClipboard

DEBUG = True

class Scene(Serializable):

  def __init__(self, parent=None):
    super().__init__()
    self.nodes = [];
    self.links = [];

    self.scene_width = 64000
    self.scene_height = 64000

    self._has_been_modified = False
    self._has_been_modified_listeners = []

    self.initUIN();
    self.history = SceneHistory(self)
    self.clipboard = SceneClipboard(self)

  @property
  def has_been_modified(self):
    return self._has_been_modified

  @has_been_modified.setter
  def has_been_modified(self, value):
    if not self._has_been_modified and value:
      self._has_been_modified = value

      for callback in self._has_been_modified_listeners:
        callback()

    self._has_been_modified = value

  def addHasBeenModifiedListeners(self,callback):
     self._has_been_modified_listeners.append(callback)

  def initUIN(self):
    self.grScene = QDMGraphicScene(self)
    self.grScene.setGrScene(self.scene_width,self.scene_height) 

  def addNode(self, node):
    self.nodes.append(node);

  def addLink(self, link):
    self.links.append(link);

  def removeNode(self, node):
    self.nodes.remove(node);

  def removeLink(self, link):
    self.links.remove(link);  

  def saveToFile(self,filename):
    with open(filename,'w') as file:
      file.write(json.dumps(self.serialize(),indent=2))
      self.has_been_modified = False

      
  def loadFromFile(self,filename):
    with open(filename,'r') as file:
      raw_data = file.read()
      data = json.loads(raw_data, encoding='utf-8')
      self.deserialize(data)

      self.has_been_modified = False

  def clear(self):
    '''
    have to trigger remove(). This method will also remove sockets and links
    '''
    if DEBUG : print('node_scene :: trigger clear')
    while len(self.nodes) > 0:
      self.nodes[0].remove()

    self.has_been_modified = False

  def serialize(self):
    _nodes,_links = [],[]
    _nodes = [node.serialize() for node in self.nodes]
    _links = [link.serialize() for link in self.links]
    return OrderedDict([
        ('id', self.id),
        ('scene_width', self.scene_width),
        ('scene_height', self.scene_height),
        ('nodes',_nodes),
        ('links',_links),
      ])   

  def deserialize(self, data, hashmap={}, restore_id = True):

    self.clear()

    if restore_id: 
      self.id = data['id']

    hashmap = {}
    
    # load nodes
    for node_data in data['nodes']:
      Node(self).deserialize(node_data, hashmap,restore_id) 

    # load links
    for link_data in data['links']:
      Link(self).deserialize(link_data, hashmap,restore_id)
    
    return True  



