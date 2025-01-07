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
Module with the DirectorySpyFrameBuilder class which is used to
populate the DirectorySpyFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectorySpyFrameBuilder"]


from pydidas.core.constants import (
    FONT_METRIC_PARAM_EDIT_WIDTH,
    POLICY_EXP_EXP,
    POLICY_FIX_EXP,
)
from pydidas.widgets import ScrollArea
from pydidas.widgets.framework import BaseFrameWithApp
from pydidas.widgets.silx_plot import PydidasPlot2D


class DirectorySpyFrameBuilder:
    """
    Builder to populate the DirectorySpyFrame with widgets.
    """

    @staticmethod
    def __param_widget_config(param_key):
        """
        Get Formatting options for create_param_widget calls.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.

        Returns
        -------
        dict :
            The dictionary with the formatting options.
        """
        return {
            "parent_widget": "config",
            "linebreak": param_key
            in [
                "filename_pattern",
                "directory_path",
                "detector_mask_file",
                "bg_file",
                "hdf5_key",
                "bg_hdf5_key",
            ],
        }

    @classmethod
    def build_frame(cls, frame: BaseFrameWithApp):
        """
        Build the frame and create all widgets.

        Parameters
        ----------
        frame : BaseFrameWithApp
            The frame instance.
        """
        frame.create_label(
            "title",
            "Directory spy",
            fontsize_offset=4,
            bold=True,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )

        frame.create_empty_widget(
            "config",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget=None,
        )
        frame.create_spacer("spacer1", parent_widget=frame._widgets["config"])
        frame.create_any_widget(
            "config_area",
            ScrollArea,
            layout_kwargs={"alignment": None},
            sizePolicy=POLICY_FIX_EXP,
            stretch=(1, 0),
            widget=frame._widgets["config"],
        )

        for _param_key in [
            "directory_path",
            "scan_for_all",
            "filename_pattern",
            "hdf5_key",
            "hdf5_slicing_axis",
            "use_detector_mask",
            "detector_mask_file",
            "detector_mask_val",
            "use_bg_file",
            "bg_file",
            "bg_hdf5_key",
            "bg_hdf5_frame",
        ]:
            frame.create_param_widget(
                frame.get_param(_param_key), **cls.__param_widget_config(_param_key)
            )
            if _param_key in ["hdf5_key", "detector_mask_val"]:
                frame.create_line(f"line_{_param_key}", parent_widget="config")

        frame.create_line("line_buttons", parent_widget="config")

        frame.create_button("but_once", "Show latest image", parent_widget="config")
        frame.create_button("but_show", "Force plot update", parent_widget="config")
        frame.create_button("but_exec", "Start scanning", parent_widget="config")

        frame.create_button(
            "but_stop", "Stop scanning", enabled=False, parent_widget="config"
        )

        frame.create_spacer("config_terminal_spacer", parent_widget="config")

        frame.create_spacer("menu_bottom_spacer")

        frame.add_any_widget(
            "plot",
            PydidasPlot2D(),
            alignment=None,
            gridPos=(0, 1, 3, 1),
            visible=True,
            stretch=(1, 1),
            sizePolicy=POLICY_EXP_EXP,
        )
