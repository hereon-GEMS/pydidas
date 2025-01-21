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
Module with the CropAndBinData Plugin which can be used to crop data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CropAndBinImage"]


from pydidas.core import Dataset, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN_IMAGE
from pydidas.core.utils import rebin2d
from pydidas.plugins import ProcPlugin


class CropAndBinImage(ProcPlugin):
    """
    Crop and bin an image (i.e. 2d input data).
    """

    plugin_subtype = PROC_PLUGIN_IMAGE
    plugin_name = "Crop and bin image"

    default_params = get_generic_param_collection(
        "use_roi", "roi_xlow", "roi_xhigh", "roi_ylow", "roi_yhigh", "binning"
    )

    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "Image intensity"
    output_data_unit = "counts"

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Apply the given cropping and binning to the input data.

        Parameters
        ----------
        data : pydidas.core.Dataset
            Input data.
        **kwargs : dict
            Keyword arguments passed to the execute method.

        Returns
        -------
        data : pydidas.core.Dataset
            The image data frame.
        kwargs : dict
            The updated input keyword arguments.
        """
        _roi = self._get_own_roi()
        _binning = self.get_param_value("binning")
        if _roi is not None:
            data = data[_roi]
        if _binning > 1:
            data = rebin2d(data, _binning)
        return data, kwargs
