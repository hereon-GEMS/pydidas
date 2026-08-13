# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["_PydidasTickBar"]

from typing import Any

from qtpy import QtCore
from silx.gui.plot.ColorBar import _TickBar

from pydidas_qtcore import PydidasQApplication


class _PydidasTickBar(_TickBar):
    """
    A subclass of silx.gui.plot.ColorBar._TickBar to handle the global font.

    This class is used to replace the original _TickBar class in silx.gui.plot.ColorBar.
    """

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
        _qtapp = PydidasQApplication.instance()
        _qtapp.sig_new_fontsize.connect(self._on_font_size_changed)
        if _qtapp.font_size != self._FONT_SIZE:
            self._on_font_size_changed(_qtapp.font_size)

    @QtCore.Slot(float)
    def _on_font_size_changed(self, new_font_size: float) -> None:
        """Handle the font size change signal."""
        _width = (
            int(
                3.5
                * (self._WIDTH_DISP_VAL - self._WIDTH_NO_DISP_VAL)
                * (new_font_size / 10)
            )
            + self._WIDTH_NO_DISP_VAL
        )
        for _item in [_TickBar, self]:
            _item._FONT_SIZE = new_font_size
            _item._WIDTH_DISP_VAL = _width
        self.computeTicks()
