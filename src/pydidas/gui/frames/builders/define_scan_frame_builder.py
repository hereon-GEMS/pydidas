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
Module with the DefineScanFrameBuilder class which is used to populate
the DefineScanFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["column_width_factor", "build_header_config", "build_scan_dim_groups"]


from pydidas.contexts import ScanContext
from pydidas.core import constants
from pydidas.widgets import ScrollArea
from pydidas.widgets.factory import SquareButton
from pydidas.widgets.utilities import get_pyqt_icon_from_str


SCAN_SETTINGS = ScanContext()

SCAN_DIMENSION_EXPLANATION_TEXT = (
    "The scan dimensions must be assigned based on the data acquisition scheme to "
    "match the incrementing image numbers.<br><b>The lowest numbered scan dimension is "
    "the slowest scan dimension and the highest numbered scan dimension is the fastest."
    "</b>"
)

_WIDTH_FACTOR_SPACER = 5


def column_width_factor(two_columns: bool) -> int:
    """
    Get the width factor based on the number of visible columns.

    Parameters
    ----------
    dim_columns : int
        The number of columns

    Returns
    -------
    float
        The resulting total width factor for font metrics.
    """
    return (
        constants.FONT_METRIC_WIDE_CONFIG_WIDTH
        + 2 * _WIDTH_FACTOR_SPACER
        + (1 + two_columns) * constants.FONT_METRIC_CONFIG_WIDTH
    )


def build_header_config():
    """
    Get information to build the frame.

    Returns
    -------
    list[list[str, tuple, dict]]
        The list with the information required to build the frame.
        The list include the callable method name, the arguments and
        the keyword arguments.
    """
    return [
        [
            "create_empty_widget",
            ("main",),
            {
                "font_metric_width_factor": (
                    constants.FONT_METRIC_WIDE_CONFIG_WIDTH
                    + 2 * _WIDTH_FACTOR_SPACER
                    + 2 * constants.FONT_METRIC_CONFIG_WIDTH
                ),
                "layout_kwargs": {"horizontalSpacing": 0},
            },
        ],
        [
            "create_any_widget",
            ("config_area", ScrollArea),
            {
                "layout_kwargs": {"alignment": None},
                "resize_to_widget_width": True,
                "widget": "main",
            },
        ],
        [
            "create_label",
            ("label_title", "Scan settings\n"),
            {
                "fontsize_offset": 4,
                "bold": True,
                "parent_widget": "main",
            },
        ],
        [
            "create_empty_widget",
            ("config_header",),
            {
                "font_metric_width_factor": constants.FONT_METRIC_WIDE_CONFIG_WIDTH,
                "parent_widget": "main",
            },
        ],
        [
            "create_button",
            ("but_import_from_pydidas", "Import scan settings from pydidas file"),
            {
                "icon": "qt-std::SP_DialogOpenButton",
                "parent_widget": "config_header",
            },
        ],
        [
            "create_button",
            (
                "but_import_bl_metadata",
                "Import scan settings from beamline scan metadata",
            ),
            {
                "parent_widget": "config_header",
            },
        ],
        [
            "create_button",
            ("but_reset", "Reset all scan settings"),
            {"icon": "qt-std::SP_BrowserReload", "parent_widget": "config_header"},
        ],
        [
            "create_spacer",
            (None,),
            {
                "fixedHeight": 15,
                "parent_widget": "config_header",
            },
        ],
        [
            "create_label",
            ("dimension_hint_title", "Scan dimension explanation"),
            {
                "bold": True,
                "fontsize_offset": 1,
                "parent_widget": "config_header",
            },
        ],
        [
            "create_label",
            ("dimension_hint_text", SCAN_DIMENSION_EXPLANATION_TEXT),
            {
                "font_metric_height_factor": 6,
                "font_metric_width_factor": constants.FONT_METRIC_WIDE_CONFIG_WIDTH,
                "parent_widget": "config_header",
                "wordWrap": True,
            },
        ],
        [
            "create_button",
            ("but_more_scan_dim_info", "More information about scan dimensions"),
            {
                "icon": "qt-std::SP_MessageBoxInformation",
                "parent_widget": "config_header",
            },
        ],
        ["create_spacer", (None,), {"parent_widget": "main"}],
    ]


def build_scan_dim_groups(start_row: int):
    """
    Build the scan dimension groups.

    Parameters
    ----------
    start_row : int
        The row to start the scan dimension groups.
    """
    _items = [
        [
            "create_empty_widget",
            ("config_global",),
            {
                "font_metric_width_factor": constants.FONT_METRIC_WIDE_CONFIG_WIDTH,
                "gridPos": (start_row, 0, 1, 1),
                "parent_widget": "main",
            },
        ],
        [
            "create_empty_widget",
            ("horizontal_spacer_A",),
            {
                "font_metric_width_factor": _WIDTH_FACTOR_SPACER,
                "gridPos": (start_row, -1, 1, 1),
                "parent_widget": "main",
            },
        ],
        [
            "create_empty_widget",
            ("config_A",),
            {
                "font_metric_width_factor": constants.FONT_METRIC_CONFIG_WIDTH,
                "gridPos": (start_row, -1, 1, 1),
                "parent_widget": "main",
            },
        ],
        [
            "create_empty_widget",
            ("horizontal_spacer_B",),
            {
                "font_metric_width_factor": _WIDTH_FACTOR_SPACER,
                "gridPos": (start_row, -1, 1, 1),
                "parent_widget": "main",
            },
        ],
        [
            "create_empty_widget",
            ("config_B",),
            {
                "font_metric_width_factor": constants.FONT_METRIC_CONFIG_WIDTH,
                "gridPos": (start_row, -1, 1, 1),
                "parent_widget": "main",
            },
        ],
        [
            "create_label",
            ("scan_global", "\nGlobal scan parameters:"),
            {"bold": True, "fontsize_offset": 1, "parent_widget": "config_global"},
        ],
        [
            "create_param_widget",
            (SCAN_SETTINGS.get_param("scan_dim"),),
            {"parent_widget": "config_global"},
        ],
    ]
    for _name in ["scan_title", "scan_base_directory", "scan_name_pattern"]:
        _items.append(
            [
                "create_param_widget",
                (SCAN_SETTINGS.get_param(_name),),
                {"linebreak": True, "parent_widget": "config_global"},
            ]
        )
    for _name in [
        "scan_start_index",
        "scan_index_stepping",
        "scan_multiplicity",
        "scan_multi_image_handling",
    ]:
        _items.append(
            [
                "create_param_widget",
                (SCAN_SETTINGS.get_param(_name),),
                {"parent_widget": "config_global"},
            ]
        )

    # populate scan_param_frame widget
    for i_dim in range(4):
        _parent = "config_A" if i_dim in [0, 1] else "config_B"
        _start_row = 0 if i_dim in [0, 2] else 7
        _items.extend(
            [
                [
                    "create_label",
                    (f"title_{i_dim}", f"\nScan dimension {i_dim}:"),
                    {
                        "alignment": constants.ALIGN_BOTTOM_LEFT,
                        "bold": True,
                        "fontsize_offset": 1,
                        "font_metric_width_factor": 35,
                        "gridPos": (_start_row, 0, 1, 1),
                        "parent_widget": _parent,
                    },
                ],
                [
                    "create_any_widget",
                    (f"button_up_{i_dim}", SquareButton),
                    {
                        "alignment": constants.ALIGN_BOTTOM_RIGHT,
                        "gridPos": (_start_row, 2, 1, 1),
                        "icon": get_pyqt_icon_from_str("mdi::chevron-up"),
                        "parent_widget": _parent,
                    },
                ],
                [
                    "create_any_widget",
                    (f"button_down_{i_dim}", SquareButton),
                    {
                        "alignment": constants.ALIGN_BOTTOM_RIGHT,
                        "gridPos": (_start_row, 3, 1, 1),
                        "icon": get_pyqt_icon_from_str("mdi::chevron-down"),
                        "parent_widget": _parent,
                    },
                ],
            ]
        )
        for basename in ["label", "n_points", "delta", "unit", "offset"]:
            _items.append(
                [
                    "create_param_widget",
                    (SCAN_SETTINGS.get_param(f"scan_dim{i_dim}_{basename}"),),
                    {
                        "font_metric_width_factor": constants.FONT_METRIC_CONFIG_WIDTH,
                        "gridPos": (-1, 0, 1, 4),
                        "parent_widget": _parent,
                        "width_text": 0.6,
                        "width_io": 0.3,
                    },
                ],
            )
        _items.append(
            ["create_spacer", ("scan_dim_spacer",), {"parent_widget": _parent}],
        )

    _items.append(
        [
            "create_button",
            ("but_save", "Export scan settings"),
            {
                "font_metric_width_factor": constants.FONT_METRIC_WIDE_CONFIG_WIDTH,
                "gridPos": (-1, 0, 1, 1),
                "icon": "qt-std::SP_DialogSaveButton",
                "parent_widget": "main",
            },
        ],
    )
    _items.append(
        [
            "create_spacer",
            ("final_spacer",),
            {"gridPos": (-1, 0, 1, 1), "sizePolicy": constants.POLICY_EXP_EXP},
        ],
    )
    return _items
