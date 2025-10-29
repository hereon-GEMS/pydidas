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
Module with the QUICK_INTEGRATION_FRAME_BUILD_CONFIG which allows to populate
the QuickIntegrationFrame with the required widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["QUICK_INTEGRATION_FRAME_BUILD_CONFIG"]


from typing import Any

from qtpy import QtWidgets

from pydidas.core import constants
from pydidas.widgets import ScrollArea
from pydidas.widgets.data_viewer import DataViewer
from pydidas.widgets.misc import (
    PointsForBeamcenterWidget,
    SelectDataFrameWidget,
    ShowIntegrationRoiParamsWidget,
)
from pydidas.widgets.silx_plot import (
    PydidasPlot2DwithIntegrationRegions,
)


def _label_header(
    parent_key: str = "config", size_offset: int = 1, **kwargs: Any
) -> dict:
    """
    Get the options for header labels.

    Parameters
    ----------
    parent_key : str, optional
        The parent widget reference key. The default is "config".
    size_offset : int, optional
        The offset to the standard font size. The default is 1.
    **kwargs : Any
        Any additional options to be added.

    Returns
    -------
    dict
        The options' dictionary.
    """
    return {
        "bold": True,
        "fontsize_offset": size_offset,
        "parent_widget": parent_key,
        **kwargs,
    }


QUICK_INTEGRATION_FRAME_BUILD_CONFIG: list[
    list[str | tuple[Any, ...] | dict[str, Any]]
] = [
    [
        "add_any_widget",
        ("tabs", QtWidgets.QTabWidget()),
        {"gridPos": (1, 1, 1, 1), "minimumWidth": 400},
    ],
    [
        "create_empty_widget",
        ("tab_plot",),
        {
            "layout_kwargs": dict(
                contentsMargins=(10, 10, 10, 10),
                columnStretch=(1, 1),
                rowStretch=(0, 1),
            ),
            "parent_widget": None,
        },
    ],
    [
        "create_any_widget",
        ("input_plot", PydidasPlot2DwithIntegrationRegions),
        {
            "enabled": False,
            "gridPos": (0, 1, 1, 1),
            "minimumHeight": 500,
            "minimumWidth": 500,
            "parent_widget": "tab_plot",
            "sizePolicy": constants.POLICY_EXP_EXP,
        },
    ],
    [
        "create_any_widget",
        ("input_beamcenter_points", PointsForBeamcenterWidget),
        {"gridPos": (0, 0, 1, 1), "parent_widget": "tab_plot", "visible": False},
    ],
    ["create_any_widget", ("res_plot", DataViewer), {"parent_widget": None}],
    [
        "create_empty_widget",
        ("config",),
        {
            "font_metric_width_factor": constants.FONT_METRIC_PARAM_EDIT_WIDTH,
            "init_layout": True,
            "parent_widget": None,
            "sizePolicy": constants.POLICY_FIX_EXP,
        },
    ],
    [
        "create_label",
        ("label_title", "Quick integration\n"),
        {
            "bold": True,
            "fontsize_offset": 4,
            "font_metric_width_factor": constants.FONT_METRIC_PARAM_EDIT_WIDTH,
            "parent_widget": "config",
        },
    ],
    [
        "create_any_widget",
        ("config_area", ScrollArea),
        {
            "gridPos": (1, 0, 1, 1),
            "layout_kwargs": {"alignment": None},
            "sizePolicy": constants.POLICY_FIX_EXP,
            "stretch": (1, 0),
            "widget": "config",
        },
    ],
    ["create_label", (None, "Input file:"), _label_header()],
    [
        "create_any_widget",
        ("file_selector", SelectDataFrameWidget),
        {
            "import_reference": "QuickIntegrationFrame__image_import",
            "parent_widget": "config",
        },
    ],
    ["create_line", (None,), {"parent_widget": "config"}],
    ["create_label", (None, "Experiment description:"), _label_header()],
    [
        "create_button",
        ("copy_exp_context", "Copy experiment description from workflow setup"),
        {"icon": "pydidas::generic_copy", "parent_widget": "config"},
    ],
    [
        "create_button",
        ("but_show_exp_section", "Show detailed experiment section"),
        {"icon": "qt-std::SP_TitleBarUnshadeButton", "parent_widget": "config"},
    ],
    [
        "create_empty_widget",
        ("exp_section",),
        {"parent_widget": "config", "visible": False},
    ],
    [
        "create_button",
        ("but_import_exp", "Import diffraction experimental parameters"),
        {"icon": "qt-std::SP_DialogOpenButton", "parent_widget": "exp_section"},
    ],
    ["create_label", (None, "X-ray energy:"), _label_header("exp_section", 0)],
    ["create_param_widget", ("xray_energy",), {"parent_widget": "exp_section"}],
    ["create_param_widget", ("xray_wavelength",), {"parent_widget": "exp_section"}],
    ["create_label", (None, "Detector:"), _label_header("exp_section", 0)],
    ["create_param_widget", ("detector_pxsize",), {"parent_widget": "exp_section"}],
    ["create_param_widget", ("detector_dist",), {"parent_widget": "exp_section"}],
    [
        "create_param_widget",
        ("detector_mask_file",),
        {"parent_widget": "exp_section", "linebreak": True},
    ],
    ["create_spacer", (None,), {"fixedHeight": 15, "parent_widget": "exp_section"}],
    [
        "create_button",
        ("but_hide_exp_section", "Hide detailed experiment section"),
        {"icon": "qt-std::SP_TitleBarShadeButton", "parent_widget": "exp_section"},
    ],
    [
        "create_param_widget",
        ("detector_model",),
        {"linebreak": True, "parent_widget": "config", "visible": False},
    ],
    ["create_spacer", (None,), {"fixedHeight": 15, "parent_widget": "exp_section"}],
    [
        "create_empty_widget",
        ("beamcenter_section",),
        {"parent_widget": "config", "visible": False},
    ],
    ["create_line", (None,), {"parent_widget": "beamcenter_section"}],
    ["create_label", (None, "Beamcenter:"), _label_header("beamcenter_section", 1)],
    [
        "create_button",
        ("but_select_beamcenter_manually", "Start graphical beamcenter selection"),
        {"parent_widget": "beamcenter_section"},
    ],
    [
        "create_button",
        ("but_set_beamcenter", "Set selected point as beamcenter"),
        {"parent_widget": "beamcenter_section", "visible": False},
    ],
    [
        "create_button",
        ("but_fit_center_circle", "Fit beamcenter from points on circle"),
        {"parent_widget": "beamcenter_section", "visible": False},
    ],
    [
        "create_button",
        ("but_confirm_beamcenter", "Confirm beamcenter"),
        {
            "icon": "qt-std::SP_DialogApplyButton",
            "parent_widget": "beamcenter_section",
            "visible": False,
        },
    ],
    ["create_param_widget", ("beamcenter_x",), {"parent_widget": "beamcenter_section"}],
    ["create_param_widget", ("beamcenter_y",), {"parent_widget": "beamcenter_section"}],
    [
        "create_empty_widget",
        ("integration_header",),
        {"parent_widget": "config", "visible": False},
    ],
    ["create_line", (None,), {"parent_widget": "integration_header"}],
    [
        "create_label",
        ("label_roi", "Integration ROI:"),
        _label_header("integration_header"),
    ],
    [
        "create_empty_widget",
        ("integration_section",),
        {"parent_widget": "config", "visible": False},
    ],
    [
        "create_button",
        ("but_show_integration_section", "Show integration ROI section"),
        {
            "icon": "qt-std::SP_TitleBarUnshadeButton",
            "parent_widget": "config",
            "visible": False,
        },
    ],
    [
        "create_label",
        ("label_overlay_color", "Integration ROI display color"),
        _label_header("integration_section", 0),
    ],
    [
        "create_any_widget",
        ("roi_selector", ShowIntegrationRoiParamsWidget),
        {
            "show_reset_button": False,
            "add_bottom_spacer": False,
            "parent_widget": "integration_section",
        },
    ],
    [
        "create_spacer",
        (None,),
        {"fixedHeight": 15, "parent_widget": "integration_section"},
    ],
    [
        "create_button",
        ("but_hide_integration_section", "Hide integration ROI section"),
        {
            "icon": "qt-std::SP_TitleBarShadeButton",
            "parent_widget": "integration_section",
        },
    ],
    [
        "create_spacer",
        (None,),
        {"fixedHeight": 15, "parent_widget": "integration_section"},
    ],
    [
        "create_empty_widget",
        ("run_integration",),
        {"parent_widget": "config", "visible": False},
    ],
    ["create_line", (None,), {"parent_widget": "run_integration"}],
    ["create_label", (None, "Run integration"), _label_header("run_integration", 1)],
    [
        "create_param_widget",
        ("integration_direction",),
        {"parent_widget": "run_integration"},
    ],
    [
        "create_param_widget",
        ("azi_npoint",),
        {"parent_widget": "run_integration"},
    ],
    [
        "create_param_widget",
        ("rad_npoint",),
        {"parent_widget": "run_integration", "visible": False},
    ],
    [
        "create_button",
        ("but_run_integration", "Run pyFAI integration"),
        {"parent_widget": "run_integration"},
    ],
    ["create_spacer", (None,), {"fixedHeight": 10}],
]
