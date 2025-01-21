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
Module with the FitTriplePeak Plugin which can be used to fit a triple peak in 1d data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitTriplePeak"]


from pydidas.core import get_generic_param_collection
from pydidas.core.fitting import FitFuncMeta
from pydidas.core.generic_params import fit_multi_peak_params
from pydidas.plugins import BaseFitPlugin


_3PEAK_PARAMS = fit_multi_peak_params(3)
_FUNC_CHOICES = FitFuncMeta.get_fitter_names_with_num_peaks(3)
_DEFAULTS = BaseFitPlugin.default_params.copy() | get_generic_param_collection(
    *_3PEAK_PARAMS
)
_DEFAULTS["fit_func"].update_value_and_choices(_FUNC_CHOICES[0], _FUNC_CHOICES)

_ADVANCED = BaseFitPlugin.advanced_parameters + _3PEAK_PARAMS


class FitTriplePeak(BaseFitPlugin):
    """
    Fit three (potentially overlapping) peaks to the input data.

    This plugin allows to fit the input data with any function defined in the
    pydidas.core.fitting package.

    The fitting range is defined through the *Peak fit lower limit* and
    *Peak fit upper limit*.

    The Fit double peak plugin always sorts peaks in ascending order of their
    x-positions. That is, the peak at the smallest x position will always be peak #1.

    By default, the plugin tries to estimate starting values for the peak
    positions and peak widths from the input data by finding the data maximum.
    These defaults can be manually overwritten with the *Peak #i fit x0 start guess*
    and *Peak #i fit sigma or Gamma start guess* values in the advanced parameter,
    where #i corresponds to the peak number (#1, #2 or #3).

    Fitting limits for the center position can be set with the *Peak #i low x boundary*
    and *Peak #i high x boundary* values.

    To discard small peaks, i.e. data points where there is no signal, the
    *Minimum peak height to fit* parameter can be set to define a minimum height
    (of the data maximum) above the background to attempt a fit.

    The quality of the fit is measured in the normalized standard deviation of the
    fit from the data
        Std(data - fit) / Mean(data)
    Fits which differ by more than the threshold defined in the
    *Fit sigma rejection threshold* will be handled as failed and will return NaN
    values. Adjusting the rejection threshold will allow to modify the goodness of the
    fits to accept.
    """

    plugin_name = "Fit triple peak"

    default_params = _DEFAULTS.copy()
    advanced_parameters = _ADVANCED.copy()

    num_peaks = 3
