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
Module with the VIEW_RESULTS_MIXIN_BUILD_CONFIG constant which is used to
populate the ViewResultsFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["VIEW_RESULTS_MIXIN_BUILD_CONFIG"]


from typing import Any

from qtpy import QtCore

from pydidas.core.constants import FONT_METRIC_CONFIG_WIDTH, POLICY_FIX_EXP
from pydidas.widgets import ScrollArea
from pydidas.widgets.data_viewer import TableWithResultDatasets
from pydidas.widgets.misc import ReadOnlyTextWidget


VIEW_RESULTS_MIXIN_BUILD_CONFIG: list[list[str | tuple[Any] | dict[str, Any]]] = [
    [
        "create_label",
        ("title", "View results"),
        {
            "bold": True,
            "fontsize_offset": 4,
            "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
            "gridPos": (0, 0, 1, 1),
        },
    ],
    ["create_spacer", ("title_spacer",), {"fixedHeight": 15}],
    [
        "create_empty_widget",
        ("config",),
        {
            "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
            "parent_widget": None,
            "sizePolicy": POLICY_FIX_EXP,
        },
    ],
    [
        "create_any_widget",
        ("config_area", ScrollArea),
        {
            "widget": "config",
            "sizePolicy": POLICY_FIX_EXP,
        },
    ],
    [
        "create_empty_widget",
        ("import_container",),
        {"gridPos": (-1, 0, 1, 1), "parent_widget": "config"},
    ],
    [
        "create_empty_widget",
        ("run_app_container",),
        {"gridPos": (-1, 0, 1, 1), "parent_widget": "config"},
    ],
    [
        "create_button",
        ("but_load", "Import results from directory"),
        {
            "icon": "qt-std::SP_DialogOpenButton",
            "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
            "parent_widget": "import_container",
        },
    ],
    [
        "create_label",
        ("label_select_header", "Select results to display:"),
        {
            "bold": True,
            "fontsize_offset": 1,
            "parent_widget": "config",
            "visible": False,
        },
    ],
    [
        "create_any_widget",
        ("result_table", TableWithResultDatasets),
        {"parent_widget": "config", "visible": False},
    ],
    [
        "create_spacer",
        ("arrangement_spacer",),
        {"fixedHeight": 15, "parent_widget": "config"},
    ],
    [
        "create_radio_button_group",
        ("radio_arrangement", ["by scan shape", "as a timeline"]),
        {
            "title": "Arrangement of results:",
            "parent_widget": "config",
            "vertical": False,
            "visible": False,
        },
    ],
    [
        "create_spacer",
        ("info_spacer",),
        {"fixedHeight": 15, "parent_widget": "config"},
    ],
    [
        "create_label",
        ("label_details", "Detailed result information:"),
        {
            "bold": True,
            "fontsize_offset": 1,
            "parent_widget": "config",
            "visible": False,
        },
    ],
    [
        "create_any_widget",
        ("result_info", ReadOnlyTextWidget),
        {
            "alignment": QtCore.Qt.AlignTop,
            "font_metric_height_factor": 25,
            "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
            "parent_widget": "config",
            "visible": False,
        },
    ],
    [
        "create_spacer",
        ("config_export_spacer",),
        {"parent_widget": "config"},
    ],
    ["create_empty_widget", ("export_container",), {"parent_widget": "config"}],
    [
        "create_param_widget",
        ("saving_format",),
        {"parent_widget": "export_container"},
    ],
    [
        "create_param_widget",
        ("squeeze_empty_dims",),
        {"parent_widget": "export_container"},
    ],
    [
        "create_param_widget",
        ("enable_overwrite",),
        {"parent_widget": "export_container"},
    ],
    [
        "create_button",
        ("but_export_current", "Export current node results"),
        {
            "enabled": False,
            "icon": "qt-std::SP_FileIcon",
            "parent_widget": "export_container",
            "toolTip": (
                "Export the current node's results to file. Note that the "
                "filenames are pre-determined based on node ID and node label."
            ),
        },
    ],
    [
        "create_button",
        ("but_export_all", "Export all results"),
        {
            "enabled": False,
            "icon": "qt-std::SP_DialogSaveButton",
            "parent_widget": "export_container",
            "tooltip": "Export all results. Note that the directory must be empty.",
        },
    ],
]
