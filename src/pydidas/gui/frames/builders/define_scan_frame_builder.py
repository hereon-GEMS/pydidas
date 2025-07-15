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
__all__ = [
    "column_width_factor",
    "scan_frame_build_config",
]

from typing import Any

from pydidas.contexts import ScanContext
from pydidas.core.constants import (
    ALIGN_BOTTOM_LEFT,
    ALIGN_BOTTOM_RIGHT,
    FONT_METRIC_CONFIG_WIDTH,
    FONT_METRIC_WIDE_CONFIG_WIDTH,
    POLICY_EXP_EXP,
)
from pydidas.widgets import ScrollArea
from pydidas.widgets.factory import SquareButton
from pydidas.widgets.utilities import get_pyqt_icon_from_str


SCAN_CONTEXT = ScanContext()

SCAN_DIMENSION_EXPLANATION_TEXT = (
    "The scan dimensions must be assigned based on the data acquisition scheme to "
    "match the incrementing image numbers.<br><b>The lowest numbered scan dimension is "
    "the slowest scan dimension and the highest numbered scan dimension is the fastest."
    "</b>"
)

_WIDTH_FACTOR_SPACER = 5


def __param_widget_config(name: str, **kwargs: Any) -> list[str, tuple, dict[str, Any]]:
    """Get the configuration for a parameter widget."""
    _kws = {"parent_widget": "config_global"} | kwargs
    return ["create_param_widget", (SCAN_CONTEXT.get_param(name),), _kws]


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
    return max(
        FONT_METRIC_WIDE_CONFIG_WIDTH
        + 2 * _WIDTH_FACTOR_SPACER
        + (1 + two_columns) * FONT_METRIC_CONFIG_WIDTH,
        FONT_METRIC_WIDE_CONFIG_WIDTH
        + 2 * _WIDTH_FACTOR_SPACER
        + int(1.5 * FONT_METRIC_CONFIG_WIDTH),
    )


def scan_frame_build_config() -> list[list[str, tuple, dict[str, Any]]]:
    """
    Get the configuration to build the DefineScanFrame.

    Returns
    -------
    list[list[str, tuple, dict[str, Any]]]
        The configuration for the frame.
    """
    _items = _container_config()
    _items += _explanation_config()
    _items += _global_header_config()
    _items += _scan_dim_groups_config()
    _items += _global_settings_config()
    return _items


def _container_config() -> list[list[str, tuple, dict[str, Any]]]:
    """Get the configuration for the container widgets."""
    _items = [
        [
            "create_empty_widget",
            ("main",),
            {"layout_kwargs": {"horizontalSpacing": 0}},
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
                "gridPos": (0, 0, 1, 1),
            },
        ],
    ]
    for _gridPos in [(1, 1, 1, 1), (2, 2, 1, 1), (3, 3, 1, 1)]:
        _items.append(
            [
                "create_empty_widget",
                (None,),
                {
                    "font_metric_width_factor": _WIDTH_FACTOR_SPACER,
                    "font_metric_height_factor": 1.5,
                    "parent_widget": "main",
                    "gridPos": _gridPos,
                },
            ]
        )
    _items += [
        [
            "create_empty_widget",
            ("config_explanation",),
            {
                "font_metric_width_factor": int(1.5 * FONT_METRIC_CONFIG_WIDTH)
                + _WIDTH_FACTOR_SPACER,
                # width of 3 columns = 1 for spacers, 2 for config_A/B
                "gridPos": (1, 2, 1, 3),
                "parent_widget": "main",
            },
        ],
        [
            "create_empty_widget",
            ("config_global",),
            {
                "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH,
                "gridPos": (1, 0, 3, 1),
                "parent_widget": "main",
            },
        ],
        [
            "create_empty_widget",
            ("config_A",),
            {
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
                "gridPos": (3, 2, 1, 1),
                "parent_widget": "main",
            },
        ],
        [
            "create_empty_widget",
            ("config_B",),
            {
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
                # width of 2 columns to extend over the config_explanation widget
                "gridPos": (3, 4, 1, 2),
                "parent_widget": "main",
            },
        ],
    ]
    return _items


def _explanation_config() -> list[list[str, tuple, dict[str, Any]]]:
    """Get the configuration for the explanation widget."""
    return [
        [
            "create_label",
            ("dimension_hint_title", "Scan dimension explanation"),
            {
                "bold": True,
                "fontsize_offset": 1,
                "parent_widget": "config_explanation",
            },
        ],
        [
            "create_label",
            ("dimension_hint_text", SCAN_DIMENSION_EXPLANATION_TEXT),
            {
                "font_metric_height_factor": 6,
                "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH,
                "parent_widget": "config_explanation",
                "wordWrap": True,
            },
        ],
        [
            "create_button",
            ("but_more_scan_dim_info", "More information about scan dimensions"),
            {
                "icon": "qt-std::SP_MessageBoxInformation",
                "parent_widget": "config_explanation",
            },
        ],
    ]


def _global_header_config() -> list[list[str, tuple, dict[str, Any]]]:
    """Get the configuration to build the global controls."""
    return [
        [
            "create_button",
            ("but_import_from_pydidas", "Import scan settings from pydidas file"),
            {
                "icon": "qt-std::SP_DialogOpenButton",
                "parent_widget": "config_global",
            },
        ],
        [
            "create_button",
            (
                "but_import_bl_metadata",
                "Import scan settings from beamline scan metadata",
            ),
            {
                "parent_widget": "config_global",
            },
        ],
        [
            "create_button",
            ("but_reset", "Reset all scan settings"),
            {"icon": "qt-std::SP_BrowserReload", "parent_widget": "config_global"},
        ],
        [
            "create_empty_widget",
            (None,),
            {
                "font_metric_height_factor": 1,
                "parent_widget": "config_global",
            },
        ],
    ]


def _scan_dim_groups_config() -> list[list[str, tuple, dict[str, Any]]]:
    """Build the scan dimension groups."""
    _items = []
    for i_dim in range(4):
        _parent = "config_A" if i_dim in [0, 1] else "config_B"
        _start_row = 0 if i_dim in [0, 2] else 7
        _items.extend(
            [
                [
                    "create_label",
                    (f"title_{i_dim}", f"\nScan dimension {i_dim}:"),
                    {
                        "alignment": ALIGN_BOTTOM_LEFT,
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
                        "alignment": ALIGN_BOTTOM_RIGHT,
                        "gridPos": (_start_row, 2, 1, 1),
                        "icon": get_pyqt_icon_from_str("mdi::chevron-up"),
                        "parent_widget": _parent,
                    },
                ],
                [
                    "create_any_widget",
                    (f"button_down_{i_dim}", SquareButton),
                    {
                        "alignment": ALIGN_BOTTOM_RIGHT,
                        "gridPos": (_start_row, 3, 1, 1),
                        "icon": get_pyqt_icon_from_str("mdi::chevron-down"),
                        "parent_widget": _parent,
                    },
                ],
            ]
        )
        for basename in ["label", "n_points", "delta", "unit", "offset"]:
            _items.append(
                __param_widget_config(
                    f"scan_dim{i_dim}_{basename}",
                    font_metric_width_factor=FONT_METRIC_CONFIG_WIDTH,
                    gridPos=(-1, 0, 1, 4),
                    parent_widget=_parent,
                    width_text=0.6,
                    width_io=0.3,
                )
            )
        _items.append(
            ["create_spacer", ("scan_dim_spacer",), {"parent_widget": _parent}]
        )
    return _items


def _global_settings_config() -> list[list[str, tuple, dict[str, Any]]]:
    """Create the items for the global scan configuration."""
    _items = [
        [
            "create_label",
            ("scan_global", "\nGlobal scan parameters:"),
            {"bold": True, "fontsize_offset": 1, "parent_widget": "config_global"},
        ],
        __param_widget_config("scan_dim"),
    ]
    for _name in ["scan_title", "scan_base_directory", "scan_name_pattern"]:
        if _name == "scan_name_pattern":
            _items.extend(__file_naming_header_config())
        _items.append(__param_widget_config(_name, linebreak=True))
    for _name in [
        "pattern_number_offset",
        "pattern_number_delta",
        "frame_indices_per_scan_point",
        "scan_frames_per_point",
        "scan_multi_frame_handling",
    ]:
        if _name == "frame_indices_per_scan_point":
            _items.extend(__multi_frame_header_config())
        _items.append(__param_widget_config(_name))
    _items.append(
        [
            "create_button",
            ("but_save", "Export scan settings"),
            {
                "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH,
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
            {"gridPos": (-1, 0, 1, 1), "sizePolicy": POLICY_EXP_EXP},
        ],
    )
    return _items


def __file_naming_header_config() -> list[list[str, tuple, dict[str, Any]]]:
    """Get the configuration for the file naming header."""
    return [
        ["create_line", ("file_line",), {"parent_widget": "config_global"}],
        [
            "create_empty_widget",
            ("_file_header",),
            {
                "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH,
                "gridPos": (-1, 0, 1, 1),
                "parent_widget": "config_global",
                "layout_kwargs": {"spacing": 0},
            },
        ],
        [
            "create_label",
            ("file_label", "File naming:"),
            {
                "parent_widget": "_file_header",
                "underline": True,
                "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 3,
            },
        ],
        [
            "create_button",
            ("but_file_naming_help", "More information about file naming"),
            {
                "icon": "qt-std::SP_MessageBoxInformation",
                "parent_widget": "_file_header",
                "font_metric_width_factor": 2 * FONT_METRIC_WIDE_CONFIG_WIDTH / 3,
                "gridPos": (0, -1, 1, 1),
            },
        ],
    ]


def __multi_frame_header_config() -> list[list[str, tuple, dict[str, Any]]]:
    """Get the configuration for the multi-frame handling header."""
    return [
        ["create_line", (None,), {"parent_widget": "config_global"}],
        [
            "create_empty_widget",
            ("_multi_frame_header",),
            {
                "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH,
                "gridPos": (-1, 0, 1, 1),
                "parent_widget": "config_global",
                "layout_kwargs": {"spacing": 0},
            },
        ],
        [
            "create_label",
            ("scan_multi_frame_handling", "Multi-frame handling:"),
            {
                "parent_widget": "_multi_frame_header",
                "underline": True,
                "font_metric_width_factor": FONT_METRIC_WIDE_CONFIG_WIDTH / 3,
            },
        ],
        [
            "create_button",
            ("but_multi_frame_help", "More information multi-frame handling"),
            {
                "icon": "qt-std::SP_MessageBoxInformation",
                "parent_widget": "_multi_frame_header",
                "font_metric_width_factor": 2 * FONT_METRIC_WIDE_CONFIG_WIDTH / 3,
                "gridPos": (0, -1, 1, 1),
            },
        ],
    ]
