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
Module with utilities for the data_viewer.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "DATA_VIEW_CONFIG",
    "DataViewConfig",
    "invalid_range_str",
    "DATA_AXIS_SELECTOR_HEADER_BUILD_CONFIG",
    "DATA_AXIS_SELECTOR_BUILD_CONFIG",
]


from dataclasses import dataclass
from typing import Any

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtWidgets import QWidget

from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
    POLICY_EXP_FIX,
    QT_REG_EXP_FLOAT_RANGE_VALIDATOR,
    QT_REG_EXP_POS_INT_RANGE_VALIDATOR,
)
from pydidas.widgets.data_viewer.silx_subclasses import (
    PydidasArrayTableWidget,
    PydidasHdf5TableView,
)
from pydidas.widgets.factory import SquareButton
from pydidas.widgets.silx_plot import PydidasPlot1D, PydidasPlot2D


@dataclass(frozen=True)
class DataViewConfig:
    id: int
    title: str
    ref: str
    widget: type[QWidget]
    use_axes_selector: bool
    additional_choices: str | None
    min_dims: int
    allow_fewer_dims: bool = False


DATA_VIEW_CONFIG = {
    "view-h5": DataViewConfig(
        id=0,
        title="Hdf5",
        ref="view-h5",
        widget=PydidasHdf5TableView,
        use_axes_selector=False,
        additional_choices=None,
        min_dims=1,
    ),
    "view-curve": DataViewConfig(
        id=1,
        title="Curve",
        ref="view-curve",
        widget=PydidasPlot1D,
        use_axes_selector=True,
        additional_choices="use as curve x",
        min_dims=1,
    ),
    "view-curve-group": DataViewConfig(
        id=2,
        title="Curve group",
        ref="view-curve-group",
        widget=PydidasPlot1D,
        use_axes_selector=True,
        additional_choices="show all curves;;use as curves' x",
        min_dims=2,
    ),
    "view-image": DataViewConfig(
        id=3,
        title="Image",
        ref="view-image",
        widget=PydidasPlot2D,
        use_axes_selector=True,
        additional_choices="use as image y;;use as image x",
        min_dims=2,
    ),
    "view-table": DataViewConfig(
        id=4,
        title="Table",
        ref="view-table",
        widget=PydidasArrayTableWidget,
        use_axes_selector=True,
        additional_choices="use as table x;;use as table y",
        min_dims=0,
        allow_fewer_dims=True,
    ),
}


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


def DATA_AXIS_SELECTOR_HEADER_BUILD_CONFIG(
    axis_index: int, multiline: bool
) -> list[str, list[Any], dict[str, Any]]:
    """
    Get the arguments required to create all necessary widgets in the header.

    Parameters
    ----------
    axis_index : int
        The index of the axis.
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


def DATA_AXIS_SELECTOR_BUILD_CONFIG(
    multiline: bool,
) -> list[str, tuple[Any], dict[str, Any]]:
    """
    Get the arguments required to create all necessary widgets in the axis selector.
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
                "visible": False,
            },
        ],
        [
            "create_label",
            ["label_single_point", "This data dimension only includes a single point"],
            {
                "font_metric_width_factor": 48,
                "gridPos": (0, -1, 1, 1),
                "visible": False,
            },
        ],
        [
            "create_lineedit",
            ["edit_range_index"],
            {
                "font_metric_width_factor": 25,
                "gridPos": (0, -1, 1, 1),
                "toolTip": (
                    "Enter the start and end index separated by a colon. Please note that "
                    "contrary to Python slicing, the end index is included in the "
                    "selection."
                ),
                "validator": QT_REG_EXP_POS_INT_RANGE_VALIDATOR,
                "visible": False,
            },
        ],
        [
            "create_lineedit",
            ["edit_range_data"],
            {
                "font_metric_width_factor": 25,
                "gridPos": (0, -1, 1, 1),
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
                "sizePolicy": POLICY_EXP_FIX,
            },
        ],
        [
            "add_any_widget",
            ["button_start", SquareButton(icon="mdi::skip-backward")],
            {"gridPos": (0, -1, 1, 1)},
        ],
        [
            "add_any_widget",
            ["button_backward", SquareButton(icon="mdi::step-backward")],
            {"gridPos": (0, -1, 1, 1)},
        ],
        [
            "create_lineedit",
            ["edit_index"],
            {
                "font_metric_width_factor": 10,
                "gridPos": (0, -1, 1, 1),
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
                "visible": False,
            },
        ],
        [
            "add_any_widget",
            ["button_forward", SquareButton(icon="mdi::step-forward")],
            {"gridPos": (0, -1, 1, 1)},
        ],
        [
            "add_any_widget",
            ["button_end", SquareButton(icon="mdi::skip-forward")],
            {"gridPos": (0, -1, 1, 1)},
        ],
    ]
