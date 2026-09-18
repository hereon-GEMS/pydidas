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
Module with the WorkflowEditFrameBuilder class which is used to populate the
WorkflowEditFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WORKFLOW_EDIT_FRAME_BUILD_CONFIG"]


from typing import Any

from qtpy.QtWidgets import QAbstractScrollArea

from pydidas.core import constants
from pydidas.core.constants import FONT_METRIC_HALF_CONSOLE_WIDTH
from pydidas.widgets.base_classes import PydidasScrollArea
from pydidas.widgets.plugin_config_widgets import EditPluginParametersWidget
from pydidas.widgets.workflow_edit import PluginCollectionBrowser, WorkflowTreeCanvas


WORKFLOW_EDIT_FRAME_BUILD_CONFIG: list[list[str | tuple[Any, ...] | dict[str, Any]]] = [
    [
        "create_any_widget",
        ("workflow_canvas", WorkflowTreeCanvas),
        {"parent_widget": None},
    ],
    [
        "create_any_widget",
        ("plugin_edit_canvas", EditPluginParametersWidget),
        {"parent_widget": None},
    ],
    [
        "create_label",
        ("label_title", "Workflow tree editor"),
        {
            "fontsize_offset": 4,
            "bold": True,
            "font_metric_width_factor": FONT_METRIC_HALF_CONSOLE_WIDTH,
            "gridPos": (0, 0, 1, 2),
        },
    ],
    [
        "create_any_widget",
        ("workflow_area", PydidasScrollArea),
        {
            "alignment": constants.ALIGN_TOP_CENTER,
            "gridPos": (1, 0, 3, 2),
            "minimumHeight": 450,
            "sizePolicy": constants.POLICY_EXP_EXP,
            "sizeAdjustPolicy": QAbstractScrollArea.AdjustToContents,
            "widget": "workflow_canvas",
        },
    ],
    [
        "create_label",
        ("plugin_title", "Available plugins:"),
        {
            "fontsize_offset": 3,
            "font_metric_width_factor": FONT_METRIC_HALF_CONSOLE_WIDTH,
            "gridPos": (4, 0, 1, 2),
            "underline": True,
        },
    ],
    [
        "create_any_widget",
        ("plugin_collection", PluginCollectionBrowser),
        {"gridPos": (5, 0, 1, 2)},
    ],
    [
        "create_any_widget",
        ("plugin_edit_area", PydidasScrollArea),
        {
            "gridPos": (1, 2, 5, 1),
            "minimumHeight": 450,
            "resize_to_widget_width": True,
            "sizePolicy": constants.POLICY_EXP_EXP,
            "widget": "plugin_edit_canvas",
        },
    ],
    [
        "create_button",
        ("but_load", "Import workflow from file"),
        {"gridPos": (1, 0, 1, 1), "icon": "qt-std::SP_DialogOpenButton"},
    ],
    [
        "create_button",
        ("but_save", "Export workflow to file"),
        {"gridPos": (2, 0, 1, 1), "icon": "qt-std::SP_DialogSaveButton"},
    ],
]
