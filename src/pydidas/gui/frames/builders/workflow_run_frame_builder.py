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
Module with the WORKFLOW_RUN_FRAME_BUILD_CONFIG constant which is used to
populate the WorkflowRunFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WORKFLOW_RUN_FRAME_BUILD_CONFIG"]


WORKFLOW_RUN_FRAME_BUILD_CONFIG = [
    [
        "create_param_widget",
        ("autosave_results",),
        {"parent_widget": "run_app_container"},
    ],
    [
        "create_param_widget",
        ("autosave_directory",),
        {
            "linebreak": True,
            "visible": False,
            "parent_widget": "run_app_container",
        },
    ],
    [
        "create_param_widget",
        ("autosave_format",),
        {"visible": False, "parent_widget": "run_app_container"},
    ],
    ["create_line", ("line_autosave",), {"parent_widget": "run_app_container"}],
    [
        "create_param_widget",
        ("live_processing",),
        {"parent_widget": "run_app_container"},
    ],
    [
        "create_button",
        ("but_exec", "Start processing"),
        {"icon": "qt-std::SP_MediaPlay", "parent_widget": "run_app_container"},
    ],
    [
        "create_progress_bar",
        ("progress",),
        {
            "minimum": 0,
            "maximum": 100,
            "visible": False,
            "parent_widget": "run_app_container",
        },
    ],
    [
        "create_button",
        ("but_abort", "Abort processing"),
        {
            "icon": "qt-std::SP_BrowserStop",
            "visible": False,
            "parent_widget": "run_app_container",
        },
    ],
    ["create_line", ("line_results",), {"parent_widget": "run_app_container"}],
]
