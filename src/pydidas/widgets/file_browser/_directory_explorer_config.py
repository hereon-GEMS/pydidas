# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with the configurations for the DirectoryExplorer.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "DIRECTORY_EXPLORER_WIDGET_BUILD_CONFIG",
    "DIRECTORY_EXPLORER_DEFAULT_PARAMS",
]


from typing import Any

from pydidas.core import (
    Parameter,
    ParameterCollection,
    get_generic_parameter,
)
from pydidas.core.constants import (
    FONT_METRIC_CONSOLE_WIDTH,
    FONT_METRIC_HALF_CONSOLE_WIDTH,
    FONT_METRIC_WIDE_BUTTON_WIDTH,
)
from pydidas.widgets.file_browser.directory_explorer_tree_view import (
    DirectoryExplorerTreeView,
)
from pydidas.widgets.selection.toggle_options_button import ToggleOptionsButton


DIRECTORY_EXPLORER_WIDGET_BUILD_CONFIG: list[
    list[str | tuple[Any, ...] | dict[str, Any]]
] = [
    [
        "create_empty_widget",
        ("header_container",),
        {"font_metric_width_factor": FONT_METRIC_CONSOLE_WIDTH},
    ],
    [
        "create_empty_widget",
        ("option_container",),
        {"font_metric_width_factor": FONT_METRIC_CONSOLE_WIDTH},
    ],
    [
        "create_label",
        ("label_option_header", "Data browsing options"),
        {
            "bold": True,
            "font_metric_width_factor": FONT_METRIC_HALF_CONSOLE_WIDTH,
            "fontsize_offset": 1,
            "parent_widget": "header_container",
        },
    ],
    [
        "create_any_widget",
        ("button_toggle_options", ToggleOptionsButton),
        {
            "gridPos": (0, 2, 1, 1),
            "font_metric_width_factor": FONT_METRIC_HALF_CONSOLE_WIDTH,
            "linked_widget": "option_container",
            "linked_widget_visible": True,
            "parent_widget": "header_container",
            "toggle_text_shown": "Hide browsing options",
            "toggle_text_hidden": "Show browsing options",
        },
    ],
    [
        "create_param_widget",
        ("map_network_drives",),
        {
            "font_metric_width_factor": FONT_METRIC_HALF_CONSOLE_WIDTH,
            "gridPos": (0, 0, 1, 1),
            "parent_widget": "option_container",
        },
    ],
    [
        "create_param_widget",
        ("case_sensitive",),
        {
            "font_metric_width_factor": FONT_METRIC_HALF_CONSOLE_WIDTH,
            "gridPos": (0, 1, 1, 1),
            "parent_widget": "option_container",
        },
    ],
    [
        "create_param_widget",
        ("use_custom_data_browsing_root",),
        {
            "font_metric_width_factor": FONT_METRIC_CONSOLE_WIDTH,
            "gridPos": (-1, 0, 1, 2),
            "parent_widget": "option_container",
        },
    ],
    [
        "create_param_widget",
        ("data_browsing_root",),
        {
            "font_metric_width_factor": FONT_METRIC_CONSOLE_WIDTH,
            "gridPos": (-1, 0, 1, 2),
            "linebreak": True,
            "parent_widget": "option_container",
            "visible": False,
        },
    ],
    [
        "create_button",
        ("button_apply_root", "Apply new root"),
        {
            "icon": "qt-std::SP_DialogApplyButton",
            "font_metric_width_factor": FONT_METRIC_HALF_CONSOLE_WIDTH,
            "parent_widget": "option_container",
            "visible": False,
        },
    ],
    [
        "create_button",
        ("button_reset_root", "Reset root"),
        {
            "icon": "qt-std::SP_BrowserReload",
            "font_metric_width_factor": FONT_METRIC_HALF_CONSOLE_WIDTH,
            "parent_widget": "option_container",
            "gridPos": ("::current::", 1, 1, 1),
            "visible": False,
        },
    ],
    [
        "create_param_widget",
        ("current_directory",),
        {
            "font_metric_width_factor": FONT_METRIC_CONSOLE_WIDTH,
            "linebreak": True,
        },
    ],
    [
        "create_empty_widget",
        ("filter_container",),
        {"font_metric_width_factor": FONT_METRIC_CONSOLE_WIDTH},
    ],
    [
        "create_lineedit",
        ("filter_edit",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_BUTTON_WIDTH,
            "parent_widget": "filter_container",
            "placeholderText": "Filename filter...",
        },
    ],
    [
        "create_button",
        ("button_reset_filter", "Reset filter"),
        {
            "font_metric_width_factor": 20,
            "gridPos": (0, -1, 1, 1),
            "parent_widget": "filter_container",
        },
    ],
    [
        "create_spacer",
        (None,),
        {
            "parent_widget": "filter_container",
            "gridPos": (0, -1, 1, 1),
        },
    ],
    [
        "create_button",
        ("button_collapse", "Collapse all"),
        {
            "font_metric_width_factor": 20,
            "gridPos": (0, -1, 1, 1),
            "parent_widget": "filter_container",
        },
    ],
    [
        "create_any_widget",
        ("tree_view", DirectoryExplorerTreeView),
        {"gridPos": (-1, 0, 1, 2)},
    ],
]

DIRECTORY_EXPLORER_DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter("current_directory"),
    get_generic_parameter("use_custom_data_browsing_root"),
    get_generic_parameter("data_browsing_root"),
    Parameter(
        "map_network_drives", bool, 1, name="Show network drives", choices=[0, 1]
    ),
    Parameter(
        "case_sensitive", bool, 1, name="Sorting is case sensitive", choices=[0, 1]
    ),
)
