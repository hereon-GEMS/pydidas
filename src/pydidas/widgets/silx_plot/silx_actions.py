# This file is part of pydidas.
#
# Copyright 2022 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2022 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "CropHistogramOutliersAction",
    "LockZoomAction",
    "AutoscaleToMeanAndThreeSigmaAction",
    "AutoscaleToMinMaxAction",
    "ChangeCanvasAction",
    "PydidasLoadImageAction",
    "PydidasGetDataInfoAction",
]


from typing import Any, Literal, NewType

import silx.gui.plot
from qtpy import QtCore, QtGui, QtWidgets
from silx.gui.colors import Colormap
from silx.gui.plot.actions import PlotAction

from pydidas.core import PydidasQsettingsMixin, UserConfigError
from pydidas.core.utils import calculate_histogram_limits
from pydidas.data_io import IoManager, import_data
from pydidas.resources import icons
from pydidas.widgets.file_dialog import PydidasFileDialog


PydidasPlot2d = NewType("PydidasPlot2d", QtWidgets.QWidget)


class _AutoscaleAction(PlotAction, PydidasQsettingsMixin):
    """
    A new custom PlotAction to set the colormap to autoscale the colormap.

    Parameters
    ----------
    plot : silx.gui.plot.PlotWidget
        The associated plot widget.
    **kwargs : Any
        Supported keyword arguments are:

        parent : QObject or None, optional
            The parent QObject. The default is None.
        forced_image_legend : str or None, optional
            A fixed image legend to use for enforcing the rescaling if multiple
            image items are in a plot. None defaults to the active image.
            The default is None.
    """

    icon: QtGui.QIcon = None
    action_text: str = None
    scale_mode: str = None

    def __init__(self, plot: PydidasPlot2d, **kwargs: Any) -> None:
        PlotAction.__init__(
            self,
            plot,  # noqa -- wrong type hinting since PydidasPlot2d is a PlotWidget
            self.icon,
            self.action_text,
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
        )
        PydidasQsettingsMixin.__init__(self)
        self.__forced_image_legend = kwargs.get("forced_image_legend", None)

    def _actionTriggered(self, checked: bool = False) -> None:  # noqa C0103
        """
        Trigger the autoscale action.

        Parameters
        ----------
        checked : bool, optional
            silx flag for a checked action. The default is False.
        """
        if self.__forced_image_legend is None:
            image = self.plot.getActiveImage()
        else:
            image = self.plot.getImage(legend=self.__forced_image_legend)

        if not isinstance(image, silx.gui.plot.items.ColormapMixIn):
            return
        colormap = image.getColormap()
        colormap.setAutoscaleMode(self.scale_mode)
        colormap.setVMin(None)
        colormap.setVMax(None)


class ChangeCanvasAction(PlotAction):
    """
    A customized silx Action to change the size of the figure canvas.

    This action can be used to toggle the canvas size from the maximum
    available size to a tight fit for the data dimensions.
    """

    toolTip = {
        "set_to_expand": "Maximize the canvas size to use the available screen space.",
        "set_to_tight": "Change the canvas shape to match the data aspect ratio.",
    }
    icon = {
        "set_to_expand": icons.create_pydidas_icon("silx_plot_canvas_full.png"),
        "set_to_tight": icons.create_pydidas_icon("silx_plot_canvas_tight.png"),
    }
    text = {
        "set_to_expand": "Maximize canvas size",
        "set_to_tight": "Change Canvas to data shape",
    }

    def __init__(self, plot: PydidasPlot2d, **kwargs: Any) -> None:
        PlotAction.__init__(
            self,
            plot,  # noqa -- wrong type hinting since PydidasPlot2d is a PlotWidget
            icon=self.icon["set_to_tight"],
            text=self.text["set_to_tight"],
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
        )
        self._full_canvas = True
        self._update_description_from_canvas()
        if kwargs.get("visible") in [True, False]:
            self.setVisible(kwargs.get("visible"))

    def _actionTriggered(self, checked: bool = False) -> None:  # noqa C0103
        """
        Trigger the "change canvas to data" action.

        Parameters
        ----------
        checked : bool, optional
            silx flag for a checked action. The default is False.
        """
        self.set_canvas_mode(not self._full_canvas)

    def set_canvas_mode(self, mode: Literal["tight", "full"] | bool) -> None:
        """
        Set the canvas mode to tight or full.

        Parameters
        ----------
        mode : Literal["tight", "full"] or bool
            The canvas mode to set. `tight` will restrict the canvas to the data
            aspect ratio, while "full" will expand the canvas to the maximum
            available size. If bool, the mode will be interpreted as the
            flag for the full canvas mode.
        """
        self._full_canvas = mode in ["full", True]
        if self._full_canvas:
            self._expand_canvas()
        else:
            self._restrict_canvas_to_data()
        self._update_description_from_canvas()
        self.plot.resetZoom()

    def _restrict_canvas_to_data(self) -> None:
        """Restrict the canvas size to match the data aspect ratio."""
        self.plot.setKeepDataAspectRatio(True)
        _range = self.plot.getDataRange()
        if _range.x is None or _range.y is None:
            return
        _plot_data_aspect = (
            1
            if self.plot._backend.ax.get_aspect() == "auto"  # noqa W0212
            else self.plot._backend.ax.get_aspect()  # noqa W0212
        )
        _data_aspect = (_range.x[1] - _range.x[0]) / (_range.y[1] - _range.y[0])
        self.plot._backend.ax.set_box_aspect(_plot_data_aspect / _data_aspect)  # noqa W0212
        self.plot._backend.ax.set_anchor("C")  # noqa W0212
        self.plot.resetZoom()

    def _expand_canvas(self) -> None:
        """Expand the canvas to the maximum available size."""
        self.plot.setKeepDataAspectRatio(False)
        self.plot._backend.ax.set_box_aspect(None)  # noqa W0212

    def _update_description_from_canvas(self) -> None:
        """Expand the action's description from the canvas mode."""
        _key = "set_to_tight" if self._full_canvas else "set_to_expand"
        self.setToolTip(self.toolTip[_key])
        self.setIcon(self.icon[_key])
        self.setText(self.text[_key])


class LockZoomAction(PlotAction):
    """
    A customized silx Action to lock the current zoom level

    This action can be used to lock the zoom settings in its current mode.
    """

    icon = {
        "lock": icons.create_pydidas_icon("silx_zoom_lock.png"),
        "unlock": icons.create_pydidas_icon("silx_zoom_unlock.png"),
    }
    text = {
        "lock": "Lock the current zoom settings and disable automatic zoom resets",
        "unlock": "Unlock the current zoom settings for automatic resets",
    }

    def __init__(self, plot: PydidasPlot2d, **kwargs: Any) -> None:
        PlotAction.__init__(
            self,
            plot,  # noqa -- wrong type hinting since PydidasPlot2d is a PlotWidget
            icon=self.icon["lock"],
            text=self.text["lock"],
            triggered=self._actionTriggered,
            checkable=True,
            parent=kwargs.get("parent", None),
        )
        self._zoom_locked = False
        self._update_action_description_from_lock()
        if kwargs.get("visible") in [True, False]:
            self.setVisible(kwargs.get("visible"))

    @property
    def locked(self) -> bool:
        """Get the zoom lock state."""
        return self._zoom_locked

    def _actionTriggered(self, checked: bool = False) -> None:  # noqa C0103
        """
        Trigger the "zoom lock" action.

        Parameters
        ----------
        checked : bool, optional
            silx flag for a checked action. The default is False.
        """
        self.set_zoom_lock(not self._zoom_locked)

    def set_zoom_lock(self, mode: bool) -> None:
        """
        Set the canvas mode to tight or full.

        Parameters
        ----------
        mode : bool
            The lock mode. If True, the zoom is locked and will not reset
            automatically on changed data.
        """
        self._zoom_locked = bool(mode)
        self._update_action_description_from_lock()

    def _update_action_description_from_lock(self) -> None:
        """Expand the action's description from the canvas mode."""
        _key = "unlock" if self._zoom_locked else "lock"
        self.setIcon(self.icon[_key])
        self.setText(self.text[_key])


class AutoscaleToMeanAndThreeSigmaAction(_AutoscaleAction):
    """
    A new custom PlotAction to set the colormap to autoscale with mean +/- 3 sigma.
    """

    icon = icons.create_pydidas_icon("silx_cmap_mean_w_sigma.png")
    action_text = "Autoscale colormap to mean +/- 3 std"
    scale_mode = Colormap.STDDEV3


class AutoscaleToMinMaxAction(_AutoscaleAction):
    """
    A new custom PlotAction to set the colormap to min/max autoscale.
    """

    icon = icons.create_pydidas_icon("silx_cmap_min_max.png")
    action_text = "Autoscale colormap to min / max"
    scale_mode = Colormap.MINMAX


class CropHistogramOutliersAction(PlotAction, PydidasQsettingsMixin):
    """
    A new custom PlotAction to crop outliers from the histogram.

    This action will use the global 'histogram_outlier_fraction' QSettings value to
    determine where to limit the histogram and pick the respective value as the new
    upper limit.

    The resolution for the upper limit is 27 bit, implemented in two tiers of 12 bit
    and 15 bit, respective to the full range of the image. For an Eiger detector,
    this corresponds to minimal final bins of 32 counts.

    The lower limit is implemented in two tiers of 12 bits.

    Parameters
    ----------
    plot : silx.gui.plot.PlotWidget
        The associated plot widget.
    **kwargs : Any
        Supported keyword arguments are:

        parent : QObject or None, optional
            The parent QObject. The default is None.
        forced_image_legend : str or None, optional
            A fixed image legend to use for enforcing the rescaling if multiple
            image items are in a plot. None defaults to the active image.
            The default is None.
    """

    def __init__(self, plot: PydidasPlot2d, **kwargs: Any) -> None:
        PlotAction.__init__(
            self,
            plot,  # noqa -- wrong type hinting since PydidasPlot2d is a PlotWidget
            icon=icons.create_pydidas_icon("silx_crop_histogram.png"),
            text="Crop colormap histogram outliers",
            tooltip="Crop the colormap's histogram outliers",
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
        )
        PydidasQsettingsMixin.__init__(self)
        self.__forced_image_legend = kwargs.get("forced_image_legend", None)

    def _actionTriggered(self, checked: bool = False) -> None:  # noqa C0103
        """
        Trigger the crop histogram outliers action.

        Parameters
        ----------
        checked : bool, optional
            silx flag for a checked action. The default is False.
        """
        if self.__forced_image_legend is None:
            image = self.plot.getActiveImage()
        else:
            image = self.plot.getImage(legend=self.__forced_image_legend)

        if not isinstance(image, silx.gui.plot.items.ColormapMixIn):
            return
        _colormap = image.getColormap()
        _cmap_limit_low, _cmap_limit_high = calculate_histogram_limits(image.getData())  # type: ignore[attr-defined]
        _colormap.setVRange(_cmap_limit_low, _cmap_limit_high)


class PydidasLoadImageAction(QtWidgets.QAction):
    """
    Action to load an image using the pydidas file dialog.

    This action is used as an additional option in the pyFAI calibration widgets.

    Parameters
    ----------
    parent : QtWidgets.QWidget or None
        The parent widget. The default is None.
    caption : str, optional
        The caption string for the file dialog. The default is 'Select image file.'
    ref : str or None, optional
        The reference for a persistent QSettings reference to the directory.
        The default is None.
    """

    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        caption: str = "Select image file",
        ref: str | None = None,
    ) -> None:
        QtWidgets.QAction.__init__(self, parent)
        self.triggered.connect(self.__execute)  # type: ignore[attr-defined]
        self._dialog = PydidasFileDialog()
        self._dialog_kwargs = {
            "caption": caption,
            "qsettings_ref": ref,
        }
        self.setText("Use pydidas file dialog")

    @QtCore.Slot()
    def __execute(self) -> None:
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
            self.parent()._setValue(filename=_filename, data=_image)  # noqa W0212


class PydidasGetDataInfoAction(PlotAction):
    """
    Action to select a datapoint and show more information about this datapoint.
    """

    sig_show_more_info_for_data = QtCore.Signal(float, float)

    def __init__(self, plot: PydidasPlot2d, **kwargs: Any) -> None:
        PlotAction.__init__(
            self,
            plot,  # noqa -- wrong type hinting since PydidasPlot2d is a PlotWidget
            icon=icons.create_pydidas_icon("silx_get_data_info.png"),
            text="Show information of scan point",
            tooltip=(
                "Show information about the scan point associated with this datapoint."
            ),
            triggered=self._actionTriggered,
            checkable=False,
            parent=kwargs.get("parent", None),
        )

    @QtCore.Slot()
    def _actionTriggered(self) -> None:  # noqa C0103
        """
        Execute the action and pick a mouse click.
        """
        self.plot.sigPlotSignal.connect(self.__process_event)
        self.setEnabled(False)

    @QtCore.Slot(dict)
    def __process_event(self, event: dict[str, Any]) -> None:
        """
        Process the event. If a mouse button click was detected, show a popup.

        Parameters
        ----------
        event : dict[str, Any]
            The event dictionary containing event information.
        """
        if event["event"] == "mouseClicked":
            self.plot.sigPlotSignal.disconnect(self.__process_event)
            self.sig_show_more_info_for_data.emit(event["x"], event["y"])  # type: ignore[attr-defined]
            self.setEnabled(True)
