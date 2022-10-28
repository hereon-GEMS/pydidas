# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WorkflowTestFrame"]

import copy

from qtpy import QtCore

from ...core import (
    Parameter,
    ParameterCollection,
    get_generic_param_collection,
    utils,
    UserConfigError,
)
from ...experiment import SetupScan
from ...workflow import WorkflowTree
from ...widgets.dialogues import WarningBox
from ...widgets.silx_plot import get_2d_silx_plot_ax_settings
from ..windows import ShowDetailedPluginResultsWindow, TweakPluginParameterWindow
from ..utils import get_main_menu
from .builders import WorkflowTestFrameBuilder


SCAN = SetupScan()
TREE = WorkflowTree()


class WorkflowTestFrame(WorkflowTestFrameBuilder):
    """
    The ProcessingSinglePluginFrame allows to run / test single plugins on a
    single datapoint.

    The selection of a frame can be done either using the absolute frame number
    (if the ``image_selection`` Parameter equals "Use image number") or by
    supplying scan indices for all active scan dimensions  (if the
    ``image_selection`` Parameter equals "Use scan indices").
    """

    menu_icon = "qta::mdi.play-protected-content"
    menu_title = "Test workflow"
    menu_entry = "Workflow processing/Test workflow"

    default_params = ParameterCollection(
        Parameter(
            "image_selection",
            str,
            "Use image number",
            name="Image selection",
            choices=["Use image number", "Use scan indices"],
            tooltip=(
                "Choose between selecing images using either the "
                "image / frame number or the multi-dimensional "
                "position in the scan."
            ),
        ),
        get_generic_param_collection(
            "image_num",
            "scan_index1",
            "scan_index2",
            "scan_index3",
            "scan_index4",
            "selected_results",
        ),
    )
    params_not_to_restore = ["selected_results"]

    def __init__(self, parent=None, **kwargs):
        WorkflowTestFrameBuilder.__init__(self, parent, **kwargs)
        self.set_default_params()
        self.__source_hash = -1
        self._tree = None
        self._active_node = -1
        self._results = {}
        self._config.update(
            {
                "shapes": {},
                "labels": {},
                "data_labels": {},
                "plot_active": False,
                "plot_dim": 1,
            }
        )

    def connect_signals(self):
        """
        Connect all required signals and slots.
        """
        self.param_widgets["image_selection"].io_edited.connect(
            self.__update_image_selection_visibility
        )
        self.param_widgets["selected_results"].currentIndexChanged.connect(
            self.__selected_new_node
        )
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
        _main = get_main_menu()
        _main.sig_close_gui.connect(self.__tweak_window.close)
        _main.sig_close_gui.connect(self.__details_window.close)

    def __check_tree_uptodate(self):
        """
        Check if the WorkflowTree has changed and update the local Tree if
        it has changed.
        """
        if self.__source_hash != hash((hash(SCAN), hash(TREE))):
            self.__source_hash = hash((hash(SCAN), hash(TREE)))
            self._tree = TREE.get_copy()

    @QtCore.Slot(int)
    def __updated_plugin_params(self, node_id):
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
        _arg = self._tree.nodes[node_id].plugin._config["input_data"].copy()
        _kwargs = self._tree.nodes[node_id].plugin._config["input_kwargs"].copy() | {
            "force_store_results": True,
            "store_input_data": True,
        }
        with utils.ShowBusyMouse():
            self._tree.nodes[node_id].execute_plugin_chain(_arg, **_kwargs)
            self.__store_tree_results()
            self.__update_selection_choices()
            if self._active_node != -1:
                self.__update_text_description_of_node_results()
                self.__plot_results()
            self.__source_hash = hash((hash(SCAN), hash(TREE)))

    @QtCore.Slot()
    def __update_image_selection_visibility(self):
        """
        Update the visibility of the image selection widgets.
        """
        _use_frame = self.get_param_value("image_selection") == "Use image number"
        self.toggle_param_widget_visibility("image_num", _use_frame)
        for _dim in [1, 2, 3, 4]:
            self.toggle_param_widget_visibility(
                f"scan_index{_dim}", not _use_frame and _dim <= SCAN.ndim
            )

    @QtCore.Slot()
    def execute_workflow_test(self):
        """
        Test the Workflow on the selected frame and store results for
        presentation.
        """
        if not self._check_tree_is_populated():
            return
        with utils.ShowBusyMouse():
            _index = self.__get_index()
            self._tree.execute_process(
                _index, force_store_results=True, store_input_data=True
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
        self._tree = TREE.get_copy()

    @staticmethod
    def _check_tree_is_populated():
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

    def __get_index(self):
        """
        Get the frame index based on the user selection for indexing using
        the absolute number or scan position numbers.

        Returns
        -------
        int
            The absolute frame number.
        """
        if self.get_param_value("image_selection") == "Use image number":
            _index = self.get_param_value("image_num", dtype=int)
            if not 0 <= _index < SCAN.n_points:
                raise UserConfigError(
                    f"The selected number {_index} is outside the scope of the number "
                    f"of images in the scan (0...{SCAN.n_points - 1})"
                )
            return _index
        _nums = [
            self.get_param_value(f"scan_index{_index+1}") for _index in range(SCAN.ndim)
        ]
        _index = SCAN.get_frame_number_from_scan_indices(_nums)
        return _index

    def __store_tree_results(self):
        """
        Store the WorkflowTree results in a local dictionary.
        """
        _meta = self._tree.get_complete_plugin_metadata()
        self._config["plugin_res_shapes"] = _meta["shapes"]
        self._config["plugin_labels"] = _meta["labels"]
        self._config["plugin_names"] = _meta["names"]
        self._config["plugin_data_labels"] = _meta["data_labels"]
        self._config["plugin_res_titles"] = _meta["result_titles"]
        for _node_id, _node in self._tree.nodes.items():
            _data = _node.results
            _data.convert_all_none_properties()
            if 1 in set(_data.shape) and _data.shape != (1,):
                _data = _data.squeeze()
            self._results[_node_id] = _data

    def __update_selection_choices(self):
        """
        Update the "selected_results" Parameter.

        A neutral entry of "No selection" is also added.
        """
        param = self.get_param("selected_results")
        _curr_choice = param.value
        _new_choices = ["No selection"]
        _new_choices.extend(self._config["plugin_res_titles"].values())
        if _curr_choice in _new_choices:
            param.choices = _new_choices
        else:
            _new_choices.append(_curr_choice)
            param.choices = _new_choices
            param.value = _new_choices[0]
            param.choices = _new_choices[:-1]
            self._active_node = -1
            self._config["plot_active"] = False
        with utils.SignalBlocker(self.param_widgets["selected_results"]):
            self.param_widgets["selected_results"].update_choices(param.choices)
            self.param_widgets["selected_results"].setCurrentText(param.value)

    @QtCore.Slot(int)
    def __selected_new_node(self, index):
        """
        Received signal that the selection in the results Parameter has
        changed.

        Parameters
        ----------
        index : int
            The new QComboBox selection index.
        """
        if index == 0:
            self._active_node = -1
            self.__set_derived_widget_visibility(False)
            self._clear_plot()
            return
        self._active_node = int(
            self.param_widgets["selected_results"].currentText()[-4:-1]
        )
        self._config["plot_active"] = True
        self.__set_derived_widget_visibility(True)
        self.__update_text_description_of_node_results()
        self.__plot_results()

    def __set_derived_widget_visibility(self, visible):
        """
        Change the visibility of all 'derived' widgets.

        This method changes the visibility of the InfoBox and selection
        widgets.

        Parameters
        ----------
        visible : bool
            Keyword to toggle visibility.
        """
        self._config["widget_visibility"] = visible
        self._widgets["result_info"].setVisible(visible)
        self._widgets["but_tweak_params"].setVisible(visible)
        _has_get_details_attr = (
            False
            if self._active_node == -1
            else hasattr(self._tree.nodes[self._active_node].plugin, "detailed_results")
        )
        self._widgets["but_show_details"].setVisible(_has_get_details_attr and visible)

    def __update_text_description_of_node_results(self):
        """
        Update the text description of the currently selected node's results.
        """
        _current_results = self._results[self._active_node]
        _plugin = self._tree.nodes[self._active_node].plugin
        _meta = {
            "axis_labels": _current_results.axis_labels,
            "axis_units": _current_results.axis_units,
            "axis_ranges": _current_results.axis_ranges,
            "metadata": _current_results.metadata,
        }
        _ax_units = {
            _dim: (_ax_unit if _ax_unit is not None else "")
            for _dim, _ax_unit in _meta["axis_units"].items()
        }
        _ax_ranges = {
            _key: utils.get_range_as_formatted_string(_range)
            for _key, _range in _meta["axis_ranges"].items()
        }
        _ax_points = dict(
            enumerate(self._config["plugin_res_shapes"][self._active_node])
        )
        _values = utils.get_simplified_array_representation(_current_results)
        _data_label = _plugin.output_data_label + (
            f" / {_plugin.output_data_unit}"
            if len(_plugin.output_data_unit) > 0
            else ""
        )
        _str = (
            self._config["plugin_names"][self._active_node]
            + ":\n\n"
            + f"Data: {_data_label}\n\n"
            + "\n\n".join(
                (
                    f"Axis #{_axis:02d}:\n"
                    f'  Label: {_meta["axis_labels"][_axis]}\n'
                    f"  N points: {_ax_points[_axis]}\n"
                    f"  Range: {_ax_ranges[_axis]} {_ax_units[_axis]}"
                )
                for _axis in _meta["axis_labels"]
            )
        )
        _str += f"\n\nValues:\n{_values}"
        _str += f'\n\nMetadata:\n{_meta["metadata"]}'
        self._widgets["result_info"].setText(_str)

    def __plot_results(self):
        """
        Update the plot.

        This method will get the latest result (subset) from the
        WorkflowResults and update the plot.
        """
        if not self._config["plot_active"]:
            return
        _ndim = self._results[self._active_node].ndim
        if _ndim == 1:
            self._config["plot_dim"] = 1
            self._plot1d()
        elif _ndim == 2:
            self._config["plot_dim"] = 2
            self._plot_2d()
        else:
            self._clear_plot()
            return
        self._widgets["plot_stack"].setCurrentIndex(_ndim - 1)
        _plot = self._widgets[f"plot{_ndim}d"]
        _plot.setGraphTitle(self._config["plugin_res_titles"][self._active_node])

    def _plot1d(self):
        """
        Plot a 1D-dataset in the 1D plot widget.
        """
        _data = self._results[self._active_node]
        _plot = self._widgets["plot1d"]
        _axlabel = _data.axis_labels[0] + (
            " / " + _data.axis_units[0] if len(_data.axis_units[0]) > 0 else ""
        )
        _plot.addCurve(_data.axis_ranges[0], _data.array, linewidth=1.5)
        _plot.setGraphYLabel(self._config["plugin_data_labels"][self._active_node])
        _plot.setGraphXLabel(_axlabel)

    def _plot_2d(self):
        """
        Plot a 2D dataset as an image.
        """
        _data = self._results[self._active_node]
        _plot = self._widgets["plot2d"]
        _ax_label = [
            _data.axis_labels[i]
            + (" / " + _data.axis_units[i] if len(_data.axis_units[i]) > 0 else "")
            for i in [0, 1]
        ]
        _originx, _scalex = get_2d_silx_plot_ax_settings(_data.axis_ranges[1])
        _originy, _scaley = get_2d_silx_plot_ax_settings(_data.axis_ranges[0])
        _plot.addImage(
            _data,
            replace=True,
            copy=False,
            origin=(_originx, _originy),
            scale=(_scalex, _scaley),
        )
        _plot.setGraphYLabel(_ax_label[0])
        _plot.setGraphXLabel(_ax_label[1])

    def _clear_plot(self):
        """
        Clear the current plot and remove all items.
        """
        _plot_dim = self._config["plot_dim"]
        self._widgets[f"plot{_plot_dim }d"].remove()
        self._widgets[f"plot{_plot_dim }d"].setGraphTitle("")
        self._widgets[f"plot{_plot_dim }d"].setGraphYLabel("")
        self._widgets[f"plot{_plot_dim }d"].setGraphXLabel("")

    @QtCore.Slot()
    def show_plugin_details(self):
        """
        Show details for the selected plugin.

        This method will get the detailed results for the active node and open a
        new window to display the detailed information.
        """
        _plugin = self._tree.nodes[self._active_node].plugin
        _details = _plugin.detailed_results
        _title = (
            _plugin.plugin_name
            + ' "'
            + self.param_widgets["selected_results"].currentText()
            + '"'
        )
        self.__details_window.update_results(_details, title=_title)
        self.__details_window.raise_()
        self.__details_window.show()
        self.__details_window.activateWindow()

    @QtCore.Slot()
    def show_tweak_params_window(self):
        """
        Show the window to tweak the Parameters for the active plugin.
        """
        _plugin = self._tree.nodes[self._active_node].plugin
        _res = self._tree.nodes[self._active_node].results
        self.__tweak_window.tweak_plugin(_plugin, _res)
        self.__tweak_window.raise_()
        self.__tweak_window.show()
        self.__tweak_window.activateWindow()

    @QtCore.Slot(int)
    def frame_activated(self, index):
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
