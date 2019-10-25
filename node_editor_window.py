import os
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):

  def __init__(self):
    super().__init__()

    self.filename = None
    self.company_name = 'ido'
    self.product_name = 'py node editor'
    # self.createNActions()
    self.initWindow()
    
  def createAct(self,name,shortcut,tooltip,callback):
    act = QAction(name,self)
    act.setShortcut(shortcut)
    act.setToolTip(tooltip)
    act.triggered.connect(callback)
    return act

  def createNActions(self):
    self.actNew = self.createAct('&New Graph',QKeySequence.New,'Create New Graph',self.onFileNew)
    self.actOpen = self.createAct('&Open',QKeySequence.Open,'Open Graph',self.onFileOpen)
    self.actSave = self.createAct('&Save',QKeySequence.Save,'Save Graph',self.onFileSave)
    self.actSaveas = self.createAct('&Save as',QKeySequence.SaveAs,'Save Graph as ...',self.onFileSaveAs)
    self.actExit = self.createAct('&Exit',QKeySequence(Qt.CTRL + Qt.Key_Q),'Exit',self.close)

    self.actUndo = self.createAct('&Undo',QKeySequence.Undo,'Undo',self.onEditUndo)
    self.actRedo = self.createAct('&Redo',QKeySequence(Qt.CTRL + Qt.Key_Y),'Redo',self.onEditRedo)
    self.actCut = self.createAct('&Cut',QKeySequence.Cut,'Cut',self.onEditCut)
    self.actCopy = self.createAct('&Copy',QKeySequence.Copy,'Copy',self.onEditCopy)
    self.actPaste = self.createAct('&Paste',QKeySequence.Paste,'Paste',self.onEditPaste)
    self.actDelete = self.createAct('&Delete',QKeySequence(Qt.Key_Backspace),'Delete',self.onEditDelete)

  def initWindow(self): 

    nodeEditor = NodeEditorWidget(self)
    nodeEditor.scene.addHasBeenModifiedListeners(self.setTitle)
    self.setCentralWidget(nodeEditor)

    self.grView = self.centralWidget().view

    # deactivate native settings
    # menuBar.setNativeMenuBar(False) 

    # status bar
    self.statusBar().showMessage('')
    self.status_mouse_pos = QLabel('')
    self.statusBar().addPermanentWidget(self.status_mouse_pos)
    nodeEditor.view.scenePosChanged.connect(self.onScenePosChanged)


    self.setGeometry(200,200,800,600)
    self.setTitle()
    # self.setWindowTitle('Node Editor');
    self.show()

  def setTitle(self):
    title = 'Node Editor - '
    if self.filename is None:
      title += 'New'
    else:
      title += os.path.basename(self.filename)

    if self.centralWidget().scene.has_been_modified:
      title += '*'

    self.setWindowTitle(title)  

  def closeEvent(self, event):
    if self.maybeSave():
      event.accept()
    else:
      event.ignore()

  def createNMenus(self):
    menuBar = self.menuBar()

    self.fileMenu = menuBar.addMenu('File')
    self.fileMenu.addAction(self.actNew)
    self.fileMenu.addSeparator()
    self.fileMenu.addAction(self.actOpen)
    self.fileMenu.addAction(self.actSave)
    self.fileMenu.addAction(self.actSaveas)
    self.fileMenu.addSeparator()
    self.fileMenu.addAction(self.actExit)

    self.editMenu = menuBar.addMenu('Edit')
    self.editMenu.addAction(self.actUndo)
    self.editMenu.addAction(self.actRedo)
    self.editMenu.addSeparator()
    self.editMenu.addAction(self.actCut)
    self.editMenu.addAction(self.actCopy)
    self.editMenu.addAction(self.actPaste)
    self.editMenu.addAction(self.actDelete)     

  def isModified(self):
    return self.centralWidget().scene.has_been_modified

  def maybeSave(self):
    if not self.isModified():
      return True

    res = QMessageBox.warning(self, 'Closing Window ?',
      'The Graph has been modified.\n Do you want to save your changes ?',
      QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
      )  

    if res == QMessageBox.Save:
      return self.onFileSave()

    elif res == QMessageBox.Cancel:
      return False  

    return True    

  def onScenePosChanged(self, x, y):
    self.status_mouse_pos.setText('Scene Pos: ({},{})'.format(x,y))
      
  def onFileNew(self):
    if self.maybeSave():
      self.centralWidget().scene.clear()
      self.filename = None
      self.setTitle()

  def onFileOpen(self):
    if self.maybeSave():
      file_dialog = QFileDialog(self)
      filename, _filter = file_dialog.getOpenFileName(self, 'Open Graph from File',filter = "Node File Extenstion (*.nd)")
      if filename =='':
        return
      elif os.path.isfile(filename):
        self.centralWidget().scene.loadFromFile(filename)  
        self.filename = filename
        self.setTitle()

    
  def onFileSave(self,filename):
    if self.filename is None: return self.onFileSaveAs()
    self.centralWidget().scene.saveToFile(self.filename)
    self.statusBar().showMessage('successfully save to '+self.filename)
    return True

    
  def onFileSaveAs(self):
    prescript = 'untitled.nd'
    file_dialog = QFileDialog(self)
    filename, _filter = file_dialog.getSaveFileName(self, 'Save Graph as',prescript,filter = "Node File Extenstion (*.nd)")
    if filename =='':
      return False
    self.filename = filename
    self.onFileSave(filename)
    return True
  

  def onEditUndo(self):
    # print('trigger undo')
    self.centralWidget().scene.history.undo() 
     
  def onEditRedo(self):
    # print('trigger redo')
    self.centralWidget().scene.history.redo() 

  def onEditDelete(self):
    if not self.grView.editingFlag:
      self.grView.deleteSelected()
    # else:
    #   self.grView.keyPressEvent(event) 

  def onEditCut(self):
    data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
    str_data = json.dumps(data,indent=4)
    QApplication.instance().clipboard().setText(str_data)
    
  def onEditCopy(self):
    data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
    str_data = json.dumps(data,indent=4)
    QApplication.instance().clipboard().setText(str_data) 
    
  def onEditPaste(self):
    clipboard = QApplication.instance().clipboard().text()

    try:
      data = json.loads(clipboard) 
    except Exception as e:
      print('exception occured:',e)
      return

    if 'nodes' not in data:
      print('JSON does not coatain nodes')
      return

    self.centralWidget().scene.clipboard.deserializeFromClipboard(data)  
                
  def readSettings(self):
    settings = QSettings(self.company_name, self.product_name)
    pos = settings.value('pos', QPoint(200, 200))
    size = settings.value('size', QSize(400, 400))
    self.move(pos)
    self.resize(size)

  def writeSettings(self):
    settings = QSettings(self.company_name, self.product_name)
    settings.setValue('pos', self.pos())
    settings.setValue('size', self.size())




