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
Module with the DefineDiffractionExpFrameBuilder class which is used to
populate the DefineDiffractionExpFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DIFFRACTION_EXP_FRAME_BUILD_CONFIG"]


from pydidas.core import constants
from pydidas.widgets import ScrollArea, get_pyqt_icon_from_str


_STD_WIDTH = constants.FONT_METRIC_PARAM_EDIT_WIDTH

DIFFRACTION_EXP_FRAME_BUILD_CONFIG = [
    [
        "create_empty_widget",
        ("config",),
        {
            "font_metric_width_factor": 2.1 * _STD_WIDTH,
            "layout_kwargs": {"horizontalSpacing": 0},
            "parent_widget": None,
            "sizePolicy": constants.POLICY_FIX_EXP,
        },
    ],
    [
        "create_label",
        (None, "Diffraction experimental setup\n"),
        {"bold": True, "fontsize_offset": 4, "gridPos": (0, 0, 1, 1)},
    ],
    [
        "create_any_widget",
        ("config_area", ScrollArea),
        {
            "layout_kwargs": {"alignment": None},
            "sizePolicy": constants.POLICY_FIX_EXP,
            "stretch": (1, 0),
            "widget": "config",
        },
    ],
    [
        "create_empty_widget",
        ("config_header",),
        {"font_metric_width_factor": _STD_WIDTH, "parent_widget": "config"},
    ],
    [
        "create_button",
        ("but_load_from_file", "Import diffraction experimental parameters"),
        {"icon": "qt-std::SP_DialogOpenButton", "parent_widget": "config_header"},
    ],
    [
        "create_button",
        ("but_copy_from_pyfai", "Copy experimental parameters from calibration"),
        {
            "icon": get_pyqt_icon_from_str("pydidas::generic_copy"),
            "parent_widget": "config_header",
        },
    ],
    [
        "create_button",
        ("but_save_to_file", "Export experimental parameters to file"),
        {
            "alignment": None,
            "parent_widget": "config_header",
            "icon": "qt-std::SP_DialogSaveButton",
        },
    ],
    [
        "create_empty_widget",
        ("config_left",),
        {
            "font_metric_width_factor": _STD_WIDTH,
            "gridPos": (1, 0, 1, 1),
            "parent_widget": "config",
        },
    ],
    [
        "create_empty_widget",
        ("config_spacer",),
        {
            "font_metric_width_factor": 0.1 * _STD_WIDTH,
            "gridPos": (1, 1, 1, 1),
            "parent_widget": "config",
        },
    ],
    [
        "create_empty_widget",
        ("config_right",),
        {
            "font_metric_width_factor": _STD_WIDTH,
            "gridPos": (1, 2, 1, 1),
            "parent_widget": "config",
        },
    ],
    [
        "create_label",
        (None, "\nBeamline X-ray energy:"),
        {"bold": True, "fontsize_offset": 1, "parent_widget": "config_left"},
    ],
    ["create_param_widget", ("xray_wavelength",), {"parent_widget": "config_left"}],
    ["create_param_widget", ("xray_energy",), {"parent_widget": "config_left"}],
    [
        "create_label",
        (None, "\nX-ray detector:"),
        {"fontsize_offset": 1, "bold": True, "parent_widget": "config_left"},
    ],
    [
        "create_button",
        ("but_select_detector", "Select X-ray detector from list"),
        {"alignment": None, "parent_widget": "config_left"},
    ],
    ["create_param_widget", ("detector_name",), {"parent_widget": "config_left"}],
    ["create_param_widget", ("detector_npixx",), {"parent_widget": "config_left"}],
    ["create_param_widget", ("detector_npixy",), {"parent_widget": "config_left"}],
    ["create_param_widget", ("detector_pxsizex",), {"parent_widget": "config_left"}],
    ["create_param_widget", ("detector_pxsizey",), {"parent_widget": "config_left"}],
    [
        "create_param_widget",
        ("detector_mask_file",),
        {"linebreak": True, "parent_widget": "config_left"},
    ],
    [
        "create_label",
        (None, "\nDetector geometry:"),
        {"fontsize_offset": 1, "bold": True, "parent_widget": "config_right"},
    ],
    [
        "create_button",
        ("but_select_beamcenter_manually", "Manual beamcenter definition"),
        {"parent_widget": "config_right"},
    ],
    [
        "create_button",
        ("but_convert_fit2d", "Convert Fit2D geometry"),
        {"parent_widget": "config_right"},
    ],
    ["create_param_widget", ("detector_dist",), {"parent_widget": "config_right"}],
    [
        "create_label",
        ("label_geometry", "Detector geometry:"),
        {"bold": True, "fontsize_offset": 1, "parent_widget": "config_right"},
    ],
    ["create_param_widget", ("detector_dist",), {"parent_widget": "config_right"}],
    ["create_param_widget", ("detector_poni1",), {"parent_widget": "config_right"}],
    ["create_param_widget", ("detector_poni2",), {"parent_widget": "config_right"}],
    ["create_param_widget", ("detector_rot1",), {"parent_widget": "config_right"}],
    ["create_param_widget", ("detector_rot2",), {"parent_widget": "config_right"}],
    ["create_param_widget", ("detector_rot3",), {"parent_widget": "config_right"}],
    [
        "create_label",
        (None, "\nDerived beamcenter pixel position:"),
        {"bold": True, "parent_widget": "config_right"},
    ],
]
