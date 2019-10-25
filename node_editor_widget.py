from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from node_scene import Scene
from node_node import Node
# from node_socket import Socket
from node_link import Link
from node_graphic_view import QDMGraphicView

class NodeEditorWidget(QWidget):
  def __init__(self,parent=None):
    super().__init__(parent)

    self.stylesheet_filename = 'css/nodestyle.css'
    self.loadStylesheet(self.stylesheet_filename)

    self.initUI()

  def initUI(self):

    self.layout = QVBoxLayout()
    self.layout.setContentsMargins(0,0,0,0)
    self.setLayout(self.layout)

    # graphic scene
    self.scene = Scene()

    # graphic view
    self.view = QDMGraphicView(self.scene.grScene)
    self.layout.addWidget(self.view)

    

    # add debug content
    # self.addDebugContent()
    # add node
    self.addNode()
      

  def loadStylesheet(self, filename):
    print('css Loading : {}'.format(filename))
    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)
    stylesheet = file.readAll()
    QApplication.instance().setStyleSheet(str(stylesheet,encoding='utf-8'))

  def addNode(self):
    # My First Node
    _input = [1,2,3]
    _output = [1]

    node1 = Node(self.scene, 'First Node',_input ,_output)
    node2 = Node(self.scene, 'Second First Node',_input ,_output)
    node3 = Node(self.scene, 'Third First Node',_input ,_output)
    node1.setNodePos(-250, -250)
    node2.setNodePos(250, -250)   

    # print('node1 id: ',id(node1))
    # print('node2 id: ',id(node2))
    # print('node3 id: ',id(node3))

    Link1 = Link(self.scene, node1.outputs[0], node2.inputs[0], 2)
      

  def addDebugContent(self):
    redBrush = QBrush(QColor(Qt.red))
    outlinePen = QPen(QColor(Qt.red))
    outlinePen.setWidth(2)

    rect = self.grScene.addRect(-100,-100,80,100,outlinePen,redBrush)
    rect.setFlag(QGraphicsItem.ItemIsMovable, True)
    # self.grScene.addItem(rect)

    text = self.grScene.addText('This is my text',QFont('helvetica'))
    text.setFlag(QGraphicsItem.ItemIsSelectable, True)
    text.setDefaultTextColor(QColor.fromRgb(255,255,255))

    button = QPushButton('hello')
    proxy1 = self.grScene.addWidget(button)
    proxy1.setFlag(QGraphicsItem.ItemIsMovable, True)
    proxy1.setPos(0,30)

    box = QTextEdit()
    proxy2 = self.grScene.addWidget(box)
    proxy2.setFlag(QGraphicsItem.ItemIsMovable, True)
    proxy2.setPos(0,60)

    line = self.grScene.addLine(-200,-200,400,100,outlinePen)
    line.setFlag(QGraphicsItem.ItemIsMovable, True)
    line.setFlag(QGraphicsItem.ItemIsSelectable, True)
