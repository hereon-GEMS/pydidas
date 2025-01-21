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
Module with the FitSinglePeak Plugin which can be used to fit a single peak in 1d data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitSinglePeak"]


from pydidas.core import get_generic_param_collection
from pydidas.core.fitting import FitFuncMeta
from pydidas.plugins import BaseFitPlugin


class FitSinglePeak(BaseFitPlugin):
    """
    Fit a single peak to the input data.

    This plugin allows to fit the input data with any function defined in the
    pydidas.core.fitting package.

    The fitting range is defined through the *Peak fit lower limit* and
    *Peak fit upper limit*.

    By default, the plugin tries to estimate starting values for the peak
    position and peak width from the input data by finding the data maximum.
    These defaults can be manually overwritten with the *Peak fit x0 start guess*
    and *Peak fit sigma or Gamma start guess* values in the advanced parameters.

    Fitting limits for the center position can be set with the *Peak low x boundary*
    and *Peak high x boundary* values.

    To discard small peaks, i.e. data points where there is no signal, the
    *Minimum peak height to fit* parameter can be set to define a minimum height
    (of the data maximum) above the background to attempt a fit.

    The quality of the fit is measured in the normalized standard deviation of the
    fit from the data:
        Std(data - fit) / Mean(data)
    Fits which differ by more than the threshold defined in the
    *Fit sigma rejection threshold* will be handled as failed and will return NaN
    values. Adjusting the rejection threshold will allow to modify the goodness of the
    fits to accept.
    """

    plugin_name = "Fit single peak"

    default_params = BaseFitPlugin.default_params | get_generic_param_collection(
        "fit_peak_xlow", "fit_peak_xhigh", "fit_peak_xstart", "fit_peak_width"
    )
    advanced_parameters = BaseFitPlugin.advanced_parameters + [
        "fit_peak_xlow",
        "fit_peak_xhigh",
        "fit_peak_xstart",
        "fit_peak_width",
    ]

    num_peaks = 1

    def __init__(self, *args: tuple, **kwargs: dict):
        BaseFitPlugin.__init__(self, *args, **kwargs)
        self.params["fit_func"].choices = FitFuncMeta.get_fitter_names_with_num_peaks(1)
