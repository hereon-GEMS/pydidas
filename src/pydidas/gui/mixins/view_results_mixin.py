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

from pydidas.core import UserConfigError
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

    # def _verify_result_shapes_uptodate(self):
    #     """
    #     Verify the consistency of the underlying information.
    #
    #     The information for the WorkflowResults is defined by the Singletons
    #     (i.e. the ScanContext and WorkflowTree) and must be checked to detect
    #     any changes.
    #     """
    #     _hash = self._RESULTS.source_hash
    #     if _hash != self._config["source_hash"]:
    #         self._config["source_hash"] = self._RESULTS.source_hash
    #         self._clear_selected_results_entries()
    #         self._clear_plot()
    #         self.update_choices_of_selected_results()
    #
    # def _clear_selected_results_entries(self):
    #     """
    #     Clear the selection of the results and reset the view.
    #
    #     This method will hide the data selection widgets.
    #     """
    #     self.set_param_value("selected_results", "No selection")
    #     self.params["selected_results"].choices = ["No selection"]
    #     self._widgets["result_selector"].reset()
    #
    # def _clear_plot(self):
    #     """
    #     Clear all curves / images from the plot and disable any new updates.
    #     """
    #     self._config["plot_active"] = False
    #     self._widgets["plot"].clear_plots()
    #
    # @QtCore.Slot(bool, object, int, object, str)
    # def update_result_selection(
    #     self,
    #     use_timeline: bool,
    #     active_plot_dims: list,
    #     node_id: int,
    #     slices: tuple,
    #     plot_type: str,
    # ):
    #     """
    #     Update the selection of results to show in the plot.
    #
    #     Parameters
    #     ----------
    #     use_timeline : bool
    #         Flag whether to use a timeline and collapse all scan dimensions
    #         or not.
    #     active_plot_dims : list
    #         The dimensions of the plot results.
    #     node_id : int
    #         The result node ID.
    #     slices : tuple
    #         The tuple with the slices which select the data for plotting.
    #     plot_type : str
    #         The type of plot to be shown.
    #     """
    #     self._config["plot_active"] = True
    #     self._config["data_use_timeline"] = use_timeline
    #     self._config["active_dims"] = active_plot_dims
    #     self._config["active_node"] = node_id
    #     self._config["data_slices"] = slices
    #     self._config["plot_type"] = plot_type
    #     _datalength = np.asarray([_n.size for _n in slices])
    #     self._config["local_dims"] = {
    #         _val: _index for _index, _val in enumerate(np.where(_datalength > 1)[0])
    #     }
    #     self.update_plot()
    #
    # def update_plot(self):
    #     """
    #     Update the plot.
    #
    #     This method will get the latest result (subset) from the
    #     WorkflowResults and update the plot.
    #     """
    #     if not self._config["plot_active"]:
    #         return
    #     _node = self._config["active_node"]
    #     _data = self._RESULTS.get_result_subset(
    #         _node,
    #         *self._config["data_slices"],
    #         flattened_scan_dim=self._config["data_use_timeline"],
    #         squeeze=True,
    #     )
    #     if self._config["plot_type"] == "group of 1D plots":
    #         self._plot_group_of_curves(_data)
    #     elif self._config["plot_type"] == "1D plot":
    #         self._plot1d(_data, replace=True)
    #     elif self._config["plot_type"] in ["2D full axes", "2D data subset"]:
    #         self._plot_2d(_data)
    #
    # def _plot_group_of_curves(self, data: Dataset):
    #     """
    #     Plot a group of 1D curves.
    #
    #     Parameters
    #     ----------
    #     data : pydidas.core.Dataset
    #         The dataset with the data to be plotted.
    #     """
    #
    #     def _legend(i):
    #         return (
    #             data.axis_labels[0]
    #             + f"= {data.axis_ranges[0][i]:.4f}"
    #             + data.axis_units[0]
    #         )
    #
    #     _active_dim = self._config["active_dims"][0]
    #     _local_dim = self._config["local_dims"][_active_dim]
    #     if _local_dim == 0:
    #         data = data.transpose()
    #     self._plot1d(data[0], replace=True, legend=_legend(0))
    #     for _index in range(1, data.shape[0]):
    #         self._plot1d(data[_index], replace=False, legend=_legend(_index))
    #
    # def _plot1d(
    #     self, data: Dataset, replace: bool = True, legend: Union[None, str] = None
    # ):
    #     """
    #     Plot a 1D-dataset in the 1D plot widget.
    #
    #     Parameters
    #     ----------
    #     data : pydidas.core.Dataset
    #         The data object.
    #     replace : bool, optional
    #         Keyword to toggle replacing the currently plotted lines or keep
    #         them and only add the new line. The default is True.
    #     legend : Union[None, str], optional
    #         If desired, a legend entry for this curve. If None, no legend
    #         entry will be added. The default is None.
    #     """
    #     if data.ndim != 1:
    #         raise UserConfigError(
    #             "The selected data is not one-dimensional. Cannot create a line plot."
    #         )
    #     if not isinstance(data.axis_ranges[0], np.ndarray):
    #         data.update_axis_range(0, np.arange(data.size))
    #     self._widgets["plot"].plot_data(
    #         data,
    #         replace=replace,
    #         legend=legend,
    #         title=self._RESULTS.result_titles[self._config["active_node"]],
    #     )
    #
    # def _plot_2d(self, data: Dataset):
    #     """
    #     Plot a 2D dataset as an image.
    #
    #     Parameters
    #     ----------
    #     data : pydidas.core.Dataset
    #         The data.
    #     """
    #     for _dim in [0, 1]:
    #         if not isinstance(data.axis_ranges[_dim], np.ndarray):
    #             data.update_axis_range(_dim, np.arange(data.shape[_dim]))
    #     _dim0, _dim1 = self._config["active_dims"]
    #     if _dim0 > _dim1:
    #         data = data.transpose()
    #     self._widgets["plot"].plot_data(
    #         data, title=self._RESULTS.result_titles[self._config["active_node"]]
    #     )

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
        self._widgets["data_viewer"].set_data(self._data)

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
