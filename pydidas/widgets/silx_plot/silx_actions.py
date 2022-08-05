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
Module with silx actions for PlotWindows.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ChangeCanvasToData", "ExpandCanvas", "CropHistogramOutliers"]

import os

import numpy as np
import silx.gui.plot
from qtpy import QtGui
from silx.gui.plot.actions import PlotAction
from silx.gui.plot.actions.control import ResetZoomAction

from ...core.utils import get_pydidas_icon_path
from ...core import PydidasQsettingsMixin


class ChangeCanvasToData(PlotAction):
    """
    A customized silx Action to change the size of the figure canvas to the data
    dimensions.
    """

    def __init__(self, plot, parent=None):
        PlotAction.__init__(
            self,
            plot,
            icon=QtGui.QIcon(
                os.path.join(get_pydidas_icon_path(), "silx_limit_plot_canvas.png")
            ),
            text="Change Canvas to data shape",
            tooltip="Change the canvas shape to match the data aspect ratio.",
            triggered=self._actionTriggered,
            checkable=False,
            parent=parent,
        )

    def _actionTriggered(self, checked=False):

        self.plot.setKeepDataAspectRatio(True)
        _range = self.plot.getDataRange()
        _plot_data_aspect = (
            1
            if self.plot._backend.ax.get_aspect() == "auto"
            else self.plot._backend.ax.get_aspect()
        )
        _data_aspect = (_range.x[1] - _range.x[0]) / (_range.y[1] - _range.y[0])
        self.plot._backend.ax.set_box_aspect(_plot_data_aspect / _data_aspect)
        self.plot._backend.ax.set_anchor("C")
        self.plot.resetZoom()
        # for some reason, need to call resetZoom twice to match data to new canvas
        self.plot.resetZoom()


class ExpandCanvas(ResetZoomAction):
    """
    A modified silx ResetZoomAction which also resets the figure canvas to the maximum
    size allowed by the widget.
    """

    def __init__(self, plot, parent=None):
        PlotAction.__init__(
            self,
            plot,
            icon=QtGui.QIcon(
                os.path.join(get_pydidas_icon_path(), "silx_expand_plot_canvas.png")
            ),
            text="Maximize canvas size",
            tooltip="Maximize the canvas size.",
            triggered=self._actionTriggered,
            checkable=False,
            parent=parent,
        )

    def _actionTriggered(self, checked=False):

        self.plot.setKeepDataAspectRatio(False)
        _figsize = self.plot._backend.ax.figure.get_size_inches()
        _aspect = _figsize[1] / _figsize[0]
        self.plot._backend.ax.set_box_aspect(_aspect)
        self.plot.resetZoom()


class CropHistogramOutliers(PlotAction, PydidasQsettingsMixin):
    """
    A new custom PlotAction to crop outliers from the histogram.

    This action will use the global 'histogram_outlier_fraction' QSettings value to
    determine where to limit the histogram and pick the respective value as new upper
    limit.
    The resolution is 27 bit, implemented in two tiers of 12 bit and 15 bit, respective
    to the full range of the image. For an Eiger detector, this corresponds to minimal
    final bins of 32 counts.
    """

    def __init__(self, plot, parent=None):
        PlotAction.__init__(
            self,
            plot,
            icon=QtGui.QIcon(
                os.path.join(get_pydidas_icon_path(), "silx_crop_histogram.png")
            ),
            text="Crop histogram outliers",
            tooltip="Crop the upper histogram outliers",
            triggered=self._actionTriggered,
            checkable=False,
            parent=parent,
        )
        PydidasQsettingsMixin.__init__(self)

    def _actionTriggered(self, checked=False):
        image = self.plot.getActiveImage()
        if not isinstance(image, silx.gui.plot.items.ColormapMixIn):
            return

        _fraction = 1 - self.q_settings_get_value(
            "global/histogram_outlier_fraction", dtype=float
        )
        _data = image.getData()
        _counts, _edges = np.histogram(_data, bins=4096)
        _cumcounts = np.cumsum(_counts / _data.size)
        _index_stop = max(1, np.where(_cumcounts <= _fraction)[0].size)

        _countsB, _edgesB = np.histogram(
            _data, bins=32768, range=(0, _edges[_index_stop])
        )
        _cumcountsB = np.cumsum(_countsB / _data.size)
        _index_stopB = max(1, np.where(_cumcountsB <= _fraction)[0].size)

        _cmap_limit_high = _edgesB[_index_stopB]

        colormap = image.getColormap()
        colormap.setVMax(_cmap_limit_high)
