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
__all__ = ["SIN_SQUARE_CHI_RESULTS_FRAME_BUILD_INFORMATION"]

from typing import Any

from pydidas.core.constants import (
    POLICY_FIX_EXP,
)
from pydidas.widgets import ScrollArea
from pydidas.widgets.plotting import GridCurvePlot


def __create_param_widget(
    param: str, parent: str, **kwargs: Any
) -> list[str, tuple[str], dict[str, Any]]:
    """Get the widget creation information for a parameter widget."""
    _new_kwargs: dict[str, Any] = {"parent_widget": parent} | kwargs
    return ["create_param_widget", (param,), _new_kwargs]


SIN_SQUARE_CHI_RESULTS_FRAME_BUILD_INFORMATION: list[list[str, tuple, dict]] = [
    [
        "create_label",
        (None, "Sin square chi result visualization"),
        {"fontsize_offset": 4, "bold": True, "gridPos": (0, 0, 1, 2)},
    ],
    [
        "create_any_widget",
        ("config_area", ScrollArea),
        {
            "gridPos": (1, 0, 1, 1),
            "layout_kwargs": {"alignment": None},
            "resize_to_widget_width": True,
            "widget": "config",
            "sizePolicy": POLICY_FIX_EXP,
        },
    ],
    [
        "create_any_widget",
        ("visualization", GridCurvePlot),
        {"gridPos": (0, 1, 2, 1)},
    ],
    ["create_empty_widget", ("config_generic",), {"parent_widget": "config"}],
    ["create_empty_widget", ("config_grid_plot",), {"parent_widget": "config"}],
    ["create_empty_widget", ("config_rel_stress",), {"parent_widget": "config"}],
    [
        "create_button",
        ("button_load_workflow_results", "Import current workflow results"),
        {"parent_widget": "config_generic"},
    ],
    [
        "create_button",
        ("button_import_from_directory", "Import results from directory"),
        {"parent_widget": "config_generic"},
    ],
    __create_param_widget("selected_data_source", "config_generic", linebreak=True),
    __create_param_widget(
        "selected_sin_square_chi_node", "config_generic", linebreak=True
    ),
    __create_param_widget("selected_sin_2chi_node", "config_generic", linebreak=True),
    ["create_line", (None,), {"parent_widget": "config_generic"}],
    [
        "create_spacer",
        (None,),
        {"parent_widget": "config_grid_plot", "fixedHeight": 15},
    ],
    [
        "create_label",
        (None, "Grid plot configuration:"),
        {"parent_widget": "config_grid_plot", "underline": True},
    ],
    __create_param_widget(
        "num_horizontal_plots",
        "config_grid_plot",
        linebreak=False,
        width_io=0.15,
    ),
    __create_param_widget(
        "num_vertical_plots",
        "config_grid_plot",
        linebreak=False,
        width_io=0.15,
    ),
    ["create_line", (None,), {"parent_widget": "config_grid_plot"}],
    [
        "create_spacer",
        (None,),
        {"parent_widget": "config_grid_plot", "fixedHeight": 15},
    ],
    [
        "create_label",
        (None, "Plot configuration for sin^2(chi):"),
        {"parent_widget": "config_grid_plot"},
    ],
    __create_param_widget("show_sin_square_chi_results", "config_grid_plot"),
    __create_param_widget("show_sin_square_chi_branches", "config_grid_plot"),
    __create_param_widget("autoscale_sin_square_chi_results", "config_grid_plot"),
    [
        "create_button",
        (
            "button_update_sin_square_chi_limits",
            "Update limits from selected data",
        ),
        {"parent_widget": "config_grid_plot", "visible": False},
    ],
    __create_param_widget(
        "sin_square_chi_limit_high",
        "config_grid_plot",
        visible=False,
        width_io=0.2,
    ),
    __create_param_widget(
        "sin_square_chi_limit_low",
        "config_grid_plot",
        visible=False,
        width_io=0.2,
    ),
    ["create_line", (None,), {"parent_widget": "config_grid_plot"}],
    [
        "create_spacer",
        (None,),
        {"parent_widget": "config_grid_plot", "fixedHeight": 15},
    ],
    [
        "create_label",
        (None, "Plot configuration for sin(2*chi):"),
        {"parent_widget": "config_grid_plot"},
    ],
    __create_param_widget("show_sin_2chi_results", "config_grid_plot"),
    __create_param_widget("autoscale_sin_2chi_results", "config_grid_plot"),
    [
        "create_button",
        (
            "button_update_sin_2chi_limits",
            "Update limits from selected data",
        ),
        {"parent_widget": "config_grid_plot", "visible": False},
    ],
    __create_param_widget(
        "sin_2chi_limit_high",
        "config_grid_plot",
        visible=False,
        width_io=0.2,
    ),
    __create_param_widget(
        "sin_2chi_limit_low", "config_grid_plot", visible=False, width_io=0.2
    ),
    ["create_line", (None,), {"parent_widget": "config_grid_plot"}],
    [
        "create_spacer",
        (None,),
        {"parent_widget": "config_grid_plot", "fixedHeight": 15},
    ],
]
