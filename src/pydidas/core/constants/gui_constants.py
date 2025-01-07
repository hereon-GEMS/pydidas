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
The gui_constants module holds global constants used for the GUI layout and
sizes.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "FLOAT_DISPLAY_ACCURACY",
    "FONT_METRIC_CONFIG_WIDTH",
    "FONT_METRIC_CONSOLE_WIDTH",
    "FONT_METRIC_HALF_CONFIG_WIDTH",
    "FONT_METRIC_HALF_CONSOLE_WIDTH",
    "FONT_METRIC_PARAM_EDIT_WIDTH",
    "FONT_METRIC_SMALL_BUTTON_WIDTH",
    "FONT_METRIC_MEDIUM_BUTTON_WIDTH",
    "FONT_METRIC_WIDE_CONFIG_WIDTH",
    "FONT_METRIC_WIDE_BUTTON_WIDTH",
    "FONT_METRIC_EXTRAWIDE_BUTTON_WIDTH",
    "GENERIC_IO_WIDGET_WIDTH",
    "GENERIC_STANDARD_WIDGET_WIDTH",
    "MINIMUN_WIDGET_DIMENSIONS",
    "PARAM_WIDGET_EDIT_WIDTH",
    "PARAM_WIDGET_TEXT_WIDTH",
    "PARAM_WIDGET_UNIT_WIDTH",
]


# Generic sizeHints for widths of pydidas (I/O) widgets
GENERIC_IO_WIDGET_WIDTH = 350
GENERIC_STANDARD_WIDGET_WIDTH = 500
MINIMUN_WIDGET_DIMENSIONS = 22

# Settings for dynamic width factors based on font metric.
FONT_METRIC_CONFIG_WIDTH = 50
FONT_METRIC_CONSOLE_WIDTH = 80
FONT_METRIC_HALF_CONFIG_WIDTH = FONT_METRIC_CONFIG_WIDTH / 2
FONT_METRIC_HALF_CONSOLE_WIDTH = FONT_METRIC_CONSOLE_WIDTH / 2
FONT_METRIC_PARAM_EDIT_WIDTH = 55
FONT_METRIC_SMALL_BUTTON_WIDTH = 15
FONT_METRIC_MEDIUM_BUTTON_WIDTH = 22
FONT_METRIC_WIDE_BUTTON_WIDTH = 30
FONT_METRIC_EXTRAWIDE_BUTTON_WIDTH = 35
FONT_METRIC_WIDE_CONFIG_WIDTH = 64


# Settings for generic Parameter widgets
PARAM_WIDGET_TEXT_WIDTH = 0.55
PARAM_WIDGET_EDIT_WIDTH = 0.38
PARAM_WIDGET_UNIT_WIDTH = 0.07


FLOAT_DISPLAY_ACCURACY = 10
