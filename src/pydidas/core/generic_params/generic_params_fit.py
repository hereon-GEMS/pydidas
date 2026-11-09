# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
Parameters which are used for fitting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FIT_OUTPUT_TOOLTIPS", "GENERIC_PARAMS_FIT"]


from itertools import combinations

from pydidas.core.constants import ASCII_TO_UNI
from pydidas.core.generic_params.param_lists import FIT_OUTPUT_OPTIONS


FIT_OUTPUT_TOOLTIPS = {
    "position": (
        "The fitted peak position(s) in the x-axis unit. For multi-peak fits, "
        "the positions are returned in the order of the peaks."
    ),
    "amplitude": (
        "The fitted peak amplitude(s) in the y-axis unit. For multi-peak fits, "
        "the amplitudes are returned in the order of the peaks."
    ),
    "area": (
        "The fitted peak area(s) in the y-axis unit times the x-axis unit. "
        "For multi-peak fits, the areas are returned in the order of the peaks."
    ),
    "FWHM": (
        "The fitted peak full width at half maximum in the x-axis unit. "
        "For multi-peak fits, the FWHMs are returned in the order of the peaks."
    ),
    "background at peak": (
        "The fitted background value(s) at the peak position(s) in the y-axis unit. "
        "For multi-peak fits, the background values are returned in the order of "
        "the peaks."
    ),
    "total count intensity": (
        "The fitted total count intensity(s) in the y-axis unit. This value "
        "will correspond to the integral of the fitted peak function to allow "
        "error estimates for the absolute intensity. For multi-peak fits, the "
        "total count intensities are returned in the order of the peaks."
    ),
    "relative sigma / (sigma + gamma)": (
        "The fitted relative sigma(s) in the unitless ratio of "
        "sigma / (sigma + gamma). This values is only relevant for Voigt fits "
        "which include a combination of Gaussian and Lorentzian peaks and "
        "this value will be in the interval [0.0, 1.0], where 0 corresponds to "
        "a pure Lorentzian and 1.0 corresponds to a pure Gaussian. "
        "For a pure Gaussian fit, this value is always 1.0. For a Lorentzian fit, "
        "this value is always 0.0."
    ),
}

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
        "fit_use_latest_as_start_guess": {
            "type": bool,
            "default": False,
            "name": "Use last fit as starting guess",
            "choices": [True, False],
            "allow_None": False,
            "unit": "",
            "tooltip": (
                "If True, the last fit result will be used as the starting "
                "guess for the next fit. If False, the starting guess will be "
                "calculated automatically. If the fit fails, the last successful "
                "fit will be used as next starting guess for the next fit."
            ),
        },
        "fit_move_range_with_results": {
            "type": bool,
            "default": False,
            "name": "Move range limits with fitted positions",
            "choices": [True, False],
            "allow_None": False,
            "unit": "",
            "tooltip": (
                "If True, the fit range will move with the fitted positions. "
                "If False, the fit range will remain fixed. The width of the "
                "fit range is still determined by the fit_xlow and fit_xhigh "
                "parameters, but the absolute position of the range will move "
                "with the fitted peak positions."
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
                (
                    "The output of the fitting plugin. The plugin can return either "
                    "any of the individual outputs given below or any combination "
                    "thereof: "
                )
                + "; ".join(
                    f"{_i} {_key} - {_desc}"
                    for _i, (_key, _desc) in enumerate(FIT_OUTPUT_TOOLTIPS.items())
                )
                + (
                    "Note that all the fitted parameters are always stored in the "
                    "metadata."
                )
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
                f"The upper boundary in x for the center position of the {_key}peak "
                "to be fitted."
            ),
        }
        for _num, _key in [
            ["", ""],
            ["0", "0th "],
            ["1", "1st "],
            ["2", "2nd "],
            ["3", "3rd "],
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
                f"The starting guess for the parameter value for the {_key}"
                "peak center position in x. Note: This is only the starting "
                "value for the fit, not a fixed value."
            ),
        }
        for _num, _key in [
            ["", ""],
            ["0", "0th "],
            ["1", "1st "],
            ["2", "2nd "],
            ["3", "3rd "],
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
                f"The starting guess for the parameter value for the "
                f"{_key}peak fit sigma/gamma width. Note: This is only the "
                "starting value for the fit, not a fixed value."
            ),
        }
        for _num, _key in [
            ["", ""],
            ["0", "0th "],
            ["1", "1st "],
            ["2", "2nd "],
            ["3", "3rd "],
        ]
    }
)
