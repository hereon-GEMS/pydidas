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
Module with the MaskImage Plugin which can be used to apply a mask to images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MaskImage"]

from typing import Union

import numpy as np

from pydidas.core import (
    Dataset,
    ParameterCollection,
    UserConfigError,
    get_generic_parameter,
)
from pydidas.core.constants import PROC_PLUGIN_IMAGE
from pydidas.data_io import import_data
from pydidas.plugins import ProcPlugin


class MaskImage(ProcPlugin):
    """
    Apply a mask to image files.
    """

    plugin_name = "Mask image"
    plugin_subtype = PROC_PLUGIN_IMAGE

    default_params = ParameterCollection(
        get_generic_parameter("detector_mask_file"),
        get_generic_parameter("detector_mask_val"),
    )

    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "Masked image"
    output_data_unit = "counts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mask = None
        self._maskval = None

    def pre_execute(self):
        """
        Check the use_global_det_mask Parameter and load the mask image.
        """
        _maskfile = self.get_param_value("detector_mask_file")
        self._maskval = self.get_param_value("detector_mask_val")
        self._mask = import_data(_maskfile)

    def execute(
        self, data: Union[Dataset, np.ndarray], **kwargs: dict
    ) -> tuple[Dataset, dict]:
        """
        Apply a mask to an image (2d data-array).

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The image / frame data .
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        new_data : pydidas.core.Dataset
            The masked image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        if data.shape != self._mask.shape:
            raise UserConfigError(
                "The mask and the data have different shapes. Please check the input "
                "data and the mask."
            )
        new_data = Dataset(
            np.where(self._mask, self._maskval, data),
            **(data.property_dict if hasattr(data, "property_dict") else {}),
        )

        return new_data, kwargs
