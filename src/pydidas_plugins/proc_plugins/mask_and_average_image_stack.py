# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MaskAndAverageImageStack"]


from typing import Union

import numpy as np
import scipy.ndimage

from pydidas.core import (
    Dataset,
    Parameter,
    ParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import PROC_PLUGIN_IMAGE
from pydidas.plugins import ProcPlugin


_BG_PARAM = Parameter(
    "background_value",
    float,
    None,
    name="Background value",
    tooltip="The value used for pixels that are masked in every image",
    allow_None=True,
)
_ADC_MASK_PARAM = Parameter(
    "adc_mask",
    str,
    "No mask",
    name="ADC artifacts direction",
    choices=[
        "No mask",
        "Mask Y-axis",
        "Mask X-axis",
        "Mask half Y-axis",
        "Mask half X-axis",
    ],
    tooltip="Direction to mask ADC artifacts, originating from a hotspot",
)
_ADC_THRESH_PARAM = Parameter(
    "adc_mask_threshold",
    float,
    None,
    name="ADC artifacts threshold",
    tooltip="Threshold needed to mask ADC artifacts from that point",
    allow_None=True,
)


class MaskAndAverageImageStack(ProcPlugin):
    """
    Mask each image in a stack of images and average the remaining pixels.

    This plugin checks each input image in a stack and applies high/low thresholds
    to each image before averaging all images. Masked pixels are ignored in the
    averaging process and the statistics are calculated accordingly.

    A `background value` can be given to set the value of those pixels which were
    masked in every image. The default of `None` will set these pixels to `np.nan`.

    The plugin can also apply a mask to remove ADC/quantum well artefacts from the
    images, like stripes. A second threshold must be set to define the value
    above which the artefacts are handled.

    These settings can be configured in the plugin's advanced parameters, if required.
    """

    plugin_name = "Mask and average image stack"
    plugin_subtype = PROC_PLUGIN_IMAGE

    default_params = ParameterCollection(
        get_generic_param_collection(
            "mask_threshold_low",
            "mask_threshold_high",
            "mask_grow",
            "kernel_iterations",
        ),
        _BG_PARAM,
        _ADC_MASK_PARAM,
        _ADC_THRESH_PARAM,
    )
    advanced_parameters = ["background_value", "adc_mask", "adc_mask_threshold"]

    input_data_dim = 3
    output_data_dim = 2
    output_data_label = "Masked images"
    output_data_unit = "counts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._background = None
        self._adc_mask = False
        self._trivial = False

    def pre_execute(self):
        """
        Set background value, check threshold values,
        select grow/shrink operation and configure adc mask
        """
        if self.get_param_value("background_value") is None:
            self._background = np.nan
        else:
            self._background = self.get_param_value("background_value")
        self._adc_mask = (
            self.get_param_value("adc_mask_threshold") is not None
            and self.get_param_value("adc_mask") != "No mask"
        )
        if (
            self.get_param_value("mask_threshold_low") is None
            and self.get_param_value("mask_threshold_high") is None
            and self._adc_mask is False
        ):
            self._trivial = True
            return
        else:
            self._trivial = False
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
        new_data : pydidas.core.Dataset
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
        _thresh_low = self.get_param_value("mask_threshold_low")
        _thresh_high = self.get_param_value("mask_threshold_high")
        for image in data:
            _image_mask = (
                np.where(image < _thresh_low, 1, 0)
                if _thresh_low is not None
                else np.zeros(image.shape, dtype=bool)
            )
            if _thresh_high is not None:
                _image_mask = _image_mask + np.where(image > _thresh_high, 1, 0)
            if self.get_param_value("mask_grow") != 0:
                _image_mask = self._operation(
                    _image_mask,
                    structure=self._kernel,
                    iterations=self.get_param_value("kernel_iterations"),
                )
            if self._adc_mask is True:
                _ycenter = image.shape[0] // 2
                _xcenter = image.shape[1] // 2
                _y, _x = np.where(image > self.get_param_value("adc_mask_threshold"))
                match self.get_param_value("adc_mask"):
                    case "Mask Y-axis":
                        _image_mask[:, _x] = 1
                    case "Mask X-axis":
                        _image_mask[_y, :] = 1
                    case "Mask half Y-axis":
                        _xlow = [__x for (__x, __y) in zip(_x, _y) if __y < _ycenter]
                        _image_mask[slice(None, _ycenter), _xlow] = 1
                        _xhigh = [__x for (__x, __y) in zip(_x, _y) if __y >= _ycenter]
                        _image_mask[slice(_ycenter, None), _xhigh] = 1
                    case "Mask half X-axis":
                        _ylow = [__y for (__x, __y) in zip(_x, _y) if __x < _xcenter]
                        _image_mask[_ylow, slice(None, _xcenter)] = 1
                        _yhigh = [__y for (__x, __y) in zip(_x, _y) if __x >= _xcenter]
                        _image_mask[_yhigh, slice(_xcenter, None)] = 1
            _mask_data = _mask_data - _image_mask
            _image_sum = np.where((_image_mask == 0), _image_sum + image, _image_sum)
        _final_image = np.where(
            _mask_data != 0,
            np.divide(
                _image_sum,
                _mask_data,
                dtype=np.float64,
            ),
            self._background,
        )

        data_kwargs = (
            {
                "axis_labels": list(data.axis_labels.values())[1:],
                "axis_ranges": list(data.axis_ranges.values())[1:],
                "axis_units": list(data.axis_units.values())[1:],
                "data_label": data.data_label,
                "data_unit": data.data_unit,
            }
            if isinstance(data, Dataset)
            else {"axis_labels": ["pixel y", "pixel x"]}
        )

        new_data = Dataset(_final_image, **data_kwargs)
        return new_data, kwargs
