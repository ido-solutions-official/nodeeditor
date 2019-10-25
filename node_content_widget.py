from PyQt5.QtWidgets import *
from collections import OrderedDict
from node_serialize import Serializable

class QDMNodeContentWidget(QWidget, Serializable):
  def __init__(self,node,parent=None):
    self.node = node
    super().__init__(parent);

    self.initUINC();

  def initUINC(self):
    self.layout = QVBoxLayout()
    self.layout.setContentsMargins(0,0,0,0)
    self.setLayout(self.layout)

    self.wdg_label = QLabel("Node Title")
    self.layout.addWidget(self.wdg_label)
    self.layout.addWidget(QDMTextEdit('enter txt'))

  def setEditingFlag(self, value):
    self.node.scene.grScene.views()[0].editingFlag = value


  def serialize(self):
    return OrderedDict([
        ('id', self.id),

      ])   

  def deserialize(self, data, hashmap={}):
    print('Deserialization data', data)
    pass  


class QDMTextEdit(QTextEdit):
  
  def focusInEvent(self, event):
    self.parentWidget().setEditingFlag(True)
    super().focusInEvent(event)
  
  def focusOutEvent(self, event): 
    self.parentWidget().setEditingFlag(False)
    super().focusOutEvent(event) 
