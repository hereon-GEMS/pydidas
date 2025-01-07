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
#
# Parts of this file are adapted from the silx.gui.plot.ColorBar._TickBar
# widget which is distributed under the MIT license.

"""
Module with methods to substitute the original in the original silx _TickBar class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["tickbar_paintEvent", "tickbar_paintTick"]


from qtpy import QtCore, QtGui, QtWidgets
from silx.gui.plot.ColorBar import _TickBar

from pydidas.core.utils import update_qobject_font


def tickbar_paintEvent(instance: QtWidgets.QWidget, event: QtCore.QEvent):
    """
    Handle the paintEvent with the global font.

    This method is meant to replace the original "paintEvent" method in
    silx.gui.plot.ColorBar._TickBar

    Parameters
    ----------
    instance : QtWidgets.QWidget
        The _TickBar instance.
    event : QtGui.QEvent
        The paint event.
    """
    _qtapp = QtWidgets.QApplication.instance()
    painter = QtGui.QPainter(instance)
    update_qobject_font(painter, pointSizeF=_qtapp.font_size - 2)
    _font_metric = QtGui.QFontMetrics(painter.font())
    instance._WIDTH_DISP_VAL = int(
        5.5 * (_font_metric.averageCharWidth()) + instance._LINE_WIDTH
    )
    instance._resetWidth()

    # paint ticks
    for val in instance.ticks:
        instance._paintTick(val, painter, majorTick=True)

    # paint subticks
    for val in instance.subTicks:
        instance._paintTick(val, painter, majorTick=False)


def tickbar_paintTick(
    instance: QtWidgets.QWidget,
    val: float,
    painter: QtGui.QPainter,
    majorTick: bool = True,
):
    """
    Paint a tick with the global font.

    This method is meant to replace the original method "_paintTick" in
    silx.gui.plot.ColorBar._TickBar

    Parameters
    ----------
    instance : QtWidgets.QWidget
        The _TickBar instance.
    val : float
        The value of the colorbar.
    painter : QtGui.QPainter
        The QPainter instance.
    majorTick : bool, optional
        Flag to handle major and minor ticks.
    """
    _font_metric = QtGui.QFontMetrics(painter.font())
    _value_str = instance.form.format(val)
    _offset = _font_metric.tightBoundingRect(_value_str).height() / 2

    viewportHeight = instance.rect().height() - instance.margin * 2 - 1
    relativePos = instance._getRelativePosition(val)
    height = int(viewportHeight * relativePos + instance.margin)
    _line_y0 = int(instance.width() - _TickBar._LINE_WIDTH / (1 if majorTick else 2))

    painter.drawLine(QtCore.QLine(_line_y0, height, instance.width(), height))
    if instance.displayValues and majorTick is True:
        painter.drawText(
            QtCore.QPoint(0, int(height + _offset)), instance.form.format(val)
        )
