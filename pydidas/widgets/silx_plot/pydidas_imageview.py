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
Module with PydidasImageView class which adds configurations to the base silx ImageView.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasImageView"]


from numpy import ndarray
from qtpy import QtCore
from silx.gui.plot import ImageView, Plot2D, tools
from silx.utils.weakref import WeakMethodProxy

from pydidas_qtcore import PydidasQApplication

from ...contexts import DiffractionExperimentContext
from ...core import PydidasQsettingsMixin
from .coordinate_transform_button import CoordinateTransformButton
from .pydidas_position_info import PydidasPositionInfo
from .silx_actions import AutoscaleToMeanAndThreeSigma, CropHistogramOutliers
from .utilities import user_config_update_func


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

    Parameters
    ----------
    **kwargs : dict
        Supported keyword arguments are:

        parent : Union[QWidget, None], optional
            The parent widget or None for no parent. The default is None.
        backend : Union[None, silx.gui.plot.backends.BackendBase], optional
            The silx backend to use. If None, this defaults to the standard
            silx settings. The default is None.
        show_cs_transform : bool, optional
            Flag whether to show the coordinate transform action. The default
            is True.
    """

    user_config_update = user_config_update_func

    _getImageValue = Plot2D._getImageValue

    def __init__(self, **kwargs: dict):
        ImageView.__init__(
            self, parent=kwargs.get("parent", None), backend=kwargs.get("backend", None)
        )
        PydidasQsettingsMixin.__init__(self)
        self._qtapp = PydidasQApplication.instance()
        self._config = {}
        if hasattr(self._qtapp, "sig_updated_user_config"):
            self._qtapp.sig_updated_user_config.connect(self.user_config_update)
        self.user_config_update("cmap_name", self.q_settings_get("user/cmap_name"))
        self.user_config_update(
            "cmap_nan_color", self.q_settings_get("user/cmap_nan_color")
        )

        pos_info = [
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

        if kwargs.get("show_cs_transform", True):
            self.cs_transform_button = CoordinateTransformButton(parent=self, plot=self)
            self._toolbar.addWidget(self.cs_transform_button)
        else:
            self.cs_transform_button = None

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        _position_widget = PydidasPositionInfo(plot=self, converters=pos_info)
        _position_widget.setSnappingMode(SNAP_MODE)
        if kwargs.get("show_cs_transform", True):
            self.cs_transform_button.sig_new_coordinate_system.connect(
                _position_widget.new_coordinate_system
            )
        _layout = self.centralWidget().layout()
        _layout.addWidget(_position_widget, 2, 0, 1, 3)

        self._positionWidget = _position_widget
        DIFFRACTION_EXP.sig_params_changed.connect(self.update_from_diffraction_exp)
        self.update_from_diffraction_exp()

        if hasattr(self._qtapp, "sig_mpl_font_change"):
            self._qtapp.sig_mpl_font_change.connect(self.update_mpl_fonts)

    @QtCore.Slot()
    def update_from_diffraction_exp(self):
        """
        Get the detector size from the DiffractionExperimentContext and store it.
        """
        if self.cs_transform_button is None:
            return
        self._config["cs_transform_valid"] = DIFFRACTION_EXP.detector_is_valid
        self._config["detector_size"] = (
            DIFFRACTION_EXP.get_param_value("detector_npixy"),
            DIFFRACTION_EXP.get_param_value("detector_npixx"),
        )
        self.cs_transform_button.set_coordinates("cartesian")
        self.cs_transform_button.setEnabled(self._config["cs_transform_valid"])

    def display_image(self, data: ndarray, **kwargs: dict):
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
        if self.cs_transform_button is not None:
            self._check_data_shape(data.shape)
        _ = kwargs.pop("legend", None)
        self._config["plot_kwargs"] = kwargs
        ImageView.setImage(self, data, **kwargs)

    def _check_data_shape(self, data_shape: tuple[int, ...]):
        """
        Check the data shape coordinate system.

        This method will reset the coordinate system to cartesian if it differs
        from the defined detector geometry.

        Parameters
        ----------
        data_shape : tuple
            The shape of the input data.
        """
        _valid = (
            data_shape == self._config["detector_size"]
            and self._config["cs_transform_valid"]
        )
        if not _valid:
            self.cs_transform_button.set_coordinates("cartesian")
        self.cs_transform_button.setEnabled(_valid)

    @QtCore.Slot()
    def update_mpl_fonts(self):
        """
        Update the plot's fonts.
        """
        _image = self.getImage()
        if _image is None:
            return
        self.getBackend().fig.gca().cla()
        ImageView.setImage(self, _image.getData(), **self._config["plot_kwargs"])
        for _histo in [self._histoHPlot, self._histoVPlot]:
            _profile = _histo.getProfile()
            _histo.getBackend().fig.gca().cla()
            _histo.setProfile(_profile)
