# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the DataAxisSelector class which allows to select a datapoint
on a specific axis.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataAxisSelector", "GENERIC_AXIS_SELECTOR_CHOICES"]


from functools import partial

import numpy as np
from numpy import ndarray
from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import UserConfigError
from pydidas.widgets.data_viewer.data_viewer_utils import (
    get_data_axis_header_creation_args,
    get_data_axis_widget_creation_args,
    invalid_range_str,
)
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


GENERIC_AXIS_SELECTOR_CHOICES = ["slice at index", "slice at data value"]


class DataAxisSelector(WidgetWithParameterCollection, PydidasWidgetMixin):
    """
    A widget to select a data point on a specific axis.
    """

    init_kwargs = WidgetWithParameterCollection.init_kwargs + ["multiline_layout"]

    sig_new_slicing = QtCore.Signal(int, str)
    sig_display_choice_changed = QtCore.Signal(int, str)

    def __init__(
        self, index: int, parent: QtWidgets.QWidget | None = None, **kwargs: dict
    ):
        WidgetWithParameterCollection.__init__(self, parent=parent, **kwargs)
        PydidasWidgetMixin.__init__(self, **kwargs)
        self._axis_index = index
        self._current_slice = slice(0, 1)
        self._npoints = 0
        self._ndim = None
        self._data_range = None
        self._data_unit = ""
        self._data_label = ""
        self._external_display_choices = ""
        self._all_choices = ["slice at index"]
        self._stored_configs = {}
        self._use_multiline = kwargs.get("multiline", False)
        self._last_slicing_at_index = True
        self._create_widgets()
        self._connect_signals()
        self.layout().setHorizontalSpacing(5)

    def _create_widgets(self):
        """
        Create the widgets for the DataAxisSelector.
        """
        _header = get_data_axis_header_creation_args(
            self._axis_index, self._use_multiline
        )
        for _method_name, _args, _kwargs in _header:
            _method = getattr(self, _method_name)
            _method(*_args, **_kwargs)
        if self._use_multiline:
            self.create_empty_widget("point_selection_container", gridPos=(3, 0, 1, 2))
        else:
            self.layout().setColumnStretch(self.layout().columnCount() - 1, 6)
        _entries = get_data_axis_widget_creation_args(self._use_multiline)
        for _method_name, _args, _kwargs in _entries:
            _method = getattr(self, _method_name)
            _method(*_args, **_kwargs)
            if "slider" in _args and not self._use_multiline:
                _nitems = self.layout().count()
                _column = self.layout().getItemPosition(_nitems - 1)[1]
                self.layout().setColumnStretch(_column, 8)

    def _connect_signals(self):
        """
        Connect the signals of the DataAxisSelector.
        """
        self._widgets["combo_axis_use"].currentTextChanged.connect(
            self._handle_new_axis_use
        )
        self._widgets["slider"].valueChanged.connect(self._new_index_selection)
        self._widgets["edit_index"].editingFinished.connect(self._manual_index_changed)
        self._widgets["edit_data"].editingFinished.connect(
            self._manual_data_value_changed
        )
        self._widgets["button_start"].clicked.connect(self._clicked_start)
        self._widgets["button_backward"].clicked.connect(self._clicked_backward)
        self._widgets["button_forward"].clicked.connect(self._clicked_forward)
        self._widgets["button_end"].clicked.connect(self._clicked_end)
        self._widgets["combo_range"].currentTextChanged.connect(
            self._handle_range_selection
        )
        self._widgets["edit_range_index"].editingFinished.connect(
            self._handle_new_index_range_selection
        )
        self._widgets["edit_range_data"].editingFinished.connect(
            self._handle_new_data_range_selection
        )
        for _key in ["edit_range_data", "edit_range_index"]:
            self._widgets[_key].textChanged.connect(
                partial(self._check_edit_range_input, _key)
            )
        self._palette_base = self._widgets["edit_range_data"].palette()
        self._palette_highlight = QtGui.QPalette(self._palette_base)
        self._palette_highlight.setColor(QtGui.QPalette.Base, QtGui.QColor("#FFA07A"))

    @property
    def npoints(self) -> int:
        """Get the number of points in the axis."""
        return self._npoints

    @property
    def data_label(self) -> str:
        """Get the label of the axis."""
        return self._data_label

    @property
    def data_unit(self) -> str:
        """Get the unit of the axis."""
        return self._data_unit

    @property
    def data_range(self) -> ndarray | None:
        """Get the axis values. If not specified, this will be None."""
        return self._data_range

    @property
    def display_choice(self) -> str:
        """
        Get the current display choice.

        Returns
        -------
        str
            The current display choice.
        """
        return self._widgets["combo_axis_use"].currentText()

    @display_choice.setter
    def display_choice(self, choice: str):
        """
        Set the display choice.

        Parameters
        ----------
        choice : str
            The choice to set.
        """
        if choice not in self._all_choices:
            raise ValueError(f"Invalid choice: `{choice}`")
        self._widgets["combo_axis_use"].setCurrentText(choice)

    @property
    def available_choices(self) -> list[str]:
        """
        Get the available display choices.

        Returns
        -------
        list[str]
            The available display choices.
        """
        return self._all_choices.copy()

    @property
    def current_slice(self) -> slice:
        """
        Get the current slice.

        Returns
        -------
        slice
            The current slice.
        """
        return self._current_slice

    @property
    def current_slice_str(self) -> str:
        """
        Get the string representation of the current slice.

        Returns
        -------
        str
            The string representation of the current slice.
        """
        return f"{self.current_slice.start}:{self.current_slice.stop}"

    @QtCore.Slot(ndarray, str, str)
    def set_axis_metadata(
        self,
        data_range: ndarray | None,
        label: str = "",
        unit: str = "",
        npoints: int | None = None,
        ndim: int | None = None,
    ):
        """
        Set the metadata for the axis.

        Parameters
        ----------
        data_range : ndarray, optional
            The axis values. If None, selecting by data value is disabled.
        label : str, optional
            The label of the axis.
        unit : str,  optional
            The unit of the axis.
        npoints : int, optional
            The number of points in the axis. This is only required if data_range
            is None and ignored if data_range is given.
        ndim : int, optional
            The number of dimensions in the data. This is only required if the
            generic choices should be hidden.
        """
        if data_range is None:
            if npoints is None:
                raise ValueError("npoints must be given if data_range is None")
            label, unit = "", ""
            self._npoints = npoints
        else:
            self._npoints = data_range.size
        self._ndim = ndim
        self._data_range = data_range
        self._data_unit = unit if unit is not None else ""
        self._data_label = label if label is not None else ""
        _max_length = 20 if not self._use_multiline else 45
        if len(self._data_label) > _max_length:
            self._data_label = self._data_label[: _max_length - 4] + " ..."
        self._widgets["label_axis"].setText(
            f"Dim {self._axis_index}"
            + (f" ({self._data_label})" if len(self._data_label) > 0 else "")
        )
        self._widgets["label_unit"].setText(
            f" [{self._data_unit}]" if len(self._data_unit) > 0 else ""
        )
        self._widgets["slider"].setRange(0, self._npoints - 1)
        self._widgets["slider"].setSliderPosition(0)
        self._widgets["edit_range_index"].setText(f"0:{self._npoints}")
        if self._data_range is not None:
            self._widgets["edit_range_data"].setText(
                f"{self._data_range[0]:.4f}:{self._data_range[-1]:.4f}"
            )
        self._stored_configs = {}
        self.define_additional_choices(
            self._external_display_choices, store_config=False
        )
        self._update_slice_from_choice(self.display_choice)

    @QtCore.Slot(str)
    def define_additional_choices(self, choices: str, store_config: bool = True):
        """
        Set additional choices for the combobox.

        Multiple choices can be separated by ';;'.

        Parameters
        ----------
        choices : str
            The new choices for the combobox as a single string.
        store_config : bool
            If True, the current configuration will be stored.
        """
        if store_config:
            self._stored_configs[self._external_display_choices] = (
                self._widgets["combo_axis_use"].currentText(),
                self._widgets["combo_range"].currentText(),
                self.current_slice,
            )
        self._external_display_choices = choices
        _old_choice = self._widgets["combo_axis_use"].currentText()
        _new_choices = [_item for _item in choices.split(";;") if len(_item) > 0]
        self._all_choices = []
        if self._ndim is None or self._ndim > len(_new_choices):
            self._all_choices.append("slice at index")
            if self._data_range is not None:
                self._all_choices.append("slice at data value")
        self._all_choices.extend(_new_choices)
        with QtCore.QSignalBlocker(self._widgets["combo_axis_use"]):
            self._widgets["combo_axis_use"].clear()
            self._widgets["combo_axis_use"].addItems(self._all_choices)
            if _old_choice in self._all_choices:
                self._widgets["combo_axis_use"].setCurrentText(_old_choice)
        if _old_choice not in self._all_choices:
            self._widgets["combo_axis_use"].currentTextChanged.emit(
                self._widgets["combo_axis_use"].currentText()
            )
        if choices in self._stored_configs:
            self._restore_old_config(choices)

    def _restore_old_config(self, choices: str):
        """
        Restore the configuration, based on the available choices.
        """
        _ax_use, _range_choice, _slice = self._stored_configs[choices]
        with QtCore.QSignalBlocker(self):
            self._widgets["combo_axis_use"].setCurrentText(_ax_use)
            self._widgets["combo_range"].setCurrentText(_range_choice)
            if (
                _slice.stop - _slice.start == 1
                and _ax_use in GENERIC_AXIS_SELECTOR_CHOICES
            ):
                self._move_to_index(_slice.start)
            else:
                self._current_slice = _slice
                self._widgets["edit_range_index"].setText(
                    f"{_slice.start}:{_slice.stop - 1}"
                )
                self._handle_new_index_range_selection()

    @QtCore.Slot(str)
    def _handle_new_axis_use(self, use_selection: str):
        """
        Handle the input of a new axis use case by the user.

        Parameters
        ----------
        use_selection : str
            The selected axis use case.
        """
        self._widgets["edit_index"].setVisible(use_selection == "slice at index")
        for _key in ["edit_data", "label_unit"]:
            self._widgets[_key].setVisible(use_selection == "slice at data value")
        if use_selection == "slice at data value":
            self._last_slicing_at_index = False
        elif use_selection == "slice at index":
            self._last_slicing_at_index = True
        _show_slider = use_selection in GENERIC_AXIS_SELECTOR_CHOICES
        for _key in [
            "slider",
            "button_start",
            "button_backward",
            "button_forward",
            "button_end",
        ]:
            self._widgets[_key].setVisible(_show_slider)
        _range_selection = self._widgets["combo_range"].currentText()
        _show_range = use_selection not in GENERIC_AXIS_SELECTOR_CHOICES
        self._widgets["combo_range"].setVisible(_show_range)
        self._widgets["edit_range_index"].setVisible(
            _range_selection == "select range by indices" and _show_range
        )
        self._widgets["edit_range_data"].setVisible(
            _range_selection == "select range by data values" and _show_range
        )
        self._update_slice_from_choice(use_selection)
        self.sig_display_choice_changed.emit(self._axis_index, use_selection)

    def _update_slice_from_choice(self, use_selection: str):
        """
        Update the slice based on the choice.

        Parameters
        ----------
        use_selection : str
            The selected axis use case.
        """
        with QtCore.QSignalBlocker(self):
            if use_selection not in GENERIC_AXIS_SELECTOR_CHOICES:
                self._update_slice_from_non_generic_choice()
            elif use_selection == "slice at data value":
                self._manual_data_value_changed()
            elif use_selection == "slice at index":
                self._manual_index_changed()

    def _update_slice_from_non_generic_choice(self):
        """
        Set the widgets to use the full axis.
        """
        if self._widgets["combo_range"].currentText() == "use full axis":
            self._current_slice = slice(0, self._npoints)
        elif self._widgets["combo_range"].currentText() == "select range by indices":
            _range = self._widgets["edit_range_index"].text().split(":")
            if len(_range) != 2:
                raise UserConfigError("Invalid range syntax")
            self._current_slice = slice(int(_range[0]), int(_range[1]))
        elif (
            self._widgets["combo_range"].currentText() == "select range by data values"
        ):
            if self._data_range is None:
                self._widgets["combo_range"].setCurrentText("use full axis")
                return
            _range = self._widgets["edit_range_data"].text().split(":")
            if len(_range) != 2:
                raise UserConfigError("Invalid range syntax")
            _start = np.argmin(np.abs(self._data_range - float(_range[0])))
            _end = np.argmin(np.abs(self._data_range - float(_range[1])))
            self._current_slice = slice(_start, _end)
        self.sig_new_slicing.emit(self._axis_index, self.current_slice_str)

    @QtCore.Slot()
    def _manual_index_changed(self):
        """
        Handle changes from users entering a new index manually.
        """
        _index = max(0, min(self._npoints - 1, int(self._widgets["edit_index"].text())))
        with QtCore.QSignalBlocker(self._widgets["slider"]):
            self._widgets["slider"].setSliderPosition(_index)
        self._new_index_selection(_index)

    @QtCore.Slot(int)
    def _new_index_selection(self, index: int):
        """
        Handle a new index selection.

        Parameters
        ----------
        index : int
            The new index.
        """
        self._current_slice = slice(index, index + 1)
        with QtCore.QSignalBlocker(self._widgets["edit_index"]):
            self._widgets["edit_index"].setText(str(index))
        if self._data_range is not None:
            with QtCore.QSignalBlocker(self._widgets["edit_data"]):
                self._widgets["edit_data"].setText(f"{self._data_range[index]:.4f}")
        self.sig_new_slicing.emit(self._axis_index, self.current_slice_str)

    @QtCore.Slot()
    def _manual_data_value_changed(self):
        """
        Handle changes from users entering a new data value manually.
        """
        _value = float(self._widgets["edit_data"].text())
        _index = np.argmin(np.abs(self._data_range - _value))
        self._current_slice = slice(_index, _index + 1)
        with QtCore.QSignalBlocker(self._widgets["edit_index"]):
            self._widgets["edit_index"].setText(str(_index))
        with QtCore.QSignalBlocker(self._widgets["slider"]):
            self._widgets["slider"].setSliderPosition(_index)
        with QtCore.QSignalBlocker(self._widgets["edit_data"]):
            self._widgets["edit_data"].setText(f"{self._data_range[_index]:.4f}")
        self.sig_new_slicing.emit(self._axis_index, self.current_slice_str)

    @QtCore.Slot()
    def _clicked_start(self):
        """
        Handle the click on the start button.
        """
        self._move_to_index(0)

    @QtCore.Slot()
    def _clicked_backward(self):
        """
        Handle the click on the backward button.
        """
        self._move_to_index(max(0, self._current_slice.start - 1))

    @QtCore.Slot()
    def _clicked_forward(self):
        """
        Handle the click on the forward button.
        """
        self._move_to_index(min(self._npoints - 1, self._current_slice.start + 1))

    @QtCore.Slot()
    def _clicked_end(self):
        """
        Handle the click on the end button.
        """
        self._move_to_index(self._npoints - 1)

    def _move_to_index(self, index: int):
        """
        Set the widgets to the given index.

        Parameters
        ----------
        index : int
            The new index.
        """
        if (
            self._widgets["combo_axis_use"].currentText()
            not in GENERIC_AXIS_SELECTOR_CHOICES
        ):
            raise UserConfigError(
                "Cannot move to individual index for a range-selecting choice."
            )
        if index == self._current_slice.start:
            return
        with QtCore.QSignalBlocker(self._widgets["slider"]):
            self._widgets["slider"].setSliderPosition(index)
        self._new_index_selection(index)

    @QtCore.Slot(str)
    def _handle_range_selection(self, selection: str):
        """
        Handle the selection of a range selection method by the user.

        Parameters
        ----------
        selection : str
            The selected range selection method.
        """
        _index_edit_visible = selection == "select range by indices"
        _data_edit_visible = selection == "select range by data values"
        if selection == "select range by indices":
            self._handle_new_index_range_selection()
        elif selection == "select range by data values":
            self._handle_new_data_range_selection()
        self._widgets["edit_range_index"].setVisible(_index_edit_visible)
        self._widgets["edit_range_data"].setVisible(_data_edit_visible)

    @QtCore.Slot()
    def _handle_new_index_range_selection(self):
        """
        Handle the input of a new index range by the user.

        Note: The indexing is inclusive of the last data point, contrary to
        Python slicing.
        """
        _input = self._widgets["edit_range_index"].text()
        _range = _input.split(":")
        if len(_range) != 2:
            raise UserConfigError(invalid_range_str(_input))
        try:
            _start = max(0, min(self._npoints, int(_range[0])))
            _stop = min(self._npoints, max(0, int(_range[1]) + 1))
        except ValueError:
            raise UserConfigError(invalid_range_str(_input))
        # need to set to stop -1 because the slicing index is incremented to
        # include the last point
        self._widgets["edit_range_index"].setText(f"{_start}:{_stop - 1}")
        if (_start, _stop) == (self._current_slice.start, self._current_slice.stop):
            return
        self._current_slice = slice(_start, _stop)
        with QtCore.QSignalBlocker(self._widgets["edit_range_data"]):
            self._widgets["edit_range_data"].setText(
                f"{self._data_range[_start]:.4f}:{self._data_range[_stop - 1]:.4f}"
            )
        self.sig_new_slicing.emit(self._axis_index, self.current_slice_str)

    @QtCore.Slot()
    def _handle_new_data_range_selection(self):
        """
        Handle the input of a new data range by the user.

        Note: The indexing is defined to include the last point in the range,
        contrary to Python slicing.
        """
        _input = self._widgets["edit_range_data"].text()
        _range = _input.split(":")
        if len(_range) != 2:
            raise UserConfigError(invalid_range_str(_input))
        try:
            _start = np.argmin(np.abs(self._data_range - float(_range[0])))
            _stop = np.argmin(np.abs(self._data_range - float(_range[1]))) + 1
        except ValueError:
            raise UserConfigError(invalid_range_str(_input))
        # need to set to stop -1 because the slicing index is incremented to
        # include the last point
        _new_input = f"{self._data_range[_start]:.4f}:{self._data_range[_stop - 1]:.4f}"
        self._widgets["edit_range_data"].setText(_new_input)
        if (_start, _stop) == (self._current_slice.start, self._current_slice.stop):
            return
        self._current_slice = slice(_start, _stop)
        with QtCore.QSignalBlocker(self._widgets["edit_range_index"]):
            self._widgets["edit_range_index"].setText(f"{_start}:{_stop - 1}")
        self.sig_new_slicing.emit(self._axis_index, self.current_slice_str)

    def _check_edit_range_input(self, edit_name: str):
        """
        Check the input of the range edit widget.

        Parameters
        ----------
        edit_name : str
            The name of the edit widget.
        """
        if self._widgets[edit_name].hasAcceptableInput():
            self._widgets[edit_name].setPalette(self._palette_base)
        else:
            self._widgets[edit_name].setPalette(self._palette_highlight)

    def reset_to_slicing(self):
        """
        Reset the widget to the slicing state.
        """
        _slice_type = (
            "slice at index" if self._last_slicing_at_index else "slice at data value"
        )
        self._widgets["combo_axis_use"].setCurrentText(_slice_type)

    def closeEvent(self, event: QtCore.QEvent):
        for child in self.findChildren(QtWidgets.QWidget):
            child.deleteLater()
        QtWidgets.QWidget.closeEvent(self, event)
