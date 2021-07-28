"""
This module includes constants for defining the look and feel of the
graphical user interface of the application.
"""
from PyQt5 import QtGui, QtCore, QtWidgets

PALETTES = {}
STYLES = {}
STANDARD_FONT_SIZE = 10

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background ,QtGui.QColor(255, 255, 255))
PALETTES['clean_bg'] = pal

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background, QtGui.QColor(225, 225, 225))
PALETTES['workflow_plugin_widget'] = pal

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background, QtGui.QColor(225, 225, 255))
PALETTES['workflow_plugin_widget_active'] = pal
del pal

STYLES['workflow_plugin_active'] = """
    QLabel{
        font-size: 12px;
        font: bold;
        color: rgb(0, 0, 0);
        border: 0px;
        border: 2px solid rgb(60, 60, 60);
        border-radius: 3px;
        background: rgb(225, 225, 255);
        margin-left: 2px;
        margin-bottom: 2px;
    }
    """
STYLES['workflow_plugin_inactive'] = """
    QPushButton{
        font-size: 11px;
        color: rgb(65, 65, 65);
        border: 1px solid rgb(205, 205, 205);
    }
    QLabel{
        font-size: 11px;
        font: bold;
        color: rgb(60, 60, 60);
        border: 0px;
        margin-left: 2px;
        margin-bottom: 2px;
        border: 1px solid rgb(60, 60, 60);
        border-radius: 3px;
        background: rgb(225, 225, 225);
    }
    """

STYLES['title'] = """QWidget {font: bold; font-size: 14pt}"""
STYLES['subtitle'] = """QWidget {font: bold; font-size: 11pt}"""
STYLES['workflow_plugin_del_button'] = "QPushButton{font-size: 10px; color: rgb(65, 65, 65);}"
STYLES['workflow_plugin_title'] = "QLabel{font-size: 12px;font: bold;color: rgb(0, 0, 0);}"

#DEFAULT_ALIGNMENT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
DEFAULT_ALIGNMENT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop

COMBO_BOX_SIZE_POLICY = (
    QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
