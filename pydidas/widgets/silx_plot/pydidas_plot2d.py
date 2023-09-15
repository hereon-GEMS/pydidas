# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPlot2D"]


import inspect
from functools import partial

from qtpy import QtCore, QtWidgets
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D

from ...contexts import DiffractionExperimentContext
from ...core import PydidasQsettingsMixin
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
from .utilities import get_2d_silx_plot_ax_settings


class PydidasPlot2D(Plot2D, PydidasQsettingsMixin):
    """
    A customized silx.gui.plot.Plot2D with an additional features.

    Additional features are implemented through additional SilxActions which
    are added to the toolbar.
    """

    setData = Plot2D.addImage
    sig_get_more_info_for_data = QtCore.Signal(float, float)
    init_kwargs = ["cs_transform", "use_data_info_action", "diffraction_exp"]

    def __init__(self, parent=None, backend=None, **kwargs):
        Plot2D.__init__(self, parent, backend)
        PydidasQsettingsMixin.__init__(self)
        self._config = {
            "cs_transform": kwargs.get("cs_transform", True),
            "cs_transform_valid": True,
            "use_data_info_action": kwargs.get("use_data_info_action", False),
            "diffraction_exp": (
                DiffractionExperimentContext()
                if kwargs.get("diffraction_exp", None) is None
                else kwargs.get("diffraction_exp")
            ),
        }
        self._plot_config = {"kwargs": {}}
        self._qtapp = QtWidgets.QApplication.instance()
        if hasattr(self._qtapp, "sig_mpl_font_change"):
            self._qtapp.sig_mpl_font_change.connect(self.update_mpl_fonts)

        self._allowed_kwargs = [
            _key
            for _key, _value in inspect.signature(self.addImage).parameters.items()
            if _value.default is not inspect.Parameter.empty
        ]
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

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

        if self._config["cs_transform"]:
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

        _cmap_name = self.q_settings_get_value("user/cmap_name", default="Gray").lower()
        if _cmap_name is not None:
            self.setDefaultColormap(
                Colormap(name=_cmap_name, normalization="linear", vmin=None, vmax=None)
            )

        if self._config["use_data_info_action"]:
            self.get_data_info_action = self.group.addAction(
                PydidasGetDataInfoAction(self, parent=self)
            )
            self.addAction(self.get_data_info_action)
            self._toolbar.addAction(self.get_data_info_action)
            self.get_data_info_action.sig_show_more_info_for_data.connect(
                self.sig_get_more_info_for_data
            )
        _tb = self.getColorBarWidget().getColorScaleBar().getTickBar()
        _tb.paintEvent = partial(tickbar_paintEvent, _tb)
        _tb._paintTick = partial(tickbar_paintTick, _tb)

    @QtCore.Slot()
    def update_exp_setup_params(self):
        """
        Check that the detector is valid for a CS transform.
        """
        self._config["cs_transform_valid"] = (
            self._config["diffraction_exp"].get_param_value("detector_pxsizex") > 0
            and self._config["diffraction_exp"].get_param_value("detector_pxsizey") > 0
            and self._config["diffraction_exp"].get_param_value("detector_npixx") > 0
            and self._config["diffraction_exp"].get_param_value("detector_npixy") > 0
        )

    def enable_cs_transform(self, enable):
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

    def update_cs_units(self, x_unit, y_unit):
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

    def plot_pydidas_dataset(self, data, **kwargs):
        """
        Plot a pydidas dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : dict
            Additional keyword arguments to be passed to the silx plot method."""
        self.enable_cs_transform(
            data.shape
            == (
                self._config["diffraction_exp"].get_param_value("detector_npixy"),
                self._config["diffraction_exp"].get_param_value("detector_npixx"),
            )
        )
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
            }
            | {
                _key: _val
                for _key, _val in kwargs.items()
                if _key in self._allowed_kwargs
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

        if data.shape == (
            self._config["diffraction_exp"].get_param_value("detector_npixy"),
            self._config["diffraction_exp"].get_param_value("detector_npixx"),
        ):
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
