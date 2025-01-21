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
Module with the CreateDynamicMask Plugin which can create dynamic data masks based on
data thresholds.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CreateDynamicMask"]


import pathlib
from typing import Union

import numpy as np
import scipy.ndimage

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN_IMAGE
from pydidas.data_io import import_data
from pydidas.plugins import ProcPlugin


class CreateDynamicMask(ProcPlugin):
    """
    Create dynamic masks based on data thresholds.

    The CreateDynamicMask plugin allows to update a detector mask based on
    input data thresholding to mask for example saturated reflection peaks.

    Note that the CreateDynamicMask plugin only creates a mask without
    applying it. It will be passed on as keyword argument "custom_mask" to
    the child plugins which can use it as required.

    If the generic detector mask is used, it is added to the dynamic mask
    after all other operations.
    """

    plugin_name = "Create dynamic data mask"
    plugin_subtype = PROC_PLUGIN_IMAGE

    default_params = get_generic_param_collection(
        "use_detector_mask",
        "mask_threshold_low",
        "mask_threshold_high",
        "mask_grow",
        "kernel_iterations",
    )

    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "image"
    output_data_unit = "counts"

    def __init__(self, *args: tuple, **kwargs: dict):
        self._EXP = kwargs.get("diffraction_exp", DiffractionExperimentContext())
        super().__init__(*args, **kwargs)
        self._mask = None
        self._trivial = False
        self.set_param_value("use_detector_mask", True)

    @property
    def detailed_results(self) -> dict:
        """
        Get the detailed results for the Remove1dPolynomialBackground plugin.

        Returns
        -------
        dict
            The dictionary with detailed results.
        """
        return self._details

    def pre_execute(self):
        """
        Check the use_global_det_mask Parameter and load the mask image.
        """
        if (
            self.get_param_value("mask_threshold_low") is None
            and self.get_param_value("mask_threshold_high") is None
        ):
            self._trivial = True
            return
        self._mask = None
        if self.get_param_value("use_detector_mask"):
            self.load_and_set_mask()

        _grow = self.get_param_value("mask_grow")
        self._kernel = np.ones((1 + 2 * abs(_grow), 1 + 2 * abs(_grow)), dtype=bool)
        if _grow < 0:
            self._operation = scipy.ndimage.binary_erosion
        if _grow > 0:
            self._operation = scipy.ndimage.binary_dilation

    def load_and_set_mask(self):
        """
        Load and store the generic detector mask.
        """
        _mask_file = self._EXP.get_param_value("detector_mask_file")
        if _mask_file != pathlib.Path():
            if _mask_file.is_file():
                self._mask = import_data(_mask_file).array.astype(bool)
            else:
                raise UserConfigError(
                    f"Cannot load detector mask: No file with the name \n{_mask_file}"
                    "\nexists."
                )

    def execute(
        self, data: Union[Dataset, np.ndarray], **kwargs: dict
    ) -> tuple[Dataset, dict]:
        """
        Create a dynamic mask based on the input data.

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The image / frame data.
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self.__data = data
        if self._trivial:
            self.__masked_pixels = np.zeros(data.shape, dtype=bool)
            self._create_detailed_results(self._mask)
            return data, kwargs
        _low = self.get_param_value("mask_threshold_low")
        if _low is not None:
            _mask = np.where(data < _low, True, False)
        else:
            _mask = np.zeros(data.shape, dtype=bool)
        _high = self.get_param_value("mask_threshold_high")
        if _high is not None:
            _mask = _mask + np.where(data > _high, True, False)
        if self.get_param_value("mask_grow") != 0:
            _mask = self._operation(
                _mask,
                structure=self._kernel,
                iterations=self.get_param_value("kernel_iterations"),
            )
        self.__masked_pixels = _mask
        if self._mask is not None:
            _mask = self._mask + _mask
        self._create_detailed_results(_mask)
        kwargs["custom_mask"] = _mask
        return data, kwargs

    def _create_detailed_results(self, final_mask: np.ndarray):
        """
        Get the detailed results for the dynamic mask plugin.

        This method will return information with the input image and the mask.

        Parameters
        ----------
        final_mask : np.ndarray
            The final masking array.

        Returns
        -------
        dict
            The dictionary with the detailed results in the format expected by pydidas.
        """
        self._details = {
            None: {
                "n_plots": 1 + (final_mask is not None),
                "plot_titles": {
                    0: "masked pixels",
                    1: "final mask (including detector mask",
                },
                "items": [
                    {
                        "plot": 0,
                        "label": "masked_pixels",
                        "data": Dataset(self.__masked_pixels),
                    },
                ],
            }
        }
        if final_mask is not None:
            self._details[None]["items"].append(
                {"plot": 1, "label": "final mask", "data": Dataset(final_mask)}
            )
