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
The qt_presets module includes constants for defining the look and feel of the
graphical user interface of the application.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "QT_STYLES",
    "STANDARD_FONT_SIZE",
    "QT_DEFAULT_ALIGNMENT",
    "QT_TOP_RIGHT_ALIGNMENT",
    "QT_BOTTOM_LEFT_ALIGNMENT",
    "QT_BOTTOM_RIGHT_ALIGNMENT",
    "QT_CENTER_LEFT_ALIGNMENT",
    "QT_CENTER_RIGHT_ALIGNMENT",
    "QT_COMBO_BOX_SIZE_POLICY",
    "QT_REG_EXP_FLOAT_VALIDATOR",
    "QT_REG_EXP_INT_VALIDATOR",
    "QT_REG_EXP_SLICE_VALIDATOR",
    "QT_REG_EXP_FLOAT_SLICE_VALIDATOR",
    "FIX_EXP_POLICY",
    "EXP_EXP_POLICY",
    "EXP_FIX_POLICY",
]

import platform

from qtpy import QtGui, QtCore, QtWidgets

if platform.system() == "Windows":
    STANDARD_FONT_SIZE = 10
else:
    STANDARD_FONT_SIZE = 8

QT_STYLES = {
    "title": "QWidget {font: bold; font-size: " + f"{STANDARD_FONT_SIZE + 4}" + "pt}",
    "subtitle": "QWidget {font: bold; font-size: "
    + f"{STANDARD_FONT_SIZE + 1}"
    + "pt}",
}

QT_DEFAULT_ALIGNMENT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop

QT_TOP_RIGHT_ALIGNMENT = QtCore.Qt.AlignRight | QtCore.Qt.AlignTop

QT_BOTTOM_LEFT_ALIGNMENT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom

QT_BOTTOM_RIGHT_ALIGNMENT = QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom

QT_CENTER_LEFT_ALIGNMENT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

QT_CENTER_RIGHT_ALIGNMENT = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

QT_COMBO_BOX_SIZE_POLICY = QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon

QT_REG_EXP_FLOAT_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(
        "-?\\d*\.?\d*|None|nan", QtCore.QRegularExpression.CaseInsensitiveOption
    )
)

QT_REG_EXP_INT_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(
        "-?\\d*|None|nan", QtCore.QRegularExpression.CaseInsensitiveOption
    )
)

QT_REG_EXP_SLICE_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression("((-?\\d*:?){1,3},?)*")
)

QT_REG_EXP_FLOAT_SLICE_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression("((-?\\d*\\.?\\d*:?){1,3},?)*")
)

FIX_EXP_POLICY = (QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)

EXP_EXP_POLICY = (QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

EXP_FIX_POLICY = (QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
