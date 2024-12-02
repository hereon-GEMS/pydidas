# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
The WorkflowTestFrameBuilder class populates the the WorkflowTestFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowTestFrameBuilder"]


from qtpy import QtCore

from ....core.constants import FONT_METRIC_PARAM_EDIT_WIDTH, POLICY_FIX_EXP
from ....core.utils import apply_qt_properties
from ....widgets import ScrollArea
from ....widgets.framework import BaseFrame
from ....widgets.misc import ReadOnlyTextWidget
from ....widgets.silx_plot import PydidasPlotStack


class WorkflowTestFrameBuilder:
    """
    Class to populate the WorkflowTestFrame with widgets.
    """

    @classmethod
    def __param_widget_config(cls, param_key: str) -> dict:
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
            "linebreak": param_key in ["image_selection", "selected_results"],
            "visible": param_key
            not in [
                "scan_index0",
                "scan_index1",
                "scan_index2",
                "scan_index3",
                "detector_image_index",
            ],
        }

    @classmethod
    def build_frame(cls, frame: BaseFrame):
        """
        Build the frame and create all widgets.

        Parameters
        ----------
        frame : BaseFrame
            The WorkflowTestFrame instance.
        """
        frame.create_label(
            "title", "Test workflow", bold=True, fontsize_offset=4, gridPos=(0, 0, 1, 2)
        )
        frame.create_spacer("title_spacer", fixedHeight=20)

        frame.create_empty_widget(
            "config",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget=None,
            sizePolicy=POLICY_FIX_EXP,
        )
        frame.create_spacer("spacer1", parent_widget="config")
        frame.create_any_widget(
            "config_area",
            ScrollArea,
            resize_to_widget_width=True,
            widget=frame._widgets["config"],
        )
        frame.create_button(
            "but_reload_tree",
            "Reset and reload workflow tree",
            icon="qt-std::SP_BrowserReload",
            parent_widget="config",
        )
        frame.create_line("line_refresh_tree", parent_widget="config")
        for _param in [
            "image_selection",
            "frame_index",
            "scan_index0",
            "scan_index1",
            "scan_index2",
            "scan_index3",
            "detector_image_index",
        ]:
            frame.create_param_widget(
                frame.get_param(_param), **cls.__param_widget_config(_param)
            )
        frame.create_line("line_selection", parent_widget="config")
        frame.create_button(
            "but_exec",
            "Process frame",
            icon="qt-std::SP_MediaPlay",
            parent_widget="config",
        )
        frame.create_line("line_results", parent_widget="config")
        frame.create_label(
            "label_results",
            "Results:",
            fontsize_offset=1,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget="config",
            underline=True,
        )
        frame.create_param_widget(
            frame.get_param("selected_results"),
            **cls.__param_widget_config("selected_results"),
        )
        frame.create_any_widget(
            "result_info",
            ReadOnlyTextWidget,
            alignment=QtCore.Qt.AlignTop,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            font_metric_height_factor=24,
            parent_widget="config",
            visible=False,
        )
        frame.create_button(
            "but_show_details",
            "Show detailed results for plugin",
            parent_widget="config",
            visible=False,
        )
        frame.create_button(
            "but_tweak_params",
            "Tweak plugin parameters",
            parent_widget="config",
            visible=False,
        )
        frame.create_spacer(
            "config_terminal_spacer",
            parent_widget="config",
        )
        frame.create_any_widget("plot", PydidasPlotStack, gridPos=(2, 1, 2, 1))
        apply_qt_properties(frame.layout(), columnStretch=((1, 10)))
