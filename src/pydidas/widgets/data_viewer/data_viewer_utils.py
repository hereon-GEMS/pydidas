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
Module with utiltities for the data_viewer.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "invalid_range_str",
    "get_data_axis_header_creation_args",
    "get_data_axis_widget_creation_args",
]


from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
    QT_REG_EXP_FLOAT_RANGE_VALIDATOR,
    QT_REG_EXP_INT_RANGE_VALIDATOR,
)
from pydidas.widgets.factory import SquareButton


def invalid_range_str(input_range: str) -> str:
    """
    Get a string for an invalid range input to be displayed as exception.

    Parameters
    ----------
    input_range : str
        The invalid input range.

    Returns
    -------
    str
        The string for the exception.
    """
    return (
        f"Invalid range syntax in the input: `{input_range}`\n"
        "Please enter the values for the first and last point separated by a colon, "
        "e.g. `0:10` or `-4.5:12.7`."
    )


def get_data_axis_header_creation_args(
    axis_index: int, multiline: bool
) -> list[str, list, dict]:
    """
    Get the arguments required to create all necessary widgets in the header.

    Parameters
    ----------
    multiline : bool
        If True, return parameters for a multiline layout.

    Returns
    -------
    list[str, list, dict]
        The arguments to create all necessary widgets. The format for each
        element is:

        - The method name to call.
        - The arguments for the method.
        - The keyword arguments for the method.
    """
    return [
        [
            "create_label",
            ["label_axis", f"Dim {axis_index}"],
            {
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH
                if multiline
                else 28,
                "gridPos": (0, 0, 1, 2),
            },
        ],
        [
            "create_combo_box",
            ["combo_axis_use"],
            {
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH - 10
                if multiline
                else 25,
                "gridPos": (1, 1, 1, 1) if multiline else (0, -1, 1, 1),
                "items": ["slice at index"],
            },
        ],
    ]


def get_data_axis_widget_creation_args(
    multiline: bool,
) -> list[str, list, dict]:
    """
    Get the arguments required to create all necessary widgets.

    Parameters
    ----------
    multiline : bool
        If True, return parameters for a multiline layout.

    Returns
    -------
    list[str, list, dict]
        The arguments to create all necessary widgets. The format for each
        element is:

        - The method name to call.
        - The arguments for the method.
        - The keyword arguments for the method.
    """
    return [
        [
            "create_combo_box",
            ["combo_range"],
            {
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH - 25,
                "gridPos": (0, -1, 1, 1),
                "items": [
                    "use full axis",
                    "select range by indices",
                    "select range by data values",
                ],
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
                "visible": False,
            },
        ],
        [
            "create_lineedit",
            ["edit_range_index"],
            {
                "font_metric_width_factor": 25,
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
                "toolTip": (
                    "Enter the start and end index separated by a colon. Please note that "
                    "contrary to Python slicing, the end index is included in the "
                    "selection."
                ),
                "validator": QT_REG_EXP_INT_RANGE_VALIDATOR,
                "visible": False,
            },
        ],
        [
            "create_lineedit",
            ["edit_range_data"],
            {
                "font_metric_width_factor": 25,
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
                "toolTip": (
                    "Enter the first and last data point to be included, separated by a "
                    "colon. Please note that contrary to Python slicing, the final data "
                    "point is included in the selection."
                ),
                "validator": QT_REG_EXP_FLOAT_RANGE_VALIDATOR,
                "visible": False,
            },
        ],
        [
            "add_any_widget",
            ["slider", QtWidgets.QSlider(QtCore.Qt.Horizontal)],
            {
                "gridPos": (0, -1, 1, 1),
                "minimumWidth": 100,
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
            },
        ],
        [
            "add_any_widget",
            ["button_start", SquareButton(icon="mdi::skip-backward")],
            {
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
            },
        ],
        [
            "add_any_widget",
            ["button_backward", SquareButton(icon="mdi::step-backward")],
            {
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
            },
        ],
        [
            "create_lineedit",
            ["edit_index"],
            {
                "font_metric_width_factor": 10,
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
                "text": "0",
                "validator": QtGui.QIntValidator(),
            },
        ],
        [
            "create_lineedit",
            ["edit_data"],
            {
                "font_metric_width_factor": 10,
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
                "text": "0.0",
                "validator": QtGui.QDoubleValidator(),
                "visible": False,
            },
        ],
        [
            "create_label",
            ["label_unit", ""],
            {
                "font_metric_width_factor": 8,
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
                "visible": False,
            },
        ],
        [
            "add_any_widget",
            ["button_forward", SquareButton(icon="mdi::step-forward")],
            {
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
            },
        ],
        [
            "add_any_widget",
            ["button_end", SquareButton(icon="mdi::skip-forward")],
            {
                "gridPos": (0, -1, 1, 1),
                "parent_widget": "point_selection_container"
                if multiline
                else "::self::",
            },
        ],
    ]
