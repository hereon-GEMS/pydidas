# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
import inspect
import os
import numpy as np
#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

exec(open('H:/myPython/Tests/plugin_workflow_gui/plugin_collection.py', 'r').read())

PLUGIN_COLLECTION = PluginCollection()

class WarningBox(QtWidgets.QMessageBox):
    def __init__(self, title, msg, info=None, details=None):
        super().__init__()
        self.setIcon(self.Warning)
        self.setWindowTitle(title)
        self.setText(msg)
        if info:
            self.setInformativeText(info)
        if details:
            self.setDetailedText(details)
        self.setStandardButtons(self.Ok)
        self.__exec__()

    def __exec__(self):
        self.exec_()


class TreeNode:
    def __init__(self, name=None, parent=None, nid=None, plugin=None):
        self.name = name
        self.parent_plugin = parent
        self.node_id = nid
        self.plugin = plugin
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def is_leaf(self):
        if len(self.children) > 0:
            return False
        return True


class PluginTree:
    def __init__(self, name, plugin):
        self.plugins = TreeNode(name, nid=0, plugin=plugin)
        self.node_ids = [0]


class DragWidget(QtWidgets.QWidget):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent


        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background,QtGui.QColor(100, 100, 100))
        self.setAcceptDrops(True)

        self.frame = QtWidgets.QFrame()
        self.frame.setGeometry(0, 0, 800, 600)
        self.frame.setAutoFillBackground(True)
        self.frame.setPalette(pal)

        _layout = QtWidgets.QVBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self.frame)
        self.setLayout(_layout)

        self.buttons = []
        #grid in 30 x 120 pixel steps from (15, 585) x (5, 795)
        self.grid = np.zeros((59, 79))

    def signal(self, s):
        print(s)

    def find_empty_spot(self, x, y):
        return

    def dragEnterEvent(self, e):
        e.accept()

    def DragMoveEvent (self, e):
        # if
        pos_x = e.pos().x()
        pos_y = e.pos().y()
        print(pos_x, pos_y)
        if not self.grid[pos_y, pos_x]:
            print(pos_x, pos_y)
            e.accept()
        else:
            print('no good')
        e.ignore()

    def dropEvent(self, e):
        index = self.parent.treeView.selectedIndexes()[0]
        name = index.model().itemFromIndex(index).text()
        if self.parent.process == None:
            pass
        pos_x = (e.pos().x() - 5) // 10
        pos_y = (e.pos().y() - 5) // 10
        if self.grid[pos_y, pos_x]:
            pos_x, pos_y = self.find_empty_spot(pos_x, pos_y)

        index = self.parent.treeView.selectedIndexes()[0]
        name = index.model().itemFromIndex(index).text()
        print(name, pos_x, pos_y)
        if not self.grid[pos_y, pos_x]:
            pass
        # print(e.mimeData().parent(), e.mimeData().__str__())
        # for item in inspect.getmembers(e.mimeData()):
        #     print(item)

class DragTest(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.process = None
        self.setGeometry(20, 40, 1400, 1000)
        self.status = self.statusBar()

        self.main_frame = QtWidgets.QWidget()
        self.setCentralWidget(self.main_frame)
        self.status.showMessage('Test status')
        _layout = QtWidgets.QVBoxLayout()
        _layout.setContentsMargins(5, 10, 10, 10)

        self.drag_drop_widget = DragWidget(self)
        self.drag_drop_widget.setFixedSize(800, 600)

        self.treeView = QtWidgets.QTreeView()
        # self.treeView.setHeaderHidden(False)
        self.treeView.setUniformRowHeights(True)
        treeModel = Qt.QStandardItemModel()
        treeModel.setHorizontalHeaderLabels(['Available plugins'])
        self.treeView.header().setStyleSheet(
            'QWidget {font: bold; font-size: 15pt}'
        )
        rootNode = treeModel.invisibleRootItem()
        input_plugins = Qt.QStandardItem('Input plugins')
        for key, item in PLUGIN_COLLECTION.plugins['input'].items():
            input_plugins.appendRow(Qt.QStandardItem(item.name))
        rootNode.appendRow(input_plugins)

        proc_plugins = Qt.QStandardItem('Processing plugins')
        for key, item in PLUGIN_COLLECTION.plugins['proc'].items():
            proc_plugins.appendRow(Qt.QStandardItem(item.name))
        rootNode.appendRow(proc_plugins)

        output_plugins = Qt.QStandardItem('Output plugins')
        for key, item in PLUGIN_COLLECTION.plugins['output'].items():
            output_plugins.appendRow(Qt.QStandardItem(item.name))
        rootNode.appendRow(output_plugins)

        self.treeView.setModel(treeModel)
        self.treeView.expandAll()
        self.treeView.setItemDelegate(PluginCollectionDelegate(rootNode))

        self.button1 = QtWidgets.QPushButton('Test button')
        self.label1 = QtWidgets.QLabel('test label 1')
        _layout.addWidget(self.label1)
        _layout.addWidget(self.button1)
        _layout.addWidget(self.drag_drop_widget)
        _layout.addWidget(QtWidgets.QLabel('Available'))
        _layout.addWidget(self.treeView)

        self.setLayout(_layout)
        self.setWindowTitle('Simple drag & drop')
        self.main_frame.setLayout(_layout)
        self.treeView.setDragEnabled(True)


class PluginCollectionDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, root):
        super().__init__()
        self.root = root

    def sizeHint(self, p_option, p_index):
        size = QtWidgets.QStyledItemDelegate.sizeHint(self, p_option, p_index)
        size.setHeight(25)
        return size

    def paint(self, painter, option, index):
        m = index.model()
        if m.itemFromIndex(index).parent() is None:
            option.font.setWeight(QtGui.QFont.Bold)
            option.font.setPointSize(12)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = DragTest()
    gui.show()
    sys.exit(app.exec_())