# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["DefineDiffractionExpFrameBuilder"]

from ....core import constants
from ....core.constants import FIX_EXP_POLICY
from ....widgets import ScrollArea
from ....widgets.framework import BaseFrame
from ....widgets.parameter_config import ParameterEditCanvas


class DefineDiffractionExpFrameBuilder(BaseFrame):
    """
    Mix-in class which includes the build_self method to populate the
    base class's UI and initialize all widgets.
    """

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self._scroll_width = 360
        self._widgets["config"] = ParameterEditCanvas(
            parent=None, init_layout=True, lineWidth=5, sizePolicy=FIX_EXP_POLICY
        )
        _2line_options = constants.DEFAULT_TWO_LINE_PARAM_CONFIG | {
            "width_total": self._scroll_width,
            "width_io": self._scroll_width - 20,
            "parent_widget": self._widgets["config"],
        }
        _1line_options = dict(
            width_text=self._scroll_width - 180,
            width_io=150,
            width_total=self._scroll_width,
            parent_widget=self._widgets["config"],
        )
        self.create_label(
            None,
            "Diffraction experimental setup\n",
            fontsize=constants.STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 1),
            fixedWidth=self._scroll_width,
        )
        self.create_any_widget(
            "config_area",
            ScrollArea,
            widget=self._widgets["config"],
            fixedWidth=self._scroll_width + 50,
            sizePolicy=FIX_EXP_POLICY,
            gridPos=(-1, 0, 1, 1),
            stretch=(1, 0),
            layout_kwargs={"alignment": None},
        )
        self.create_button(
            "but_load_from_file",
            "Import diffraction experimental parameters from file",
            icon=self.style().standardIcon(42),
            gridPos=(-1, 0, 1, 1),
            alignment=None,
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )
        self.create_button(
            "but_copy_from_pyfai",
            "Copy all experimental parameters from calibration",
            gridPos=(-1, 0, 1, 1),
            alignment=None,
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )
        for _param in self.params.values():
            if _param.refkey == "xray_wavelength":
                self.__create_xray_header()
            if _param.refkey == "detector_name":
                self.__create_detector_header()
            if _param.refkey == "detector_dist":
                self.__create_geometry_header()
            _options = (
                _2line_options
                if _param.refkey == "detector_mask_file"
                else _1line_options
            )
            self.create_param_widget(_param, **_options)

        self.create_spacer(
            None, gridPos=(-1, 0, 1, 1), parent_widget=self._widgets["config"]
        )
        self.create_button(
            "but_save_to_file",
            "Export experimental parameters to file",
            gridPos=(-1, 0, 1, 1),
            alignment=None,
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
            icon=self.style().standardIcon(43),
        )

    def __create_xray_header(self):
        """
        Create header items (label / buttons) for X-ray energy settings.
        """
        self.create_label(
            None,
            "\nBeamline X-ray energy:",
            fontsize=constants.STANDARD_FONT_SIZE + 1,
            bold=True,
            gridPos=(-1, 0, 1, 1),
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )
        self.create_button(
            "but_copy_energy_from_pyfai",
            "Copy X-ray energy from pyFAI calibration",
            gridPos=(-1, 0, 1, 1),
            alignment=None,
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )

    def __create_detector_header(self):
        """
        Create header items (label / buttons) for the detector.
        """
        self.create_label(
            None,
            "\nX-ray detector:",
            fontsize=constants.STANDARD_FONT_SIZE + 1,
            bold=True,
            gridPos=(-1, 0, 1, 1),
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )
        self.create_button(
            "but_select_detector",
            "Select X-ray detector from list",
            gridPos=(-1, 0, 1, 1),
            alignment=None,
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )
        self.create_button(
            "but_copy_det_from_pyfai",
            "Copy X-ray detector from pyFAI calibration",
            gridPos=(-1, 0, 1, 1),
            alignment=None,
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )

    def __create_geometry_header(self):
        """
        Create header items (label / buttons) for the detector.
        """
        self.create_label(
            None,
            "\nDetector geometry:",
            fontsize=constants.STANDARD_FONT_SIZE + 1,
            bold=True,
            gridPos=(-1, 0, 1, 1),
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )
        self.create_button(
            "but_copy_geo_from_pyfai",
            "Copy X-ray detector geometry from pyFAI calibration",
            gridPos=(-1, 0, 1, 1),
            fixedWidth=self._scroll_width,
            parent_widget=self._widgets["config"],
        )
