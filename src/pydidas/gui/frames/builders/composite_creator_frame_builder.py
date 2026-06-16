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
Module with the CompositeCreatorFrameBuilder class which is used to
populate the CompositeCreatorFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "COMPOSITE_CREATOR_FRAME_BUILD_CONFIG",
    "ccf_param_widget_config",
    "KEYS_TO_INSERT_LINES_AFTER",
]


from typing import Any

from qtpy import QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
    POLICY_FIX_EXP,
)
from pydidas.widgets import ScrollArea, silx_plot


KEYS_TO_INSERT_LINES_AFTER = [
    "n_files",
    "images_per_file",
    "bg_hdf5_frame",
    "detector_mask_val",
    "roi_yhigh",
    "threshold_high",
    "binning",
    "output_fname",
    "n_total",
    "composite_ydir_orientation",
    "mosaic_border_value",
]


def ccf_param_widget_config(param_key):
    """
    Get Formatting options for create_param_widget instances.

    Parameters
    ----------
    param_key : str
        The reference key for Parameter.

    Returns
    -------
    dict
        The keyword dictionary to be passed to the ParamWidget creation.
    """
    return {
        "linebreak": param_key
        in [
            "first_file",
            "last_file",
            "hdf5_key",
            "bg_file",
            "bg_hdf5_key",
            "output_fname",
            "detector_mask_file",
            "composite_image_op",
        ],
        "enabled": param_key
        not in [
            "n_total",
            "hdf5_dataset_shape",
            "n_files",
            "raw_image_shape",
            "images_per_file",
        ],
        "parent_widget": "param_container",
        "visible": param_key
        not in [
            "hdf5_key",
            "hdf5_slicing_axis",
            "hdf5_first_image_num",
            "hdf5_last_image_num",
            "last_file",
            "hdf5_stepping",
            "hdf5_dataset_shape",
            "hdf5_stepping",
            "raw_image_shape",
        ],
    }


COMPOSITE_CREATOR_FRAME_BUILD_CONFIG: list[
    list[str | tuple[Any, ...] | dict[str, Any]]
] = [
    [
        "create_empty_widget",
        ("config_canvas",),
        {"font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH},
    ],
    [
        "create_any_widget",
        ("config_scroll_area", ScrollArea),
        {
            "layout_kwargs": {"alignment": None},
            "stretch": (1, 0),
            "sizePolicy": POLICY_FIX_EXP,
            "widget": "config_canvas",
        },
    ],
    [
        "create_label",
        ("title", "Composite image creator"),
        {"bold": True, "fontsize_offset": 4, "parent_widget": "config_canvas"},
    ],
    ["create_spacer", ("spacer1",), {"parent_widget": "config_canvas"}],
    [
        "create_button",
        ("but_clear", "Clear all entries"),
        {"icon": "qt-std::SP_BrowserReload", "parent_widget": "config_canvas"},
    ],
    [
        "create_any_widget",
        ("plot_window", silx_plot.PydidasPlot2D),
        {
            "alignment": None,
            "sizePolicy": POLICY_FIX_EXP,
            "cs_transform": False,
            "gridPos": (0, 1, 1, 1),
            "minimumWidth": 900,
            "visible": False,
            "stretch": (1, 1),
        },
    ],
    ["create_empty_widget", ("param_container",), {"parent_widget": "config_canvas"}],
    [
        "create_button",
        ("but_exec", "Generate composite"),
        {
            "enabled": False,
            "icon": "qt-std::SP_MediaPlay",
            "parent_widget": "config_canvas",
        },
    ],
    [
        "create_progress_bar",
        ("progress",),
        {
            "maximum": 100,
            "minimum": 0,
            "parent_widget": "config_canvas",
            "visible": False,
        },
    ],
    [
        "create_button",
        ("but_abort", "Abort composite creation"),
        {
            "enabled": True,
            "icon": "qt-std::SP_BrowserStop",
            "parent_widget": "config_canvas",
            "visible": False,
        },
    ],
    [
        "create_button",
        ("but_show", "Show composite creation"),
        {
            "enabled": False,
            "icon": "qt-std::SP_DesktopIcon",
            "parent_widget": "config_canvas",
        },
    ],
    [
        "create_button",
        ("but_save", "Export composite image to file"),
        {
            "enabled": False,
            "icon": "qt-std::SP_DialogSaveButton",
            "parent_widget": "config_canvas",
        },
    ],
    [
        "create_spacer",
        ("spacer_bottom",),
        {
            "height": 300,
            "parent_widget": "config_canvas",
            "policy": QtWidgets.QSizePolicy.Expanding,
        },
    ],
]
