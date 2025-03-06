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
from functools import partial
from typing import Union

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
from pydidas.widgets.silx_plot.utilities import (
    get_2d_silx_plot_ax_settings,
    user_config_update_func,
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
    init_kwargs = ["cs_transform", "use_data_info_action", "diffraction_exp"]
    user_config_update = user_config_update_func

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

    def __init__(self, **kwargs: dict):
        PydidasQsettingsMixin.__init__(self)
        Plot2D.__init__(
            self, parent=kwargs.get("parent", None), backend=kwargs.get("backend", None)
        )
        self._qtapp = PydidasQApplication.instance()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if hasattr(self._qtapp, "sig_mpl_font_change"):
            self._qtapp.sig_mpl_font_change.connect(self.update_mpl_fonts)
        if hasattr(self._qtapp, "sig_updated_user_config"):
            self._qtapp.sig_updated_user_config.connect(self.user_config_update)
        self._update_config(kwargs)
        self._update_position_widget()
        self._add_canvas_resize_actions()
        self._add_histogram_actions()
        if self._config["cs_transform"]:
            self._add_cs_transform_actions()
        self._set_colormap_and_bar()

        if self._config["use_data_info_action"]:
            self._add_data_info_action()

    def _update_config(self, kwargs: dict):
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
            "allowed_add_image_kwargs": [
                _key
                for _key, _value in inspect.signature(self.addImage).parameters.items()
                if _value.default is not inspect.Parameter.empty
            ],
        }
        self._plot_config = {"kwargs": {}}

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
        self._config["diffraction_exp"].sig_params_changed.connect(
            self.update_exp_setup_params
        )
        self.update_exp_setup_params()
        self.cs_transform = CoordinateTransformButton(parent=self, plot=self)
        self._toolbar.addWidget(self.cs_transform)
        self.cs_transform.sig_new_coordinate_system.connect(
            self._positionWidget.new_coordinate_system
        )

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

    @QtCore.Slot()
    def update_exp_setup_params(self):
        """
        Check that the detector is valid for a CS transform.
        """
        _exp = self._config["diffraction_exp"]
        self._config["cs_transform_valid"] = _exp.detector_is_valid

    def enable_cs_transform(self):
        """
        Enable or disable the coordinate system transformations.

        The CS transform is enabled if the image has the same shape as the detector
        configured in the DiffractionExperimentContext.
        """
        _data = self.getImage()
        if _data is None or not self._config["cs_transform"]:
            return
        _data = _data.getData()
        _enable = self._data_has_det_dim(_data)
        if not _enable:
            self.cs_transform.set_coordinates("cartesian")
        self.cs_transform.setEnabled(_enable and self._config["cs_transform_valid"])

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
        x_unit = "no unit" if x_unit == "" else x_unit
        y_unit = "no unit" if y_unit == "" else y_unit
        self._positionWidget.update_coordinate_units(x_unit, y_unit)

    def addImage(self, data: Union[Dataset, np.ndarray], **kwargs: dict):
        """
        Add an image to the plot.

        This method implements an additional dimensionality check before passing
        the image to the Plot2d.addImage method.

        Parameters
        ----------
        data : Union[Dataset, np.ndarray]
            The input data to be displayed.

        **kwargs : dict
            Any supported Plot2d.addImage keyword arguments.
        """
        self.remove(_SCATTER_LEGEND, kind="scatter")
        if isinstance(data, Dataset):
            self.plot_pydidas_dataset(data, **kwargs)
        else:
            self._check_data_dim(data)
            kwargs.update({"legend": _IMAGE_LEGEND, "replace": True})
            Plot2D.addImage(self, data, **kwargs)
            self.__handle_cs_transform()
            self.update_cs_units("", "")

    def addNonUniformImage(self, data: Dataset, **kwargs: dict):
        """
        Add a non-uniform image to the plot.

        This method implements an additional dimensionality check before passing
        the image to the Plot2d.addImage method.

        Parameters
        ----------
        data : Dataset
            The input data to be displayed.

        **kwargs : dict
            Any supported Plot2d.addImage keyword arguments.
        """
        self._check_data_dim(data)
        self.remove(_IMAGE_LEGEND, kind="image")
        self.cs_transform.set_coordinates("cartesian")
        self.cs_transform.setEnabled(False)
        self.profile.setEnabled(False)
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

    def __handle_cs_transform(self):
        """
        Handle the setting of the CS transform.
        """
        if not self._config["cs_transform"]:
            return
        self.enable_cs_transform()
        if self.cs_transform.isEnabled():
            self.changeCanvasToDataAction._actionTriggered()

    def plot_pydidas_dataset(self, data: Dataset, **kwargs: dict):
        """
        Plot a pydidas Dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : dict
            Additional keyword arguments to be passed to the silx plot method.
        """
        self._check_data_dim(data)
        self.update_cs_units(data.axis_units[1], data.axis_units[0])
        self._plot_config = {
            "ax_labels": [data.get_axis_description(i) for i in [0, 1]],
            "kwargs": {
                "replace": kwargs.pop("replace", True),
                "copy": kwargs.pop("copy", False),
                "legend": _IMAGE_LEGEND,
            }
            | {
                _key: _val
                for _key, _val in kwargs.items()
                if _key in self._config["allowed_add_image_kwargs"]
            },
        }
        if data.is_axis_nonlinear(0) or data.is_axis_nonlinear(1):
            self.addNonUniformImage(data, **kwargs)
        else:
            self.remove(_SCATTER_LEGEND, kind="scatter")
            _origin, _scale = get_2d_silx_plot_ax_settings(data)
            self._plot_config["kwargs"]["origin"] = _origin
            self._plot_config["kwargs"]["scale"] = _scale
            self.profile.setEnabled(True)
            Plot2D.addImage(self, data.array, **self._plot_config["kwargs"])
            self.setActiveImage(_IMAGE_LEGEND)
            self.__handle_cs_transform()
        self.setGraphYLabel(self._plot_config["ax_labels"][0])
        self.setGraphXLabel(self._plot_config["ax_labels"][1])
        self._plot_config["cbar_legend"] = ""
        if len(data.data_label) > 0:
            self._plot_config["cbar_legend"] += data.data_label
        if len(data.data_unit) > 0:
            self._plot_config["cbar_legend"] += f" / {data.data_unit}"
        if len(self._plot_config["cbar_legend"]) > 0:
            self.getColorBarWidget().setLegend(self._plot_config["cbar_legend"])
        _action = (
            self.changeCanvasToDataAction
            if self._data_has_det_dim(data)
            else self.expandCanvasAction
        )
        _action._actionTriggered()

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
        Update the plot's fonts.
        """
        _image = self.getImage()
        if _image is None:
            return
        _title = self.getGraphTitle()
        self.getBackend().fig.gca().cla()
        _cb = self.getColorBarWidget()
        _cb.setLegend(self._plot_config.get("cbar_legend", ""))
        _cb.getColorScaleBar().setFixedWidth(int(1.6 * self._qtapp.font_height))
        _cb.update()
        self.addImage(_image.getData(), **self._plot_config["kwargs"])
        self.setGraphTitle(_title)

    def _activeItemChanged(self, type_):
        """
        Listen for active item changed signal and broadcast signal

        :param item.ItemChangedType type_: The type of item change
        """
        if self.sender() == self._qtapp:
            return
        Plot2D._activeItemChanged(self, type_)
