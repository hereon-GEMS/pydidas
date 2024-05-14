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
Module with the PydidasPlot2D class which extends the generic silx Plot2D class by
additional actions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPlot2D"]


import inspect
from functools import partial

import numpy as np
from qtpy import QtCore
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D

from pydidas_qtcore import PydidasQApplication

from ...contexts import DiffractionExperimentContext
from ...core import Dataset, PydidasQsettingsMixin, UserConfigError
from .coordinate_transform_button import CoordinateTransformButton
from .pydidas_position_info import PydidasPositionInfo
from .silx_actions import (
    AutoscaleToMeanAndThreeSigma,
    ChangeCanvasToData,
    CropHistogramOutliers,
    ExpandCanvas,
    PydidasGetDataInfoAction,
)
from .silx_tickbar import tickbar_paintEvent, tickbar_paintTick
from .utilities import get_2d_silx_plot_ax_settings, user_config_update_func


class PydidasPlot2D(Plot2D, PydidasQsettingsMixin):
    """
    A customized silx.gui.plot.Plot2D with an additional features.

    Additional features are implemented through additional SilxActions which
    are added to the toolbar.
    """

    setData = Plot2D.addImage
    sig_get_more_info_for_data = QtCore.Signal(float, float)
    init_kwargs = ["cs_transform", "use_data_info_action", "diffraction_exp"]
    user_config_update = user_config_update_func

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

        self._add_canvas_resize_actions()
        self._add_histogram_actions()
        if self._config["cs_transform"]:
            self._add_cs_transform_actions()
        self._set_colormap_and_bar()

        if self._config["use_data_info_action"]:
            self._add_data_info_action()

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
        self.cs_transform.sig_new_coordinate_system.connect(
            _new_position_widget.new_coordinate_system
        )
        self._positionWidget = _new_position_widget

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

    def enable_cs_transform(self, enable: bool):
        """
        Enable or disable the coordinate system transformations.

        Parameters
        ----------
        enable : bool
            Flag to enable the coordinate system transformations.
        """
        if not self._config["cs_transform"]:
            return
        if not enable:
            self.cs_transform.set_coordinates("cartesian")
        self.cs_transform.setEnabled(enable and self._config["cs_transform_valid"])

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
        if not self._config["cs_transform"]:
            return
        self._positionWidget.update_coordinate_units(x_unit, y_unit)

    def addImage(self, data: np.ndarray, **kwargs: dict):
        """
        Add an image to the plot.

        This method implements an additional dimensionality check before passing
        the image to the Plot2d.addImage method.

        Parameters
        ----------
        data : np.ndarray
            The input data to be displayed.

        **kwargs : dict
            Any supported Plot2d.addImage keyword arguments.
        """
        if not data.ndim == 2:
            raise UserConfigError(
                "The given dataset does not have exactly 2 dimensions. Please check "
                f"the input data definition:\n The input data has {data.ndim} "
                "dimensions."
            )
        Plot2D.addImage(self, data, **kwargs)

    def plot_pydidas_dataset(self, data: Dataset, **kwargs: dict):
        """
        Plot a pydidas dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : dict
            Additional keyword arguments to be passed to the silx plot method.
        """
        if not data.ndim == 2:
            raise UserConfigError(
                "The given dataset does not have exactly 2 dimensions. Please check "
                f"the input data definition. (input data has {data.ndim} dimensions)"
            )
        _has_detector_image_shape = data.shape == (
            self._config["diffraction_exp"].get_param_value("detector_npixy"),
            self._config["diffraction_exp"].get_param_value("detector_npixx"),
        )
        self.enable_cs_transform(_has_detector_image_shape)
        if data.axis_units[0] != "" and data.axis_units[1] != "":
            self.update_cs_units(data.axis_units[1], data.axis_units[0])
        _originx, _scalex = get_2d_silx_plot_ax_settings(data.axis_ranges[1])
        _originy, _scaley = get_2d_silx_plot_ax_settings(data.axis_ranges[0])
        self._plot_config = {
            "ax_labels": [
                data.axis_labels[i]
                + (" / " + data.axis_units[i] if len(data.axis_units[i]) > 0 else "")
                for i in [0, 1]
            ],
            "kwargs": {
                "replace": kwargs.pop("replace", True),
                "copy": kwargs.pop("copy", False),
                "origin": (_originx, _originy),
                "scale": (_scalex, _scaley),
                "legend": "pydidas image",
            }
            | {
                _key: _val
                for _key, _val in kwargs.items()
                if _key in self._config["allowed_add_image_kwargs"]
            },
        }
        self.setGraphYLabel(self._plot_config["ax_labels"][0])
        self.setGraphXLabel(self._plot_config["ax_labels"][1])
        self.addImage(data, **self._plot_config["kwargs"])
        self._plot_config["cbar_legend"] = ""
        if len(data.data_label) > 0:
            self._plot_config["cbar_legend"] += data.data_label
        if len(data.data_unit) > 0:
            self._plot_config["cbar_legend"] += f" / {data.data_unit}"
        if len(self._plot_config["cbar_legend"]) > 0:
            self.getColorBarWidget().setLegend(self._plot_config["cbar_legend"])

        if _has_detector_image_shape:
            self.changeCanvasToDataAction._actionTriggered()

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
