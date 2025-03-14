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
Function to define the build configuration for the WorkflowTestFrame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_WorkflowTestFrame_build_config"]


from qtpy import QtCore

from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH, POLICY_FIX_EXP
from pydidas.widgets import ScrollArea
from pydidas.widgets.data_viewer import DataViewer, TableWithResultDatasets
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.misc import ReadOnlyTextWidget


def __param_widget_config(param_key: str) -> dict:
    """
    Get Formatting options for create_param_widget calls.

    Parameters
    ----------
    param_key : str
        The Parameter reference key.

    Returns
    -------
    dict :
        The dictionary with the formatting options.
    """
    return {
        "parent_widget": "config",
        "linebreak": param_key in ["image_selection", "selected_results"],
        "visible": param_key
        not in [
            "scan_index0",
            "scan_index1",
            "scan_index2",
            "scan_index3",
            "detector_image_index",
        ],
    }


def get_WorkflowTestFrame_build_config(
    frame: BaseFrame,
) -> list[list[str, tuple[str], dict]]:
    """
    Return the build configuration for the WorkflowTestFrame.

    Parameters
    ----------
    frame : BaseFrame
        The WorkflowTestFrame instance.

    Returns
    -------
    list[list[str, tuple[str], dict]]
        The build configuration in form of a list. Each list entry consists of the
        widget creation method name, the method arguments and the method
    """
    return (
        [
            [
                "create_label",
                ("title", "Test workflow"),
                {
                    "fontsize_offset": 4,
                    "bold": True,
                    "gridPos": (0, 0, 1, 2),
                },
            ],
            # [
            #     "create_spacer",
            #     ("title_spacer",),
            #     {"fixedHeight": 20},
            # ],
            [
                "create_empty_widget",
                ("config",),
                {
                    "font_metric_width_factor": FONT_METRIC_PARAM_EDIT_WIDTH,
                    "parent_widget": None,
                    "sizePolicy": POLICY_FIX_EXP,
                },
            ],
            [
                "create_spacer",
                ("spacer1",),
                {"parent_widget": "config"},
            ],
            [
                "create_any_widget",
                ("config_area", ScrollArea),
                {
                    "resize_to_widget_width": True,
                },
            ],
            [
                "create_button",
                ("but_reload_tree", "Reset and reload workflow tree"),
                {
                    "icon": "qt-std::SP_BrowserReload",
                    "parent_widget": "config",
                },
            ],
            [
                "create_line",
                ("line_refresh_tree",),
                {"parent_widget": "config"},
            ],
        ]
        + [
            [
                "create_param_widget",
                (frame.get_param(_param),),
                __param_widget_config(_param),
            ]
            for _param in [
                "image_selection",
                "frame_index",
                "scan_index0",
                "scan_index1",
                "scan_index2",
                "scan_index3",
                "detector_image_index",
            ]
        ]
        + [
            [
                "create_line",
                ("line_selection",),
                {"parent_widget": "config"},
            ],
            [
                "create_button",
                ("but_exec", "Process frame"),
                {
                    "icon": "qt-std::SP_MediaPlay",
                    "parent_widget": "config",
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
                {
                    "font_metric_width_factor": FONT_METRIC_PARAM_EDIT_WIDTH,
                    "font_metric_height_factor": 10,
                    "parent_widget": "config",
                    "visible": False,
                },
            ],
            [
                "create_spacer",
                ("arrangement_spacer",),
                {"fixedHeight": 15, "parent_widget": "config"},
            ],
            [
                "create_any_widget",
                ("result_info", ReadOnlyTextWidget),
                {
                    "alignment": QtCore.Qt.AlignTop,
                    "font_metric_width_factor": FONT_METRIC_PARAM_EDIT_WIDTH,
                    "font_metric_height_factor": 24,
                    "parent_widget": "config",
                    "visible": False,
                },
            ],
            [
                "create_button",
                ("but_show_details", "Show detailed results for plugin"),
                {"parent_widget": "config", "visible": False},
            ],
            [
                "create_button",
                ("but_tweak_params", "Tweak plugin parameters"),
                {"parent_widget": "config", "visible": False},
            ],
            [
                "create_spacer",
                ("config_terminal_spacer",),
                {"parent_widget": "config"},
            ],
            [
                "create_any_widget",
                ("plot", DataViewer),
                {"gridPos": (1, 1, 1, 1), "visible": False},
            ],
        ]
    )
