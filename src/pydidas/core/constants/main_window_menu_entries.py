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
The main_menu_menu_entries module defines the setup of the generic menus.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MAIN_WINDOW_MENU_ENTRIES"]


MAIN_WINDOW_MENU_ENTRIES = {
    "Workflow processing": {
        "label": "Show\nWorkflow\nprocessing",
        "icon": "pydidas::workflow_processing_expand",
        "label_visible": "Hide\nworkflow\nprocessing",
        "label_invisible": "Show\nworkflow\nprocessing",
        "icon_visible": "pydidas::workflow_processing_hide",
        "icon_invisible": "pydidas::workflow_processing_expand",
        "menu_tree": ["", "Workflow processing"],
    },
    "Analysis tools": {
        "label": "Show\nanalysis\ntools",
        "icon": "pydidas::analysis_tools_expand",
        "label_visible": "Hide\nanalysis\ntools",
        "label_invisible": "Show\nanalysis\ntools",
        "icon_visible": "pydidas::analysis_tools_hide",
        "icon_invisible": "pydidas::analysis_tools_expand",
        "menu_tree": ["", "Analysis tools"],
    },
}
