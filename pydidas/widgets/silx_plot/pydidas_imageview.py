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
Module with PydidasImageView class which adds configurations to the base silx ImageView.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasImageView"]


from qtpy import QtCore, QtWidgets
from silx.gui.colors import Colormap
from silx.gui.plot import ImageView, Plot2D, tools
from silx.utils.weakref import WeakMethodProxy

from ...contexts import DiffractionExperimentContext
from ...core import PydidasQsettingsMixin
from .coordinate_transform_button import CoordinateTransformButton
from .pydidas_position_info import PydidasPositionInfo
from .silx_actions import AutoscaleToMeanAndThreeSigma, CropHistogramOutliers


SNAP_MODE = (
    tools.PositionInfo.SNAPPING_CROSSHAIR
    | tools.PositionInfo.SNAPPING_ACTIVE_ONLY
    | tools.PositionInfo.SNAPPING_SYMBOLS_ONLY
    | tools.PositionInfo.SNAPPING_CURVE
    | tools.PositionInfo.SNAPPING_SCATTER
)

DIFFRACTION_EXP = DiffractionExperimentContext()


class PydidasImageView(ImageView, PydidasQsettingsMixin):
    """
    A customized silx.gui.plot.ImageView with an additional configuration.
    """

    _getImageValue = Plot2D._getImageValue

    def __init__(self, parent=None, backend=None, show_cs_transform=True):
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
        self.cropHistOutliersAction.setVisible(True)
        self.addAction(self.cropHistOutliersAction)
        self._toolbar.insertAction(
            self.keepDataAspectRatioAction, self.cropHistOutliersAction
        )

        self.autoscaleToMeanAndThreeSigmaAction = self.group.addAction(
            AutoscaleToMeanAndThreeSigma(self, parent=self)
        )
        self.autoscaleToMeanAndThreeSigmaAction.setVisible(True)
        self.addAction(self.autoscaleToMeanAndThreeSigmaAction)
        self._toolbar.insertAction(
            self.keepDataAspectRatioAction, self.autoscaleToMeanAndThreeSigmaAction
        )

        if show_cs_transform:
            self.cs_transform = CoordinateTransformButton(parent=self, plot=self)
            self._toolbar.addWidget(self.cs_transform)
        else:
            self.cs_transform = None

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        _position_widget = PydidasPositionInfo(plot=self, converters=posInfo)
        _position_widget.setSnappingMode(SNAP_MODE)
        if show_cs_transform:
            self.cs_transform.sig_new_coordinate_system.connect(
                _position_widget.new_coordinate_system
            )
        _layout = self.centralWidget().layout()
        _layout.addWidget(_position_widget, 2, 0, 1, 3)

        self._positionWidget = _position_widget
        DIFFRACTION_EXP.sig_params_changed.connect(self.update_from_diffraction_exp)
        self.update_from_diffraction_exp()

        _cmap_name = self.q_settings_get_value("user/cmap_name", default="Gray").lower()
        if _cmap_name is not None:
            self.setDefaultColormap(
                Colormap(name=_cmap_name, normalization="linear", vmin=None, vmax=None)
            )
        self._qtapp = QtWidgets.QApplication.instance()
        if hasattr(self._qtapp, "sig_mpl_font_change"):
            self._qtapp.sig_mpl_font_change.connect(self.update_mpl_fonts)

    @QtCore.Slot()
    def update_from_diffraction_exp(self):
        """
        Get the detector size from the DiffractionExperimentContext and store it.
        """
        if self.cs_transform is None:
            return
        self._cs_transform_valid = (
            DIFFRACTION_EXP.get_param_value("detector_pxsizex") > 0
            and DIFFRACTION_EXP.get_param_value("detector_pxsizey") > 0
            and DIFFRACTION_EXP.get_param_value("detector_npixx") > 0
            and DIFFRACTION_EXP.get_param_value("detector_npixy") > 0
        )
        self._detector_size = (
            DIFFRACTION_EXP.get_param_value("detector_npixy"),
            DIFFRACTION_EXP.get_param_value("detector_npixx"),
        )
        self.cs_transform.set_coordinates("cartesian")
        self.cs_transform.setEnabled(self._cs_transform_valid)

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
        if self.cs_transform is not None:
            self._check_data_shape(data.shape)
        self._plot_kwargs = kwargs
        ImageView.setImage(self, data, **kwargs)

    def _check_data_shape(self, data_shape):
        """
        Check the data shape coordinate system.

        This method will reset the coordinate system to cartesian if it differs
        from the defined detector geometry.

        Parameters
        ----------
        data_shape : tuple
            The shape of the input data.
        """
        _valid = data_shape == self._detector_size and self._cs_transform_valid
        if not _valid:
            self.cs_transform.set_coordinates("cartesian")
        self.cs_transform.setEnabled(_valid)

    @QtCore.Slot()
    def update_mpl_fonts(self):
        """
        Update the plot's fonts.
        """
        _image = self.getImage()
        if _image is None:
            return
        self.getBackend().fig.gca().cla()
        ImageView.setImage(self, _image.getData(), **self._plot_kwargs)
        for _histo in [self._histoHPlot, self._histoVPlot]:
            _profile = _histo.getProfile()
            _histo.getBackend().fig.gca().cla()
            _histo.setProfile(_profile)
