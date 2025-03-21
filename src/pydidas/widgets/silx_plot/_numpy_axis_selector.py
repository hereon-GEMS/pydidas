# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with custom Pydidas DataViews to be used in silx widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasNumpyAxesSelector"]


from silx.gui.data.NumpyAxesSelector import NumpyAxesSelector, _Axis
from silx.gui.utils import blockSignals


# TODO : Use this file


class _AxisFromNumpyAxesSelector(_Axis):
    def setAxis(self, number, position, size):
        """
        Set axis information.

        This method is intended to be used as a replacement for the original setAxis
        method to use a custom label with `Data dimension` instead of `Dimension`.

        Parameters
        ----------
        number : int
            The number of the axis (from the original numpy array)
        position : int
            The current position in the axis (for slicing)
        size : int
            The size of this axis (0..n)
        """
        self._Axis__label.setText(f"Data dimension {number}:")
        self._Axis__axisNumber = number
        self._Axis__slider.setMaximum(size - 1)

    def setAxisNames(self, axesNames):
        """
        Set the Axes names.

        This method is intended to be used as a replacement for the original setAxisNames
        and defines the generic key as `use slice:` instead of an empty label.
        """
        self._Axis__axes.clear()
        with blockSignals(self._Axis__axes):
            self._Axis__axes.addItem("use for slicing", "")
            for axis in axesNames:
                self._Axis__axes.addItem(axis, axis)
        self._Axis__updateSliderVisibility()


class PydidasNumpyAxesSelector(NumpyAxesSelector):
    def setAxis(self, number, position, size):
        self._Axis__label.setText(f"Data dimension {number}:")
        self._Axis__axisNumber = number
        self._Axis__slider.setMaximum(size - 1)

    def _Axis_setAxisNames(self, axesNames):
        self._Axis__axes.clear()
        with blockSignals(self._Axis__axes):
            self._Axis__axes.addItem("use for slicing", "")
            for axis in axesNames:
                self._Axis__axes.addItem(axis, axis)

        self._Axis__updateSliderVisibility()
