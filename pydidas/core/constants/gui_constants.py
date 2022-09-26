# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The gui_constants module holds global constants used for the GUI layout and
sizes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "GENERIC_PLUGIN_WIDGET_WIDTH",
    "GENERIC_PLUGIN_WIDGET_HEIGHT",
    "GENERIC_PLUGIN_WIDGET_Y_OFFSET",
    "GENERIC_PLUGIN_WIDGET_X_OFFSET",
    "WORKFLOW_EDIT_CANVAS_X",
    "WORKFLOW_EDIT_CANVAS_Y",
    "PLUGIN_PARAM_WIDGET_WIDTH",
    "PARAM_INPUT_WIDGET_HEIGHT",
    "PARAM_INPUT_WIDGET_WIDTH",
    "PARAM_INPUT_EDIT_WIDTH",
    "PARAM_INPUT_TEXT_WIDTH",
    "PARAM_INPUT_UNIT_WIDTH",
    "CONFIG_WIDGET_WIDTH",
    "DEFAULT_TWO_LINE_PARAM_CONFIG",
    "FLOAT_DISPLAY_ACCURACY",
]


from qtpy import QtCore

# Settings for arranging plugin box-widgets on the WorkflowEditCcanvas
GENERIC_PLUGIN_WIDGET_WIDTH = 220
GENERIC_PLUGIN_WIDGET_HEIGHT = 50
GENERIC_PLUGIN_WIDGET_Y_OFFSET = 30
GENERIC_PLUGIN_WIDGET_X_OFFSET = 10

WORKFLOW_EDIT_CANVAS_X = 1000
WORKFLOW_EDIT_CANVAS_Y = 600

# Settings for generic ConfigurePluginWidget
PLUGIN_PARAM_WIDGET_WIDTH = 385

# Settings for generic Parameter widgets
PARAM_INPUT_WIDGET_HEIGHT = 22
PARAM_INPUT_WIDGET_WIDTH = 410
PARAM_INPUT_EDIT_WIDTH = 255
PARAM_INPUT_TEXT_WIDTH = 120
PARAM_INPUT_UNIT_WIDTH = 25

# The width of config widgets for the App Parameters
CONFIG_WIDGET_WIDTH = 300

DEFAULT_TWO_LINE_PARAM_CONFIG = dict(
    linebreak=True,
    halign_text=QtCore.Qt.AlignLeft,
    valign_text=QtCore.Qt.AlignBottom,
    width_total=CONFIG_WIDGET_WIDTH,
    width_io=CONFIG_WIDGET_WIDTH - 50,
    width_text=CONFIG_WIDGET_WIDTH - 20,
    width_unit=0,
)

FLOAT_DISPLAY_ACCURACY = 10
