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
Module with the WorkflowTestFrame which allows to test the processing
workflow on a single data frame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowTestFrame"]


import copy

from qtpy import QtCore

from pydidas.contexts import DiffractionExperimentContext, ScanContext
from pydidas.core import (
    Dataset,
    Parameter,
    ParameterCollection,
    UserConfigError,
    get_generic_param_collection,
    utils,
)
from pydidas.core.utils import apply_qt_properties
from pydidas.gui.frames.builders import get_WorkflowTestFrame_build_config
from pydidas.widgets.dialogues import WarningBox
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.windows import (
    ShowDetailedPluginResultsWindow,
    TweakPluginParameterWindow,
)
from pydidas.workflow import WorkflowNode, WorkflowTree


SCAN = ScanContext()
TREE = WorkflowTree()
EXP = DiffractionExperimentContext()


IMAGE_SELECTION_PARAM = Parameter(
    "image_selection",
    str,
    "Use global index",
    name="Scan point selection",
    choices=[
        "Use global index",
        "Use scan dimensional indices",
        "Use detector image number",
    ],
    tooltip=(
        "Choose between selecting frames using either the global index for the "
        "flattened image / frame index (the 'timeline'), the multi-dimensional "
        "position in the scan or the detector image number."
    ),
)


def _create_str_description_of_node_result(
    node: WorkflowNode, plugin_results: Dataset
) -> str:
    """
    Create a string description of the node results with all axes and data units
    and metadata for the node.

    Parameters
    ----------
    node : pydidas.workflow.WorkflowNode
        The WorkflowNode which created the results.
    plugin_results : pydidas.core.Dataset
        The resulting Dataset.
    config : dict
        The

    Returns
    -------
    str
        The string description of the nodes result.s
    """
    _meta = {
        "axis_labels": plugin_results.axis_labels,
        "axis_units": plugin_results.axis_units,
        "axis_ranges": plugin_results.axis_ranges,
        "metadata": plugin_results.metadata,
    }
    _ax_units = {
        _dim: (_ax_unit if _ax_unit is not None else "")
        for _dim, _ax_unit in _meta["axis_units"].items()
    }
    _ax_ranges = {
        _key: utils.get_range_as_formatted_string(_range)
        for _key, _range in _meta["axis_ranges"].items()
    }
    _ax_points = dict(enumerate(plugin_results.shape))
    _values = utils.get_simplified_array_representation(plugin_results)
    _data_label = node.plugin.output_data_label + (
        f" / {node.plugin.output_data_unit}"
        if len(node.plugin.output_data_unit) > 0
        else ""
    )
    _str = (
        node.plugin.plugin_name
        + ":\n\n"
        + f"Data: {_data_label}\n\n"
        + "\n\n".join(
            (
                f"Axis #{_axis:02d}:\n"
                f"  Label: {_meta['axis_labels'][_axis]}\n"
                f"  N points: {_ax_points[_axis]}\n"
                f"  Range: {_ax_ranges[_axis]} {_ax_units[_axis]}"
            )
            for _axis in _meta["axis_labels"]
        )
    )
    _str += f"\n\nValues:\n{_values}"
    _str += f"\n\nMetadata:\n{_meta['metadata']}"
    _str += f"\n\nPlugin runtime: {node.runtime:.4f} s"
    return _str


class _ResultsMock:
    def __init__(self):
        self.result_titles = {}


class WorkflowTestFrame(BaseFrame):
    """
    The ProcessingSinglePluginFrame allows to run / test single plugins on a
    single datapoint.

    The selection of a frame can be done either using the absolute frame number
    (if the ``image_selection`` Parameter equals "Use global index") or by
    supplying scan indices for all active scan dimensions (if the
    ``image_selection`` Parameter equals "Use scan indices").
    """

    menu_icon = "pydidas::frame_icon_workflow_test"
    menu_title = "Test workflow"
    menu_entry = "Workflow processing/Test workflow"

    default_params = ParameterCollection(
        IMAGE_SELECTION_PARAM.copy(),
        get_generic_param_collection(
            "frame_index",
            "scan_index0",
            "scan_index1",
            "scan_index2",
            "scan_index3",
            "detector_image_index",
        ),
    )

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self.set_default_params()
        self._tree = None
        self._active_node = -1
        self._results = {}
        self._local_results_mock = _ResultsMock()
        self._config.update(
            {
                "shapes": {},
                "labels": {},
                "data_labels": {},
                "plot_active": False,
                "plot_dim": 1,
                "details_active": False,
                "exp_hash": -1,
                "context_hash": -1,
                "has_details": False,
            }
        )

    def build_frame(self):
        """
        Build the frame and create all necessary widgets.
        """
        for _method, _args, _kwargs in get_WorkflowTestFrame_build_config(self):
            if _args == ("config_terminal_spacer",):
                _nrow = self._widgets["config"].layout().rowCount()
                self._widgets["config"].layout().setRowStretch(_nrow, 10)
            _method = getattr(self, _method)
            _method(*_args, **_kwargs)
        self._widgets["config_area"].setWidget(self._widgets["config"])

        apply_qt_properties(self.layout(), columnStretch=((1, 10)))

    def connect_signals(self):
        """
        Connect all required signals and slots.
        """
        self.param_widgets["image_selection"].io_edited.connect(
            self.__update_image_selection_visibility
        )
        self._widgets["result_table"].sig_new_selection.connect(self._selected_new_node)
        self._widgets["but_exec"].clicked.connect(self.execute_workflow_test)
        self._widgets["but_reload_tree"].clicked.connect(self.reload_workflow)
        self._widgets["but_show_details"].clicked.connect(self.show_plugin_details)
        self._widgets["but_tweak_params"].clicked.connect(self.show_tweak_params_window)

    def finalize_ui(self):
        """
        Check the local WorkflowTree is up to date and create the window to show the
        plugin results.
        """
        self.__check_tree_uptodate()
        self.__details_window = ShowDetailedPluginResultsWindow()
        self.__tweak_window = TweakPluginParameterWindow()
        self.__tweak_window.sig_new_params.connect(self.__updated_plugin_params)
        self.__details_window.sig_minimized.connect(self.__details_hidden)

    def __check_tree_uptodate(self):
        """
        Check if the WorkflowTree has changed and update the local Tree if
        it has changed.
        """
        if self._config["context_hash"] != hash((hash(SCAN), hash(TREE), hash(EXP))):
            self._config["context_hash"] = hash((hash(SCAN), hash(TREE), hash(EXP)))
            self.reload_workflow()

    @QtCore.Slot()
    def __details_hidden(self):
        """
        Set the flag to hide the details window.
        """
        self._config["details_active"] = False

    @QtCore.Slot(int)
    def __updated_plugin_params(self, node_id: int):
        """
        Run the subtree with the new Parameters.

        Parameters
        ----------
        node_id : int
            The node ID with the changed Parameters.
        """
        TREE.nodes[node_id].plugin.params = copy.deepcopy(
            self._tree.nodes[node_id].plugin.params
        )

        _arg = copy.copy(self._tree.nodes[node_id].plugin._config["input_data"])
        _kwargs = self._tree.nodes[node_id].plugin._config["input_kwargs"].copy() | {
            "force_store_results": True,
            "store_input_data": True,
        }
        with utils.ShowBusyMouse():
            self._tree.nodes[node_id].prepare_execution()
            self._tree.nodes[node_id].execute_plugin_chain(_arg, **_kwargs)
            self.__store_tree_results()
            self.__update_selection_choices()
            if self._active_node != -1:
                self.__update_text_description_of_node_results()
                self.__plot_results()
            self._config["context_hash"] = hash((hash(SCAN), hash(TREE), hash(EXP)))

    @QtCore.Slot()
    def __update_image_selection_visibility(self):
        """
        Update the visibility of the image selection widgets.
        """
        _selection = self.get_param_value("image_selection")
        self.toggle_param_widget_visibility(
            "frame_index", _selection == "Use global index"
        )
        _use_scan_dim = _selection == "Use scan dimensional indices"
        for _dim in range(4):
            self.toggle_param_widget_visibility(
                f"scan_index{_dim}", _use_scan_dim and _dim < SCAN.ndim
            )
        self.toggle_param_widget_visibility(
            "detector_image_index", _selection == "Use detector image number"
        )

    @QtCore.Slot()
    def execute_workflow_test(self):
        """
        Test the Workflow on the selected frame and store results for presentation.
        """
        if not self._check_tree_is_populated():
            return
        with utils.ShowBusyMouse():
            _index = self.__get_index()
            self._tree.execute_process(
                _index,
                force_store_results=True,
                store_input_data=True,
                store_details=True,
                test=True,
            )
            self.__store_tree_results()
            self.__update_selection_choices()
            if self._active_node != -1:
                self.__update_text_description_of_node_results()
                self.__plot_results()

    @QtCore.Slot()
    def reload_workflow(self):
        """
        Reload the local WorkflowTree from the global one, e.g. to propagate changes
        to global settings.
        """
        self._tree = TREE.deepcopy()
        self.clear_results()

    @staticmethod
    def _check_tree_is_populated() -> bool:
        """
        Check if the WorkflowTree is populated, i.e. not empty.

        Returns
        -------
        bool
            Flag whether the WorkflowTree is populated.
        """
        if TREE.root is None:
            WarningBox(
                "Empty WorkflowTree",
                "The WorkflowTree is empty. Workflow processing has not been started.",
            )
            return False
        return True

    def __get_index(self) -> int:
        """
        Get the frame index.

        The frame in dex is based on the user selection for indexing using
        the absolute number, scan position numbers or the detector image number.

        Returns
        -------
        int
            The absolute frame number.
        """
        if self.get_param_value("image_selection") == "Use global index":
            return self.__get_global_index()
        if self.get_param_value("image_selection") == "Use scan dimensional indices":
            return self.__get_index_from_scan_dim_indices()
        # last choice is using the detector image number
        return self.__get_index_of_image()

    def __get_global_index(self) -> int:
        """
        Get the global index from the respective Parameter.

        Returns
        -------
        int
            The global image index.
        """
        _index = self.get_param_value("frame_index", dtype=int)
        if not 0 <= _index < SCAN.n_points:
            if SCAN.n_points < 3:
                _text = "[" + ", ".join(str(_i) for _i in range(SCAN.n_points)) + "]."
            else:
                _text = f"[0, 1, ..., {SCAN.n_points - 1}]."
            raise UserConfigError(
                f"The selected number {_index} is outside the scope of the number "
                f"of images in the scan {_text}"
            )
        return _index

    def __get_index_from_scan_dim_indices(self) -> int:
        """
        Get the global index from the individual scan indices.

        Returns
        -------
        int
            The global image index.
        """
        _nums = [
            self.get_param_value(f"scan_index{_index}") for _index in range(SCAN.ndim)
        ]
        _index = SCAN.get_frame_from_indices(_nums)
        if _index >= SCAN.n_points:
            raise UserConfigError(
                f"The selected scan point {_nums} is outside the scope of the scan "
                f"dimensions. (Please note that python starts counting at zero)."
            )
        return _index

    def __get_index_of_image(self) -> int:
        """
        Get the global index from the detector image number.

        Returns
        -------
        int
            The global index.
        """
        _i0 = SCAN.get_param_value("scan_start_index")
        _delta = SCAN.get_param_value("scan_index_stepping")
        _num = self.get_param_value("detector_image_index")
        _index = (_num - _i0) // _delta
        if not 0 <= _index < SCAN.n_points:
            if SCAN.n_points <= 3:
                _points = ", ".join(
                    str(_i0 + _delta * _i) for _i in range(SCAN.n_points)
                )
            else:
                _points = (
                    f"{_i0}, {_i0 + _delta}, ..., {_i0 + (SCAN.n_points - 1) * _delta}"
                )
            raise UserConfigError(
                f"The selected number {_num} is not included in the images of the scan "
                + "["
                + _points
                + "]."
            )
        return _index

    def __store_tree_results(self):
        """
        Store the WorkflowTree results in a local dictionary.
        """
        _meta = self._tree.get_complete_plugin_metadata()
        self._local_results_mock.result_titles = _meta["result_titles"]
        for _node_id, _node in self._tree.nodes.items():
            _data = _node.results
            if _data is not None:
                if 1 in set(_data.shape) and _data.shape != (1,):
                    _data = _data.squeeze()
                self._results[_node_id] = _data

    def __update_selection_choices(self):
        """Update the choice of results to display"""
        self._widgets["result_table"].update_choices_from_workflow_results(
            self._local_results_mock
        )

    @QtCore.Slot(int)
    def _selected_new_node(self, index: int):
        """
        Handle the selection of a new node.

        Parameters
        ----------
        index : int
            The node_id of the selected results.
        """
        self._active_node = index
        if index == -1:
            self._config["has_details"] = False
            return
        else:
            self._config["plot_active"] = True
            self._config["has_details"] = hasattr(
                self._tree.nodes[self._active_node].plugin, "detailed_results"
            )
        self.__set_derived_widget_visibility(index != -1)
        self.__update_text_description_of_node_results()
        self.__plot_results()

    def clear_results(self):
        """Clear all stored results."""
        self._results = {}
        self._local_results_mock.result_titles = {}
        self.__update_selection_choices()
        self.__set_derived_widget_visibility(False)

    def __set_derived_widget_visibility(self, visible: bool):
        """
        Change the visibility of all 'derived' widgets.

        This method changes the visibility of the InfoBox and selection
        widgets.

        Parameters
        ----------
        visible : bool
            Keyword to toggle visibility.
        """
        for _key in ["result_info", "but_tweak_params", "label_select_header", "plot"]:
            self._widgets[_key].setVisible(visible)
        self._widgets["but_show_details"].setVisible(
            self._config["has_details"] and visible
        )

    def __update_text_description_of_node_results(self):
        """
        Update the text description of the currently selected node's results.
        """
        if self._active_node == -1:
            return
        _str = _create_str_description_of_node_result(
            self._tree.nodes[self._active_node], self._results[self._active_node]
        )
        self._widgets["result_info"].setText(_str)

    def __plot_results(self):
        """
        Update the plot.

        This method will get the latest result (subset) from the
        ProcessingResults and update the plot.
        """
        if self._active_node == -1 or not self._config["plot_active"]:
            return
        self._widgets["plot"].set_data(self._results[self._active_node])
        if self._config["details_active"] and self._config["has_details"]:
            self.show_plugin_details(set_focus=False)

    @QtCore.Slot()
    def show_plugin_details(self, set_focus: bool = True):
        """
        Show details for the selected plugin.

        This method will get the detailed results for the active node and open a
        new window to display the detailed information.

        Parameters
        ----------
        set_focus : bool, optional
            Keyword to set the focus on the new window. The default is True.
        """
        self._config["details_active"] = True
        _plugin = self._tree.nodes[self._active_node].plugin
        _details = _plugin.detailed_results
        _title = _plugin.plugin_name + ' "' + _plugin.result_title + '"'
        self.__details_window.update_results(_details, title=_title)
        self.__details_window.raise_()
        self.__details_window.show()
        if set_focus:
            self.__details_window.activateWindow()

    @QtCore.Slot()
    def show_tweak_params_window(self):
        """
        Show the window to tweak the Parameters for the active plugin.
        """
        _plugin = self._tree.nodes[self._active_node].plugin
        _res = self._tree.nodes[self._active_node].results
        self.__details_window.hide()
        self.__tweak_window.tweak_plugin(_plugin, _res)
        self.__tweak_window.raise_()
        self.__tweak_window.show()
        self.__tweak_window.activateWindow()

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
        super().frame_activated(index)
        if index == self.frame_index:
            self.__update_image_selection_visibility()
            self.__check_tree_uptodate()
        else:
            if self._config["built"]:
                self.__tweak_window.hide()
                self.__details_window.hide()
