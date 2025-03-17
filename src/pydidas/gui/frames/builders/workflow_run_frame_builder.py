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
Module with the get_WorkflowRunFrame_build_config function which is used to
populate the WorkflowRunFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_WorkflowRunFrame_build_config"]


from pydidas.core.constants import FONT_METRIC_CONFIG_WIDTH, POLICY_FIX_EXP
from pydidas.widgets.framework import BaseFrame


def get_WorkflowRunFrame_build_config(
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
            ("title", "Run full workflow processing"),
            {
                "fontsize_offset": 4,
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
                "bold": True,
                "gridPos": (0, 0, 1, 2),
            },
        ],
        ["create_spacer", ("title_spacer",), {"fixedHeight": 15}],
        [
            "create_empty_widget",
            ("workflow_run_config",),
            {
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
                "sizePolicy": POLICY_FIX_EXP,
            },
        ],
        [
            "create_param_widget",
            (frame.get_param("autosave_results"),),
            {"parent_widget": "workflow_run_config"},
        ],
        [
            "create_param_widget",
            (frame.get_param("autosave_directory"),),
            {
                "linebreak": True,
                "visible": False,
                "parent_widget": "workflow_run_config",
            },
        ],
        [
            "create_param_widget",
            (frame.get_param("autosave_format"),),
            {"visible": False, "parent_widget": "workflow_run_config"},
        ],
        ["create_line", ("line_autosave",), {"parent_widget": "workflow_run_config"}],
        [
            "create_button",
            ("but_exec", "Start processing"),
            {"icon": "qt-std::SP_MediaPlay", "parent_widget": "workflow_run_config"},
        ],
        [
            "create_progress_bar",
            ("progress",),
            {
                "minimum": 0,
                "maximum": 100,
                "visible": False,
                "parent_widget": "workflow_run_config",
            },
        ],
        [
            "create_button",
            ("but_abort", "Abort processing"),
            {
                "icon": "qt-std::SP_BrowserStop",
                "visible": False,
                "parent_widget": "workflow_run_config",
            },
        ],
        ["create_line", ("line_results",), {"parent_widget": "workflow_run_config"}],
    ]
