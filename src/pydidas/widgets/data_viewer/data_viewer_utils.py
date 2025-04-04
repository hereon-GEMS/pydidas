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
    "DATA_VIEW_CONFIG",
    "DATA_VIEW_TITLES",
    "DATA_VIEW_REFS",
    "invalid_range_str",
    "get_data_axis_header_creation_args",
    "get_data_axis_widget_creation_args",
]


from qtpy import QtCore, QtGui, QtWidgets
from silx.gui.data.DataViews import _Hdf5View, _RawView

from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
    POLICY_EXP_FIX,
    QT_REG_EXP_FLOAT_RANGE_VALIDATOR,
    QT_REG_EXP_INT_RANGE_VALIDATOR,
)
from pydidas.widgets.factory import SquareButton
from pydidas.widgets.silx_plot._data_views import (
    Pydidas_Plot1dGroupView,
    Pydidas_Plot1dView,
    Pydidas_Plot2dView,
)


DATA_VIEW_CONFIG = {
    0: {
        "title": "Hdf5",
        "ref": "view-h5",
        "view": _Hdf5View,
        "use_axes_selector": False,
        "additional choices": None,
        "min_dims": 1,
    },
    1: {
        "title": "Curve",
        "ref": "view-curve",
        "view": Pydidas_Plot1dView,
        "use_axes_selector": True,
        "additional choices": "use as curve y",
        "min_dims": 1,
    },
    2: {
        "title": "Curve group",
        "ref": "view-curve-group",
        "view": Pydidas_Plot1dGroupView,
        "use_axes_selector": True,
        "additional choices": "show all curves;;use as curve y",
        "min_dims": 2,
    },
    3: {
        "title": "Image",
        "ref": "view-image",
        "view": Pydidas_Plot2dView,
        "use_axes_selector": True,
        "additional choices": "use as image y;;use as image x",
        "min_dims": 2,
    },
    4: {
        "title": "Table",
        "ref": "view-table",
        "view": _RawView,
        "use_axes_selector": True,
        "additional choices": "use as table x;;use as table y",
        "min_dims": 0,
    },
}
DATA_VIEW_TITLES = {_value["title"]: _key for _key, _value in DATA_VIEW_CONFIG.items()}
DATA_VIEW_REFS = {_value["ref"]: _key for _key, _value in DATA_VIEW_CONFIG.items()}


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
                "sizePolicy": POLICY_EXP_FIX,
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
                "font_metric_width_factor": 10 if multiline else 15,
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
                "font_metric_width_factor": 8 if multiline else 12,
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
