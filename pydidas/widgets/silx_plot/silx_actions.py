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
Module with silx actions to extend the functionality of the generic silx plotting
widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "ChangeCanvasToData",
    "ExpandCanvas",
    "CropHistogramOutliers",
    "PydidasLoadImageAction",
]

from numbers import Real

from qtpy import QtWidgets, QtCore
import numpy as np
import silx.gui.plot
from silx.gui.plot.actions import PlotAction

from ...core import PydidasQsettingsMixin, UserConfigError, utils
from ...data_io import IoMaster, import_data
from ..file_dialog import PydidasFileDialog


class ChangeCanvasToData(PlotAction):
    """
    A customized silx Action to change the size of the figure canvas to the data
    dimensions.
    """

    def __init__(self, plot, parent=None):
        PlotAction.__init__(
            self,
            plot,
            icon=utils.get_pydidas_qt_icon("silx_limit_plot_canvas.png"),
            text="Change Canvas to data shape",
            tooltip="Change the canvas shape to match the data aspect ratio.",
            triggered=self._actionTriggered,
            checkable=False,
            parent=parent,
        )

    def _actionTriggered(self, checked=False):
        """
        Trigger the "change canvas to data" action.

        Parameters
        ----------
        checked : bool, optional
            Silx flag for a checked action. The default is False.
        """
        self.plot.setKeepDataAspectRatio(True)
        _range = self.plot.getDataRange()
        if _range.x is None or _range.y is None:
            return
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


class ExpandCanvas(PlotAction):
    """
    A modified silx ResetZoomAction which also resets the figure canvas to the maximum
    size allowed by the widget.
    """

    def __init__(self, plot, parent=None):
        PlotAction.__init__(
            self,
            plot,
            icon=utils.get_pydidas_qt_icon("silx_expand_plot_canvas.png"),
            text="Maximize canvas size",
            tooltip="Maximize the canvas size.",
            triggered=self._actionTriggered,
            checkable=False,
            parent=parent,
        )

    def _actionTriggered(self, checked=False):
        """
        Trigger the "expand canvas" action.

        Parameters
        ----------
        checked : bool, optional
            Silx flag for a checked action. The default is False.
        """
        self.plot.setKeepDataAspectRatio(False)
        self.plot._backend.ax.set_box_aspect(None)
        self.plot.resetZoom()


class CropHistogramOutliers(PlotAction, PydidasQsettingsMixin):
    """
    A new custom PlotAction to crop outliers from the histogram.

    This action will use the global 'histogram_outlier_fraction' QSettings value to
    determine where to limit the histogram and pick the respective value as new upper
    limit.

    The resolution for the upper limit is 27 bit, implemented in two tiers of 12 bit
    and 15 bit, respective to the full range of the image. For an Eiger detector, this
    corresponds to minimal final bins of 32 counts.

    The lower limit is implemented in two tiers of 12 bit
    """

    def __init__(self, plot, parent=None):
        PlotAction.__init__(
            self,
            plot,
            icon=utils.get_pydidas_qt_icon("silx_crop_histogram.png"),
            text="Crop colormap histogram outliers",
            tooltip="Crop the colormap's histogram outliers",
            triggered=self._actionTriggered,
            checkable=False,
            parent=parent,
        )
        PydidasQsettingsMixin.__init__(self)

    def _actionTriggered(self, checked=False):
        image = self.plot.getActiveImage()
        if not isinstance(image, silx.gui.plot.items.ColormapMixIn):
            return

        _fraction_low = self.q_settings_get_value(
            "user/histogram_outlier_fraction_low", dtype=float
        )
        _fraction_high = 1 - self.q_settings_get_value(
            "user/histogram_outlier_fraction_high", dtype=float
        )
        if _fraction_high - _fraction_low <= 0:
            raise UserConfigError(
                "The selected outlier fractions are too large. No data left to display."
            )

        _data = image.getData()
        colormap = image.getColormap()

        _cmap_limit_low = None
        _cmap_limit_high = None

        if _fraction_high < 1:
            _counts, _edges = np.histogram(_data[np.isfinite(_data)], bins=4096)
            _cumcounts = np.cumsum(_counts / _data.size)
            _index_stop = max(1, np.where(_cumcounts <= _fraction_high)[0].size)

            _counts2, _edges2 = np.histogram(
                _data, bins=32768, range=(0, _edges[_index_stop])
            )
            _cumcounts2 = np.cumsum(_counts2 / _data.size)
            _index_stop2 = max(1, np.where(_cumcounts2 <= _fraction_high)[0].size)

            _cmap_limit_high = _edges2[_index_stop2]

        if _fraction_low > 0:
            _counts, _edges = np.histogram(_data[np.isfinite(_data)], bins=4096)
            _cumcounts = np.cumsum(_counts / _data.size)
            _index_stop = np.where(_fraction_low <= _cumcounts)[0].size

            _counts2, _edges2 = np.histogram(
                _data, bins=32768, range=(0, _edges[_index_stop])
            )
            _cumcounts2 = np.cumsum(_counts2 / _data.size)
            _index_stop2 = max(1, np.where(_cumcounts2 <= _fraction_low)[0].size)

            _cmap_limit_low = _edges2[_index_stop2]

        if isinstance(_cmap_limit_low, Real) and isinstance(_cmap_limit_high, Real):
            if _cmap_limit_low >= _cmap_limit_high:
                _cmap_limit_low = 0.8 * _cmap_limit_high
        colormap.setVRange(_cmap_limit_low, _cmap_limit_high)


class PydidasLoadImageAction(QtWidgets.QAction):
    """
    Action to load an image using the pydidas file dialog.

    This action is used as additional option in the pyFAI calibration widgets.
    """

    def __init__(self, parent, caption="Select image file", ref=None):
        QtWidgets.QAction.__init__(self, parent)
        self.triggered.connect(self.__execute)
        self._dialog = PydidasFileDialog(
            caption=caption,
            dialog_type="open_file",
            extensions=IoMaster.get_string_of_formats(),
            qsettings_ref=ref,
        )
        self.setText("Use pydidas file dialog")

    @QtCore.Slot()
    def __execute(self):
        """
        Execute the dialog and select a filename.
        """
        _filename = self._dialog.get_user_response()
        if _filename is not None:
            _image = import_data(_filename)
            self.parent()._setValue(filename=_filename, data=_image)
