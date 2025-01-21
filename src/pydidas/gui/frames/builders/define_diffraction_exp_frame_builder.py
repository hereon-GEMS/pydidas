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
__all__ = ["DefineDiffractionExpFrameBuilder"]


from qtpy import QtGui

from pydidas.core import constants
from pydidas.core.utils import update_palette
from pydidas.widgets import ScrollArea, get_pyqt_icon_from_str
from pydidas.widgets.framework import BaseFrame


class DefineDiffractionExpFrameBuilder:
    """
    Class to populate the DefineDiffractionExpFrame with widgets.
    """

    frame = None

    @classmethod
    def build_frame(cls, frame: BaseFrame):
        """
        Populate the input frame with the required widgets.

        Parameters
        ----------
        frame : BaseFrame
            The DefineDiffractionExpFrame instance.
        """
        cls.frame = frame
        frame.create_empty_widget(
            "config",
            parent_widget=None,
            sizePolicy=constants.POLICY_FIX_EXP,
            font_metric_width_factor=2.1 * constants.FONT_METRIC_PARAM_EDIT_WIDTH,
            layout_kwargs={"horizontalSpacing": 0},
        )
        frame.create_label(
            None,
            "Diffraction experimental setup\n",
            bold=True,
            fontsize_offset=4,
            gridPos=(0, 0, 1, 1),
        )
        frame.create_any_widget(
            "config_area",
            ScrollArea,
            layout_kwargs={"alignment": None},
            sizePolicy=constants.POLICY_FIX_EXP,
            stretch=(1, 0),
            widget=frame._widgets["config"],
        )
        frame.create_button(
            "but_load_from_file",
            "Import diffraction experimental parameters",
            icon="qt-std::SP_DialogOpenButton",
            parent_widget="config",
        )
        frame.create_button(
            "but_copy_from_pyfai",
            "Copy experimental parameters from calibration",
            icon=get_pyqt_icon_from_str("pydidas::generic_copy"),
            parent_widget=frame._widgets["config"],
        )

        _row = frame.layout().rowCount()
        _parent = "config_left"
        frame.create_empty_widget(
            "config_left",
            parent_widget="config",
            font_metric_width_factor=constants.FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(_row, 0, 1, 1),
        )
        frame.create_empty_widget(
            "config_spacer",
            parent_widget="config",
            font_metric_width_factor=0.1 * constants.FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(_row, 1, 1, 1),
        )
        frame.create_empty_widget(
            "config_right",
            parent_widget="config",
            font_metric_width_factor=constants.FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(_row, 2, 1, 1),
        )

        for _param in frame.params.values():
            if _param.refkey == "xray_wavelength":
                frame.create_label(
                    None,
                    "\nBeamline X-ray energy:",
                    bold=True,
                    fontsize_offset=1,
                    parent_widget=_parent,
                )
            if _param.refkey == "detector_name":
                cls.create_detector_header()
            if _param.refkey == "detector_dist":
                cls.create_geometry_header()
                _parent = "config_right"
            frame.create_param_widget(
                _param,
                linebreak=_param.refkey == "detector_mask_file",
                parent_widget=_parent,
            )

        frame.create_label(
            "bc_label",
            "Derived beamcenter pixel position:",
            bold=True,
            parent_widget="config_right",
        )
        for _key in ["beamcenter_x", "beamcenter_y"]:
            frame.create_param_widget(
                frame._bc_params[_key], parent_widget="config_right"
            )
            update_palette(
                frame.param_widgets[_key],
                base=QtGui.QColor(235, 235, 235),
            )
            frame.param_widgets[_key].setReadOnly(True)

        frame.create_spacer(None, parent_widget="config")
        frame.create_button(
            "but_save_to_file",
            "Export experimental parameters to file",
            alignment=None,
            parent_widget="config",
            icon="qt-std::SP_DialogSaveButton",
        )

    @classmethod
    def create_detector_header(cls):
        """
        Create header items (label / buttons) for the detector.
        """
        cls.frame.create_label(
            None,
            "\nX-ray detector:",
            fontsize_offset=1,
            bold=True,
            parent_widget="config_left",
        )
        cls.frame.create_button(
            "but_select_detector",
            "Select X-ray detector from list",
            alignment=None,
            parent_widget="config_left",
        )

    @classmethod
    def create_geometry_header(cls):
        """
        Create header items (label / buttons) for the detector.
        """
        cls.frame.create_label(
            None,
            "\nDetector geometry:",
            fontsize_offset=1,
            bold=True,
            parent_widget="config_right",
        )
        cls.frame.create_button(
            "but_select_beamcenter_manually",
            "Manual beamcenter definition",
            parent_widget="config_right",
        )
        cls.frame.create_button(
            "but_convert_fit2d",
            "Convert Fit2D geometry",
            parent_widget="config_right",
        )
