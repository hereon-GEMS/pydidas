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
Module with the SilxPlotWindowMixIn which allows to control a silx PlotWindow.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SilxPlotWindowMixIn"]


import warnings

import numpy as np
from silx.gui.plot.backends.BackendMatplotlib import BackendMatplotlibQt

from pydidas.core.utils import LOGGING_LEVEL, pydidas_logger


logger = pydidas_logger(LOGGING_LEVEL)


class SilxPlotWindowMixIn:
    """
    MixIn class with Controls for Silx PlotWindow.

    NOTE: This class expects a PlotWindow widget with the reference
    class._widgets['PlotWindow']. Due to the different layouts, this MixIn
    does *not* create the PlotWindow instance.
    """

    def __init__(self):
        """
        Create the required dictionary.
        """
        self._plot_config = {}

    def setup_plot_params(
        self, shape: tuple, xrange_target: tuple, yrange_target: tuple
    ):
        """
        Setup the required configuration to map the data to the demanded
        range and set the aspect to have square pixels.

        Parameters
        ----------
        shape : tuple
            The final shape of the displayed data in the format
            (size y, size x).
        xrange_target : tuple
            The target range of the data range in the format (x_min, x_max).
        yrange_target : tuple
            The target range of the data range in the format (y_min, y_max).
        """
        self._plot_config["shape"] = shape
        self._plot_config["xrange_target"] = xrange_target
        self._plot_config["yrange_target"] = yrange_target
        self._plot_config["scale"] = None
        self._plot_config["origin"] = None
        self._update_plot_origin_scale_aspect()

    def _update_plot_origin_scale_aspect(self):
        """
        Update the plot settings to map the data shape to the demanded
        ranges.
        """
        _scale = self._plot_config.get("scale", None)
        _origin = self._plot_config.get("origin", None)
        if _origin is None:
            self._update_plot_origin()
        if _scale is None:
            self._update_plot_scale()
        self.__update_plot_aspect()

    def _update_plot_origin(self):
        """
        Update the plot's origin based on the axes range and store the value.
        """
        _origin = (
            self._plot_config["xrange_target"][0],
            self._plot_config["yrange_target"][0],
        )
        self._plot_config["origin"] = _origin

    def _update_plot_scale(self):
        """
        Update the plot's scale based on the axes range and data shape
        and store the value.
        """
        _dx = (
            self._plot_config["xrange_target"][1]
            - self._plot_config["xrange_target"][0]
        )
        _dy = (
            self._plot_config["yrange_target"][1]
            - self._plot_config["yrange_target"][0]
        )
        _scalex = _dx / self._plot_config["shape"][1]
        _scaley = _dy / self._plot_config["shape"][0]
        _scale = (_scalex, _scaley)
        self._plot_config["scale"] = _scale

    def __update_plot_aspect(self):
        """
        Set the aspect in images of MatplotlibQt backend.

        If the backend is not :py:class:
            `silx.gui.plot.backends.BackendMatplotlib.BackendMatplotlibQt`,
        the aspect setting will be ignored.

        Raises
        ------
        Warning
            If backend is not BackendMatplotlibQt.
        """
        _aspect = self._plot_config["scale"][0] / self._plot_config["scale"][1]
        self._plot_config["aspect"] = _aspect
        _backend = self._widgets["plot_window"].getBackend()
        if not isinstance(_backend, BackendMatplotlibQt):
            warnings.warn(
                "Backend is not Matplotlib QT backend. Image "
                "aspects will not be equal.",
                TypeError,
            )
            return
        _old_aspect = _backend.ax.get_aspect()
        if _aspect != _old_aspect:
            self._widgets["plot_window"].addImage(
                np.zeros((10, 10)), legend="pydidas/silx.PlotWindow"
            )
            _backend.ax.set_aspect(_aspect)

    def show_image_in_plot(self, image):
        """
        Show the composite image in the Viewwer.
        """
        self._widgets["plot_window"].setVisible(True)
        self._widgets["plot_window"].addImage(
            image,
            replace=True,
            origin=self._plot_config["origin"],
            scale=self._plot_config["scale"],
            legend="pydidas/silx.PlotWindow",
        )
