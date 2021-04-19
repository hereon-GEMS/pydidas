# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 10:24:52 2021

@author: ogurreck
"""

import sys
import inspect
import os
import numpy as np
from functools import partial
from copy import copy
import numbers
#from qtpy import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore, Qt

# p = 'h:/myPython'
# if not p in sys.path:
#     sys.path.insert(0, p)

import plugin_workflow_gui as pwg

WORKFLOW_EDIT_MANAGER = pwg.gui.GuiWorkflowEditTreeManager()
PLUGIN_COLLECTION = pwg.PluginCollection()
STYLES = pwg.config.STYLES
PALETTES = pwg.config.PALETTES
STANDARD_FONT_SIZE = 10
#WorkflowTree = pwg.WorkflowTree()

def deleteItemsOfLayout(layout):
     if layout is not None:
         while layout.count():
             item = layout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                 widget.setParent(None)
                 widget.deleteLater()
             else:
                 deleteItemsOfLayout(item.layout())

class WorkflowTreeCanvas(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.title = QtWidgets.QLabel(self)
        self.title.setStyleSheet(STYLES['title'])
        self.title.setText('Workflow tree')
        self.title.move(10, 10)
        self.painter =  QtGui.QPainter()
        self.setAutoFillBackground(True)
        # self.setPalette(PALETTES['clean_bg'])

        self.setLineWidth(2)
        self.setFrameStyle(QtWidgets.QFrame.Raised)
        self.widget_connections = []


    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setPen(QtGui.QPen(QtGui.QColor(120, 120, 120), 2))
        self.draw_connections()
        self.painter.end()

    def draw_connections(self):
        for x0, y0, x1, y1 in self.widget_connections:
            self.painter.drawLine(x0, y0, x1, y1)


    def update_widget_connections(self, widget_conns):
        self.widget_connections = widget_conns
        self.update()


class IOwidget(QtWidgets.QWidget):
    """Widgets for I/O during plugin parameter editing."""
    def __init__(self, parent, param):
        super().__init__(parent)
        self.setFixedWidth(175)
        self.setFixedHeight(25)
        self.__ptype = param.type
        self.setToolTip(f'{param.tooltip}')

    def get_value_from_text(self, text):
        if self.__ptype == numbers.Integral:
            return int(text)
        elif self.__ptype == numbers.Real:
            return float(text)
        return text


class IOwidget_combo(QtWidgets.QComboBox, IOwidget):
    """Widgets for I/O during plugin parameter editing with predefined choices."""
    #for some reason, inhering the signal does not work
    io_edited = QtCore.pyqtSignal(str)

    def __init__(self, parent, param):
        super().__init__(parent, param)
        for choice in param.choices:
            self.addItem(f'{choice}')
        self.currentIndexChanged.connect(self.emit_signal)

    def emit_signal(self):
        self.io_edited.emit(self.currentText())

    def get_value(self):
        text = self.currentText()
        return self.get_value_from_text(text)

    def set_value(self, value):
        self.setCurrentIndex(self.findText(f'{value}'))

class IOwidget_line(QtWidgets.QLineEdit, IOwidget):
    """Widgets for I/O during plugin parameter editing without choices."""
    #for some reason, inhering the signal does not work
    io_edited = QtCore.pyqtSignal(str)

    def __init__(self, parent, param):
        super().__init__(parent, param)
        self.editingFinished.connect(self.emit_signal)
        if param.type == numbers.Integral:
            self.setValidator(QtGui.QIntValidator())
        elif param.type == numbers.Real:
            self.setValidator(QtGui.QDoubleValidator())

    def emit_signal(self):
        self.io_edited.emit(self.text())

    def get_value(self):
        text = self.text()
        return self.get_value_from_text(text)

    def set_value(self, value):
        self.setText(f'{value}')


class PluginEditCanvas(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.painter =  QtGui.QPainter()
        self.setAutoFillBackground(True)
        self.setLineWidth(2)
        self.setFrameStyle(QtWidgets.QFrame.Raised)
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setLayout(self._layout)

    def configure_plugin(self, node_id):
        self.plugin = WORKFLOW_EDIT_MANAGER.plugins[node_id]
        self.param_links = {}
        #delete current widgets
        for i in reversed(range(self._layout.count())):
            item = self._layout.itemAt(i)
            if isinstance(item, QtWidgets.QLayout):
                deleteItemsOfLayout(item)
                self._layout.removeItem(item)
                item.deleteLater()
            elif isinstance(item.widget(), QtWidgets.QWidget):
                widgetToRemove = item.widget()
                self._layout.removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                widgetToRemove.deleteLater()

        #setup new widgets:
        self.add_label(f'Plugin: {self.plugin.plugin_name}', fontsize=12, width=385)
        self.add_label(f'Node id: {node_id}', fontsize=12)
        self.add_label('\nParameters:', fontsize=12)
        self.setup_restore_default_button()
        for param in self.plugin.params:
            self.add_param(param)

    def setup_restore_default_button(self):
        but = QtWidgets.QPushButton(self.style().standardIcon(59),
                                    'Restore default parameters')
        but.clicked.connect(partial(self.plugin.restore_defaults, force=True))
        but.clicked.connect(self.update_edits)
        but.setFixedHeight(25)
        self._layout.addWidget(but, 0, QtCore.Qt.AlignRight)

    # def restore_plugin_defaults(self):
    #     ...

    def update_edits(self):
        for param in self.plugin.params:
            self.param_links[param.name].setText(param.value)

    def add_label(self, text, fontsize=STANDARD_FONT_SIZE, width=None):
        w = QtWidgets.QLabel(text)
        if fontsize != STANDARD_FONT_SIZE:
            _font = app.font()
            _font.setPointSize(fontsize)
            w.setFont(_font)
        if width:
            w.setFixedWidth(width)
        w.setFixedHeight(fontsize * (1 + text.count('\n')) + 8)
        self._layout.addWidget(w, 0, QtCore.Qt.AlignLeft)

    def add_param(self, param):
        _l = QtWidgets.QHBoxLayout()
        _txt = QtWidgets.QLabel(f'{param.name}:')
        _txt.setFixedWidth(120)
        _txt.setFixedHeight(25)
        _txt.setToolTip(param.tooltip)
        _l.addWidget(_txt, 0, QtCore.Qt.AlignRight)

        if param.choices:
            _io = IOwidget_combo(None, param)
        else:
            _io= IOwidget_line(None, param)
        _io.io_edited.connect(partial(self.set_plugin_param, param, _io))
        _io.set_value(param.value)
        _l.addWidget(_io, 0, QtCore.Qt.AlignRight)
        self.param_links[param.name] = _io
        self._layout.addLayout(_l)

    def update_param_value(self, param):
        ...

    # def set_plugin_param(self, param, widget):
    #     if isinstance(widget, QtWidgets.QComboBox):
    #         value = widget.currentText()
    #     if isinstance(widget, QtWidgets.QLineEdit):
    #         value = widget.text()
    #     self.plugin.set_param(param.name, value)

    def set_plugin_param(self, param, widget):
        param.value = widget.get_value()
        print(param.value)
        # if isinstance(widget, QtWidgets.QComboBox):
        #     value = widget.currentText()
        # if isinstance(widget, QtWidgets.QLineEdit):
        #     value = widget.text()
        # self.plugin.set_param(param.name, value)

class _ScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent=None, widget=None, width=None, height=None):
        super().__init__(parent)
        self.parent = parent
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.setAutoFillBackground(True)
        #self.setPalette(PALETTES['clean_bg'])
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)


class WorkflowEditTab(QtWidgets.QWidget):
    def __init__(self, parent=None, qt_main=None):
        super().__init__(parent)
        self.parent = parent
        self.qt_main = qt_main
        self.workflow_canvas = WorkflowTreeCanvas(self)
        self.plugin_edit_canvas = PluginEditCanvas(self)
        self.w_plugin_collection = pwg.widgets.PluginCollectionPresenter(self, self.qt_main, self.qt_main)
        self.workflow_area = _ScrollArea(
            self, self.workflow_canvas,
            self.qt_main.params['workflow_edit_canvas_x'],
            self.qt_main.params['workflow_edit_canvas_y']
        )
        self.plugin_edit_area = _ScrollArea(self, self.plugin_edit_canvas, 400, None)
        self.plugin_edit_area.setMinimumHeight(500)

        self.w_plugin_collection.selection_confirmed.connect(self.workflow_add_plugin)

        _layout0 = QtWidgets.QHBoxLayout()
        _layout0.setContentsMargins(5, 5, 5, 5)

        _layout1 = QtWidgets.QVBoxLayout()
        _layout1.setContentsMargins(0, 0, 0, 0)
        _layout1.addWidget(self.workflow_area)
        _layout1.addWidget(self.w_plugin_collection)

        _layout0.addLayout(_layout1)
        _layout0.addWidget(self.plugin_edit_area)

        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addLayout(_layout0)
        _layout.addWidget(pwg.widgets.ConfirmationBar())
        self.setLayout(_layout)
        self.qt_main.workflow_edit_manager.plugin_to_edit.connect(self.configure_plugin)

    def workflow_add_plugin(self, name):
        self.qt_main.workflow_edit_manager.add_plugin_node(name)

    @QtCore.pyqtSlot(int)
    def configure_plugin(self, node_id):
        # print(f'configure plugin {node_id}')
        self.plugin_edit_canvas.configure_plugin(node_id)


class ExperimentEditTab(QtWidgets.QWidget):
    def __init__(self, parent=None, qt_main=None, master=None):
        super().__init__(parent)
        self.parent = parent
        self.qt_main = qt_main
        self._layout = QtWidgets.QVBoxLayout()
        _label = QtWidgets.QLabel('Test 123')
        self._layout.addWidget(_label)
        self._layout.addWidget(pwg.widgets.ConfirmationBar())
        self.setLayout(self._layout)


class MainTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)



class LayoutTest(QtWidgets.QMainWindow):
    name_selected_signal = QtCore.pyqtSlot(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.process = None
        self.setGeometry(20, 40, 1400, 1000)
        self.params = {'workflow_edit_canvas_x': 1000,
                       'workflow_edit_canvas_y': 600}
        self.status = self.statusBar()

        self.workflow_edit_manager = pwg.gui.GuiWorkflowEditTreeManager()


        self.main_frame = QtWidgets.QTabWidget()
        self.setCentralWidget(self.main_frame)
        self.status.showMessage('Test status')

        self.experiment_edit_tab = ExperimentEditTab(self.main_frame, self)
        self.workflow_edit_tab = WorkflowEditTab(self.main_frame, self)
        self.main_frame.addTab(self.experiment_edit_tab, 'Experiment editor')
        self.main_frame.addTab(self.workflow_edit_tab, 'Workflow editor')
        self.workflow_edit_manager.update_qt_items(
            self.workflow_edit_tab.workflow_canvas, self
        )

        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 0')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 1')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 2')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 3')
        self.workflow_edit_manager.set_active_node(2)
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 4')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 5')
        self.workflow_edit_manager.set_active_node(2)
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 6')
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 7')
        self.workflow_edit_manager.set_active_node(6)
        self.workflow_edit_manager.add_plugin_node('HDF loader', 'Test title 8')

        self.setWindowTitle('Plugin edit test')
        self._createMenu()

    def action_new(self):
        print('new')

    def action_open(self):
        print('open')

    def _createMenu(self):
        self._menu = self.menuBar()

        newAction = QtWidgets.QAction(QtGui.QIcon('new.png'), '&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New document')
        newAction.triggered.connect(self.action_new)

        # Create new action
        openAction = QtWidgets.QAction(QtGui.QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open document')
        openAction.triggered.connect(self.action_open)

        # Create exit action
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.closeEvent)

        fileMenu = QtWidgets.QMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        self._menu.addMenu(fileMenu)
        self._menu.addMenu("&Edit")
        self._menu.addMenu("&Help")


# class MasterApplication:
#     def __init__(self):
#         self.

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
# new_font.setPointSize( int ** ); //your option
# new_font.setWeight( int ** ); //your option
# app.setFont( new_font );
    # app.setFont(QtGui.Font('{font-size: 11px;}'))
    gui = LayoutTest()
    gui.show()
    sys.exit(app.exec_())
