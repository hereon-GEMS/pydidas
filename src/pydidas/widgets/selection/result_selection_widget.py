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
Module with the ResultSelectionWidget widget which can handle the selection
of a node with results from the WorkflowResults and returns a signal with
information on how to access the new data selection.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ResultSelectionWidget"]


from functools import partial
from typing import Union

import numpy as np
from qtpy import QtCore

from pydidas.core import (
    Parameter,
    ParameterCollection,
    ParameterCollectionMixIn,
    UserConfigError,
    get_generic_parameter,
    utils,
)
from pydidas.core.constants import (
    FONT_METRIC_CONFIG_WIDTH,
    QT_REG_EXP_FLOAT_SLICE_VALIDATOR,
    QT_REG_EXP_SLICE_VALIDATOR,
)
from pydidas.widgets.factory import CreateWidgetsMixIn, EmptyWidget
from pydidas.widgets.misc import ReadOnlyTextWidget
from pydidas.widgets.parameter_config.parameter_widgets_mixin import (
    ParameterWidgetsMixIn,
)
from pydidas.widgets.utilities import update_param_and_widget_choices
from pydidas.widgets.windows import ShowInformationForResult
from pydidas.workflow import WorkflowResults, WorkflowResultsSelector


class ResultSelectionWidget(
    EmptyWidget,
    CreateWidgetsMixIn,
    ParameterWidgetsMixIn,
    ParameterCollectionMixIn,
):
    """
    A Widget to select data slices from WorkflowResults for plotting.

    The widget allows to select a :py:class:`WorkflowNode
    <pydidas.workflow.WorkflowNode>`, using meta information from the
    :py:class:`ScanContext <pydidas.core.ScanContext>` and
    :py:class:`WorkflowResults <pydidas.workflow.WorkflowResults>`
    singletons.
    It displays information for all dimensions in the results (label, unit,
    range) and allows selecting data dimension(s) (based on the dimensionality
    of the plot) and slice indices for other dimensions. In addition, an option
    to hande the Scan as a "timeline" is given. In a timeline, all Scan points
    will be flattened to a 1d-dataset.

    Notes
    -----
    The ResultSelectionWidget offers the following signal which can be used:

    .. code-block::

        .sig_new_selection : QtCore.Signal(
            use_timeline : int,
            active_dims : list,
            active_node : int,
            selection : tuple,
            plot_type : str
        )

    The signal signature is: flag to use timeline or scan shape,
    active scan dimensions, node ID of the active node,
    the selection in form of a tuple with entries for every dimension
    (in form of a numpy array), the type of plot in form of a string.

    Parameters
    ----------
    parent : QtWidgets.QWidget
        The parent widget.
    select_results_param : pydidas.core.Parameter
        The select_results Parameter instance. This instance should be
        shared between the ResultSelectionWidget and the parent.
    """

    sig_new_selection = QtCore.Signal(bool, object, int, object, str)
    init_kwargs = EmptyWidget.init_kwargs + [
        "select_results_param",
        "scan_context",
        "workflow_results",
    ]

    default_params = ParameterCollection(
        get_generic_parameter("selected_results"),
        Parameter("plot_ax1", str, "", name="Data axis no. 1 for plot", choices=[""]),
        Parameter("plot_ax2", str, "", name="Data axis no. 2 for plot", choices=[""]),
        get_generic_parameter("use_scan_timeline"),
    )

    def __init__(
        self, select_results_param: Union[None, Parameter] = None, **kwargs: dict
    ):
        self.__width_factor = kwargs.get(
            "font_metric_width_factor", FONT_METRIC_CONFIG_WIDTH
        )
        EmptyWidget.__init__(self, **kwargs)
        ParameterWidgetsMixIn.__init__(self)
        CreateWidgetsMixIn.__init__(self)
        ParameterCollectionMixIn.__init__(self)
        self._config = {
            "widget_visibility": False,
            "result_ndim": -1,
            "active_dims": (0,),
            "plot_type": "1D plot",
            "n_slice_params": 0,
            "selection_by_data_values": True,
            "validator": QT_REG_EXP_FLOAT_SLICE_VALIDATOR,
            "selected_node": -1,
        }
        _results = kwargs.get("workflow_results", None)
        self._RESULTS = WorkflowResults() if _results is None else _results
        self._active_node = -1
        if select_results_param is not None:
            self.add_param(select_results_param)
        self.set_default_params()
        self._selector = WorkflowResultsSelector(
            self.get_param("use_scan_timeline"),
            scan_context=self._RESULTS.frozen_scan,
            workflow_results=self._RESULTS,
        )
        self.__result_window = None
        self.__create_widgets()
        self.__connect_signals()

    def __create_widgets(self):
        """
        Create all sub-widgets and populate the UI.
        """
        self.create_label("label_results", "Results:", fontsize=11, underline=True)
        self.create_param_widget(
            self.get_param("selected_results"),
            linebreak=True,
        )
        self.create_radio_button_group(
            "radio_arrangement",
            ["by scan shape", "as a timeline"],
            title="Arrangement of results:",
            vertical=False,
            visible=False,
        )
        self.create_any_widget(
            "result_info",
            ReadOnlyTextWidget,
            alignment=QtCore.Qt.AlignTop,
            font_metric_height_factor=20,
            font_metric_width_factor=self.__width_factor,
            visible=False,
        )
        self.create_radio_button_group(
            "radio_plot_type",
            ["1D plot", "group of 1D plots", "2D full axes", "2D data subset"],
            columns=2,
            rows=2,
            title="Result plot type:",
            visible=False,
        )
        self.create_radio_button_group(
            "radio_data_selection",
            ["Data values", "Axis index"],
            columns=2,
            title="Data selection:",
            visible=False,
        )
        self.create_empty_widget("plot_ax_group")
        self.create_param_widget(
            self.get_param("plot_ax1"),
            linebreak=True,
            parent_widget="plot_ax_group",
            visible=False,
        )
        self.create_param_widget(
            self.get_param("plot_ax2"),
            linebreak=True,
            parent_widget="plot_ax_group",
            visible=False,
        )
        self.create_button("but_confirm", "Confirm selection", visible=False)

    def __connect_signals(self):
        """
        Connect all required signals.
        """
        self.param_widgets["selected_results"].currentIndexChanged.connect(
            self.__selected_new_node
        )
        self._widgets["radio_plot_type"].new_button_label.connect(
            self.__select_type_of_plot
        )
        self._widgets["radio_arrangement"].new_button_index.connect(
            self.__arrange_results_in_timeline_or_scan_shape
        )
        self._widgets["radio_data_selection"].new_button_label.connect(
            self.__modify_data_selection
        )
        self.param_widgets["plot_ax1"].currentTextChanged.connect(
            partial(self.__selected_new_plot_axis, 1)
        )
        self.param_widgets["plot_ax2"].currentTextChanged.connect(
            partial(self.__selected_new_plot_axis, 2)
        )
        self._widgets["but_confirm"].clicked.connect(self.__confirm_selection)

    def reset(self):
        """
        Reset the instance to its default selection.

        This method should be called for example when a new processing has been
        started and the old information is no longer valid.
        """
        self._config.update(
            {"widget_visibility": False, "result_ndim": -1, "plot_type": "1D plot"}
        )
        self._active_node = -1
        with QtCore.QSignalBlocker(self.param_widgets["selected_results"]):
            self.param_widgets["selected_results"].update_choices(["No selection"])
        self.param_widgets["selected_results"].setCurrentText("No selection")
        with QtCore.QSignalBlocker(self._widgets["radio_plot_type"]):
            self._widgets["radio_plot_type"].select_by_index(0)
        with QtCore.QSignalBlocker(self._widgets["radio_data_selection"]):
            self._widgets["radio_data_selection"].select_by_index(0)
        with QtCore.QSignalBlocker(self._widgets["radio_arrangement"]):
            self._widgets["radio_arrangement"].select_by_index(0)
        self.__set_derived_widget_visibility(False)

    @QtCore.Slot()
    def get_and_store_result_node_labels(self):
        """
        Get and store the labels of the current nodes in the WorkflowResults.

        This method will also update the choice of selections based on these
        items.
        """
        _param = self.get_param("selected_results")
        # store the labels for the different nodes from the RESULTS
        self._RESULTS.update_param_choices_from_labels(_param)
        with QtCore.QSignalBlocker(self.param_widgets["selected_results"]):
            self.param_widgets["selected_results"].update_choices(_param.choices)
            self.param_widgets["selected_results"].setCurrentText(_param.value)

    @QtCore.Slot(str)
    def __select_type_of_plot(self, label: str):
        """
        Update the selection of plot dimensions.

        Parameters
        ----------
        label : str
            The index of the dimension selection.
        """
        self._config["plot_type"] = label
        self.__update_slice_param_widgets()

    def __update_slice_param_widgets(self, hide_all: bool = False):
        """
        Change the visibility and text of Parameter selection widgets for the slice
        dimensions in the dataset.

        Parameters
        ----------
        hide_all : bool, optional
            Keyword to force hiding of all Parameter slice dimension widgets.
        """
        _ax1_used, _ax2_used = self.__are_axes_used()
        self.param_composite_widgets["plot_ax1"].setVisible(_ax1_used and not hide_all)
        self.param_composite_widgets["plot_ax2"].setVisible(_ax2_used and not hide_all)
        _frozendims = []
        _labels_and_units = self._get_axis_labels_and_units()
        if _ax1_used and self._config["result_ndim"] > 0:
            _frozendims.append(int(self.get_param_value("plot_ax1").split(":")[0]))
        if _ax2_used and self._config["result_ndim"] > 0:
            _frozendims.append(int(self.get_param_value("plot_ax2").split(":")[0]))
        for _dim in range(self._config["n_slice_params"]):
            _refkey = f"plot_slice_{_dim}"
            _composite_widget = self.param_composite_widgets[_refkey]
            _vis = (
                False
                if hide_all
                else (_dim < self._config["result_ndim"] and _dim not in _frozendims)
            )
            _composite_widget.setVisible(_vis)
            if _dim < self._config["result_ndim"] and self._active_node != -1:
                _label, _unit = _labels_and_units[_dim]
                _label = _label[:20] + "..." if len(_label) > 25 else _label
                _composite_widget._widgets["name_label"].setText(
                    f"Slice of data dim #{_dim}"
                    + (f" ({_label}):" if len(_label) > 0 else ":")
                )
                _composite_widget._widgets["unit_label"].setText(
                    _unit if self._config["selection_by_data_values"] else " "
                )

    def __are_axes_used(self) -> tuple[bool, bool]:
        """
        Check whether the axes are in use and return the flags.

        Returns
        -------
        bool
            Flag whether axis 1 is in use.
        bool
            Flag whether axis 2 is in use.
        """
        _ax1_used = self._config["plot_type"] in [
            "1D plot",
            "group of 1D plots",
            "2D full axes",
        ]
        _ax2_used = self._config["plot_type"] == "2D full axes"
        return _ax1_used, _ax2_used

    @QtCore.Slot(str)
    def __modify_data_selection(self, label: str):
        """
        Received the signal that the data selection modality (data values
        / indices) has been changed and update the internal reference.

        Parameters
        ----------
        label : str
            The label how to select the data.
        """
        self._config["selection_by_data_values"] = label == "Data values"
        if label == "Data values":
            self._config["validator"] = QT_REG_EXP_FLOAT_SLICE_VALIDATOR
        else:
            self._config["validator"] = QT_REG_EXP_SLICE_VALIDATOR
        for _dim in range(self._config["n_slice_params"]):
            _refkey = f"plot_slice_{_dim}"
            self.param_widgets[_refkey].setValidator(self._config["validator"])
        self.__update_slice_param_widgets()

    @QtCore.Slot(int)
    def __selected_new_node(self, index: int):
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
        elif index > 0:
            self._active_node = int(
                self.param_widgets["selected_results"].currentText()[-4:-1]
            )
            self._selector.select_active_node(self._active_node)
            self.__calc_and_store_ndim_of_results()
            self.__update_dim_choices_for_plot_selection()
            self.__update_text_description_of_node_results()
            self.__enable_valid_result_plot_selection()
            self.__check_and_create_params_for_slice_selection()

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
        self._config["widget_visibility"] = visible
        self._widgets["result_info"].setVisible(visible)
        self._widgets["radio_plot_type"].setVisible(visible)
        self._widgets["radio_arrangement"].setVisible(visible)
        self._widgets["radio_data_selection"].setVisible(visible)
        self.param_composite_widgets["plot_ax1"].setVisible(visible)
        self.param_composite_widgets["plot_ax2"].setVisible(
            visible and (self._config["plot_type"] == 2)
        )
        self._widgets["but_confirm"].setVisible(visible)
        self.__update_slice_param_widgets(hide_all=not visible)

    def __calc_and_store_ndim_of_results(self):
        """
        Update the information about the number of dimensions the results will have.
        """
        _ndim = self._RESULTS.ndims[self._active_node]
        _active_shape = self._RESULTS.shapes[self._active_node]
        _ndim_scan = np.where(
            np.asarray(_active_shape[: self._RESULTS.frozen_scan.ndim]) > 1
        )[0].size
        _ndim = np.where(np.asarray(_active_shape) > 1)[0].size
        if self.get_param_value("use_scan_timeline"):
            _ndim -= _ndim_scan - 1
        self._config["result_ndim"] = _ndim

    def __update_text_description_of_node_results(self):
        """
        Update the text in the "result_info" ReadOnlyTextWidget.
        """
        self._widgets["result_info"].setText(
            self._RESULTS.get_node_result_metadata_string(
                self._active_node, self.get_param_value("use_scan_timeline")
            )
        )
        self.__set_derived_widget_visibility(True)

    def __enable_valid_result_plot_selection(self):
        """
        Validate the dimensionality of the results and enable plot choices accordingly.
        """
        _not_zero_dim = self._config["result_ndim"] > 0
        self._widgets["radio_plot_type"].setEnabled(_not_zero_dim)
        self._widgets["radio_data_selection"].setEnabled(_not_zero_dim)
        self._widgets["but_confirm"].setEnabled(_not_zero_dim)
        if self._config["result_ndim"] == 1:
            self._config["plot_type"] = "1D plot"
            self._widgets["radio_plot_type"].select_by_index(0)
            _2d_enabled = False
        else:
            self._config["plot_type"] = "2D full axes"
            self._widgets["radio_plot_type"].select_by_index(2)
            _2d_enabled = True
        for _id in [1, 2, 3]:
            self._widgets["radio_plot_type"]._buttons[_id].setEnabled(_2d_enabled)

    @QtCore.Slot(int)
    def __arrange_results_in_timeline_or_scan_shape(self, index: int):
        """
        Organize the scan results in a timeline or using the ScanContext shape.

        This method also updates the text in the ReadOnlyTextWidget to
        reflect the selection of the dimensions of the scan.

        Parameters
        ----------
        index : int
            The index of the newly activated button.
        """
        self.set_param_value("use_scan_timeline", bool(index))
        self.__calc_and_store_ndim_of_results()
        self.__update_dim_choices_for_plot_selection()
        self.__update_text_description_of_node_results()
        self.__enable_valid_result_plot_selection()
        self.__update_slice_param_widgets()

    @QtCore.Slot(int, str)
    def __selected_new_plot_axis(self, plot_axis: int, new_dim: str):
        """
        Perform operations after a new plot axis has been selected.

        Parameters
        ----------
        plot_axis : int
            The axis of the plot.
        new_dim : str
            The string representation of the new dimension for the selected
            plot axis.
        """
        # get the other axis (1, 2) from the input axis:
        _other_ax = 3 - plot_axis % 3
        _selected_param = self.params[f"plot_ax{plot_axis}"]
        _selected_param.value = utils.convert_unicode_to_ascii(new_dim)
        self.param_widgets[f"plot_ax{plot_axis}"].set_value(_selected_param.value)
        _other_param = self.params[f"plot_ax{_other_ax}"]
        if _other_param.value == utils.convert_unicode_to_ascii(new_dim):
            if new_dim == _other_param.choices[0]:
                _other_param.value = _other_param.choices[1]
            else:
                _other_param.value = _other_param.choices[0]
            self.param_widgets[f"plot_ax{_other_ax}"].set_value(_other_param.value)
        self.__update_slice_param_widgets()

    @QtCore.Slot()
    def __confirm_selection(self):
        """
        Confirm the selection of axes for the plot and sends a signal.

        The signal has the following form:
            bool, int, tuple

        With the first entry a flag to use a timeline (i.e. flattening of scan
        dimensions) and the tuple with the slicing object. The second entry
        is the dimensionality of the resulting data. The third entry is the
        slice object required to access the selected subset of data from the
        full array.
        """
        self.__update_selector_dim_params()
        self.sig_new_selection.emit(
            self.get_param_value("use_scan_timeline"),
            self._config["active_dims"],
            self._active_node,
            self._selector.selection,
            self._config["plot_type"],
        )
        self._config["selected_node"] = self._active_node

    def __update_selector_dim_params(self):
        """
        Update the dimension selections in the WorkflowResultsSelector.

        This method will update the necessary values in the WorkflowResultSelector and
        store the active dimensions in the 'active_dims' config key.

        Returns
        -------
        list
            The active dimensions in form of integer entries.
        """
        _target_dim = 1 if self._config["plot_type"] == "1D plot" else 2
        self._selector.select_active_node(self._active_node)
        self._selector.set_param_value("result_n_dim", _target_dim)
        self._selector.set_param_value(
            "use_data_range", self._config["selection_by_data_values"]
        )
        for _dim in range(self._config["result_ndim"]):
            self._selector.set_param_value(
                f"data_slice_{_dim}", self.get_param_value(f"plot_slice_{_dim}")
            )
        _active_dim1 = int(self.get_param_value("plot_ax1").split(":")[0])
        if self._config["plot_type"] in ["1D plot", "group of 1D plots"]:
            self._selector.set_param_value(f"data_slice_{_active_dim1}", ":")
            self._config["active_dims"] = (_active_dim1,)
        if self._config["plot_type"] == "2D full axes":
            self._selector.set_param_value(f"data_slice_{_active_dim1}", ":")
            _active_dim2 = int(self.get_param_value("plot_ax2").split(":")[0])
            self._selector.set_param_value(f"data_slice_{_active_dim2}", ":")
            self._config["active_dims"] = (_active_dim1, _active_dim2)
        if self._config["plot_type"] == "2D data subset":
            self._config["active_dims"] = self._selector.active_dims

    def __update_dim_choices_for_plot_selection(self):
        """
        Calculate and update the basic dimension choices for the plot slicing.
        """
        _new_choices = self._get_axis_index_labels()
        for _ax in [1, 2]:
            update_param_and_widget_choices(
                self.param_composite_widgets[f"plot_ax{_ax}"], _new_choices
            )
        if (
            self.params.values_equal("plot_ax1", "plot_ax2")
            and self._config["result_ndim"] > 1
        ):
            if self.get_param_value("plot_ax1") == _new_choices[0]:
                self.set_param_value("plot_ax2", _new_choices[1])
                self.param_widgets["plot_ax2"].set_value(_new_choices[1])
            else:
                self.set_param_value("plot_ax2", _new_choices[0])
                self.param_widgets["plot_ax2"].set_value(_new_choices[0])

    def __check_and_create_params_for_slice_selection(self):
        """
        Create the required Parameters for the slice selection, if required.
        """
        for _dim in range(self._RESULTS.ndims[self._active_node]):
            _refkey = f"plot_slice_{_dim}"
            if _refkey not in self.params:
                _param = Parameter(
                    _refkey,
                    str,
                    "0",
                    name=f"Slice of data dim #{_dim}",
                    tooltip=(
                        "The scan/data position index to be displayed. Note: "
                        "The selection will be modulated to match the number "
                        "of datapoints."
                    ),
                    unit=" ",
                )
                self.add_param(_param)
                self.create_param_widget(
                    _param,
                    parent_widget="plot_ax_group",
                    linebreak=True,
                    visible=False,
                    width_unit=0.1,
                    width_io=0.4,
                )
                self.param_widgets[_refkey].setValidator(self._config["validator"])
        self._config["n_slice_params"] = max(
            self._config["n_slice_params"], self._RESULTS.ndims[self._active_node]
        )
        self.__update_slice_param_widgets()

    def _get_axis_index_labels(self) -> list[str]:
        """
        Get the indices and axis labels for the selected node ID.

        This function will filter labels of dimensions with length 0 or 1.

        Returns
        -------
        List[str]
            The node's axis labels.
        """
        _metadata, _active_dims = self._get_metadata_and_active_dims()
        return [
            (
                f"{_index}: {_metadata['axis_labels'][_dim]}"
                if len(_metadata["axis_labels"][_dim]) > 0
                else f"{_index}"
            )
            for _index, _dim in enumerate(_active_dims)
        ]

    def _get_axis_labels_and_units(self) -> list[list[str]]:
        """
        Get the axis labels and units.

        Returns
        -------
        list[list[str]]
            A list with pair entries for label and unit.
        """
        if self._active_node == -1:
            return [[]]
        _metadata, _active_dims = self._get_metadata_and_active_dims()
        return [
            [_metadata["axis_labels"][_dim], _metadata["axis_units"][_dim]]
            for _dim in _active_dims
        ]

    def _get_metadata_and_active_dims(self) -> tuple[dict, list]:
        """
        Get the metadata and active dimensions of the active node.

        Returns
        -------
        Tuple[dict, list]
            The metadata dictionary and the list of active dimensions.
        """
        _node_metadata = self._RESULTS.get_result_metadata(
            self._active_node, self.get_param_value("use_scan_timeline")
        )
        _dims = [_dim for _dim, _val in enumerate(_node_metadata["shape"]) if _val > 1]
        return _node_metadata, _dims

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
        if self._config["selected_node"] == -1:
            raise UserConfigError(
                "No node has been selected. Please check the result selection"
            )
        _loader_plugin = self._RESULTS.frozen_tree.root.plugin.copy()
        _loader_plugin._SCAN = self._RESULTS.frozen_scan
        if _loader_plugin.filename_string == "":
            _loader_plugin.pre_execute()
        _timeline = self.get_param_value("use_scan_timeline")
        _node_metadata = self._RESULTS.get_result_metadata(
            self._config["selected_node"], _timeline
        )
        _selection_config = self.get_param_values_as_dict() | {
            "selection_by_data_values": self._config["selection_by_data_values"],
            "active_dims": self._config["active_dims"],
            "use_timeline": _timeline,
        }
        _selection_config["selected_results"] = self._config["selected_node"]
        if self.__result_window is None:
            self.__result_window = ShowInformationForResult()
        self.__result_window.display_information(
            (data_y, data_x), _selection_config, _node_metadata, _loader_plugin
        )
