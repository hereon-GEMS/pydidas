# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
Module with the MaskImage Plugin which can be used to apply a mask to images.
"""

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MaskMultipleImages"]


from typing import Union

import numpy as np
import scipy.ndimage

from pydidas.core import (
    Dataset,
    Parameter,
    ParameterCollection,
    UserConfigError,
    get_generic_parameter,
)
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_IMAGE
from pydidas.plugins import ProcPlugin


class MaskMultipleImages(ProcPlugin):
    """
    This plugin generates and applies a dynamic data mask for each individual image,
    then averages the remaining pixels
    """

    plugin_name = "Mask multiple images"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_IMAGE
    default_params = ParameterCollection(
        get_generic_parameter("mask_threshold_low"),
        get_generic_parameter("mask_threshold_high"),
        get_generic_parameter("mask_grow"),
        get_generic_parameter("kernel_iterations"),
        Parameter(
            "background_value",
            float,
            0,
            name="Background value",
            tooltip="The value used for pixels that are masked in every image",
        ),
    )
    advanced_parameters = ("background_value",)
    input_data_dim = 3
    output_data_dim = 2
    output_data_label = "Masked images"
    output_data_unit = "counts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._trivial = False
        self._mask_data = []

    def pre_execute(self):
        """
        Check thresholds and select grow/shrink operation
        """
        if (
            self.get_param_value("mask_threshold_low") is None
            and self.get_param_value("mask_threshold_high") is None
        ):
            self._trivial = True
            return
        if (
            self.get_param_value("mask_threshold_low") is not None
            and self.get_param_value("mask_threshold_high") is not None
            and self.get_param_value("mask_threshold_low")
            > self.get_param_value("mask_threshold_high")
        ):
            raise UserConfigError(
                "Lower mask threshold must not be higher than higher mask threshold"
            )
        _grow = self.get_param_value("mask_grow")
        self._kernel = np.ones((1 + 2 * abs(_grow), 1 + 2 * abs(_grow)), dtype=bool)
        if _grow < 0:
            self._operation = scipy.ndimage.binary_erosion
        if _grow > 0:
            self._operation = scipy.ndimage.binary_dilation

    def execute(
        self, data: Union[Dataset, np.ndarray], **kwargs: dict
    ) -> tuple[Dataset, dict]:
        """
        Generate and apply dynamic mask for images, average the remaining pixels

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            A stack of image / frame data. The input data must be a 3D array.
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        if isinstance(data, np.ndarray) is False or data.ndim != 3:
            raise UserConfigError("Input data must be a 3D array")
        if self._trivial:
            return np.sum(data, axis=0) / data.shape[0], kwargs
        _mask_data = np.full(data.shape[1:], data.shape[0])
        _image_sum = np.zeros(data.shape[1:], dtype=float)
        for image in data:
            _image_mask = np.zeros((data.shape[1], data.shape[2]))
            if self.get_param_value("mask_threshold_low") is not None:
                _image_mask = np.where(
                    image < self.get_param_value("mask_threshold_low"), 1, 0
                )
            else:
                _image_mask = np.zeros(image.shape, dtype=bool)
            if self.get_param_value("mask_threshold_high") is not None:
                _image_mask = _image_mask + np.where(
                    image > self.get_param_value("mask_threshold_high"), 1, 0
                )
            if self.get_param_value("mask_grow") != 0:
                _image_mask = self._operation(
                    _image_mask,
                    structure=self._kernel,
                    iterations=self.get_param_value("kernel_iterations"),
                )
            _mask_data = _mask_data - _image_mask
            _image_sum = np.where((_image_mask == 0), _image_sum + image, _image_sum)
        _final_image = np.divide(
            _image_sum,
            _mask_data,
            where=self._mask_data != 0,
            dtype=np.float64,
        )

        _final_image = np.where(
            ~np.isfinite(_final_image),
            self.get_param_value("background_value"),
            _final_image,
        )

        if isinstance(data, Dataset):
            data_kwargs = {
                "axis_labels": list(data.axis_labels.values())[1:],
                "axis_ranges": list(data.axis_ranges.values())[1:],
                "axis_units": list(data.axis_units.values())[1:],
                "data_label": data.data_label,
                "data_unit": data.data_unit,
            }
        else:
            data_kwargs = {"axis_labels": ["pixel y", "pixel x"]}

        new_data = Dataset(_final_image, **data_kwargs)
        return new_data, kwargs

    def calculate_result_shape(self):
        """
        Calculate the shape of the results based on the Plugin processing and
        the input data shape.

        This method only updates the shape and stores it internally. Use the
        "result_shape" property to access the Plugin's result_shape. The
        generic implementation assumes the output shape to be equal to the
        input shape.
        """
        _shape = self._config.get("input_shape", None)
        if _shape is None:
            self._config["result_shape"] = (-1,) * self.output_data_dim
        else:
            self._config["result_shape"] = _shape[1:]
