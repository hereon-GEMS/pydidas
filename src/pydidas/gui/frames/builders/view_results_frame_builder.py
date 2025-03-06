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
Module with the ViewResultsFrameBuilder class which is used to
populate the ViewResultsFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_ViewResultsFrame_build_config"]

from qtpy import QtCore

from pydidas.core.constants import FONT_METRIC_CONFIG_WIDTH, POLICY_FIX_EXP
from pydidas.widgets import ScrollArea
from pydidas.widgets.data_viewer import DataViewer, TableWithResultDatasets
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.misc import ReadOnlyTextWidget


def get_ViewResultsFrame_build_config(
    frame: BaseFrame,
) -> list[list[str, tuple[str], dict]]:
    """
    Return the build configuration for the ViewResultsFrame.

    Parameters
    ----------
    frame : BaseFrame
        The ViewResultsFrame instance.

    Returns
    -------
    list[list[str, tuple[str], dict]]
        The build configuration in form of a list. Each list entry consists of the
        widget creation method name, the method arguments and the method keywords.
    """
    return [
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
                "sizePolicy": POLICY_FIX_EXP,
            },
        ],
        [
            "create_button",
            ("but_load", "Import results from directory"),
            {"icon": "qt-std::SP_DialogOpenButton", "parent_widget": "config"},
        ],
        [
            "create_spacer",
            ("title_spacer",),
            {"fixedHeight": 15, "parent_widget": "config"},
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
        [
            "create_param_widget",
            (frame.get_param("saving_format"),),
            {"parent_widget": "config", "visible": False},
        ],
        [
            "create_param_widget",
            (frame.get_param("enable_overwrite"),),
            {"parent_widget": "config", "visible": False},
        ],
        [
            "create_button",
            ("but_export_current", "Export current node results"),
            {
                "enabled": False,
                "icon": "qt-std::SP_FileIcon",
                "parent_widget": "config",
                "toolTip": (
                    "Export the current node's results to file. Note that the "
                    "filenames are pre-determined based on node ID and node label."
                ),
                "visible": False,
            },
        ],
        [
            "create_button",
            ("but_export_all", "Export all results"),
            {
                "enabled": False,
                "icon": "qt-std::SP_DialogSaveButton",
                "parent_widget": "config",
                "tooltip": "Export all results. Note that the directory must be empty.",
                "visible": False,
            },
        ],
        [
            "create_any_widget",
            ("data_viewer", DataViewer),
            {
                "plot2d_diffraction_exp": frame._EXP,
                "plot2d_use_data_info_action": True,
                "gridPos": (0, 1, 3, 1),
                "visible": False,
            },
        ],
    ]
