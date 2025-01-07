# This file is part of pydidas.
#
# Copyright 2022 - 2025, Helmholtz-Zentrum Hereon
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
Module with silx actions to extend the functionality of the generic silx plotting
widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2022 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "AutoscaleToMeanAndThreeSigma",
    "CropHistogramOutliers",
    "ChangeCanvasToData",
    "ExpandCanvas",
    "PydidasLoadImageAction",
    "PydidasGetDataInfoAction",
]


from typing import NewType

import silx.gui.plot
from qtpy import QtCore, QtWidgets
from silx.gui.colors import Colormap
from silx.gui.plot.actions import PlotAction

from pydidas.core import PydidasQsettingsMixin, UserConfigError
from pydidas.core.utils import calculate_histogram_limits
from pydidas.data_io import IoManager, import_data
from pydidas.resources import icons
from pydidas.widgets.file_dialog import PydidasFileDialog


PydidasPlot2d = NewType("PydidasPlot2d", QtWidgets.QWidget)


class ChangeCanvasToData(PlotAction):
    """
    A customized silx Action to change the size of the figure canvas to the data
    dimensions.
    """

    def __init__(self, plot: PydidasPlot2d, **kwargs: dict):
        PlotAction.__init__(
            self,
            plot,
            icon=icons.get_pydidas_qt_icon("silx_limit_plot_canvas.png"),
            text="Change Canvas to data shape",
            tooltip="Change the canvas shape to match the data aspect ratio.",
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
        )

    def _actionTriggered(self, checked: bool = False):
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

    def __init__(self, plot: PydidasPlot2d, **kwargs: dict):
        PlotAction.__init__(
            self,
            plot,
            icon=icons.get_pydidas_qt_icon("silx_expand_plot_canvas.png"),
            text="Maximize canvas size",
            tooltip="Maximize the canvas size.",
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
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


class AutoscaleToMeanAndThreeSigma(PlotAction):
    """
    A new custom PlotAction to set the colormap to autoscale with mean +/- 3 sigma.

    Parameters
    ----------
    plot : silx.gui.plot.PlotWidget
        The associated plot widget.
    **kwargs:
        Supported keyword arguments are:

        parent : Union[None, QObject], optional
            The parent QObject. The default is None.
        forced_image_legend : Union[None, str], optional
            A fixed image legend to use for enforcing the rescaling, if multiple
            image items are in a plot. None defaults to the active image.
            The default is None.
    """

    def __init__(self, plot: PydidasPlot2d, **kwargs: dict):
        PlotAction.__init__(
            self,
            plot,
            icon=icons.get_pydidas_qt_icon("silx_cmap_autoscale.png"),
            text="Autoscale colormap to mean +/- 3 std",
            tooltip="Autoscale colormap to mean +/- 3 std",
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
        )
        PydidasQsettingsMixin.__init__(self)
        self.__forced_image_legend = kwargs.get("forced_image_legend", None)

    def _actionTriggered(self, checked=False):
        if self.__forced_image_legend is None:
            image = self.plot.getActiveImage()
        else:
            image = self.plot.getImage(legend=self.__forced_image_legend)

        if not isinstance(image, silx.gui.plot.items.ColormapMixIn):
            return
        colormap = image.getColormap()
        colormap.setAutoscaleMode(Colormap.STDDEV3)
        colormap.setVMin(None)
        colormap.setVMax(None)


class CropHistogramOutliers(PlotAction, PydidasQsettingsMixin):
    """
    A new custom PlotAction to crop outliers from the histogram.

    This action will use the global 'histogram_outlier_fraction' QSettings value to
    determine where to limit the histogram and pick the respective value as new upper
    limit.

    The resolution for the upper limit is 27 bit, implemented in two tiers of 12 bit
    and 15 bit, respective to the full range of the image. For an Eiger detector, this
    corresponds to minimal final bins of 32 counts.

    The lower limit is implemented in two tiers of 12 bit.

    Parameters
    ----------
    plot : silx.gui.plot.PlotWidget
        The associated plot widget.
    **kwargs:
        Supported keyword arguments are:

        parent : Union[None, QObject], optional
            The parent QObject. The default is None.
        forced_image_legend : Union[None, str], optional
            A fixed image legend to use for enforcing the rescaling, if multiple
            image items are in a plot. None defaults to the active image.
            The default is None.
    """

    def __init__(self, plot: PydidasPlot2d, **kwargs: dict):
        PlotAction.__init__(
            self,
            plot,
            icon=icons.get_pydidas_qt_icon("silx_crop_histogram.png"),
            text="Crop colormap histogram outliers",
            tooltip="Crop the colormap's histogram outliers",
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
        )
        PydidasQsettingsMixin.__init__(self)
        self.__forced_image_legend = kwargs.get("forced_image_legend", None)

    def _actionTriggered(self, checked=False):
        if self.__forced_image_legend is None:
            image = self.plot.getActiveImage()
        else:
            image = self.plot.getImage(legend=self.__forced_image_legend)

        if not isinstance(image, silx.gui.plot.items.ColormapMixIn):
            return
        _colormap = image.getColormap()
        _cmap_limit_low, _cmap_limit_high = calculate_histogram_limits(image.getData())

        _colormap.setVRange(_cmap_limit_low, _cmap_limit_high)


class PydidasLoadImageAction(QtWidgets.QAction):
    """
    Action to load an image using the pydidas file dialog.

    This action is used as additional option in the pyFAI calibration widgets.

    Parameters
    ----------
    caption : str, optional
        The caption string for the file dialog. The default is 'Select image file.'
    ref : str, optional
        The reference for a persistent QSettings reference to the directory.
        The default is None.
    """

    def __init__(self, parent, caption="Select image file", ref=None):
        QtWidgets.QAction.__init__(self, parent)
        self.triggered.connect(self.__execute)
        self._dialog = PydidasFileDialog()
        self._dialog_kwargs = {
            "caption": caption,
            "qsettings_ref": ref,
        }
        self.setText("Use pydidas file dialog")

    @QtCore.Slot()
    def __execute(self):
        """
        Execute the dialog and select a filename.
        """
        _filename = self._dialog.get_existing_filename(
            caption=self._dialog_kwargs["caption"],
            formats=IoManager.get_string_of_formats(),
            qsettings_ref=self._dialog_kwargs["qsettings_ref"],
        )
        if _filename is not None:
            _image = import_data(_filename).array
            if _image.ndim == 3:
                _image = _image.mean(axis=0)
            if _image.ndim != 2:
                raise UserConfigError("The input data is not a 2D image.")
            self.parent()._setValue(filename=_filename, data=_image)


class PydidasGetDataInfoAction(PlotAction):
    """
    Action to select a datapoint and show more information about this datapoint.
    """

    sig_show_more_info_for_data = QtCore.Signal(float, float)

    def __init__(self, plot: PydidasPlot2d, **kwargs: dict):
        PlotAction.__init__(
            self,
            plot,
            icon=icons.get_pydidas_qt_icon("silx_get_data_info.png"),
            text="Show information of scan point",
            tooltip=(
                "Show information about the scan point associated with this datapoint."
            ),
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
        )

    @QtCore.Slot()
    def _actionTriggered(self):
        """
        Execute the action and pick a mouse click.
        """
        self.plot.sigPlotSignal.connect(self.__process_event)
        self.setEnabled(False)

    @QtCore.Slot(dict)
    def __process_event(self, event):
        """
        Process the event. If a mouse button click was detected, show popup.
        """
        if event["event"] == "mouseClicked":
            self.plot.sigPlotSignal.disconnect(self.__process_event)
            self.sig_show_more_info_for_data.emit(event["x"], event["y"])
            self.setEnabled(True)
