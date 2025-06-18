# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the required utilities to create all the necessary widgets for the
SinSquareChiResultsFrame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_widget_creation_information"]

from typing import Any

from pydidas.core import Parameter, ParameterCollection
from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
)
from pydidas.widgets import ScrollArea
from pydidas.widgets.plotting import GridCurvePlot


def __create_param_widget(param: Parameter, **kwargs: Any) -> list[str, tuple, dict]:
    """
    Get the widget creation information for a parameter widget.
    """
    return [
        "create_param_widget",
        (param,),
        {
            "parent_widget": "config",
            "linebreak": True if param.choices else False,
        }
        | kwargs,
    ]


def get_widget_creation_information(
    params: ParameterCollection,
) -> list[list[str, tuple, dict]]:
    """
    Get the widget creation information for the SinSquareChiResultsFrame.

    Parameters
    ----------
    params : ParameterCollection
        The ParameterCollection instance containing the parameters for the
        SinSquareChiResultsFrame.

    Returns
    -------
    list[list[str, tuple, dict]]
        The widget creation information. Each list entry includes all the
        necessary information to create a single widget in the form of a
        list with the following entries:

        - The widget creation method name.
        - The arguments for the widget creation method.
        - The keyword arguments for the widget creation method.
    """
    return [
        [
            "create_label",
            (None, "Sin square chi result analysis"),
            {"fontsize_offset": 4, "bold": True, "gridPos": (0, 0, 1, 2)},
        ],
        [
            "create_empty_widget",
            ("config",),
            {
                "gridPos": (1, 0, 1, 1),
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
            },
        ],
        [
            "create_any_widget",
            ("config_area", ScrollArea),
            {
                "layout_kwargs": {"alignment": None},
                "resize_to_widget_width": True,
                "widget": "config",
            },
        ],
        [
            "create_any_widget",
            ("visualization", GridCurvePlot),
            {
                "gridPos": (1, 1, 1, 1),
            },
        ],
        [
            "create_button",
            ("button_load_workflow_results", "Import current workflow results"),
            {"parent_widget": "config"},
        ],
        [
            "create_button",
            ("button_import_from_directory", "Import results from directory"),
            {"parent_widget": "config"},
        ],
        __create_param_widget(params.get_param("selected_data_source"), linebreak=True),
        ["create_line", (None,), {"parent_widget": "config"}],
        ["create_spacer", (None,), {"parent_widget": "config", "fixedHeight": 15}],
        [
            "create_label",
            (None, "Source plugin for sin^2(chi):"),
            {"parent_widget": "config"},
        ],
        __create_param_widget(params.get_param("selected_sin_square_chi_node")),
        __create_param_widget(params.get_param("show_sin_square_chi_results")),
        __create_param_widget(params.get_param("show_sin_square_chi_branches")),
        __create_param_widget(params.get_param("autoscale_sin_square_chi_results")),
        [
            "create_button",
            (
                "button_update_sin_square_chi_limits",
                "Update limits from selected data",
            ),
            {"parent_widget": "config", "visible": False},
        ],
        __create_param_widget(
            params.get_param("sin_square_chi_limit_low"), visible=False, width_io=0.2
        ),
        __create_param_widget(
            params.get_param("sin_square_chi_limit_high"), visible=False, width_io=0.2
        ),
        ["create_line", (None,), {"parent_widget": "config"}],
        ["create_spacer", (None,), {"parent_widget": "config", "fixedHeight": 15}],
        [
            "create_label",
            (None, "Source plugin for sin(2*chi):"),
            {"parent_widget": "config"},
        ],
        __create_param_widget(params.get_param("selected_sin_2chi_node")),
        __create_param_widget(params.get_param("show_sin_2chi_results")),
        __create_param_widget(params.get_param("autoscale_sin_2chi_results")),
        [
            "create_button",
            (
                "button_update_sin_2chi_limits",
                "Update limits from selected data",
            ),
            {"parent_widget": "config", "visible": False},
        ],
        __create_param_widget(
            params.get_param("sin_2chi_limit_low"), visible=False, width_io=0.2
        ),
        __create_param_widget(
            params.get_param("sin_2chi_limit_high"), visible=False, width_io=0.2
        ),
        ["create_line", (None,), {"parent_widget": "config"}],
        ["create_spacer", (None,), {"parent_widget": "config", "fixedHeight": 15}],
    ]
