"""
This module includes constants for defining the look and feel of the
graphical user interface of the application.
"""
from PyQt5 import QtGui, QtCore, QtWidgets

QT_PALETTES = {}
QT_STYLES = {}
STANDARD_FONT_SIZE = 10

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background ,QtGui.QColor(255, 255, 255))
QT_PALETTES['clean_bg'] = pal

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background, QtGui.QColor(225, 225, 225))
QT_PALETTES['workflow_plugin_widget'] = pal

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background, QtGui.QColor(225, 225, 255))
QT_PALETTES['workflow_plugin_widget_active'] = pal
del pal

QT_STYLES['workflow_plugin_active'] = """
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
QT_STYLES['workflow_plugin_inactive'] = """
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

QT_STYLES['title'] = """QWidget {font: bold; font-size: 14pt}"""
QT_STYLES['subtitle'] = """QWidget {font: bold; font-size: 11pt}"""
QT_STYLES['workflow_plugin_del_button'] = "QPushButton{font-size: 10px; color: rgb(65, 65, 65);}"
QT_STYLES['workflow_plugin_title'] = "QLabel{font-size: 12px;font: bold;color: rgb(0, 0, 0);}"

#DEFAULT_ALIGNMENT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
QT_DEFAULT_ALIGNMENT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop

QT_COMBO_BOX_SIZE_POLICY = (
    QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)

QT_REG_EXP_FLOAT_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(
    '-?\\d*\.?\d*|None|nan',
    QtCore.QRegularExpression.CaseInsensitiveOption))

QT_REG_EXP_INT_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(
    '-?\\d*|None|nan',
    QtCore.QRegularExpression.CaseInsensitiveOption))
