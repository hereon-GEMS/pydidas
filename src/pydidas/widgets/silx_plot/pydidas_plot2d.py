# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPlot2D"]


import inspect
from contextlib import nullcontext
from functools import partial
from typing import Any

import numpy as np
from qtpy import QtCore
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D
from silx.gui.plot.items import Scatter

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import Dataset, PydidasQsettingsMixin, UserConfigError
from pydidas.widgets.silx_plot._coordinate_transform_button import (
    CoordinateTransformButton,
)
from pydidas.widgets.silx_plot._silx_tickbar import (
    tickbar_paintEvent,
    tickbar_paintTick,
)
from pydidas.widgets.silx_plot.pydidas_position_info import PydidasPositionInfo
from pydidas.widgets.silx_plot.silx_actions import (
    AutoscaleToMeanAndThreeSigma,
    ChangeCanvasToData,
    CropHistogramOutliers,
    ExpandCanvas,
    PydidasGetDataInfoAction,
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
    _allowed_Plot2D_addImage_kwarg_keys: list[str] | None = None

    @classmethod
    def _get_allowed_addImage_kwargs(cls, kwargs: dict[str, Any]) -> dict[str, Any]:  # noqa
        """
        Filter the kwargs dictionary to only include those allowed by addImage.

        Parameters
        ----------
        kwargs : dict[str, Any]
            The input keyword arguments.

        Returns
        -------
        dict[str, Any]
            The filtered keyword arguments.
        """
        if cls._allowed_Plot2D_addImage_kwarg_keys is None:
            _addImage_params = inspect.signature(Plot2D.addImage).parameters
            cls._allowed_Plot2D_addImage_kwarg_keys = [
                _key
                for _key, _value in _addImage_params.items()
                if _value.default is not inspect.Parameter.empty
            ]
        return {
            _key: _val
            for _key, _val in kwargs.items()
            if _key in cls._allowed_Plot2D_addImage_kwarg_keys
        }

    @staticmethod
    def _check_data_dim(data: np.ndarray):
        """
        Check the data dimensionality.

        Parameters
        ----------
        data : np.ndarray
            The input data to be checked.
        """
        if not data.ndim == 2:
            raise UserConfigError(
                "The given dataset does not have exactly 2 dimensions. Please check "
                f"the input data definition:\n The input data has {data.ndim} "
                "dimensions."
            )

    @staticmethod
    def _get_origin_and_scale(
        data: Dataset,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Get the axis settings to have pixels centered at their values.

        Parameters
        ----------
        data : Dataset
            The dataset to get the axis settings from.

        Returns
        -------
        origin : tuple[float, float]
            The values for the axis origins.
        scale : tuple[float, float]
            The values for the axis scales to squeeze it into the correct
            dimensions for silx plotting.
        """
        origin = []
        scale = []
        # calling axis #1 with x first because silx expects (x, y) values.
        for _dim in (1, 0):
            _ax = data.get_axis_range(_dim)
            _delta = (_ax.max() - _ax.min()) / _ax.size
            scale.append(_delta * (_ax.size + 1) / _ax.size)
            origin.append(_ax[0] - _delta / 2)
        return tuple(origin), tuple(scale)

    def __init__(self, **kwargs: Any):
        PydidasQsettingsMixin.__init__(self)
        Plot2D.__init__(
            self, parent=kwargs.get("parent", None), backend=kwargs.get("backend", None)
        )
        self._qtapp = PydidasQApplication.instance()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # noqa
        if hasattr(self._qtapp, "sig_mpl_font_change"):
            self._qtapp.sig_mpl_font_change.connect(self.update_mpl_fonts)
        if hasattr(self._qtapp, "sig_updated_user_config"):
            self._qtapp.sig_updated_user_config.connect(self.user_config_update)
        self._update_config(kwargs)
        self._update_position_widget()
        self._add_canvas_resize_actions()
        self._add_histogram_actions()
        self._default_unit = "no unit"
        if self._config["cs_transform"]:
            self._add_cs_transform_actions()
        self._set_colormap_and_bar()
        if self._config["use_data_info_action"]:
            self._add_data_info_action()

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
    def default_unit(self, value: str):
        """
        Set the default unit for the plot axes.

        Parameters
        ----------
        value : str
            The new default unit for the plot axes.
        """
        self._default_unit = value
        self.update_cs_units(value, value)

    def _update_config(self, kwargs: Any):
        """
        Update the plot configuration.

        Parameters
        ----------
        kwargs : dict
            The keyword arguments to update the configuration
        """
        self.user_config_update("cmap_name", self.q_settings_get("user/cmap_name"))
        self.user_config_update(
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

    def _update_position_widget(self):
        """
        Update the position widget to be able to display units.
        """

        _pos_widget_converters = [
            (_field[1], _field[2]) for _field in self._positionWidget._fields
        ]
        _new_position_widget = PydidasPositionInfo(
            plot=self,
            converters=_pos_widget_converters,
            diffraction_exp=self._config["diffraction_exp"],
        )
        _new_position_widget.setSnappingMode(self._positionWidget._snappingMode)
        _layout = self.findChild(self._positionWidget.__class__).parent().layout()
        _layout.replaceWidget(self._positionWidget, _new_position_widget)
        self._positionWidget = _new_position_widget

    def _add_canvas_resize_actions(self):
        """
        Add actions to resize the canvas.

        Two actions for changing the canvas to the data shape (with square pixels)
        and to maximize its shape are added.
        """
        self.changeCanvasToDataAction = self.group.addAction(
            ChangeCanvasToData(self, parent=self)
        )
        self.changeCanvasToDataAction.setVisible(True)
        self.addAction(self.changeCanvasToDataAction)
        self._toolbar.insertAction(self.colormapAction, self.changeCanvasToDataAction)

        self.expandCanvasAction = self.group.addAction(ExpandCanvas(self, parent=self))
        self.expandCanvasAction.setVisible(True)
        self.addAction(self.expandCanvasAction)
        self._toolbar.insertAction(self.colormapAction, self.expandCanvasAction)

    def _add_histogram_actions(self):
        """
        Add actions to change the histogram scale based on the data range.

        Two actions for cropping histogram outliers and for changing the histogram
        to the data mean and 3 sigma ranges.
        """
        self.cropHistOutliersAction = self.group.addAction(
            CropHistogramOutliers(self, parent=self)
        )
        self.addAction(self.cropHistOutliersAction)
        self._toolbar.insertAction(
            self.keepDataAspectRatioAction, self.cropHistOutliersAction
        )

        self.autoscaleToMeanAndThreeSigmaAction = self.group.addAction(
            AutoscaleToMeanAndThreeSigma(self, parent=self)
        )
        self.addAction(self.autoscaleToMeanAndThreeSigmaAction)
        self._toolbar.insertAction(
            self.keepDataAspectRatioAction, self.autoscaleToMeanAndThreeSigmaAction
        )

    def _add_cs_transform_actions(self):
        """
        Add the action to transform the coordinate system.

        This action allows to display image coordinates in polar coordinates
        (with r / mm, 2theta / deg or q / nm^-1) scaling.
        """
        self.cs_transform = CoordinateTransformButton(
            parent=self, plot=self, diffraction_exp=self._config["diffraction_exp"]
        )
        self._toolbar.addWidget(self.cs_transform)
        self.cs_transform.sig_new_coordinate_system.connect(
            self._positionWidget.new_coordinate_system
        )
        self.sig_new_data_size.connect(self.cs_transform.set_raw_data_size)
        self.sig_data_linearity.connect(self.cs_transform.set_data_linearity)

    def _set_colormap_and_bar(self):
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

    def _add_data_info_action(self):
        """
        Add the data info action to demand more information for data points.
        """
        self.get_data_info_action = self.group.addAction(
            PydidasGetDataInfoAction(self, parent=self)
        )
        self.addAction(self.get_data_info_action)
        self._toolbar.addAction(self.get_data_info_action)
        self.get_data_info_action.sig_show_more_info_for_data.connect(
            self.sig_get_more_info_for_data
        )

    @QtCore.Slot(str, str)
    def user_config_update(self, key: str, value: str):
        """
        Handle a user config update.

        Parameters
        ----------
        key : str
            The name of the updated key.
        value :
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

    def update_cs_units(self, x_unit: str, y_unit: str):
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

    def addImage(self, data: Dataset | np.ndarray, **kwargs: Any):
        """
        Add an image to the plot.

        This method implements an additional dimensionality check before passing
        the image to the Plot2d.addImage method.

        Parameters
        ----------
        data : Dataset | np.ndarray
            The input data to be displayed.

        **kwargs : Any
            Any supported Plot2d.addImage keyword arguments.
        """
        self.remove(_SCATTER_LEGEND, kind="scatter")
        if isinstance(data, Dataset):
            self.plot_pydidas_dataset(data, **kwargs)
        else:
            self._check_data_dim(data)
            kwargs.update({"legend": _IMAGE_LEGEND, "replace": True})
            Plot2D.addImage(self, data, **kwargs)
            self.sig_new_data_size.emit(*data.shape)
            self.sig_data_linearity.emit(True)
            self.update_cs_units("", "")

    def plot_nonlinear_axes_image(self, data: Dataset, **kwargs: Any):  # noqa ARG001
        """
        Add an image with non-linear axes to the plot.

        This method implements an additional dimensionality check before passing
        the image to the Plot2d.addImage method.

        Parameters
        ----------
        data : Dataset
            The input data to be displayed.

        **kwargs : Any
            Any supported Plot2d.addImage keyword arguments.
        """
        self._check_data_dim(data)
        self.remove(_IMAGE_LEGEND, kind="image")
        self.sig_data_linearity.emit(False)
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

    def plot_pydidas_dataset(self, data: Dataset, **kwargs: Any):
        """
        Plot a pydidas Dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : Any
            Additional keyword arguments to be passed to the silx plot method.
        """
        self._check_data_dim(data)
        _title = kwargs.pop("title", "")
        _plot_kwargs = {
            "replace": kwargs.pop("replace", True),
            "copy": kwargs.pop("copy", False),
            "legend": _IMAGE_LEGEND,
        } | self._get_allowed_addImage_kwargs(kwargs)
        _data_is_linear = not (data.is_axis_nonlinear(0) or data.is_axis_nonlinear(1))
        self.profile.setEnabled(_data_is_linear)
        self.sig_data_linearity.emit(_data_is_linear)
        if _data_is_linear:
            self.remove(_SCATTER_LEGEND, kind="scatter")
            _origin, _scale = self._get_origin_and_scale(data)
            _plot_kwargs["origin"] = _origin
            _plot_kwargs["scale"] = _scale
            Plot2D.addImage(self, data.array, **_plot_kwargs)
            self.setActiveImage(_IMAGE_LEGEND)
            self.sig_new_data_size.emit(*data.shape)
        else:
            self.plot_nonlinear_axes_image(data, **kwargs)
        self.update_cs_units(data.axis_units[1], data.axis_units[0])
        if _title:
            self.setGraphTitle(_title)
        self.setGraphYLabel(data.get_axis_description(0))
        self.setGraphXLabel(data.get_axis_description(1))
        _cbar_legend = data.data_label
        if data.data_unit:
            if not _cbar_legend:
                _cbar_legend += "unspecified"
            _cbar_legend += f" / {data.data_unit}"
        if _cbar_legend:
            self.getColorBarWidget().setLegend(_cbar_legend)
        _action = (
            self.changeCanvasToDataAction
            if self._data_has_det_dim(data)
            else self.expandCanvasAction
        )
        _action._actionTriggered()

    # display_data is a generic alias used in all custom silx plots to have a
    # uniform interface call to display data
    display_data = plot_pydidas_dataset

    def _data_has_det_dim(self, data: np.ndarray):
        """
        Check if the data has the detector dimensions.

        Parameters
        ----------
        data : np.ndarray
            The input data to be checked.
        """
        return data.shape == (
            self._config["diffraction_exp"].get_param_value("detector_npixy"),
            self._config["diffraction_exp"].get_param_value("detector_npixx"),
        )

    def clear_plot(self):
        """
        Clear the plot and remove all items.
        """
        self.remove()
        self.setGraphTitle("")
        self.setGraphYLabel("")
        self.setGraphXLabel("")
        self.getColorBarWidget().setLegend("")

    @QtCore.Slot()
    def update_mpl_fonts(self):
        """
        Update the plot's fonts. This is done by resetting the backend.
        """
        _image = self.getImage()
        if _image is None:
            return
        self.setBackend("matplotlib")  # noqa

    # TODO: check if still needed with silx 2.2.2
    def _activeItemChanged(self, type_):
        """Override generic Plot2D._activeItemChanged to catch QApplication signals."""
        if self.sender() == self._qtapp:
            return
        Plot2D._activeItemChanged(self, type_)
