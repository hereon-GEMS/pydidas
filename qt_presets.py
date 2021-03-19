from PyQt5 import QtGui

PALETTES = {}
STYLES = {}

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background,QtGui.QColor(160, 160, 160))

PALETTES['workflow_widget'] = pal

pal = QtGui.QPalette()
pal.setColor(QtGui.QPalette.Background,QtGui.QColor(190, 190, 190))

PALETTES['workflow_plugin_widget'] = pal

STYLES['plugin_del_button'] = "QPushButton{font-size: 11px; color: rgb(65, 65, 65);}"
STYLES['plugin_title'] = "QLabel{font-size: 12px;font: bold;color: rgb(0, 0, 0);}"

