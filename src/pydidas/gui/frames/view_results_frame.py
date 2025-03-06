# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the ViewResultsFrame which allows to visualize results from
running the pydidas WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ViewResultsFrame"]


from typing import Self

from qtpy import QtCore

from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.gui.frames.builders.view_results_frame_builder import (
    get_ViewResultsFrame_build_config,
)
from pydidas.widgets import PydidasFileDialog, ScrollArea
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.windows import ShowInformationForResult
from pydidas.workflow import ProcessingResults, ProcessingTree, result_io


SAVER = result_io.ProcessingResultIoMeta


class ViewResultsFrame(BaseFrame):
    """
    The ViewResultsFrame is used to import and visualize the pydidas ProcessingResults.
    """

    menu_icon = "pydidas::frame_icon_workflow_results"
    menu_title = "Import and display workflow results"
    menu_entry = "Workflow processing/View workflow results"

    default_params = get_generic_param_collection(
        "selected_results", "saving_format", "enable_overwrite", "use_scan_timeline"
    )
    params_not_to_restore = ["selected_results"]

    def __init__(self, **kwargs: dict) -> Self:
        self._SCAN = Scan()
        self._TREE = ProcessingTree()
        self._EXP = DiffractionExperiment()
        self._RESULTS = ProcessingResults(
            diffraction_exp_context=self._EXP,
            scan_context=self._SCAN,
            workflow_tree=self._TREE,
        )
        BaseFrame.__init__(self, **kwargs)
        self.set_default_params()
        self.__import_dialog = PydidasFileDialog()
        self._active_node_id = -1
        self.__result_window = None

    def build_frame(self):
        """
        Build the frame and populate it with widgets.
        """
        for _method, _args, _kwargs in get_ViewResultsFrame_build_config(self):
            if _args == ("config_area", ScrollArea):
                _kwargs["widget"] = self._widgets["config"]
            if _args == ("config_export_spacer",):
                self._widgets["config"].layout().setRowStretch(
                    self._widgets["config"].layout().rowCount(), 1
                )
            _method = getattr(self, _method)
            _method(*_args, **_kwargs)

    def connect_signals(self):
        self._widgets["but_load"].clicked.connect(self.import_data_to_workflow_results)
        self._widgets["data_viewer"].sig_plot2d_get_more_info_for_data.connect(
            self._show_info_popup
        )
        self._widgets["result_table"].sig_new_selection.connect(self._selected_new_node)
        self._widgets["radio_arrangement"].new_button_index.connect(
            self._arrange_results_in_timeline_or_scan_shape
        )

    @QtCore.Slot(int)
    def frame_activated(self, index: int):
        """
        Received a signal that a new frame has been selected.

        This method checks whether the selected frame is the current class
        and if yes, it will call some updates.

        Parameters
        ----------
        index : int
            The index of the newly activated frame.
        """
        BaseFrame.frame_activated(self, index)
        self._config["frame_active"] = index == self.frame_index

    def import_data_to_workflow_results(self):
        """
        Import data to the workflow results.
        """
        _dir = self.__import_dialog.get_existing_directory(
            caption="Workflow results directory",
            qsettings_ref="WorkflowResults__import",
        )
        if _dir is not None:
            self._RESULTS.import_data_from_directory(_dir)
            self._RESULTS._TREE.root.plugin._SCAN = self._RESULTS._SCAN
            self._RESULTS._TREE.root.plugin.update_filename_string()
            self.update_choices_of_selected_results()
            self.update_export_button_activation()

    @QtCore.Slot(float, float)
    def show_info_popup(self, data_x: float, data_y: float):
        """
        Open a pop-up to show more information for the selected datapoint.

        Parameters
        ----------
        data_x : float
            The data x value.
        data_y : float
            the data y value.
        """

    def update_choices_of_selected_results(self):
        """
        Update the choices of the selected results.
        """
        self._widgets["label_select_header"].setVisible(True)
        self._widgets["result_table"].update_choices_from_workflow_results(
            self._RESULTS
        )

    def update_export_button_activation(self):
        """
        Update the enabled state of the export buttons based on available results.
        """
        _active = self._RESULTS.shapes != {}
        self._widgets["but_export_all"].setEnabled(_active)
        for _key in ["saving_format", "enable_overwrite"]:
            self.param_widgets[_key].setVisible(_active)
        for _key in ["but_export_current", "but_export_all"]:
            self._widgets[_key].setVisible(_active)

    @QtCore.Slot(int)
    def _selected_new_node(self, node_id: int):
        """
        Received a new selection of a node.
        """
        self._active_node_id = node_id
        for _key in [
            "radio_arrangement",
            "result_info",
            "data_viewer",
            "label_details",
        ]:
            self._widgets[_key].setVisible(node_id != -1)
        self._widgets["but_export_current"].setEnabled(node_id != -1)
        if node_id == -1:
            return
        self._update_data()

    @QtCore.Slot(int)
    def _arrange_results_in_timeline_or_scan_shape(self, index: int):
        """
        Arrange the results in the timeline or scan shape.
        """
        self.set_param_value("use_scan_timeline", index == 1)
        self._update_data()

    def _update_data(self):
        """Update the data to display."""
        if self.get_param_value("use_scan_timeline"):
            self._data = self._RESULTS.get_results_for_flattened_scan(
                self._active_node_id
            )
        else:
            self._data = self._RESULTS.get_results(self._active_node_id)
        self._widgets["result_info"].setText(
            self._RESULTS.get_node_result_metadata_string(
                self._active_node_id, self.get_param_value("use_scan_timeline")
            )
        )
        self._widgets["data_viewer"].set_data(self._data)

    @QtCore.Slot(float, float)
    def _show_info_popup(self, data_x: float, data_y: float):
        """Show the information popup."""
        print("show info popup for ", data_x, data_y)
        if self._active_node_id == -1:
            raise UserConfigError(
                "No node has been selected. Please check the result selection"
            )

        _loader_plugin = self._RESULTS.frozen_tree.root.plugin.copy()
        _loader_plugin._SCAN = self._RESULTS.frozen_scan
        if _loader_plugin.filename_string == "":
            _loader_plugin.pre_execute()
        _timeline = self.get_param_value("use_scan_timeline")
        if self.__result_window is None:
            self.__result_window = ShowInformationForResult()
        self.__result_window.display_information(
            (data_y, data_x),
            self._widgets["data_viewer"].active_dims,
            self._widgets["data_viewer"].current_selected_indices,
            self._data.property_dict,
            _loader_plugin,
            use_timeline=self.get_param_value("use_scan_timeline"),
        )
