import sys
from PyQt5.QtWidgets import *

from node_editor_window import NodeEditorWindow

def main():
  app = QApplication(sys.argv)

  wnd = NodeEditorWindow()

  sys.exit(app.exec_())

if __name__ == '__main__':
  main()