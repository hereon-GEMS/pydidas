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
The generic_params_other module holds all the required data to create generic
Parameters which are are not included in other specialized modules.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_STRESS_STRAIN"]


GENERIC_PARAMS_STRESS_STRAIN = {
    ###############################
    # Generic processing parameters
    ###############################
    "sin_square_chi_low_fit_limit": {
        "type": float,
        "default": 0,
        "name": "Lower bounds for fitting",
        "choices": None,
        "unit": "",
        "range": (0, 1),
        "allow_None": False,
        "tooltip": (
            "The lower boundary for the fitting range (in sin^2(chi)). This "
            "parameter is used to set the lower limit for the fitting range and "
            "it allows to ignore the first few points of the data."
        ),
    },
    "sin_square_chi_high_fit_limit": {
        "type": float,
        "default": 1,
        "name": "Upper bounds for fitting",
        "choices": None,
        "unit": "",
        "range": (0, 1),
        "allow_None": False,
        "tooltip": (
            "The upper boundary for the fitting range (in sin^2(chi)). This "
            "parameter is used to set the upper limit for the fitting range and "
            "it allows to ignore the last few points of the data."
        ),
    },
    "selected_data_source": {
        "type": str,
        "default": "None",
        "name": "Selected data source",
        "choices": None,
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": ("The data source to be used for the visualization."),
    },
    "selected_sin_square_chi_node": {
        "type": str,
        "default": "no selection",
        "name": "Selected sin^2(chi) node",
        "choices": ["no selection"],
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "The node which includes the stored information with the results of the "
            "fit plotted vs sin^2(chi)."
        ),
    },
    "selected_sin_2chi_node": {
        "type": str,
        "default": "no selection",
        "name": "Selected sin(2*chi) node",
        "choices": ["no selection"],
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "The node which includes the stored information with the results of the "
            "fit results plotted vs. sin(2*chi)."
        ),
    },
    "plot_type": {
        "type": str,
        "default": "Inspect data and fits in plot grid",
        "name": "Autoscale sin^2(chi) results",
        "choices": ["Inspect data and fits in plot grid", "Calculate relative stress"],
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "Flag to autoscale the results of the sin^2(chi) analysis in the plot. "
            "If False, the plot will not be autoscaled."
        ),
    },
    "show_sin_square_chi_results": {
        "type": bool,
        "default": True,
        "choices": [True, False],
        "name": "Show sin^2(chi) results in plot",
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "Flag to show the results of the sin^2(chi) analysis in the plot. "
            "If False, no results will be shown."
        ),
    },
    "show_sin_square_chi_branches": {
        "type": bool,
        "default": False,
        "choices": [True, False],
        "name": "Show sin^2(chi) branches in plot",
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "Flag to show the positive and negative branches of the sin^2(chi) "
            "analysis in the plot. If False, no branches will be shown but only the "
            "average and the fit results."
        ),
    },
    "autoscale_sin_square_chi_results": {
        "type": bool,
        "default": True,
        "choices": [True, False],
        "name": "Autoscale sin^2(chi) results",
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "Flag to autoscale the results of the sin^2(chi) analysis in the plot. "
            "If False, the plot will not be autoscaled."
        ),
    },
    "sin_square_chi_limit_low": {
        "type": float,
        "default": 0.0,
        "name": "Lower limit for sin^2(chi) results",
        "choices": None,
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "The lower limit for the sin^2(chi) results in the plot. "
            "If autoscaling is enabled, this value will be ignored."
        ),
    },
    "sin_square_chi_limit_high": {
        "type": float,
        "default": 1.0,
        "name": "Upper limit for sin^2(chi) results",
        "choices": None,
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "The upper limit for the sin^2(chi) results in the plot. "
            "If autoscaling is enabled, this value will be ignored."
        ),
    },
    "show_sin_2chi_results": {
        "type": bool,
        "default": True,
        "choices": [True, False],
        "name": "Show sin(2*chi) results in plot",
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "Flag to show the results of the sin(2*chi) analysis in the plot. "
            "If False, no results will be shown."
        ),
    },
    "autoscale_sin_2chi_results": {
        "type": bool,
        "default": True,
        "choices": [True, False],
        "name": "Autoscale sin(2*chi) results",
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "Flag to autoscale the results of the sin(2*chi) analysis in the plot. "
            "If False, the plot will not be autoscaled."
        ),
    },
    "sin_2chi_limit_low": {
        "type": float,
        "default": 0.0,
        "name": "Lower limit for sin(2*chi) results",
        "choices": None,
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "The lower limit for the sin(2*chi) results in the plot. "
            "If autoscaling is enabled, this value will be ignored."
        ),
    },
    "sin_2chi_limit_high": {
        "type": float,
        "default": 1.0,
        "name": "Upper limit for sin(2*chi) results",
        "choices": None,
        "unit": "",
        "range": None,
        "allow_None": False,
        "tooltip": (
            "The upper limit for the sin(2*chi) results in the plot. "
            "If autoscaling is enabled, this value will be ignored."
        ),
    },
}
