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
Module with the CorrectSplineDistortion Plugin which can be used to correct
images with a spline-based distortion field.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CorrectSplineDistortion"]


import os
import warnings
from pathlib import Path
from typing import Union

import numpy as np
import pyFAI
from pyFAI.distortion import Distortion

from pydidas.core import Dataset, Parameter, ParameterCollection, UserConfigError
from pydidas.core.constants import PROC_PLUGIN_IMAGE
from pydidas.plugins import ProcPlugin


_SPLINE_PARAMS = ParameterCollection(
    Parameter(
        "spline_file",
        Path,
        Path(),
        name="Spline file",
        tooltip=(
            "Apply a spline-file distortion correction to account for detector "
            "distortion."
        ),
    ),
    Parameter(
        "geometry",
        str,
        "Fit2D",
        name="Spline geometry",
        choices=["Fit2D", "pyFAI"],
        tooltip=(
            "The geometry of the spline file. The origin in pyFAI is defined opposite "
            "to the Fit2D definition and Fit2D files must be corrected."
        ),
    ),
    Parameter(
        "fill_nan",
        bool,
        True,
        name="Fill empty pixel with NaN",
        choices=[True, False],
        tooltip=(
            "Choice whether to fill invalid pixels with NaN instead of zeros. "
            "Invalid pixels appear when the correction shrinks the image and empty "
            "image regions appear."
        ),
    ),
)


class CorrectSplineDistortion(ProcPlugin):
    """
    Apply a Fit2D spline correction to the input data acquired with a FReLoN detector.

    The spline file format is used as exported from Fit2D and the spline is
    flipped up/down to have the correct orientation with respect to pyFAI.
    """

    plugin_name = "Correct spline distortion"
    plugin_subtype = PROC_PLUGIN_IMAGE

    default_params = _SPLINE_PARAMS.copy()

    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "Distortion-corrected image"
    output_data_unit = "counts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._detector = None
        self._correction = None
        self._nan_mask = None

    def pre_execute(self):
        """
        Initialize the detector and modify the spline, if necessary.
        """
        _spline = self.get_param_value("spline_file")
        if not os.path.isfile(_spline):
            raise UserConfigError(f"The given path `{_spline}` is not a valid file.")
        self._detector = pyFAI.detector_factory("FReLoN", {"splineFile": _spline})
        if self.get_param_value("geometry") == "Fit2D":
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._detector.spline = self._detector.spline.flipud()
                self._detector.mask = np.flipud(self._detector.mask)
        self._correction = Distortion(self._detector)
        if self.get_param_value("fill_nan"):
            _dummy = self._correction.correct(np.ones(self._detector.max_shape))
            self._nan_mask = np.where(_dummy < 0.8, 1, 0)

    def execute(
        self, data: Union[Dataset, np.ndarray], **kwargs: dict
    ) -> tuple[Dataset, dict]:
        """
        Apply a distortion correction to an image (2d data-array).

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The image / frame data.
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        data : pydidas.core.Dataset
            The distortion-corrected image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        data[:] = self._correction.correct(data)
        if self.get_param_value("fill_nan"):
            data[:] = np.where(self._nan_mask, np.nan, data)
        return data, kwargs
