# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["_PydidasTickBar"]


from typing import Any

from qtpy import QtCore
from qtpy.QtGui import QPainter
from silx.gui.plot.ColorBar import _TickBar

from pydidas_qtcore import PydidasQApplication


class _PydidasTickBar(_TickBar):
    """
    A subclass of silx.gui.plot.ColorBar._TickBar to handle the global font.

    This class is used to replace the original _TickBar class
    in silx.gui.plot.ColorBar.
    """

    _DEFAULT_WIDTH_DELTA = _TickBar._WIDTH_DISP_VAL - _TickBar._WIDTH_NO_DISP_VAL

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the _PydidasTickBar instance.

        Parameters
        ----------
        *args : Any
            Positional arguments for the _TickBar constructor.
        **kwargs : Any
            Keyword arguments for the _TickBar constructor.
        """
        super().__init__(*args, **kwargs)
        self._font = self.font()
        self._viewport_height: int = 0
        _qtapp = PydidasQApplication.instance()
        self._font.setPointSizeF(_qtapp.font_size)
        _qtapp.sig_new_fontsize.connect(self._process_font_size_change)

    @QtCore.Slot(float)
    def _process_font_size_change(self, new_size: float) -> None:
        """
        Slot to process the font size change signal.

        Parameters
        ----------
        new_size : float
            The new font size to be set.
        """
        self._font.setPointSizeF(new_size)
        self.repaint()

    def paintEvent(self, event) -> None:
        """Subclass the paintEvent to use the global font size."""
        _painter = QPainter(self)
        _painter.setFont(self._font)
        _font_metrics = _painter.fontMetrics()
        self._viewport_height = self.rect().height() - self.margin * 2 - 1

        _tick_texts = [self.form.format(_val) for _val in self.ticks]
        _max_width = 0

        for val, _text in zip(self.ticks, _tick_texts):
            _text = self.form.format(val)
            _bbox = _font_metrics.tightBoundingRect(_text)
            _width = _bbox.width()
            _offset = int(_bbox.height() / 2)
            _max_width = max(_max_width, _width)
            self._paintTick(
                val, _painter, majorTick=True, text=_text, text_offset=_offset
            )
        for val in self.subTicks:
            self._paintTick(val, _painter, majorTick=False)

        self.setFixedWidth(_max_width + _TickBar._WIDTH_NO_DISP_VAL + self.margin)

    def _paintTick(
        self,
        val: float,
        _painter,
        majorTick: bool = True,
        text: str = "",
        text_offset: int = 0,
    ) -> None:
        """
        Paint a single tick on the tick bar.

        Parameters
        ----------
        val : float
            The value of the tick to paint.
        majorTick : bool, optional
            Whether the tick is a major tick, by default True
        text : str
            The text to display for the tick, by default an empty string.
        text_offset : int
            The offset of the text to display for the tick, by default 0.

        """
        _rel_pos = self._getRelativePosition(val)
        _y_pos = int(self._viewport_height * _rel_pos + self.margin)
        _line_width = _TickBar._LINE_WIDTH if majorTick else _TickBar._LINE_WIDTH / 2

        _painter.drawLine(
            QtCore.QLine(int(self.width() - _line_width), _y_pos, self.width(), _y_pos)
        )
        if self.displayValues and majorTick:
            _painter.drawText(QtCore.QPoint(0, _y_pos + text_offset), text)
