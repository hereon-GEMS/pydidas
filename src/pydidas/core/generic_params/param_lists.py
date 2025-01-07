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
The generic_param_lists module holds key lists for defining subsets of required
Parameters in an object.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FIT_OUTPUT_OPTIONS", "SCAN_GENERIC_PARAM_NAMES", "fit_multi_peak_params"]


SCAN_GENERIC_PARAM_NAMES = [
    "scan_dim",
    "scan_title",
    "scan_base_directory",
    "scan_name_pattern",
    "scan_start_index",
    "scan_index_stepping",
    "scan_multiplicity",
    "scan_multi_image_handling",
]


FIT_OUTPUT_OPTIONS = [
    "position",
    "amplitude",
    "area",
    "FWHM",
    "background at peak",
    "total count intensity",
]


def fit_multi_peak_params(num_peaks: int) -> list[str]:
    """
    Get the parameter names for multi-peak fitting Parameters.

    Parameters
    ----------
    num_peaks : int
        The number of peaks to be used.

    Returns
    -------
    list[str]
        The list of the Parameter names for the given number of peaks.
    """
    return [
        f"fit_peak{i}_{key}"
        for i in range(num_peaks)
        for key in ["xlow", "xhigh", "xstart", "width"]
    ]
