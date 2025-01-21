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
The generic_params_fit module holds all the required data to create generic
Parameters which are are used for fitting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_FIT"]


from itertools import combinations

from pydidas.core.constants import ASCII_TO_UNI
from pydidas.core.generic_params.param_lists import FIT_OUTPUT_OPTIONS


GENERIC_PARAMS_FIT = (
    {
        "fit_sigma_threshold": {
            "type": float,
            "default": 0.25,
            "name": f"Fit {ASCII_TO_UNI['sigma']} rejection threshold",
            "choices": None,
            "allow_None": False,
            "unit": "",
            "tooltip": (
                "The threshold to select which fitting points to reject, based on the "
                "normalized standard deviation. Any fit which has a normalized std "
                "which is worse than the threshold will be rejected as failed."
            ),
        },
        "fit_min_peak_height": {
            "type": float,
            "default": None,
            "name": "Minimum peak height to fit",
            "choices": None,
            "allow_None": True,
            "unit": "",
            "tooltip": (
                "The minimum height a peak must have to attempt a fit. A value of "
                "'None' will not impose any limits on the peak height."
            ),
        },
        "fit_func": {
            "type": str,
            "default": "Gaussian",
            "name": "Fit function",
            "choices": None,
            "unit": "",
            "allow_None": False,
            "tooltip": (
                "Select the type of fit function to be used in the single peak fit."
            ),
        },
        "fit_bg_order": {
            "type": int,
            "default": 0,
            "name": "Fit background order",
            "choices": [None, 0, 1],
            "unit": "",
            "allow_None": True,
            "tooltip": (
                "The order of the background. None corresponds to no background."
            ),
        },
        "fit_upper_limit": {
            "type": float,
            "default": None,
            "name": "Peak fit upper limit",
            "choices": None,
            "unit": "",
            "allow_None": True,
            "tooltip": (
                "The upper limit (in the x-axis´ unit) to the fit region. None "
                "corresponds to using no upper limit but the data limits."
            ),
        },
        "fit_lower_limit": {
            "type": float,
            "default": None,
            "name": "Peak fit lower limit",
            "choices": None,
            "unit": "",
            "allow_None": True,
            "tooltip": (
                "The lower limit (in the x-axis´ unit) to the fit region. None "
                "corresponds to using no upper limit but the data limits."
            ),
        },
        "fit_output": {
            "type": str,
            "default": "position; area; FWHM",
            "name": "Output",
            "choices": ["no output"]
            + [
                "; ".join(subset)
                for L in range(1, len(FIT_OUTPUT_OPTIONS) + 1)
                for subset in combinations(FIT_OUTPUT_OPTIONS, L)
            ],
            "unit": "",
            "allow_None": True,
            "tooltip": (
                "The output of the fitting plugin. The plugin can either return the "
                "peak area, the peak position or the FWHM. Alternatively, any "
                "combination of these values can be retured as well. Note that the fit "
                "parameters are always stored in the metadata."
            ),
        },
    }
    | {
        f"fit_peak{_num}_xlow": {
            "type": float,
            "default": None,
            "name": "Peak " + (f"#{_num} " if _num != "" else "") + "low x boundary",
            "choices": None,
            "unit": "",
            "allow_None": True,
            "tooltip": (
                f"The lower boundary in x for the center position of the {_key} peak "
                "to be fitted."
            ),
        }
        for _num, _key in [
            ["", ""],
            ["0", "0th"],
            ["1", "1st"],
            ["2", "2nd"],
            ["3", "3rd"],
        ]
    }
    | {
        f"fit_peak{_num}_xhigh": {
            "type": float,
            "default": None,
            "name": "Peak " + (f"#{_num} " if _num != "" else "") + "high x boundary",
            "choices": None,
            "unit": "",
            "allow_None": True,
            "tooltip": (
                f"The upper boundary in x for the center position of the {_key} peak "
                "to be fitted."
            ),
        }
        for _num, _key in [
            ["", ""],
            ["0", "0th"],
            ["1", "1st"],
            ["2", "2nd"],
            ["3", "3rd"],
        ]
    }
    | {
        f"fit_peak{_num}_xstart": {
            "type": float,
            "default": None,
            "name": "Peak "
            + (f"#{_num} " if _num != "" else "")
            + "fit x0 start guess",
            "choices": None,
            "unit": "",
            "allow_None": True,
            "tooltip": (
                "The starting guess for the parameter value for the peak center "
                "position in x. Note: This is only the starting value for the fit, not "
                "a fixed value."
            ),
        }
        for _num, _key in [
            ["", ""],
            ["0", "0th"],
            ["1", "1st"],
            ["2", "2nd"],
            ["3", "3rd"],
        ]
    }
    | {
        f"fit_peak{_num}_width": {
            "type": float,
            "default": None,
            "name": (
                "Peak "
                + (f"#{_num} " if _num != "" else "")
                + f"fit {ASCII_TO_UNI['sigma']} or {ASCII_TO_UNI['Gamma']} "
                + "start guess"
            ),
            "choices": None,
            "unit": "",
            "allow_None": True,
            "tooltip": (
                "The starting guess for the parameter value for the fit sigma/gamma "
                "peak width. Note: This is only the starting value for the fit, not a "
                "fixed value."
            ),
        }
        for _num, _key in [
            ["", ""],
            ["0", "0th"],
            ["1", "1st"],
            ["2", "2nd"],
            ["3", "3rd"],
        ]
    }
)
