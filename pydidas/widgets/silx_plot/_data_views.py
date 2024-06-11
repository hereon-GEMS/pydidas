# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasImageDataView"]


from functools import partialmethod

import silx.gui.data
from silx.gui import icons
from silx.gui.data.DataViews import (
    IMAGE_MODE,
    CompositeDataView,
    _ComplexImageView,
    _Plot2dView,
)
from silx.gui.utils import blockSignals

from .pydidas_plot2d import PydidasPlot2D


class PydidasImageDataView(CompositeDataView):
    """
    Display data as 2D image.

    This class replaces the generic Plot2d and ComplexImageView with the
    respective pydidas classes to access pydidas's functionality.
    """

    def __init__(self, parent):
        super(PydidasImageDataView, self).__init__(
            parent=parent,
            modeId=IMAGE_MODE,
            label="Pydidas Image",
            icon=icons.getQIcon("view-2d"),
        )
        self.addView(_ComplexImageView(parent))
        self.addView(_PydidasPlot2dView(parent))


class _PydidasPlot2dView(_Plot2dView):
    """
    View data using a PydidasPlot2d widget.
    """

    def createWidget(self, parent):
        widget = PydidasPlot2D(parent=parent)
        widget.getIntensityHistogramAction().setVisible(True)
        widget.setKeepDataAspectRatio(True)
        widget.getXAxis().setLabel("X")
        widget.getYAxis().setLabel("Y")
        maskToolsWidget = widget.getMaskToolsDockWidget().widget()
        maskToolsWidget.setItemMaskUpdated(True)
        return widget

    def axesNames(self, data, info):
        return ["use as image x-axis", "use as image y-axis"]


DATA_VIEW_AXES_NAMES = {
    "_Plot1dView": ["use as curve y"],
    "_Plot3dView": ["use as z", "use as y", "use as x"],
    "_ComplexImageView": ["use as image y", "use as image x"],
    "_ArrayView": ["use as column", "use as row"],
    "_StackView": ["depth", "use as image y", "use as image x"],
    "_NXdataScalarView": ["use as column", "use as row"],
}


def _DataView_axes_names(self, label, data, info):
    """
    Return the axes names for DataView classes
    """
    return DATA_VIEW_AXES_NAMES.get(label, None)


for _cls_name in DATA_VIEW_AXES_NAMES:
    _cls = getattr(silx.gui.data.DataViews, _cls_name)
    _method = getattr(_cls, "axesNames")
    setattr(_cls, "axesNames", partialmethod(_DataView_axes_names, _cls_name))
    setattr(silx.gui.data.DataViews, _cls_name, _cls)


def _Axis_setAxis(self, number, position, size):
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


def _Axis_setAxisNames(self, axesNames):
    """
    Set the Axes names.

    This method is intended to be used as a replacement for the original setAxisNames
    and defines the generic key as `use slice:` instead of an empty label.
    """
    self._Axis__axes.clear()
    with blockSignals(self._Axis__axes):
        self._Axis__axes.addItem("use slice:", "")
        for axis in axesNames:
            self._Axis__axes.addItem(axis, axis)

    self._Axis__updateSliderVisibility()


silx.gui.data.NumpyAxesSelector._Axis.setAxis = _Axis_setAxis
silx.gui.data.NumpyAxesSelector._Axis.setAxisNames = _Axis_setAxisNames
