# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasImageDataView"]


from silx.gui import icons
from silx.gui.data.DataViews import (
    IMAGE_MODE,
    CompositeDataView,
    _ComplexImageView,
    _Plot2dView,
)

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
            label="Image",
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
