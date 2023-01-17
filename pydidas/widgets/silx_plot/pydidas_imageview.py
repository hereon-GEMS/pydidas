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
Module with PydidasImageView class which adds configurations to the base silx ImageView.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasImageView"]

from qtpy import QtCore
from silx.gui.plot import ImageView, tools, Plot2D
from silx.gui.colors import Colormap
from silx.utils.weakref import WeakMethodProxy

from ...core import PydidasQsettingsMixin
from ...contexts import ExperimentContext
from .silx_actions import CropHistogramOutliers
from .coordinate_transform_button import CoordinateTransformButton
from .pydidas_position_info import PydidasPositionInfo


SNAP_MODE = (
    tools.PositionInfo.SNAPPING_CROSSHAIR
    | tools.PositionInfo.SNAPPING_ACTIVE_ONLY
    | tools.PositionInfo.SNAPPING_SYMBOLS_ONLY
    | tools.PositionInfo.SNAPPING_CURVE
    | tools.PositionInfo.SNAPPING_SCATTER
)

EXP = ExperimentContext()


class PydidasImageView(ImageView, PydidasQsettingsMixin):
    """
    A customized silx.gui.plot.ImageView with an additional configuration.
    """

    _getImageValue = Plot2D._getImageValue

    def __init__(self, parent=None, backend=None):

        ImageView.__init__(self, parent, backend)
        PydidasQsettingsMixin.__init__(self)

        posInfo = [
            ("X", lambda x, y: x),
            ("Y", lambda x, y: y),
            ("Data", WeakMethodProxy(self._getImageValue)),
        ]

        self.cropHistOutliersAction = self.group.addAction(
            CropHistogramOutliers(self, parent=self)
        )

        self.cs_transform = CoordinateTransformButton(parent=self, plot=self)
        self._toolbar.addWidget(self.cs_transform)

        self.cropHistOutliersAction.setVisible(True)
        self.addAction(self.cropHistOutliersAction)
        self._toolbar.insertAction(
            self.keepDataAspectRatioAction, self.cropHistOutliersAction
        )

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        _position_widget = PydidasPositionInfo(plot=self, converters=posInfo)
        _position_widget.setSnappingMode(SNAP_MODE)
        self.cs_transform.sig_new_coordinate_system.connect(
            _position_widget.new_coordinate_system
        )
        _layout = self.centralWidget().layout()
        _layout.addWidget(_position_widget, 2, 0, 1, 3)

        self._positionWidget = _position_widget
        self.get_detector_size()

        _cmap_name = self.q_settings_get_value("user/cmap_name", default="Gray").lower()
        if _cmap_name is not None:
            self.setDefaultColormap(
                Colormap(name=_cmap_name, normalization="linear", vmin=None, vmax=None)
            )

    @QtCore.Slot()
    def get_detector_size(self):
        """
        Get the detector size from the ExperimentContext and store it.
        """
        self._detector_size = (
            EXP.get_param_value("detector_npixy"),
            EXP.get_param_value("detector_npixx"),
        )

    def setData(self, data, **kwargs):
        """
        Set the image data, handle the coordinate system and forward the data to
        plotting.

        Parameters
        ----------
        data : np.ndarray
            The image data.
        **kwargs : dict
            Optional kwargs for the ImageView.setImage method.
        """
        self._check_data_shape(data.shape)
        ImageView.setImage(self, data, **kwargs)

    def _check_data_shape(self, data_shape):
        """
        Check the data shape and reset the coordinate system to cartesian if it differs
        from the defined detector geometry.

        Parameters
        ----------
        data_shape : tuple
            The shape of the input data.
        """
        if data_shape != self._detector_size:
            self.cs_transform.set_coordinates("cartesian")
            for _action in self.cs_transform.menu().actions()[1:]:
                _action.setEnabled(False)
        else:
            for _action in self.cs_transform.menu().actions()[1:]:
                _action.setEnabled(True)
