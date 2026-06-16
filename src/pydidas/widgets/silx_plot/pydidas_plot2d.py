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

"""
Module with the PydidasPlot2D class which extends the generic silx Plot2D class by
additional actions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPlot2D"]


from contextlib import nullcontext
from functools import partial
from typing import Any

import numpy as np
from matplotlib.ticker import AutoLocator, ScalarFormatter
from qtpy import QtCore, QtGui, QtWidgets
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D
from silx.gui.plot.items import Scatter

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import Dataset, PydidasQsettingsMixin
from pydidas.widgets.silx_plot._coordinate_transform_button import (
    CoordinateTransformButton,
)
from pydidas.widgets.silx_plot._silx_tickbar import (
    tickbar_paintEvent,
    tickbar_paintTick,
)
from pydidas.widgets.silx_plot.pydidas_position_info import PydidasPositionInfo
from pydidas.widgets.silx_plot.silx_actions import (
    AutoscaleToMeanAndThreeSigmaAction,
    AutoscaleToMinMaxAction,
    ChangeCanvasAction,
    CropHistogramOutliersAction,
    LockZoomAction,
    PydidasGetDataInfoAction,
)
from pydidas.widgets.silx_plot.utilities import (
    axis_is_columns,
    check_data_dimensions,
    get_allowed_kwargs,
    get_column_labels,
)
from pydidas_qtcore import PydidasQApplication


_SCATTER_LEGEND = "pydidas non-uniform image"
_IMAGE_LEGEND = "pydidas image"


class PydidasPlot2D(Plot2D, PydidasQsettingsMixin):
    """
    A customized silx.gui.plot.Plot2D with an additional features.

    Additional features are implemented through additional SilxActions which
    are added to the toolbar.
    """

    sig_get_more_info_for_data = QtCore.Signal(float, float)
    sig_new_data_size = QtCore.Signal(int, int)
    sig_data_linearity = QtCore.Signal(bool)
    init_kwargs = ["cs_transform", "use_data_info_action", "diffraction_exp"]

    def __init__(self, **kwargs: Any) -> None:
        PydidasQsettingsMixin.__init__(self)
        Plot2D.__init__(
            self, parent=kwargs.get("parent", None), backend=kwargs.get("backend", None)
        )
        self._default_unit: str = "no unit"
        self.__plotted_data_shape: tuple[int, int] = (0, 0)
        self._qtapp = PydidasQApplication.instance()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # type: ignore[attr-defined]
        self._update_config(kwargs)
        self._update_position_widget()
        self._set_up_custom_actions()
        self._set_colormap_and_bar()
        self._qtapp.sig_mpl_font_change.connect(self._update_mpl_fonts)
        self._qtapp.sig_updated_user_config.connect(self._user_config_update)

    # -----------------------------------------#
    # re-implemented public Plot2D functions  #
    # -----------------------------------------#

    def addImage(self, data: Dataset | np.ndarray, **kwargs: Any) -> None:
        """
        Add an image to the plot.

        This method implements an additional dimensionality check before passing
        the image to the Plot2D.addImage method.

        Parameters
        ----------
        data : Dataset or np.ndarray
            The input data to be displayed.

        **kwargs : Any
            Any supported Plot2D.addImage keyword arguments.
        """
        self.remove(_SCATTER_LEGEND, kind="scatter")
        if isinstance(data, Dataset):
            self.plot_pydidas_dataset(data, **kwargs)
        else:
            check_data_dimensions(data, 2)
            kwargs.update({"legend": _IMAGE_LEGEND, "replace": True})
            Plot2D.addImage(self, data, **kwargs)
            self.sig_new_data_size.emit(*data.shape)  # type: ignore[attr-defined]
            self.sig_data_linearity.emit(True)  # type: ignore[attr-defined]
            self._update_cs_units("", "")

    def clear(self) -> None:
        """Override clear to also clear the stored data."""
        super().clear()
        self.clear_plot()

    # -----------------------------------------#
    # new properties                          #
    # -----------------------------------------#

    @property
    def default_unit(self) -> str:
        """
        The default unit for the plot axes.

        Returns
        -------
        str
            The default unit for the plot axes.
        """
        return self._default_unit

    @default_unit.setter
    def default_unit(self, value: str) -> None:
        """
        Set the default unit for the plot axes.

        Parameters
        ----------
        value : str
            The new default unit for the plot axes.
        """
        self._default_unit = value
        self._update_cs_units(value, value)

    # -----------------------------------------#
    # new public methods                      #
    # -----------------------------------------#

    def clear_plot(self) -> None:
        """Clear the plot and remove all items."""
        self.reset_ticks()
        self.remove()
        self.setGraphTitle("")
        self.setGraphYLabel("")
        self.setGraphXLabel("")
        self.getColorBarWidget().setLegend("")

    def reset_ticks(self) -> None:
        """Reset the axis ticks to their default state."""
        _backend = self.getBackend()
        _ax = _backend.ax
        _ax.xaxis.set_major_locator(AutoLocator())
        _ax.xaxis.set_major_formatter(ScalarFormatter())
        _ax.yaxis.set_major_locator(AutoLocator())
        _ax.yaxis.set_major_formatter(ScalarFormatter())
        _ax.tick_params(axis="x", labelrotation=0)

    def plot_pydidas_dataset(self, data: Dataset, **kwargs: Any) -> None:
        """
        Plot a pydidas Dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : Any
            Additional keyword arguments to be passed to the silx plot method.
        """
        self.reset_ticks()
        check_data_dimensions(data, 2)
        _title = kwargs.pop("title", "")
        _data_is_linear = not (data.is_axis_nonlinear(0) or data.is_axis_nonlinear(1))
        _data_has_same_shape = data.shape == self.__plotted_data_shape
        self.__plotted_data_shape = (int(data.shape[0]), int(data.shape[1]))
        self._config["data_shape"] = data.shape
        self.profile.setEnabled(_data_is_linear)
        self.sig_data_linearity.emit(_data_is_linear)
        if _data_is_linear:
            self._plot_linear_image(data, kwargs)
        else:
            self._plot_nonlinear_axes_image(data)
        self._update_cs_units(data.axis_units[1], data.axis_units[0])
        if _title:
            self.setGraphTitle(_title)
        self._set_axis_labels(0, data)
        self._set_axis_labels(1, data)
        self._update_colorbar(data)
        if not self._actions["lock_zoom"].locked and not _data_has_same_shape:
            self._actions["canvas"].set_canvas_mode(
                data.shape != self._config["diffraction_exp"].det_shape
            )

    # display_data is a generic alias used in all custom silx plots to have a
    # uniform interface call to display data in DataViewer-like classes
    display_data = plot_pydidas_dataset

    # -----------------------------------------#
    # private plotting methods                 #
    # -----------------------------------------#

    def _plot_linear_image(self, data: Dataset, plot_kwargs: dict[str, Any]) -> None:
        """
        Add an image with linear axes to the plot.

        This method directly passes the image to the Plot2D.addImage method.

        Parameters
        ----------
        data : Dataset
            The input data to be displayed.
        plot_kwargs : dict[str, Any]
            The keyword arguments to be passed to the Plot2D.addImage method.
        """
        _plot_kwargs = {
            "replace": plot_kwargs.pop("replace", True),
            "copy": plot_kwargs.pop("copy", False),
            "legend": _IMAGE_LEGEND,
        } | get_allowed_kwargs(Plot2D.addImage, plot_kwargs)
        self.remove(_SCATTER_LEGEND, kind="scatter")
        _xlimit, _ylimit, _origin, _scale = self._get_display_settings(data)
        _plot_kwargs["origin"] = _origin
        _plot_kwargs["scale"] = _scale
        Plot2D.addImage(self, data.array, **_plot_kwargs)
        self.setActiveImage(_IMAGE_LEGEND)
        if _xlimit is not None:
            self.setGraphXLimits(*_xlimit)
        if _ylimit is not None:
            self.setGraphYLimits(*_ylimit)
        self.sig_new_data_size.emit(*data.shape)

    def _get_display_settings(
        self,
        data: Dataset,
    ) -> tuple[
        tuple[float, float] | None,
        tuple[float, float] | None,
        tuple[float, float],
        tuple[float, float],
    ]:
        """
        Get the settings to have pixels centered at their values.

        Parameters
        ----------
        data : Dataset
            The dataset to get the axis settings from.

        Returns
        -------
        xlimits : tuple[float, float] or None
            The values for the x-axis limits if the zoom is locked, otherwise None.
        ylimits : tuple[float, float] or None
            The values for the y-axis limits if the zoom is locked, otherwise None.
        origin : tuple[float, float]
            The values for the axis origins.
        scale : tuple[float, float]
            The values for the axis scales to squeeze it into the correct
            dimensions for silx plotting.
        """
        _origin: list[float] = []
        _scale: list[float] = []
        _xlimit = self.getGraphXLimits() if self._actions["lock_zoom"].locked else None
        _ylimit = self.getGraphYLimits() if self._actions["lock_zoom"].locked else None
        # calling axis #1 [with x values]  first because silx expects (x, y) values.
        for _dim in (1, 0):
            _ax = data.get_axis_range(_dim)
            _delta = (_ax.max() - _ax.min()) / _ax.size
            _scale.append(float(_delta * (_ax.size + 1) / _ax.size))
            _origin.append(float(_ax[0] - _delta / 2))
        return _xlimit, _ylimit, tuple(_origin), tuple(_scale)  # noqa

    def _plot_nonlinear_axes_image(self, data: Dataset) -> None:
        """
        Add an image with non-linear axes to the plot.

        This method implements an additional dimensionality check before passing
        the image to the Plot2D.addImage method.

        Parameters
        ----------
        data : Dataset
            The input data to be displayed.
        """
        check_data_dimensions(data, 2)
        self.remove(_IMAGE_LEGEND, kind="image")
        self.sig_data_linearity.emit(False)  # type: ignore[attr-defined]
        _scatter = self.getScatter(_SCATTER_LEGEND)
        if _scatter is None:
            _scatter = Scatter()
            _scatter.setName(_SCATTER_LEGEND)
            Plot2D.addItem(self, _scatter)
        _grid_x, _grid_y = np.meshgrid(data.get_axis_range(1), data.get_axis_range(0))
        _scatter.setData(_grid_x.ravel(), _grid_y.ravel(), data.array.ravel())
        _scatter.setVisualization(_scatter.Visualization.IRREGULAR_GRID)
        self._notifyContentChanged(_scatter)
        self.setActiveScatter(_SCATTER_LEGEND)

    def _set_axis_labels(self, axis: int, data: Dataset) -> None:
        """
        Set the axis labels for the given axis.

        Parameters
        ----------
        axis : int
            The axis index to set the labels for. 0 for y-axis, 1 for x-axis.
        data : Dataset
            The dataset to get the labels from.
        """
        if axis_is_columns(axis, data):
            labels = get_column_labels(axis, data)
            backend = self.getBackend()
            ax = backend.ax
            if axis == 0:
                ax.set_yticks(list(range(len(labels))), labels)
            elif axis == 1:
                ax.set_xticks(list(range(len(labels))), labels, rotation=90)
            backend.fig.canvas.draw_idle()
        else:
            axis_desc = data.get_axis_description(axis)
            if axis == 0:
                self.setGraphYLabel(axis_desc)
            elif axis == 1:
                self.setGraphXLabel(axis_desc)

    def _update_colorbar(self, data: Dataset) -> None:
        """
        Update the colorbar limits and normalization based on the data.

        Parameters
        ----------
        data : Dataset
            The dataset to get the colorbar settings from.
        """
        if not axis_is_columns(0, data) and not axis_is_columns(1, data):
            _cbar_legend = data.data_description or "unspecified"
        else:
            _cbar_legend = ""
        self.getColorBarWidget().setLegend(_cbar_legend)

    # -----------------------------------------#
    # private initialization methods           #
    # -----------------------------------------#

    def _update_config(self, kwargs: dict[str, Any]) -> None:
        """
        Update the plot configuration.

        Parameters
        ----------
        kwargs : dict[str, Any]
            The keyword arguments to update the configuration.
        """
        self._user_config_update("cmap_name", self.q_settings_get("user/cmap_name"))
        self._user_config_update(
            "cmap_nan_color", self.q_settings_get("user/cmap_nan_color")
        )
        self._config = {
            "cs_transform": kwargs.get("cs_transform", True),
            "cs_transform_valid": False,
            "use_data_info_action": kwargs.get("use_data_info_action", False),
            "diffraction_exp": (
                DiffractionExperimentContext()
                if kwargs.get("diffraction_exp", None) is None
                else kwargs.get("diffraction_exp")
            ),
        }

    def _update_position_widget(self) -> None:
        """Update the position widget to be able to display units."""
        _pos_widget_converters = [
            (_field[1], _field[2]) for _field in self._positionWidget._fields
        ]
        _new_position_widget = PydidasPositionInfo(
            plot=self,
            converters=_pos_widget_converters,
            diffraction_exp=self._config["diffraction_exp"],
        )
        _new_position_widget.setSnappingMode(self._positionWidget._snappingMode)
        # _layout = self.findChild(self._positionWidget.__class__).parent().layout()
        _layout = self._positionWidget.parent().layout()
        _layout.replaceWidget(self._positionWidget, _new_position_widget)
        self._positionWidget = _new_position_widget

    def _set_up_custom_actions(self) -> None:
        """Add the pydidas custom actions"""
        self._create_custom_actions()
        self._add_actions_to_toolbar()
        self._connect_action_signals()

    def _create_custom_actions(self) -> None:
        """Create the custom actions"""
        self._actions: dict[str, QtGui.QAction | QtWidgets.QToolButton] = {}
        # The LockZoomAction can be used to disable automatic zooming
        # noinspection PyTypeChecker
        self._actions["lock_zoom"] = LockZoomAction(self, parent=self)

        # The ChangeCanvasAction will toggle between expanding the canvas
        # and setting a tight canvas fitting to the data
        # noinspection PyTypeChecker
        self._actions["canvas"] = ChangeCanvasAction(self, parent=self)  # type: ignore[arg-type]

        # The CropHistogramOutliersAction is used to crop the histogram
        # to ignore low and high outliers in the scaling
        # noinspection PyTypeChecker
        self._actions["outliers"] = CropHistogramOutliersAction(self, parent=self)  # type: ignore[arg-type]

        # The AutoscaleToMinMaxAction is used to reset the colormap to
        # autoscaling to min / max of the image.
        self._actions["autoscale_min_max"] = AutoscaleToMinMaxAction(self, parent=self)

        # The AutoscaleToMeanAndThreeSigmaAction resets the automatic histogram
        # mode to the data mean and 3 sigma ranges
        # noinspection PyTypeChecker
        self._actions["autoscale_mean_3sigma"] = AutoscaleToMeanAndThreeSigmaAction(
            self, parent=self
        )  # type: ignore[arg-type]
        # The data info action is used to click on a point in the data and
        # request more information for the data point including all other
        # sliced dimensions.
        if self._config["use_data_info_action"]:
            self._actions["data_info"] = self.group.addAction(
                PydidasGetDataInfoAction(self, parent=self)  # type: ignore[arg-type]
            )
        if self._config["cs_transform"]:
            # The coordinate transform actions (implemented as QToolButton)
            # allow to transform the coordinate system and to display image
            # coordinates in polar coordinates
            # (with r / mm, 2theta / deg or q / nm^-1) scaling.
            # noinspection PyTypeChecker
            self._actions["cs_transform"] = CoordinateTransformButton(
                parent=self,
                plot=self,
                diffraction_exp=self._config["diffraction_exp"],
            )

    def _add_actions_to_toolbar(self) -> None:
        """Add the pydidas custom actions to the toolbar."""
        _insert_behind = {
            "lock_zoom": self.colormapAction,
            "canvas": self.colormapAction,
            "outliers": self.keepDataAspectRatioAction,
            "autoscale_min_max": self.keepDataAspectRatioAction,
            "autoscale_mean_3sigma": self.keepDataAspectRatioAction,
            "data_info": None,
        }
        for _key in self._actions.keys():
            if _key == "cs_transform":
                continue
            self.group.addAction(self._actions[_key])
            self.addAction(self._actions[_key])
            self._toolbar.insertAction(_insert_behind[_key], self._actions[_key])

        if self._config["cs_transform"]:
            self._toolbar.addWidget(self._actions["cs_transform"])

    def _connect_action_signals(self) -> None:
        """Connect the signals of the custom actions to the plot."""
        if self._config["cs_transform"]:
            self._actions["cs_transform"].sig_new_coordinate_system.connect(
                self._positionWidget.new_coordinate_system
            )
            self.sig_new_data_size.connect(
                self._actions["cs_transform"].set_raw_data_size
            )  # type: ignore[attr-defined]
            self.sig_data_linearity.connect(
                self._actions["cs_transform"].set_data_linearity
            )  # type: ignore[attr-defined]
        if self._config["use_data_info_action"]:
            self._actions["data_info"].sig_show_more_info_for_data.connect(
                self.sig_get_more_info_for_data
            )

    def _set_colormap_and_bar(self) -> None:
        """
        Set the default colormap from the PydidasQSettings.

        This method also updates the colorbar widget's labels paint events
        to handle changed font sizes and families.
        """
        _cmap_name = self.q_settings_get("user/cmap_name", default="Gray").lower()
        if _cmap_name is not None:
            _cmap = Colormap(
                name=_cmap_name, normalization="linear", vmin=None, vmax=None
            )
            _cmap.setNaNColor(self.q_settings_get("user/cmap_nan_color"))
            self.setDefaultColormap(_cmap)
        _tb = self.getColorBarWidget().getColorScaleBar().getTickBar()
        _tb.paintEvent = partial(tickbar_paintEvent, _tb)
        _tb._paintTick = partial(tickbar_paintTick, _tb)

    # -----------------------------------------#
    # private update methods                   #
    # -----------------------------------------#

    @QtCore.Slot(str, str)
    def _user_config_update(self, key: str, value: str) -> None:
        """
        Handle a user config update.

        Parameters
        ----------
        key : str
            The name of the updated key.
        value : str
            The new value of the updated key.
        """
        if key not in ["cmap_name", "cmap_nan_color"]:
            return
        _current_image = self.getImage()
        if _current_image is None:
            _current_cmap = self.getDefaultColormap()
            _context = nullcontext()
        else:
            _current_cmap = _current_image.getColormap()
            _context = QtCore.QSignalBlocker(_current_image)
        with _context:
            if key == "cmap_name":
                _current_cmap.setName(value.lower())
            elif key == "cmap_nan_color":
                _current_cmap.setNaNColor(value)

    def _update_cs_units(self, x_unit: str, y_unit: str) -> None:
        """
        Update the coordinate system units.

        Note: Any changes to the CS transform will overwrite these settings.

        Parameters
        ----------
        x_unit : str
            The unit for the data x-axis.
        y_unit : str
            The unit for the data y-axis
        """
        x_unit = self._default_unit if x_unit == "" else x_unit
        y_unit = self._default_unit if y_unit == "" else y_unit
        self._positionWidget.update_coordinate_units(x_unit, y_unit)

    @QtCore.Slot()
    def _update_mpl_fonts(self) -> None:
        """Update the plot's fonts. This is done by resetting the backend."""
        _image = self.getImage()
        if _image is None:
            return
        self.setBackend("matplotlib")  # type: ignore[arg-type]
