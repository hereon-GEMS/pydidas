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
Module with PydidasImageView class which adds configurations to the base silx ImageView.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasDataViewer"]


import logging

from silx.gui import icons
from silx.gui.data import DataViewer, DataViews
from silx.gui.data.DataViews import (
    IMAGE_MODE,
    CompositeDataView,
    _Plot2dView,
)

from .pydidas_plot2d import PydidasPlot2D


class _PydidasImageView(CompositeDataView):
    """
    Display data as 2D image.

    This class replaces the generic Plot2d and ComplexImageView with the
    respective pydidas classes to access pydidas's functionality.
    """

    def __init__(self, parent):
        super(_PydidasImageView, self).__init__(
            parent=parent,
            modeId=IMAGE_MODE,
            label="Image",
            icon=icons.getQIcon("view-2d"),
        )
        self.addView(DataViews._ComplexImageView(parent))
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


class PydidasDataViewer(DataViewer.DataViewer):
    """Overwrite methods to avoid to create views while the instance
    is not created. `initializeViews` have to be called manually."""

    def _initializeViews(self):
        pass

    def initializeViews(self):
        """Avoid to create views while the instance is not created."""
        super(PydidasDataViewer, self)._initializeViews()

    def createDefaultViews(self, parent=None):
        """Allow the DataViewerFrame to override this function"""
        return self.parent().createDefaultViews(parent)

    def _createDefaultViews(self, parent):
        """
        Replace the _ImageView with the PydidasImageView
        :param QWidget parent: QWidget parent of the views
        :rtype: List[silx.gui.data.DataView]
        """
        _logger = logging.getLogger("silx.gui.data.DataViewer")
        _logger.setLevel(logging.ERROR)
        viewClasses = [
            DataViews._EmptyView,
            DataViews._Hdf5View,
            DataViews._NXdataView,
            DataViews._Plot1dView,
            _PydidasImageView,
            DataViews._Plot3dView,
            DataViews._RawView,
            DataViews._StackView,
            DataViews._Plot2dRecordView,
        ]
        views = []
        for viewClass in viewClasses:
            try:
                view = viewClass(parent)
                views.append(view)
            except Exception:
                _logger.warning(
                    "%s instantiation failed. View is ignored" % viewClass.__name__
                )
                _logger.debug("Backtrace", exc_info=True)
        return views
