# This file is part of pydidas.
#
# Copyright 2022 - 2025, Helmholtz-Zentrum Hereon
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
Module with the ViewResultsMixin which allows other classes to implement viewing of
WorkflowTree results when running the pydidas WorkflowTree.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2022 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_ViewResultsMixin_build_config", "ViewResultsMixin"]


import os

from qtpy import QtCore

from pydidas.core import (
    ParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import FONT_METRIC_CONFIG_WIDTH, POLICY_FIX_EXP
from pydidas.widgets import PydidasFileDialog, ScrollArea
from pydidas.widgets.data_viewer import DataViewer, TableWithResultDatasets
from pydidas.widgets.dialogues import critical_warning
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.misc import ReadOnlyTextWidget
from pydidas.widgets.windows import ShowInformationForResult
from pydidas.workflow import WorkflowResults


def get_ViewResultsMixin_build_config(
    frame: BaseFrame,
) -> list[list[str, tuple[str], dict]]:
    """
    Return the build configuration for the ViewResultsFrame.

    Parameters
    ----------
    frame : BaseFrame
        The ViewResultsFrame instance.

    Returns
    -------
    list[list[str, tuple[str], dict]]
        The build configuration in form of a list. Each list entry consists of the
        widget creation method name, the method arguments and the method keywords.
    """
    return [
        [
            "create_empty_widget",
            ("config",),
            {
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
                "parent_widget": None,
                "sizePolicy": POLICY_FIX_EXP,
            },
        ],
        [
            "create_any_widget",
            ("config_area", ScrollArea),
            {
                "sizePolicy": POLICY_FIX_EXP,
            },
        ],
        [
            "create_spacer",
            ("title_spacer",),
            {"fixedHeight": 15, "parent_widget": "config"},
        ],
        [
            "create_label",
            ("label_select_header", "Select results to display:"),
            {
                "bold": True,
                "fontsize_offset": 1,
                "parent_widget": "config",
                "visible": False,
            },
        ],
        [
            "create_any_widget",
            ("result_table", TableWithResultDatasets),
            {"parent_widget": "config", "visible": False},
        ],
        [
            "create_spacer",
            ("arrangement_spacer",),
            {"fixedHeight": 15, "parent_widget": "config"},
        ],
        [
            "create_radio_button_group",
            ("radio_arrangement", ["by scan shape", "as a timeline"]),
            {
                "title": "Arrangement of results:",
                "parent_widget": "config",
                "vertical": False,
                "visible": False,
            },
        ],
        [
            "create_spacer",
            ("info_spacer",),
            {"fixedHeight": 15, "parent_widget": "config"},
        ],
        [
            "create_label",
            ("label_details", "Detailed result information:"),
            {
                "bold": True,
                "fontsize_offset": 1,
                "parent_widget": "config",
                "visible": False,
            },
        ],
        [
            "create_any_widget",
            ("result_info", ReadOnlyTextWidget),
            {
                "alignment": QtCore.Qt.AlignTop,
                "font_metric_height_factor": 25,
                "font_metric_width_factor": FONT_METRIC_CONFIG_WIDTH,
                "parent_widget": "config",
                "visible": False,
            },
        ],
        [
            "create_spacer",
            ("config_export_spacer",),
            {"parent_widget": "config"},
        ],
        [
            "create_param_widget",
            (frame.get_param("saving_format"),),
            {"parent_widget": "config", "visible": False},
        ],
        [
            "create_param_widget",
            (frame.get_param("enable_overwrite"),),
            {"parent_widget": "config", "visible": False},
        ],
        [
            "create_button",
            ("but_export_current", "Export current node results"),
            {
                "enabled": False,
                "icon": "qt-std::SP_FileIcon",
                "parent_widget": "config",
                "toolTip": (
                    "Export the current node's results to file. Note that the "
                    "filenames are pre-determined based on node ID and node label."
                ),
                "visible": False,
            },
        ],
        [
            "create_button",
            ("but_export_all", "Export all results"),
            {
                "enabled": False,
                "icon": "qt-std::SP_DialogSaveButton",
                "parent_widget": "config",
                "tooltip": "Export all results. Note that the directory must be empty.",
                "visible": False,
            },
        ],
        [
            "create_any_widget",
            ("data_viewer", DataViewer),
            {
                "plot2d_diffraction_exp": frame._EXP,
                "plot2d_use_data_info_action": True,
                "gridPos": (0, 1, frame.layout().rowCount(), 1),
                "visible": False,
            },
        ],
    ]


class ViewResultsMixin:
    """
    The ViewResultsMixin adds functionality to show and export results.

    It requires specific widgets which can be added to Frame by using the
    `get_ViewResultsMixin_build_config` function.
    """

    def __init__(self, **kwargs: dict):
        _results = kwargs.get("workflow_results", None)
        self._RESULTS = _results if _results is not None else WorkflowResults()
        self._active_node_id = -1
        self._result_window = None
        self.__export_dialog = PydidasFileDialog()
        self.params_not_to_restore = self.params_not_to_restore + ["use_scan_timeline"]
        self.default_params = ParameterCollection(
            self.default_params,
            get_generic_param_collection(
                "saving_format", "enable_overwrite", "use_scan_timeline"
            ),
        )

    def build_view_results_mixin(self):
        """Build the widgets required for the ViewResultsMixin functionality."""
        for _method, _args, _kwargs in get_ViewResultsMixin_build_config(self):
            if _args == ("config_area", ScrollArea):
                _kwargs["widget"] = self._widgets["config"]
            if _args == ("config_export_spacer",):
                self._widgets["config"].layout().setRowStretch(
                    self._widgets["config"].layout().rowCount(), 1
                )
            if _args == ("data_viewer", DataViewer):
                _kwargs["gridPos"] = (0, 1, self.layout().rowCount(), 1)
            _method = getattr(self, _method)
            _method(*_args, **_kwargs)
        self.layout().setRowStretch(self.layout().rowCount() - 1, 1)

    def connect_view_results_mixin_signals(self):
        """Connect all required Qt slots and signals."""
        self._widgets["data_viewer"].sig_plot2d_get_more_info_for_data.connect(
            self._show_info_popup
        )
        self._widgets["result_table"].sig_new_selection.connect(self._selected_new_node)
        self._widgets["radio_arrangement"].new_button_index.connect(
            self._arrange_results_in_timeline_or_scan_shape
        )
        self._widgets["but_export_current"].clicked.connect(self._export_current)
        self._widgets["but_export_all"].clicked.connect(self._export_all)

    def update_choices_of_selected_results(self):
        """
        Update the choices of the selected results.
        """
        self._widgets["label_select_header"].setVisible(True)
        self._widgets["result_table"].setVisible(True)
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
                self._active_node_id
            )
        else:
            self._data = self._RESULTS.get_results(self._active_node_id)
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
        _overwrite = self.get_param_value("enable_overwrite")
        while True:
            _dirname = self.__export_dialog.get_existing_directory(
                caption="Export results",
                qsettings_ref="WorkflowResults__export",
                info_string=(
                    "<b>Please select an empty an empty directory to export all "
                    "results<br> or enable overwriting of results:</b>"
                ),
            )
            if _dirname is None or len(os.listdir(_dirname)) == 0 or _overwrite:
                break
            critical_warning(
                "Directory not empty",
                "The selected directory is not empty. Please "
                "select an empty directory or cancel.",
            )
        if _dirname is None:
            return
        self._RESULTS.save_results_to_disk(
            _dirname, _formats, overwrite=_overwrite, node_id=node
        )
