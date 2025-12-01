# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the ImageMathFrameBuilder class which is used to populate
the ImageMathFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["IMAGE_BUFFER_SIZE", "IMAGE_MATH_FRAME_BUILD_CONFIG"]


from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import constants
from pydidas.core.constants import FONT_METRIC_WIDE_CONFIG_WIDTH
from pydidas.widgets import ScrollArea
from pydidas.widgets.selection import SelectDataFrameWidget
from pydidas.widgets.silx_plot import PydidasPlot2D


UFUNCS = ["absolute", "exp", "fmax", "fmin", "log", "log2", "log10", "power", "sqrt"]

LOCAL_SETTINGS = QtCore.QLocale(QtCore.QLocale.C)
LOCAL_SETTINGS.setNumberOptions(QtCore.QLocale.RejectGroupSeparator)

FLOAT_VALIDATOR = QtGui.QDoubleValidator()
FLOAT_VALIDATOR.setNotation(QtGui.QDoubleValidator.ScientificNotation)
FLOAT_VALIDATOR.setLocale(LOCAL_SETTINGS)


_kwargs_for_single_char_label = {
    "bold": True,
    "fontsize_offset": 1,
    "font_metric_width_factor": 0.7,
    "gridPos": (0, -1, 1, 1),
    "margin": 2,
    "minimum_width": 12,
}

IMAGE_BUFFER_SIZE = 3
_INPUT_IMAGES = tuple(f"Input image #{i}" for i in range(1, IMAGE_BUFFER_SIZE + 1))
_IMAGES = tuple(f"Image #{i}" for i in range(1, IMAGE_BUFFER_SIZE + 1))
_ALL_IMAGES = ("Opened file",) + _INPUT_IMAGES + _IMAGES
_CURRENT_IMAGES = ("Current image",) + _INPUT_IMAGES + _IMAGES

IMAGE_MATH_FRAME_BUILD_CONFIG: list[list[str | tuple[Any] | dict[str, Any]]] = [
    [
        "create_label",
        ("title", "Image mathematics"),
        {
            "bold": True,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH,
            "fontsize_offset": 4,
            "gridPos": (0, 0, 1, 1),
        },
    ],
    [
        "create_empty_widget",
        ("left_container",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH,
            "minimumHeight": 600,
            "parent_widget": None,
        },
    ],
    [
        "create_any_widget",
        ("left_scroll_area", ScrollArea),
        {
            "layout_kwargs": {"alignment": None},
            "sizePolicy": constants.POLICY_FIX_EXP,
            "stretch": (1, 0),
            "widget": "left_container",
        },
    ],
    ["create_line", ("line_top",), {"parent_widget": "left_container"}],
    [
        "create_label",
        ("label_open", "Open new image:"),
        {"fontsize_offset": 1, "bold": True, "parent_widget": "left_container"},
    ],
    # Add widgets to load images and store them in the buffer
    [
        "create_any_widget",
        ("file_selector", SelectDataFrameWidget),
        {
            "import_reference": "ImageMathFrame__image_import",
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH,
            "parent_widget": "left_container",
        },
    ],
    ["create_spacer", (None,), {"parent_widget": "left_container", "fixedHeight": 5}],
    [
        "create_empty_widget",
        ("store_input_image",),
        {"parent_widget": "left_container"},
    ],
    [
        "create_label",
        ("label_store_input_image", "Store loaded image as "),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 2,
            "parent_widget": "store_input_image",
            "sizePolicy": constants.POLICY_MIN_MIN,
            "wordWrap": False,
        },
    ],
    [
        "create_combo_box",
        ("combo_store_input_image",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 3,
            "gridPos": (0, 1, 1, 1),
            "items": _INPUT_IMAGES,
            "parent_widget": "store_input_image",
        },
    ],
    [
        "create_button",
        ("but_store_input_image", "Store"),
        {
            "parent_widget": "store_input_image",
            "gridPos": (0, 2, 1, 1),
            "alignment": None,
            "sizePolicy": constants.POLICY_EXP_FIX,
            "icon": "qt-std::SP_CommandLink",
        },
    ],
    ["create_line", ("line_input",), {"parent_widget": "left_container"}],
    # Create widgets to display images from the buffer
    [
        "create_spacer",
        (None,),
        {"parent_widget": "left_container", "fixedHeight": 5},
    ],
    [
        "create_empty_widget",
        ("display_from_buffer",),
        {"parent_widget": "left_container"},
    ],
    [
        "create_label",
        ("label_display_from_buffer", "Display image:"),
        {
            "bold": True,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 3,
            "parent_widget": "display_from_buffer",
            "sizePolicy": constants.POLICY_MIN_MIN,
            "wordWrap": False,
        },
    ],
    [
        "create_spacer",
        (None,),
        {
            "gridPos": (0, 1, 1, 1),
            "parent_widget": "display_from_buffer",
            "policy": QtWidgets.QSizePolicy.Expanding,
            "vertical_policy": QtWidgets.QSizePolicy.Fixed,
        },
    ],
    [
        "create_combo_box",
        ("combo_display_image",),
        {
            "alignment": constants.ALIGN_TOP_RIGHT,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 2,
            "font_metric_height_factor": 1,
            "gridPos": (0, 2, 1, 1),
            "items": _ALL_IMAGES,
            "parent_widget": "display_from_buffer",
        },
    ],
    ["create_line", ("line_buffer",), {"parent_widget": "left_container"}],
    # Create widgets for image operations
    [
        "create_label",
        ("label_ops", "Image operations:"),
        {"bold": True, "fontsize_offset": 1, "parent_widget": "left_container"},
    ],
    ["create_spacer", (None,), {"parent_widget": "left_container", "fixedHeight": 10}],
    [
        "create_label",
        ("label_arithmetic", "Elementary arithmetic operations:"),
        {"bold": True, "parent_widget": "left_container"},
    ],
    [
        "create_empty_widget",
        ("ops_arithmetic",),
        {"layout_kwargs": {"horizontalSpacing": 2}, "parent_widget": "left_container"},
    ],
    [
        "create_combo_box",
        ("ops_arithmetic_target",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            "gridPos": (0, 0, 1, 1),
            "items": _IMAGES,
            "parent_widget": "ops_arithmetic",
        },
    ],
    [
        "create_label",
        (None, "="),
        {"parent_widget": "ops_arithmetic", **_kwargs_for_single_char_label},
    ],
    [
        "create_combo_box",
        ("combo_ops_arithmetic_input",),
        {
            "alignment": constants.ALIGN_CENTER_LEFT,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 3.2,
            "gridPos": (0, -1, 1, 1),
            "items": _CURRENT_IMAGES,
            "parent_widget": "ops_arithmetic",
        },
    ],
    [
        "create_combo_box",
        ("combo_ops_arithmetic_operation",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 10,
            "gridPos": (0, -1, 1, 1),
            "items": ["+", "-", "/", "x"],
            "minimum_width": 35,
            "parent_widget": "ops_arithmetic",
        },
    ],
    [
        "create_lineedit",
        ("io_ops_arithmetic_input",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            "font_metric_height_factor": 1,
            "gridPos": (0, -1, 1, 1),
            "parent_widget": "ops_arithmetic",
            "validator": FLOAT_VALIDATOR,
        },
    ],
    [
        "create_spacer",
        ("spacer_arithmetic_end",),
        {
            "gridPos": (0, -1, 1, 1),
            "parent_widget": "ops_arithmetic",
            "policy": QtWidgets.QSizePolicy.Expanding,
            "vertical_policy": QtWidgets.QSizePolicy.Fixed,
        },
    ],
    [
        "create_button",
        ("but_ops_arithmetic_execute", "Apply arithmetic operation"),
        {
            "alignment": constants.ALIGN_TOP_RIGHT,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 2.25,
            "parent_widget": "left_container",
        },
    ],
    ["create_spacer", (None,), {"parent_widget": "left_container", "fixedHeight": 10}],
    [
        "create_label",
        ("label_ops", "Apply operator to image:"),
        {"bold": True, "parent_widget": "left_container"},
    ],
    [
        "create_empty_widget",
        ("ops_operator",),
        {"layout_kwargs": {"horizontalSpacing": 2}, "parent_widget": "left_container"},
    ],
    [
        "create_combo_box",
        ("ops_operator_target",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            "gridPos": (0, 0, 1, 1),
            "items": _IMAGES,
            "parent_widget": "ops_operator",
        },
    ],
    [
        "create_label",
        (None, "="),
        {"parent_widget": "ops_operator", **_kwargs_for_single_char_label},
    ],
    [
        "create_combo_box",
        ("ops_operator_func",),
        {
            "currentIndex": 4,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            "gridPos": (0, -1, 1, 1),
            "items": UFUNCS,
            "parent_widget": "ops_operator",
        },
    ],
    [
        "create_label",
        (None, " ( "),
        {"parent_widget": "ops_operator", **_kwargs_for_single_char_label},
    ],
    [
        "create_combo_box",
        ("combo_ops_operator_input",),
        {
            "alignment": constants.ALIGN_CENTER_LEFT,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 3.5,
            "gridPos": (0, -1, 1, 1),
            "items": _CURRENT_IMAGES,
            "parent_widget": "ops_operator",
        },
    ],
    [
        "create_label",
        ("label_ops_operator_sep", ", "),
        {
            "parent_widget": "ops_operator",
            "visible": False,
            **_kwargs_for_single_char_label,
        },
    ],
    [
        "create_lineedit",
        ("io_ops_operator_input",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 9,
            "gridPos": (0, -1, 1, 1),
            "parent_widget": "ops_operator",
            "validator": FLOAT_VALIDATOR,
            "visible": False,
        },
    ],
    [
        "create_label",
        ("label_ops_operator_closing_bracket", ")"),
        {"parent_widget": "ops_operator", **_kwargs_for_single_char_label},
    ],
    [
        "create_spacer",
        ("spacer_operator_end",),
        {
            "gridPos": (0, -1, 1, 1),
            "parent_widget": "ops_operator",
            "policy": QtWidgets.QSizePolicy.Expanding,
            "vertical_policy": QtWidgets.QSizePolicy.Fixed,
        },
    ],
    [
        "create_button",
        ("but_ops_operator_execute", "Apply operator"),
        {
            "alignment": constants.ALIGN_TOP_RIGHT,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 2.25,
            "parent_widget": "left_container",
        },
    ],
    ["create_spacer", (None,), {"parent_widget": "left_container", "fixedHeight": 10}],
    [
        "create_label",
        ("label_image_arithmetic", "Arithmetic image operations:"),
        {"bold": True, "parent_widget": "left_container"},
    ],
    [
        "create_empty_widget",
        ("ops_image_arithmetic",),
        {"parent_widget": "left_container"},
    ],
    [
        "create_combo_box",
        ("ops_image_arithmetic_target",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 4.8,
            "items": _IMAGES,
            "parent_widget": "ops_image_arithmetic",
        },
    ],
    [
        "create_label",
        (None, "="),
        {"parent_widget": "ops_image_arithmetic", **_kwargs_for_single_char_label},
    ],
    [
        "create_combo_box",
        ("combo_ops_image_arithmetic_input_1",),
        {
            "alignment": constants.ALIGN_CENTER_LEFT,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 3.5,
            "gridPos": (0, -1, 1, 1),
            "items": _CURRENT_IMAGES,
            "parent_widget": "ops_image_arithmetic",
        },
    ],
    [
        "create_combo_box",
        ("combo_ops_image_arithmetic_operation",),
        {
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 10,
            "minimum_width": 35,
            "gridPos": (0, -1, 1, 1),
            "items": ["+", "-", "/", "x"],
            "parent_widget": "ops_image_arithmetic",
        },
    ],
    [
        "create_combo_box",
        ("combo_ops_image_arithmetic_input_2",),
        {
            "alignment": constants.ALIGN_CENTER_LEFT,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 3.5,
            "gridPos": (0, -1, 1, 1),
            "items": _CURRENT_IMAGES,
            "parent_widget": "ops_image_arithmetic",
        },
    ],
    [
        "create_spacer",
        ("spacer_arithmetic_end",),
        {
            "gridPos": (0, -1, 1, 1),
            "parent_widget": "ops_arithmetic",
            "policy": QtWidgets.QSizePolicy.Expanding,
            "vertical_policy": QtWidgets.QSizePolicy.Fixed,
        },
    ],
    [
        "create_button",
        ("but_ops_image_arithmetic_execute", "Apply arithmetic operation"),
        {
            "alignment": constants.ALIGN_TOP_RIGHT,
            "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 2.25,
            "parent_widget": "left_container",
        },
    ],
    # Create widgets for exporting images
    [
        "create_spacer",
        (None,),
        {"parent_widget": "left_container", "fixedHeight": 10},
    ],
    [
        "create_line",
        ("line_export",),
        {"parent_widget": "left_container"},
    ],
    [
        "create_button",
        ("but_export", "Export current image"),
        {"parent_widget": "left_container"},
    ],
    # Create widgets for plotting the images
    [
        "create_any_widget",
        ("viewer", PydidasPlot2D),
        {"gridPos": (1, 1, 1, 1)},
    ],
]
