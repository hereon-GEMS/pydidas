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
Module with the PydidasPlot2D class which extends the generic silx Plot2D class by
additional actions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasPlot2D"]


from qtpy import QtCore
from silx.gui.plot import Plot2D
from silx.gui.colors import Colormap

from ...core import PydidasQsettingsMixin
from ...contexts import DiffractionExperimentContext
from .silx_actions import ChangeCanvasToData, ExpandCanvas, CropHistogramOutliers
from .coordinate_transform_button import CoordinateTransformButton
from .pydidas_position_info import PydidasPositionInfo
from .utilities import get_2d_silx_plot_ax_settings

DIFFRACTION_EXP = DiffractionExperimentContext()


class PydidasPlot2D(Plot2D, PydidasQsettingsMixin):
    """
    A customized silx.gui.plot.Plot2D with an additional features to limit the figure
    canvas to the data limits.
    """

    setData = Plot2D.addImage

    def __init__(self, parent=None, backend=None, **kwargs):
        Plot2D.__init__(self, parent, backend)
        PydidasQsettingsMixin.__init__(self)

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
        self.cropHistOutliersAction.setVisible(True)
        self.addAction(self.cropHistOutliersAction)
        self._toolbar.insertAction(
            self.keepDataAspectRatioAction, self.cropHistOutliersAction
        )

        if kwargs.get("cs_transform", True):
            self.cs_transform = CoordinateTransformButton(parent=self, plot=self)
            self._toolbar.addWidget(self.cs_transform)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        _pos_widget_converters = [
            (_field[1], _field[2]) for _field in self._positionWidget._fields
        ]
        _new_position_widget = PydidasPositionInfo(
            plot=self, converters=_pos_widget_converters
        )
        _new_position_widget.setSnappingMode(self._positionWidget._snappingMode)
        if kwargs.get("cs_transform", True):
            self.cs_transform.sig_new_coordinate_system.connect(
                _new_position_widget.new_coordinate_system
            )
        _layout = self.centralWidget().layout().itemAt(2).widget().layout()
        _layout.replaceWidget(self._positionWidget, _new_position_widget)
        self._positionWidget = _new_position_widget

        _cmap_name = self.q_settings_get_value("user/cmap_name", default="Gray").lower()
        if _cmap_name is not None:
            self.setDefaultColormap(
                Colormap(name=_cmap_name, normalization="linear", vmin=None, vmax=None)
            )

    def enable_cs_transform(self, enable):
        """
        Enable or disable the coordinate system transformations.

        Parameters
        ----------
        enable : bool
            Flag to enable the coordinate system transformations.
        """
        if not enable:
            self.cs_transform.set_coordinates("cartesian")
        self.cs_transform.setEnabled(enable)

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
        self._positionWidget.update_coordinate_units(x_unit, y_unit)

    def plot_pydidas_dataset(self, data, title=None):
        """
        Plot a pydidas dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        title : Union[None, str], optional
            The title for the plot. If None, no title will be added to the plot.
        """
        self.enable_cs_transform(
            data.shape
            == (
                DIFFRACTION_EXP.get_param_value("detector_npixy"),
                DIFFRACTION_EXP.get_param_value("detector_npixx"),
            )
        )
        self.update_cs_units(data.axis_units[1], data.axis_units[0])
        _ax_label = [
            data.axis_labels[i]
            + (" / " + data.axis_units[i] if len(data.axis_units[i]) > 0 else "")
            for i in [0, 1]
        ]
        _originx, _scalex = get_2d_silx_plot_ax_settings(data.axis_ranges[1])
        _originy, _scaley = get_2d_silx_plot_ax_settings(data.axis_ranges[0])
        self.addImage(
            data,
            replace=True,
            copy=False,
            origin=(_originx, _originy),
            scale=(_scalex, _scaley),
        )
        self.setGraphYLabel(_ax_label[0])
        self.setGraphXLabel(_ax_label[1])
        if title is not None:
            self.setGraphTitle(title)

    def clear_plot(self):
        """
        Clear the plot and remove all items.
        """
        self.remove()
        self.setGraphTitle("")
        self.setGraphYLabel("")
        self.setGraphXLabel("")
