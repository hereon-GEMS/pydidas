# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
This module includes constants for defining the look and feel of the
graphical user interface of the application.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['QT_PALETTES', 'QT_STYLES', 'STANDARD_FONT_SIZE',
           'QT_DEFAULT_ALIGNMENT', 'QT_COMBO_BOX_SIZE_POLICY',
           'QT_REG_EXP_FLOAT_VALIDATOR', 'QT_REG_EXP_INT_VALIDATOR']

from PyQt5 import QtGui, QtCore, QtWidgets


STANDARD_FONT_SIZE = 10

QT_PALETTES = {}
for _key, _colors in {'clean_bg': (255, 255, 255),
                      'workflow_plugin_widget': (225, 225, 225),
                      'workflow_plugin_widget_active': (225, 225, 255)
                      }.items():
    _pal = QtGui.QPalette()
    _pal.setColor(QtGui.QPalette.Background, QtGui.QColor(*_colors))
    QT_PALETTES[_key] = _pal

QT_STYLES = {}
QT_STYLES['workflow_plugin_active'] = """
    QLabel{font-size: 11px;
           font: bold;
           color: rgb(0, 0, 0);
           border: 0px;
           border: 2px solid rgb(60, 60, 60);
           border-radius: 3px;
           background: rgb(225, 225, 255);
           margin-left: 2px;
           margin-bottom: 2px;}"""
QT_STYLES['workflow_plugin_inactive'] = """
    QPushButton{font-size: 11px;
                color: rgb(65, 65, 65);
                border: 0px solid rgb(205, 205, 205);}
    QLabel{font-size: 11px;
           font: bold;
           color: rgb(60, 60, 60);
           border: 0px;
           margin-left: 2px;
           margin-bottom: 2px;
           border: 1px solid rgb(60, 60, 60);
           border-radius: 3px;
           background: rgb(225, 225, 225);}"""
QT_STYLES['title'] = """QWidget {font: bold; font-size: 14pt}"""
QT_STYLES['subtitle'] = """QWidget {font: bold; font-size: 11pt}"""
QT_STYLES['workflow_plugin_title'] = (
    "QLabel{font-size: 12px;font: bold;color: rgb(0, 0, 0);}")

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
