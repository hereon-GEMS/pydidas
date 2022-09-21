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
from .silx_actions import ChangeCanvasToData, ExpandCanvas, CropHistogramOutliers
from .coordinate_transform_button import CoordinateTransformButton
from .pydidas_position_info import PydidasPositionInfo


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

        _pos_widget_snap_mode = self._positionWidget._snappingMode
        _pos_widget_converters = [
            (_field[1], _field[2]) for _field in self._positionWidget._fields
        ]

        _new_position_widget = PydidasPositionInfo(
            plot=self, converters=_pos_widget_converters
        )
        _new_position_widget.setSnappingMode(_pos_widget_snap_mode)
        if kwargs.get("cs_transform", True):
            self.cs_transform.sig_new_coordinate_system.connect(
                _new_position_widget.new_coordinate_system
            )
        _layout = self.centralWidget().layout().itemAt(2).widget().layout()
        _layout.replaceWidget(self._positionWidget, _new_position_widget)
        self._positionWidget = _new_position_widget

        _cmap_name = self.q_settings_get_value("global/cmap_name").lower()
        if _cmap_name is not None:
            self.setDefaultColormap(
                Colormap(name=_cmap_name, normalization="linear", vmin=None, vmax=None)
            )
