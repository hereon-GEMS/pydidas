# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "ALIGN_TOP_LEFT",
    "ALIGN_TOP_CENTER",
    "ALIGN_TOP_RIGHT",
    "ALIGN_CENTER_LEFT",
    "ALIGN_CENTER",
    "ALIGN_CENTER_RIGHT",
    "ALIGN_BOTTOM_CENTER",
    "ALIGN_BOTTOM_LEFT",
    "ALIGN_BOTTOM_RIGHT",
    "QT_COMBO_BOX_SIZE_POLICY",
    "QT_REG_EXP_FLOAT_VALIDATOR",
    "QT_REG_EXP_INT_VALIDATOR",
    "QT_REG_EXP_SLICE_VALIDATOR",
    "QT_REG_EXP_INT_RANGE_VALIDATOR",
    "QT_REG_EXP_FLOAT_SLICE_VALIDATOR",
    "QT_REG_EXP_FLOAT_RANGE_VALIDATOR",
    "QT_REG_EXP_RGB_VALIDATOR",
    "POLICY_FIX_EXP",
    "POLICY_EXP_EXP",
    "POLICY_EXP_FIX",
    "POLICY_FIX_FIX",
    "POLICY_MIN_MIN",
]

from qtpy import QtCore, QtGui, QtWidgets


ALIGN_TOP_LEFT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop

ALIGN_TOP_CENTER = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop

ALIGN_TOP_RIGHT = QtCore.Qt.AlignRight | QtCore.Qt.AlignTop

ALIGN_CENTER_LEFT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

ALIGN_CENTER = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter

ALIGN_CENTER_RIGHT = QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

ALIGN_BOTTOM_LEFT = QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom

ALIGN_BOTTOM_CENTER = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom

ALIGN_BOTTOM_RIGHT = QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom

QT_COMBO_BOX_SIZE_POLICY = QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon

QT_REG_EXP_FLOAT_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(
        r"-?\d*\.?\d*|None|nan", QtCore.QRegularExpression.CaseInsensitiveOption
    )
)

QT_REG_EXP_INT_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(
        r"-?\d*|None|nan", QtCore.QRegularExpression.CaseInsensitiveOption
    )
)

QT_REG_EXP_SLICE_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(r"((-?\d*:?){1,3},?)*")
)

# validate a single range of type <start [int]>:<end [int]>
QT_REG_EXP_INT_RANGE_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(r"-?\d+:-?\d+")
)

# validate a single range of type <start [float]>:<end [float]>
QT_REG_EXP_FLOAT_SLICE_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(r"((-?\d*\.?\d*:?){1,3},?)*")
)
QT_REG_EXP_FLOAT_RANGE_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(r"-?\d+\.?\d*:-?\d+\.?\d*")
)


QT_REG_EXP_RGB_VALIDATOR = QtGui.QRegularExpressionValidator(
    QtCore.QRegularExpression(r"#[0-9A-Fa-f]{6}")
)

POLICY_FIX_EXP = (QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)

POLICY_EXP_EXP = (QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

POLICY_EXP_FIX = (QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

POLICY_FIX_FIX = (QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

POLICY_MIN_MIN = (QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
