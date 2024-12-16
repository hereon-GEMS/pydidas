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
Module with the WorkflowRunFrameBuilder class which is used to
populate the WorkflowRunFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowRunFrameBuilder"]


from pydidas.core.constants import FONT_METRIC_CONFIG_WIDTH, POLICY_FIX_EXP
from pydidas.widgets import ScrollArea
from pydidas.widgets.framework import BaseFrameWithApp
from pydidas.widgets.selection import ResultSelectionWidget
from pydidas.widgets.silx_plot import PydidasPlotStack


class WorkflowRunFrameBuilder:
    """
    Builder class to build the WorkflowRunFrame.
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
            "linebreak": param_key in ["autosave_directory", "selected_results"],
            "parent_widget": "config",
            "visible": param_key not in ["autosave_directory", "autosave_format"],
        }

    @classmethod
    def build_frame(cls, frame: BaseFrameWithApp):
        """
        Build the frame and create all widgets.

        Parameters
        ----------
        frame : BaseFrameWithApp
            The WorkflowRunFrame instance.
        """
        frame.create_label(
            "title",
            "Run full workflow processing",
            fontsize_offset=4,
            bold=True,
            gridPos=(0, 0, 1, 2),
        )

        frame.create_spacer("title_spacer", fixedHeight=10)

        frame.create_empty_widget(
            "config",
            font_metric_width_factor=FONT_METRIC_CONFIG_WIDTH,
            parent_widget=None,
            sizePolicy=POLICY_FIX_EXP,
        )
        frame.create_any_widget(
            "config_area",
            ScrollArea,
            sizePolicy=POLICY_FIX_EXP,
            widget=frame._widgets["config"],
        )
        frame.create_spacer("spacer1", parent_widget="config")
        for _param in ["autosave_results", "autosave_directory", "autosave_format"]:
            frame.create_param_widget(
                frame.get_param(_param), **cls.__param_widget_config(_param)
            )

        frame.create_line("line_autosave", parent_widget="config")
        frame.create_button(
            "but_exec",
            "Start processing",
            icon="qt-std::SP_MediaPlay",
            parent_widget="config",
        )
        frame.create_progress_bar(
            "progress",
            minimum=0,
            maximum=100,
            parent_widget="config",
            visible=False,
        )
        frame.create_button(
            "but_abort",
            "Abort processing",
            icon="qt-std::SP_BrowserStop",
            parent_widget="config",
            visible=False,
        )
        frame.create_line(
            "line_results",
            parent_widget="config",
        )
        frame.create_any_widget(
            "result_selector",
            ResultSelectionWidget,
            parent_widget="config",
            select_results_param=frame.get_param("selected_results"),
        )
        frame.create_line(
            "line_export",
            parent_widget="config",
        )
        frame.create_param_widget(
            frame.get_param("saving_format"),
            **cls.__param_widget_config("saving_format"),
        )
        frame.create_param_widget(
            frame.get_param("enable_overwrite"),
            **cls.__param_widget_config("enable_overwrite"),
        )
        frame.create_button(
            "but_export_current",
            "Export current node results",
            enabled=False,
            icon="qt-std::SP_FileIcon",
            parent_widget="config",
            toolTip=(
                "Export the current node's results to file. Note that "
                "the filenames are pre-determined based on node ID "
                "and node label."
            ),
        )
        frame.create_button(
            "but_export_all",
            "Export all results",
            enabled=False,
            icon="qt-std::SP_DialogSaveButton",
            parent_widget="config",
            tooltip=("Export all results. Note that the directory must be empty."),
        )
        frame.create_spacer(
            "config_terminal_spacer",
            parent_widget="config",
        )
        frame.create_spacer("menu_bottom_spacer")

        frame.create_any_widget(
            "plot", PydidasPlotStack, gridPos=(0, 1, 3, 1), use_data_info_action=True
        )
