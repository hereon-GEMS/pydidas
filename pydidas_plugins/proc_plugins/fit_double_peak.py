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
Module with the FitDoublePeak Plugin which can be used to fit a double peak in 1d data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitDoublePeak"]


from pydidas.core import get_generic_param_collection
from pydidas.core.fitting import FitFuncMeta
from pydidas.plugins import FitMultiPeak


_FUNC_CHOICES = FitFuncMeta.get_fitter_names_with_num_peaks(2)
_DEFAULTS = FitMultiPeak.default_params.copy() | get_generic_param_collection(
    "fit_peak1_xlow",
    "fit_peak1_xhigh",
    "fit_peak1_xstart",
    "fit_peak1_width",
    "fit_peak2_xlow",
    "fit_peak2_xhigh",
    "fit_peak2_xstart",
    "fit_peak2_width",
)
_DEFAULTS["fit_func"].update_value_and_choices(_FUNC_CHOICES[0], _FUNC_CHOICES)

_ADVANCED = FitMultiPeak.advanced_parameters + [
    "fit_peak1_xlow",
    "fit_peak1_xhigh",
    "fit_peak1_xstart",
    "fit_peak1_width",
    "fit_peak2_xlow",
    "fit_peak2_xhigh",
    "fit_peak2_xstart",
    "fit_peak2_width",
]


class FitDoublePeak(FitMultiPeak):
    """
    Fit a single peak to the input data.

    This plugin allows to fit the input data with any function defined in the
    pydidas.core.fitting package.
    """

    plugin_name = "Fit double peak"
    basic_plugin = False
    default_params = _DEFAULTS.copy()
    advanced_parameters = _ADVANCED.copy()
    num_peaks = 2
