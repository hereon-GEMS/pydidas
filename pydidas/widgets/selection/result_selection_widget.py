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
Module with the ResultSelectionWidget widget which can handle the selection
of a node with results from the WorkflowResults and returns a signal with
information on how to access the new data selection.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ResultSelectionWidget"]

from functools import partial

import numpy as np
from qtpy import QtWidgets, QtCore

from ...core import (
    Parameter,
    ParameterCollection,
    ParameterCollectionMixIn,
    get_generic_parameter,
)
from ...core.constants import (
    CONFIG_WIDGET_WIDTH,
    QT_REG_EXP_SLICE_VALIDATOR,
    QT_REG_EXP_FLOAT_SLICE_VALIDATOR,
)
from ...core.utils import SignalBlocker
from ...experiment import SetupScan
from ...workflow import WorkflowResults, WorkflowResultsSelector
from ..factory import CreateWidgetsMixIn
from ..parameter_config.parameter_widgets_mixin import ParameterWidgetsMixIn
from ..read_only_text_widget import ReadOnlyTextWidget
from ..utilities import apply_widget_properties


SCAN = SetupScan()
RESULTS = WorkflowResults()


def _param_widget_config(param_key):
    """
    Get Formatting options for create_param_widget instances.
    """
    if param_key in ["selected_results"]:
        return dict(
            linebreak=True,
            halign_text=QtCore.Qt.AlignLeft,
            valign_text=QtCore.Qt.AlignBottom,
            width_total=CONFIG_WIDGET_WIDTH - 10,
            width_io=CONFIG_WIDGET_WIDTH - 50,
            width_text=CONFIG_WIDGET_WIDTH - 20,
            width_unit=0,
        )
    return dict(
        width_io=100,
        width_unit=0,
        width_text=CONFIG_WIDGET_WIDTH - 100,
        width_total=CONFIG_WIDGET_WIDTH - 10,
        visible=False,
    )


class ResultSelectionWidget(
    QtWidgets.QWidget,
    CreateWidgetsMixIn,
    ParameterWidgetsMixIn,
    ParameterCollectionMixIn,
):
    """
    The ResultSelectionWidget widget allows to select data slices for
    plotting using meta information from the
    :py:class:`SetupScan <pydidas.core.SetupScan<` and
    :py:class:`WorkflowResults <pydidas.workflow.WorkflowResults>`
    singletons.

    The widget allows to select a :py:class:`WorkflowNode
    <pydidas.workflow.WorkflowNode>`, display all the meta information
    for all dimensions in the results (label, unit, range) and select data
    dimension(s) (based on the dimensionality of the plot) and slice indices
    for other dimensions. In addition, an option to hande the Scan as a
    "timeline" is given. In a timeline, all Scan points will be flattened to
    a 1d-dataset.

    Notes
    -----
    The ResultSelectionWidget offers the following signal which can be
    used:

        new_selection : QtCore.Signal(use_timeline : int, active_dims : list,\
                                      active_node : int, selection : tuple, \
                                      plot_type : str)
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

    new_selection = QtCore.Signal(bool, object, int, object, str)

    default_params = ParameterCollection(
        get_generic_parameter("selected_results"),
        Parameter("plot_ax1", int, 0, name="Data axis no. 1 for plot", choices=[0]),
        Parameter("plot_ax2", int, 1, name="Data axis no. 2 for plot", choices=[0, 1]),
        get_generic_parameter("use_scan_timeline"),
    )

    def __init__(self, parent=None, select_results_param=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        ParameterWidgetsMixIn.__init__(self)
        CreateWidgetsMixIn.__init__(self)
        apply_widget_properties(self, **kwargs)
        self.params = ParameterCollection()
        self._config = {
            "widget_visibility": False,
            "result_ndim": -1,
            "plot_type": "1D plot",
            "n_slice_params": 0,
            "selection_by_data_values": True,
            "validator": QT_REG_EXP_FLOAT_SLICE_VALIDATOR,
        }
        self._active_node = -1
        if select_results_param is not None:
            self.add_param(select_results_param)
        self.set_default_params()
        self._selector = WorkflowResultsSelector(self.get_param("use_scan_timeline"))
        self.__create_widgets()
        self.__connect_signals()

    def __create_widgets(self):
        """
        Create all sub-widgets and populate the UI.
        """
        _layout = QtWidgets.QGridLayout()
        _layout.setContentsMargins(0, 5, 0, 0)
        _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setLayout(_layout)
        self.create_label("label_results", "Results:", fontsize=11, underline=True)
        self.create_param_widget(
            self.get_param("selected_results"),
            **_param_widget_config("selected_results"),
        )
        self.create_radio_button_group(
            "radio_arrangement",
            ["by scan shape", "as a timeline"],
            vertical=False,
            gridPos=(-1, 0, 1, 1),
            visible=False,
            title="Arrangement of results:",
        )
        self.create_any_widget(
            "result_info",
            ReadOnlyTextWidget,
            gridPos=(-1, 0, 1, 1),
            fixedWidth=CONFIG_WIDGET_WIDTH,
            fixedHeight=300,
            alignment=QtCore.Qt.AlignTop,
            visible=False,
        )
        self.create_radio_button_group(
            "radio_plot_type",
            ["1D plot", "group of 1D plots", "2D full axes", "2D data subset"],
            rows=2,
            columns=2,
            gridPos=(-1, 0, 1, 1),
            visible=False,
            title="Result plot type:",
            fixedWidth=CONFIG_WIDGET_WIDTH - 10,
        )
        self.create_radio_button_group(
            "radio_data_selection",
            ["Data values", "Axis index"],
            columns=2,
            gridPos=(-1, 0, 1, 1),
            visible=False,
            title="Data selection:",
            fixedWidth=CONFIG_WIDGET_WIDTH - 10,
        )
        _w = QtWidgets.QFrame()
        _w.setLayout(QtWidgets.QGridLayout())
        self.add_any_widget("plot_ax_group", _w)
        self.create_param_widget(
            self.get_param("plot_ax1"),
            parent_widget=self._widgets["plot_ax_group"],
            **_param_widget_config("plot_ax1"),
        )
        self.create_param_widget(
            self.get_param("plot_ax2"),
            parent_widget=self._widgets["plot_ax_group"],
            **_param_widget_config("plot_ax2"),
        )
        self.create_button(
            "but_confirm",
            "Confirm selection",
            fixedWidth=CONFIG_WIDGET_WIDTH,
            visible=False,
        )

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
        self.param_widgets["plot_ax1"].currentIndexChanged.connect(
            partial(self.__selected_new_plot_axis, 1)
        )
        self.param_widgets["plot_ax2"].currentIndexChanged.connect(
            partial(self.__selected_new_plot_axis, 2)
        )
        self._widgets["but_confirm"].clicked.connect(self.__confirm_selection)

    def reset(self):
        """
        Reset the instance to its default selection, for example when a new
        processing has been started and the old information is no longer valid.
        """
        self._config.update(
            {"widget_visibility": False, "result_ndim": -1, "plot_type": "1D plot"}
        )
        self._active_node = -1
        with SignalBlocker(self.param_widgets["selected_results"]):
            self.param_widgets["selected_results"].update_choices(["No selection"])
        self.param_widgets["selected_results"].setCurrentText("No selection")
        with SignalBlocker(self._widgets["radio_plot_type"]):
            self._widgets["radio_plot_type"].select_by_index(0)
        with SignalBlocker(self._widgets["radio_data_selection"]):
            self._widgets["radio_data_selection"].select_by_index(0)
        with SignalBlocker(self._widgets["radio_arrangement"]):
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
        RESULTS.update_param_choices_from_labels(_param)
        with SignalBlocker(self.param_widgets["selected_results"]):
            self.param_widgets["selected_results"].update_choices(_param.choices)
            self.param_widgets["selected_results"].setCurrentText(_param.value)

    @QtCore.Slot(str)
    def __select_type_of_plot(self, label):
        """
        Update the selection of plot dimensions.

        Parameters
        ----------
        label : str
            The index of the dimension selection.
        """
        self._config["plot_type"] = label
        self.__change_slice_param_widget_visibility()

    def __change_slice_param_widget_visibility(self, hide_all=False):
        """
        Change the visibility of Parameter selection widgets for the slice
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
        if _ax1_used:
            _frozendims.append(self.get_param_value("plot_ax1"))
        if _ax2_used:
            _frozendims.append(self.get_param_value("plot_ax2"))
        for _dim in range(self._config["n_slice_params"]):
            _refkey = f"plot_slice_{_dim}"
            _vis = (
                False
                if hide_all
                else (_dim < self._config["result_ndim"] and _dim not in _frozendims)
            )
            self.param_composite_widgets[_refkey].setVisible(_vis)

    def __are_axes_used(self):
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
    def __modify_data_selection(self, label):
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
        elif index > 0:
            self._active_node = int(
                self.param_widgets["selected_results"].currentText()[-4:-1]
            )
            self._selector.select_active_node(self._active_node)
            self.__calc_and_store_ndim_of_results()
            self.__update_text_description_of_node_results()
            self.__enable_valid_result_plot_selection()
            self.__update_dim_choices_for_plot_selection()
            self.__check_and_create_params_for_slice_selection()

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
        self._widgets["radio_plot_type"].setVisible(visible)
        self._widgets["radio_arrangement"].setVisible(visible)
        self._widgets["radio_data_selection"].setVisible(visible)
        self.param_composite_widgets["plot_ax1"].setVisible(visible)
        self.param_composite_widgets["plot_ax2"].setVisible(
            visible and (self._config["plot_type"] == 2)
        )
        self._widgets["but_confirm"].setVisible(visible)
        self.__change_slice_param_widget_visibility(hide_all=not visible)

    def __calc_and_store_ndim_of_results(self):
        """
        Update the number of dimensions the results will have and store the
        new number.
        """
        _ndim = RESULTS.ndims[self._active_node]
        _ndim_scan = np.where(
            np.asarray(RESULTS.shapes[self._active_node][: SCAN.ndim]) > 1
        )[0].size
        _ndim = np.where(np.asarray(RESULTS.shapes[self._active_node]) > 1)[0].size
        if self.get_param_value("use_scan_timeline"):
            _ndim -= _ndim_scan - 1
        self._config["result_ndim"] = _ndim

    def __update_text_description_of_node_results(self):
        """
        Update the text in the "result_info" ReadOnlyTextWidget based on the
        selection of the "selected_results" Parameter.
        """
        self._widgets["result_info"].setText(
            RESULTS.get_node_result_metadata_string(
                self._active_node, self.get_param_value("use_scan_timeline")
            )
        )
        self.__set_derived_widget_visibility(True)

    def __enable_valid_result_plot_selection(self):
        """
        Validate the dimensionality of the results and enable/disable plot choices
        accordingly.
        """
        _group = self._widgets["radio_plot_type"]
        if self._config["result_ndim"] == 1:
            self._config["plot_type"] = "1D plot"
            _group.select_by_index(0)
            for _id in [1, 2, 3]:
                _group._buttons[_id].setEnabled(False)
        else:
            for _id in [1, 2, 3]:
                _group._buttons[_id].setEnabled(True)

    @QtCore.Slot(int)
    def __arrange_results_in_timeline_or_scan_shape(self, index):
        """
        Get and store the current selection for the organization of the
        scan results in a timeline or using the SetupScan shape.

        This method also updates the text in the ReadOnlyTextWidget to
        reflect the selection of the dimensions of the scan.

        Parameters
        ----------
        index : int
            The index of the newly activated button.
        """
        self.set_param_value("use_scan_timeline", bool(index))
        self.__calc_and_store_ndim_of_results()
        self.__update_text_description_of_node_results()
        self.__update_dim_choices_for_plot_selection()
        self.__change_slice_param_widget_visibility()

    @QtCore.Slot(int, str)
    def __selected_new_plot_axis(self, plot_axis, new_dim):
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
        new_dim = int(new_dim)
        _selected_param = self.params[f"plot_ax{plot_axis}"]
        _selected_param.value = new_dim
        self.param_widgets[f"plot_ax{plot_axis}"].set_value(_selected_param.value)

        _other_param = self.params[f"plot_ax{_other_ax}"]
        if _other_param.value == new_dim:
            if new_dim == _other_param.choices[0]:
                _other_param.value = _other_param.choices[1]
            else:
                _other_param.value = _other_param.choices[0]
            self.param_widgets[f"plot_ax{_other_ax}"].set_value(_other_param.value)
        self.__change_slice_param_widget_visibility()

    @QtCore.Slot()
    def __confirm_selection(self):
        """
        Confirm the selection of axes for the plot and sends a signal.

        The signal has the following form:
            bool, int, tuple

        With the first entry a flag to use a timeline (ie. flattening of scan
        dimensions) and the tuple with the slicing object. The second entry
        is the dimensionality of the resulting data. The third entry is the
        slice object required to access the selected subset of data from the
        full array.
        """
        self._selector.select_active_node(self._active_node)
        self._selector.set_param_value(
            "use_data_range", self._config["selection_by_data_values"]
        )
        for _dim in range(self._config["result_ndim"]):
            self._selector.set_param_value(
                f"data_slice_{_dim}", self.get_param_value(f"plot_slice_{_dim}")
            )
        _target_dim = 1 if self._config["plot_type"] == "1D plot" else 2
        self._selector.set_param_value("result_n_dim", _target_dim)
        _active_dims = self.__process_active_dims()
        _selection = self._selector.selection
        self.new_selection.emit(
            self.get_param_value("use_scan_timeline"),
            _active_dims,
            self._active_node,
            _selection,
            self._config["plot_type"],
        )

    def __process_active_dims(self):
        """
        Process the active dimensions for the plot.

        This method will update the necessary values in the
        WorkflowResultSelector and return the active dimensions.

        Returns
        -------
        list
            The active dimensions in form of integer entries.
        """
        if self._config["plot_type"] in ["1D plot", "group of 1D plots"]:
            _active_dim = self.get_param_value("plot_ax1")
            self._selector.set_param_value(f"data_slice_{_active_dim}", ":")
            return [_active_dim]
        if self._config["plot_type"] == "2D full axes":
            _active_dim1 = self.get_param_value("plot_ax1")
            self._selector.set_param_value(f"data_slice_{_active_dim1}", ":")
            _active_dim2 = self.get_param_value("plot_ax2")
            self._selector.set_param_value(f"data_slice_{_active_dim2}", ":")
            return [_active_dim1, _active_dim2]
        if self._config["plot_type"] == "2D data subset":
            return self._selector.active_dims
        raise ValueError("Undefined plot type.")

    def __update_dim_choices_for_plot_selection(self):
        """
        Calculate and update the basic dimension choices for the plot
        slicing.
        """
        _new_choices = list(np.arange((self._config["result_ndim"])))
        for _ax in [1, 2]:
            _axwidget = self.param_widgets[f"plot_ax{_ax}"]
            _axparam = self.params[f"plot_ax{_ax}"]
            _curr_choices = _axparam.choices
            if _axparam.value not in _new_choices:
                _axparam.choices = _curr_choices + [_new_choices[0]]
                _axparam.value = _new_choices[0]
            _axparam.choices = _new_choices
            with SignalBlocker(_axwidget):
                _axwidget.update_choices(_new_choices)
                _axwidget.setCurrentIndex(_axparam.value)
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
        Check whether the required Parameters for the slice selection exist
        and create and add them if they do not.
        """
        for _dim in range(RESULTS.ndims[self._active_node]):
            _refkey = f"plot_slice_{_dim}"
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
            )
            if _refkey not in self.params:
                self.add_param(_param)
                self.create_param_widget(
                    _param,
                    parent_widget=self._widgets["plot_ax_group"],
                    **_param_widget_config(_refkey),
                )
                self.param_widgets[_refkey].setValidator(self._config["validator"])
        self._config["n_slice_params"] = max(
            self._config["n_slice_params"], RESULTS.ndims[self._active_node]
        )
        self.__change_slice_param_widget_visibility()
