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
Module with the ViewResultsFrameBuilder class which is used to
populate the ViewResultsFrame with widgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ViewResultsFrameBuilder"]


from ....core.constants import FONT_METRIC_CONFIG_WIDTH, POLICY_FIX_EXP
from ....widgets import ScrollArea
from ....widgets.framework import BaseFrame
from ....widgets.selection import ResultSelectionWidget
from ....widgets.silx_plot import PydidasPlotStack


class ViewResultsFrameBuilder:
    """
    The ViewResultsFrameBuilder allows to populate a ViewResultsFrame with widgets.
    """

    @classmethod
    def build_frame(cls, frame: BaseFrame):
        """
        Build the frame and create all widgets.

        Parameters
        ----------
        frame : BaseFrame
            The ViewResultsFrame instance.
        """
        frame.create_label(
            "title",
            "View results",
            bold=True,
            fontsize_offset=4,
            gridPos=(0, 0, 1, 2),
        )
        frame.create_spacer("title_spacer", fixedHeight=15)
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
        frame.create_button(
            "but_load",
            "Import results from directory",
            icon="qt-std::SP_DialogOpenButton",
            parent_widget="config",
        )
        frame.create_any_widget(
            "result_selector",
            ResultSelectionWidget,
            parent_widget="config",
            select_results_param=frame.get_param("selected_results"),
            workflow_results=frame._RESULTS,
        )
        # frame.create_line("line_export", parent_widget="config")
        frame.create_param_widget(
            frame.get_param("saving_format"),
            parent_widget="config",
            visible=False,
        )
        frame.create_param_widget(
            frame.get_param("enable_overwrite"),
            parent_widget="config",
            visible=False,
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
            visible=False,
        )
        frame.create_button(
            "but_export_all",
            "Export all results",
            enabled=False,
            icon="qt-std::SP_DialogSaveButton",
            parent_widget="config",
            tooltip="Export all results. Note that the directory must be empty.",
            visible=False,
        )
        frame.create_spacer(
            "config_terminal_spacer",
            fixedHeight=20,
            parent_widget="config",
        )
        frame.create_spacer("menu_bottom_spacer")
        frame.create_any_widget(
            "plot",
            PydidasPlotStack,
            diffraction_exp=frame._EXP,
            gridPos=(0, 1, 3, 1),
            use_data_info_action=True,
        )
