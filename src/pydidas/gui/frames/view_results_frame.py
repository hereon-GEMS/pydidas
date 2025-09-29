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

import os
from typing import Any

from qtpy import QtCore

from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.scan import Scan
from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.gui.frames.builders.view_results_frame_builder import (
    VIEW_RESULTS_MIXIN_BUILD_CONFIG,
)
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.data_viewer import DataViewer
from pydidas.widgets.dialogues import critical_warning
from pydidas.widgets.framework import BaseFrame, BaseFrameWithApp
from pydidas.widgets.windows import ShowInformationForResult
from pydidas.workflow import (
    ProcessingResults,
    ProcessingTree,
    result_io,
)


SAVER = result_io.ProcessingResultIoMeta


class ViewResultsFrame(BaseFrameWithApp):
    """
    The ViewResultsFrame is used to import and visualize the pydidas ProcessingResults.
    """

    menu_icon = "pydidas::frame_icon_workflow_results"
    menu_title = "Import and display workflow results"
    menu_entry = "Workflow processing/View workflow results"
    params_not_to_restore = ["use_scan_timeline"]
    default_params = get_generic_param_collection(
        "saving_format",
        "squeeze_empty_dims",
        "enable_overwrite",
        "use_scan_timeline",
    )

    def __init__(self, **kwargs: Any):
        self._SCAN = kwargs.get("scan", Scan())
        self._TREE = kwargs.get("processing_tree", ProcessingTree())
        self._EXP = kwargs.get("diffraction_exp", DiffractionExperiment())
        BaseFrameWithApp.__init__(self, **kwargs)
        self._RESULTS = kwargs.get("workflow_results", ProcessingResults())
        self._active_node_id = -1
        self._result_window = None
        self.__export_dialog = PydidasFileDialog()
        self._config["enable_export"] = kwargs.get("enable_export", False)
        self._config["enable_import"] = kwargs.get("enable_import", True)
        self._config["enable_app"] = kwargs.get("enable_app", False)
        self._config["export_available"] = False
        self.set_default_params()

    def build_frame(self):
        """
        Build the frame and populate it with widgets.
        """
        for _method, _args, _kwargs in VIEW_RESULTS_MIXIN_BUILD_CONFIG:
            if _args == ("config_export_spacer",):
                self._widgets["config"].layout().setRowStretch(
                    self._widgets["config"].layout().rowCount(), 1
                )
            _method = getattr(self, _method)
            _method(*_args, **_kwargs)
        self.create_any_widget(
            "data_viewer",
            DataViewer,
            plot2d_diffraction_exp=self._EXP,
            plot2d_use_data_info_action=True,
            gridPos=(1, 1, 2, 1),
        )
        self.layout().setRowStretch(self.layout().rowCount() - 1, 1)  # noqa
        if self._config["enable_import"]:
            self.__import_dialog = PydidasFileDialog()
        self._widgets["import_container"].setVisible(self._config["enable_import"])
        self._widgets["export_container"].setVisible(self._config["enable_export"])
        self._widgets["run_app_container"].setVisible(self._config["enable_app"])

    def connect_signals(self):
        self._widgets["but_load"].clicked.connect(self.import_data_to_workflow_results)
        self._widgets["data_viewer"].sig_plot2d_get_more_info_for_data.connect(
            self._show_info_popup
        )
        self._widgets["result_table"].sig_node_selected.connect(self._selected_new_node)
        self._widgets["radio_arrangement"].new_button_index.connect(
            self._arrange_results_in_timeline_or_scan_shape
        )
        self._widgets["but_export_current"].clicked.connect(self._export_current)
        self._widgets["but_export_all"].clicked.connect(self._export_all)

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
            self._RESULTS.import_data_from_directory(_dir)  # noqa W0212
            self._RESULTS._TREE.root.plugin._SCAN = self._RESULTS._SCAN  # noqa W0212
            self._RESULTS._TREE.root.plugin.update_filename_string()  # noqa W0212
            self.update_choices_of_selected_results()

    def update_choices_of_selected_results(self):
        """
        Update the choices of the selected results.
        """
        _should_be_visible = len(self._RESULTS.result_titles) > 0
        self._widgets["label_select_header"].setVisible(_should_be_visible)
        self._widgets["result_table"].setVisible(_should_be_visible)
        self._widgets["result_table"].update_choices_from_workflow_results(
            self._RESULTS
        )

    def update_export_setting_visibility(self):
        """
        Update the enabled state of the export buttons based on available results.
        """
        _active = self._RESULTS.shapes != {}
        self._widgets["but_export_all"].setEnabled(_active)
        self._widgets["export_container"].setVisible(_active)

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
        self._widgets["but_export_current"].setEnabled(
            node_id != -1 and self._config["export_available"]
        )
        if node_id == -1:
            return
        self.set_displayed_data()

    @QtCore.Slot(int)
    def _arrange_results_in_timeline_or_scan_shape(self, index: int):
        """
        Arrange the results in the timeline or scan shape.
        """
        self.set_param_value("use_scan_timeline", index == 1)
        self.set_displayed_data()

    def set_displayed_data(self, update: bool = False):
        """
        Set the data to display.

        Parameters
        ----------
        update : bool
            Flag to update the data without updating the DataViewer metadata.
            The default is False.
        """
        if self._active_node_id == -1:
            return
        if self.get_param_value("use_scan_timeline"):
            self._data = self._RESULTS.get_results_for_flattened_scan(
                self._active_node_id, squeeze=True
            )
        else:
            self._data = self._RESULTS.get_results(self._active_node_id).squeeze()
        self._widgets["result_info"].setText(
            self._RESULTS.get_node_result_metadata_string(
                self._active_node_id, self.get_param_value("use_scan_timeline")
            )
        )
        _title = self._RESULTS.result_titles[self._active_node_id]
        if update and self._widgets["data_viewer"].data_is_set:
            self._widgets["data_viewer"].update_data(self._data, title=_title)
        else:
            self._widgets["data_viewer"].set_data(self._data, title=_title)

    def update_displayed_data(self):
        """Update the data to display"""
        self.set_displayed_data(update=True)

    @QtCore.Slot(float, float)
    def _show_info_popup(self, data_x: float, data_y: float):
        """Show the information popup."""
        if self._active_node_id == -1:
            raise UserConfigError(
                "No node has been selected. Please check the result selection"
            )
        _loader_plugin = self._RESULTS.frozen_tree.root.plugin.copy()
        _loader_plugin._SCAN = self._RESULTS.frozen_scan
        if _loader_plugin.filename_string == "":
            # if the result has been imported from disk, set the local
            # images_per_file parameter to the counted value in case the file
            # is not available under the stored path.
            if (
                _loader_plugin.get_param_value("images_per_file") == -1
                and _loader_plugin.get_param_value("_counted_images_per_file") > 0
            ):
                _loader_plugin.set_param_value(
                    "images_per_file",
                    _loader_plugin.get_param_value("_counted_images_per_file"),
                )
            _loader_plugin.pre_execute()
        _timeline = self.get_param_value("use_scan_timeline")
        if self._result_window is None:
            self._result_window = ShowInformationForResult()
        self._result_window.display_information(
            (data_y, data_x),
            self._widgets["data_viewer"].active_dims,
            self._widgets["data_viewer"].current_selected_indices,
            self._data.property_dict,
            _loader_plugin,
            use_timeline=self.get_param_value("use_scan_timeline"),
        )

    @QtCore.Slot()
    def _export_current(self):
        """
        Export the current node's data to a WorkflowResults saver.
        """
        if self._active_node_id == -1:
            critical_warning(
                "No node selected",
                "No node has been selected. Please select a node and try again.",
            )
            return
        self._export(self._active_node_id)

    @QtCore.Slot()
    def _export_all(self):
        """
        Export all datasets to a WorkflowResults saver.
        """
        self._export(None)

    def _export(self, node: int | None = None):
        """
        Export data of the specified node.

        If no node is chosen (i.e. None), all nodes will be exported.

        Parameters
        ----------
        node : int | None
            The single node to be exported. If None, all nodes will be
            exported. The default is None.
        """
        _formats = self.get_param_value("saving_format")
        if _formats is None:
            critical_warning(
                "No format selected",
                (
                    "No saving format node has been selected. "
                    "Please select a format and try again."
                ),
            )
            return
        _squeeze_flag = self.get_param_value("squeeze_empty_dims")
        _overwrite = self.get_param_value("enable_overwrite")
        while True:
            _dir_name = self.__export_dialog.get_existing_directory(
                caption="Export results",
                qsettings_ref="WorkflowResults__export",
                info_string=(
                    "<b>Please select an empty an empty directory to export all "
                    "results<br> or enable overwriting of results:</b>"
                ),
            )
            if _dir_name is None or len(os.listdir(_dir_name)) == 0 or _overwrite:
                break
            critical_warning(
                "Directory not empty",
                "The selected directory is not empty. Please "
                "select an empty directory or cancel.",
            )
        if _dir_name is None:
            return
        self._RESULTS.save_results_to_disk(
            _dir_name,
            _formats,
            overwrite=_overwrite,
            node_id=node,
            squeeze_results=_squeeze_flag,
        )
