from PyQt5 import QtGui

PALETTES = {}
STYLES = {}

pal = QtGui.QPalette()

pal.setColor(QtGui.QPalette.Background ,QtGui.QColor(160, 160, 160))
PALETTES['workflow_widget'] = pal

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background, QtGui.QColor(190, 190, 190))
PALETTES['workflow_plugin_widget'] = pal

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background, QtGui.QColor(190, 190, 255))
PALETTES['workflow_plugin_widget_active'] = pal

STYLES['workflow_plugin_active'] = """
    QPushButton{font-size: 11px; color: rgb(65, 65, 65);};
    QLabel{font-size: 12px;font: bold;color: rgb(0, 0, 0); border: 0px};
    QFrame{border: 3px solid rgb(250, 250, 250);}"""

STYLES['workflow_plugin_inactive'] = """
    QPushButton{font-size: 11px; color: rgb(65, 65, 65);};
    QLabel{font-size: 12px;font: bold;color: rgb(20, 20, 20); border: 0px};
    QFrame{border: 1px solid rgb(250, 250, 250);}"""

STYLES['title'] = """QWidget {font: bold; font-size: 14pt}"""
STYLES['workflow_plugin_del_button'] = "QPushButton{font-size: 10px; color: rgb(65, 65, 65);}"
STYLES['workflow_plugin_title'] = "QLabel{font-size: 12px;font: bold;color: rgb(0, 0, 0);}"

del pal