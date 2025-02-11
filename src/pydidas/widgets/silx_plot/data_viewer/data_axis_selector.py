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
__all__ = ["DataAxisSelector"]

from typing import Optional

import numpy as np
from numpy import ndarray
from qtpy import QtCore, QtGui, QtWidgets

from pydidas.widgets.factory import SquareButton
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class DataAxisSelector(WidgetWithParameterCollection):
    """
    A widget to select a data point on a specific axis.
    """

    sig_new_slicing = QtCore.Signal(int, str)
    sig_display_choice_changed = QtCore.Signal(int, str)

    def __init__(self, index: int, parent=None, **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, parent=parent, **kwargs)
        self._axis_index = index
        self._current_index = 0
        self._npoints = 0
        self._data_range = None
        self._data_unit = ""
        self._data_label = ""
        self._external_display_choices = ""
        self._all_choices = []

        self.create_label(
            "label_axis",
            f"Dim {self._axis_index}",
            font_metric_width_factor=28,
            gridPos=(0, -1, 1, 1),
        )
        self.create_combo_box(
            "combo_axis_use",
            gridPos=(0, -1, 1, 1),
            items=["slice at index"],
            font_metric_width_factor=25,
        )
        self.add_any_widget(
            "slider",
            QtWidgets.QSlider(QtCore.Qt.Horizontal),
            gridPos=(0, -1, 1, 1),
        )
        self.layout().setColumnStretch(self.layout().columnCount() - 1, 6)
        self.add_any_widget(
            "button_start",
            SquareButton(icon="mdi::skip-backward"),
            gridPos=(0, -1, 1, 1),
        )
        self.add_any_widget(
            "button_backward",
            SquareButton(icon="mdi::step-backward"),
            gridPos=(0, -1, 1, 1),
        )
        self.create_lineedit(
            "edit_index",
            font_metric_width_factor=10,
            gridPos=(0, -1, 1, 1),
            text="0",
            validator=QtGui.QIntValidator(),
        )
        self.create_lineedit(
            "edit_data",
            font_metric_width_factor=10,
            gridPos=(0, -1, 1, 1),
            text="0.0",
            validator=QtGui.QDoubleValidator(),
            visible=False,
        )
        self.create_label(
            "label_unit",
            "",
            font_metric_width_factor=10,
            gridPos=(0, -1, 1, 1),
            visible=False,
        )
        self.add_any_widget(
            "button_forward",
            SquareButton(icon="mdi::step-forward"),
            gridPos=(0, -1, 1, 1),
        )
        self.add_any_widget(
            "button_end",
            SquareButton(icon="mdi::skip-forward"),
            gridPos=(0, -1, 1, 1),
        )

        self.create_spacer("final_spacer", fixedHeight=5, gridPos=(0, -1, 1, 1))
        self.__spacer_column = self.layout().columnCount() - 1
        self.layout().setColumnStretch(self.__spacer_column, 1)

        self._widgets["combo_axis_use"].currentTextChanged.connect(
            self._axis_use_changed
        )
        self._widgets["slider"].valueChanged.connect(self._slider_changed)
        self._widgets["edit_index"].editingFinished.connect(self._manual_index_changed)
        self._widgets["edit_data"].editingFinished.connect(
            self._manual_data_value_changed
        )
        self._widgets["button_start"].clicked.connect(self._clicked_start)
        self._widgets["button_backward"].clicked.connect(self._clicked_backward)
        self._widgets["button_forward"].clicked.connect(self._clicked_forward)
        self._widgets["button_end"].clicked.connect(self._clicked_end)

    @property
    def npoints(self) -> int:
        """
        Get the number of points in the axis.

        Returns
        -------
        int
            The number of points in the axis.
        """
        return self._npoints

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
            raise ValueError(f"Invalid choice {choice}")
        self._widgets["combo_axis_use"].setCurrentText(choice)

    @property
    def current_slice(self) -> slice:
        """
        Get the current slice.

        Returns
        -------
        slice
            The current slice.
        """
        _current_choice = self._widgets["combo_axis_use"].currentText()
        if _current_choice == "slice at index":
            return slice(self._current_index, self._current_index + 1)
        elif _current_choice == "slice at data value":
            return slice(self._current_index, self._current_index + 1)
        return slice(None)

    @property
    def current_slice_str(self) -> str:
        """
        Get the string representation of the current slice.

        Returns
        -------
        str
            The string representation of the current slice.
        """
        _start = self.current_slice.start
        return "::None::" if _start is None else str(_start)

    @QtCore.Slot(ndarray, str, str)
    def set_axis_metadata(
        self,
        data_range: Optional[ndarray],
        label: str = "",
        unit: str = "",
        npoints: Optional[int] = None,
    ):
        """
        Set the metadata for the axis.

        Parameters
        ----------
        data_range : Optional[ndarray]
            The axis values. If None, selecting by data value is disabled.
        label : str, optional
            The label of the axis.
        unit : str,  optional
            The unit of the axis.
        npoints : int, optional
            The number of points in the axis. This is only required if data_range
            is None and ignored if data_range is given.
        """
        if data_range is None:
            if npoints is None:
                raise ValueError("npoints must be given if data_range is None")
            label, unit = None, None
            self._npoints = npoints
            self._widgets["slider"].setRange(0, self._npoints - 1)
        self._data_range = data_range
        self._data_unit = unit if unit is not None else ""
        self._data_label = label if label is not None else ""
        if len(self._data_label) > 20:
            self._data_label = self._data_label[:16] + " ..."
        self._widgets["label_axis"].setText(
            f"Dim {self._axis_index}"
            + (f" ({self._data_label})" if len(self._data_label) > 0 else "")
        )
        self._widgets["label_unit"].setText(
            f" [{self._data_unit}]" if len(self._data_unit) > 0 else ""
        )
        if self._data_range is not None:
            self._npoints = data_range.size
            self._widgets["slider"].setRange(0, self._npoints - 1)
            self._widgets["slider"].setSliderPosition(0)
        self.define_additional_choices(self._external_display_choices)

    @QtCore.Slot(str)
    def define_additional_choices(self, choices: str):
        """
        Set additional choices for the combobox.

        Multiple choices can be separated by ';;'.

        Parameters
        ----------
        choices : str
            The new choices for the combobox as a single string.
        """
        self._external_display_choices = choices
        _old_choice = self._widgets["combo_axis_use"].currentText()
        self._all_choices = ["slice at index"]
        if self._data_range is not None:
            self._all_choices.append("slice at data value")
        self._all_choices.extend(
            [_item for _item in choices.split(";;") if len(_item) > 0]
        )
        with QtCore.QSignalBlocker(self._widgets["combo_axis_use"]):
            self._widgets["combo_axis_use"].clear()
            self._widgets["combo_axis_use"].addItems(self._all_choices)
            if _old_choice in self._all_choices:
                self._widgets["combo_axis_use"].setCurrentText(_old_choice)
        if _old_choice not in self._all_choices:
            self._widgets["combo_axis_use"].currentTextChanged.emit(
                self._widgets["combo_axis_use"].currentText()
            )

    @QtCore.Slot(str)
    def _axis_use_changed(self, use_selection: str):
        """
        Show the correct widgets for the selected axis use.

        Parameters
        ----------
        use_selection : str
            The selected axis use case.
        """
        self._widgets["edit_index"].setVisible(use_selection == "slice at index")
        for _key in ["edit_data", "label_unit"]:
            self._widgets[_key].setVisible(use_selection == "slice at data value")
        _show = use_selection in ["slice at data value", "slice at index"]
        for _key in [
            "slider",
            "button_start",
            "button_backward",
            "button_forward",
            "button_end",
        ]:
            self._widgets[_key].setVisible(_show)
        if _show:
            self.layout().removeItem(self._widgets["final_spacer"])
        else:
            self.layout().addItem(
                self._widgets["final_spacer"], 0, self.__spacer_column
            )
        self.sig_display_choice_changed.emit(self._axis_index, use_selection)

    @QtCore.Slot(int)
    def _slider_changed(self, value: int):
        """
        Handle changes from users dragging the slider.

        Parameters
        ----------
        value : int
            The new slider value.
        """
        self._current_index = value
        with QtCore.QSignalBlocker(self._widgets["edit_index"]):
            self._widgets["edit_index"].setText(str(value))
        if self._data_range is not None:
            with QtCore.QSignalBlocker(self._widgets["edit_data"]):
                self._widgets["edit_data"].setText(f"{self._data_range[value]:.4f}")
        self.sig_new_slicing.emit(self._axis_index, self.current_slice_str)

    @QtCore.Slot()
    def _manual_index_changed(self):
        """
        Handle changes from users entering a new index manually.
        """
        _entry = self._widgets["edit_index"].text()
        self._current_index = max(0, min(self._npoints - 1, int(_entry)))
        with QtCore.QSignalBlocker(self._widgets["edit_index"]):
            self._widgets["edit_index"].setText(str(self._current_index))
        with QtCore.QSignalBlocker(self._widgets["edit_data"]):
            self._widgets["edit_data"].setText(
                f"{self._data_range[self._current_index]:.4f}"
            )
        with QtCore.QSignalBlocker(self._widgets["slider"]):
            self._widgets["slider"].setSliderPosition(self._current_index)
        self.sig_new_slicing.emit(self._axis_index, self.current_slice_str)

    @QtCore.Slot()
    def _manual_data_value_changed(self):
        """
        Handle changes from users entering a new data value manually.
        """
        _value = float(self._widgets["edit_data"].text())
        _index = np.argmin(np.abs(self._data_range - _value))
        self._current_index = _index
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
        self._move_to_index(max(0, self._current_index - 1))

    @QtCore.Slot()
    def _clicked_forward(self):
        """
        Handle the click on the forward button.
        """
        self._move_to_index(min(self._npoints - 1, self._current_index + 1))

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
        if index == self._current_index:
            return
        self._current_index = index
        with QtCore.QSignalBlocker(self._widgets["slider"]):
            self._widgets["slider"].setSliderPosition(index)
        with QtCore.QSignalBlocker(self._widgets["edit_index"]):
            self._widgets["edit_index"].setText(str(index))
        if self._data_range is not None:
            with QtCore.QSignalBlocker(self._widgets["edit_data"]):
                self._widgets["edit_data"].setText(f"{self._data_range[index]:.4f}")
        self.sig_new_slicing.emit(self._axis_index, self.current_slice_str)

    def closeEvent(self, event: QtCore.QEvent):
        for child in self.findChildren(QtWidgets.QWidget):
            child.deleteLater()
        QtWidgets.QWidget.closeEvent(self, event)


if __name__ == "__main__":
    import pydidas_qtcore

    app = pydidas_qtcore.PydidasQApplication([])
    window = DataAxisSelector(0)
    window.set_axis_metadata(
        0.643 * np.arange(20), "Distance and other things to be used", "m"
    )
    window.define_additional_choices("choice1;;choice2")
    window.display_choice = "slice at data value"
    window.show()
    app.exec_()
