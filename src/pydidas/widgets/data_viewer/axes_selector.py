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
Module with the AxesSelector which allows to select slicing for a dataset.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AxesSelector"]

from typing import Optional

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.core import Dataset, UserConfigError
from pydidas.core.constants import POLICY_EXP_FIX
from pydidas.widgets.data_viewer.data_axis_selector import (
    _GENERIC_CHOICES,
    DataAxisSelector,
)
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class AxesSelector(WidgetWithParameterCollection):
    sig_new_slicing = QtCore.Signal()
    sig_new_slicing_str_repr = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, parent=parent, **kwargs)
        self._axwidgets = {}
        self._data_shape = ()
        self._data_ndim = 0
        self._additional_choices_str = ""
        self._additional_choices = []
        self._current_slice_strings = {}
        self._current_slice = []
        self._multiline_layout = kwargs.get("multiline_layout", False)
        self.layout().setColumnStretch(0, 1)
        self.create_spacer("final_spacer", gridPos=(0, 1, 1, 1), fixedWidth=5)

    @property
    def current_display_selection(self) -> tuple[str]:
        """
        Get the current display selection.

        Returns
        -------
        tuple[str]
            The current display selection.
        """
        return tuple(
            self._axwidgets[_dim].display_choice for _dim in range(self._data_ndim)
        )

    @property
    def current_slice_str(self) -> str:
        """The string representation of the current slicing."""
        return ";;".join(
            f"{_dim}::{_slice}" for _dim, _slice in self._current_slice_strings.items()
        )

    @property
    def current_slice(self) -> list[slice]:
        """The current slicing."""
        return self._current_slice

    def set_data_shape(self, shape: tuple[int]):
        """
        Set the shape of the data to be sliced.

        Parameters
        ----------
        shape : tuple[int]
            The shape of the data to be sliced.
        """
        if not isinstance(shape, tuple):
            raise UserConfigError(
                f"Invalid data shape `{shape}`. Please provide a tuple."
            )
        self._data_shape = shape
        self._data_ndim = len(shape)
        self._create_data_axis_selectors()
        for _dim, _npoints in enumerate(shape):
            self._axwidgets[_dim].set_axis_metadata(None, "", "", npoints=_npoints)

    def _create_data_axis_selectors(self):
        """
        Create the DataAxisSelector widgets for the axes.
        """
        for _dim in range(self._data_ndim):
            if _dim not in self._axwidgets:
                self.add_any_widget(
                    f"axis_{_dim}",
                    DataAxisSelector(_dim, multiline=self._multiline_layout),
                    gridPos=(-1, 0, 1, 1),
                    sizePolicy=POLICY_EXP_FIX,
                )
                if self._multiline_layout:
                    self.create_line(f"line_{_dim}", gridPos=(-1, 0, 1, 1))
                self._current_slice.append(slice(None))
                self._axwidgets[_dim] = self._widgets[f"axis_{_dim}"]
                self._axwidgets[_dim].define_additional_choices(
                    self._additional_choices_str
                )
                self._axwidgets[_dim].sig_display_choice_changed.connect(
                    self._process_new_display_choice
                )
                self._axwidgets[_dim].sig_new_slicing.connect(self._update_ax_slicing)
        for _key in self._axwidgets:
            self._axwidgets[_key].setVisible(_key < self._data_ndim)
            if self._multiline_layout:
                self._widgets[f"line_{_key}"].setVisible(_key < self._data_ndim)

            if _key >= self._data_ndim:
                with QtCore.QSignalBlocker(self._axwidgets[_key]):
                    self._axwidgets[_key].display_choice = "slice at index"

    def set_axis_metadata(
        self,
        axis: int,
        data_range: Optional[np.ndarray],
        label: str = "",
        unit: str = "",
        npoints: Optional[int] = None,
    ):
        """
        Set the metadata for an axis.

        Parameters
        ----------
        axis : int
            The axis index.
        data_range : Optional[np.ndarray]
            The data range for the axis. Set to None, if no metadata for the
            range is available.
        label : str, optional
            The descriptive label for the axis.
        unit : str, optional
            The unit of the axis.
        npoints : int, optional
            The number of points in the axis. Use this to set the number
            of points if data_range is None.
        """
        if axis not in self._axwidgets:
            raise UserConfigError(
                f"The axis `{axis}` not defined in the AxesSelector. Please update "
                "the data shape first."
            )
        self._axwidgets[axis].set_axis_metadata(data_range, label, unit, npoints)

    def set_metadata_from_dataset(self, dataset: Dataset):
        """
        Set the metadata from a pydidas Dataset.

        Parameters
        ----------
        dataset : Dataset
            The dataset to get the metadata from.
        """
        if not isinstance(dataset, Dataset):
            raise UserConfigError(
                "Invalid dataset: The given object is not a pydidas Dataset but "
                f"`{type(dataset)}`. \nAlternatively, please set the metadata "
                "manually using the `set_axis_metadata` method."
            )
        if dataset.ndim < len(self._additional_choices):
            raise UserConfigError(
                "The dataset has less dimensions than required for the display. "
                "Please change the dataset or how to display the dataset."
            )
        self.set_data_shape(dataset.shape)
        for _dim in range(self._data_ndim):
            self.set_axis_metadata(
                _dim,
                dataset.axis_ranges[_dim],
                dataset.axis_labels[_dim],
                dataset.axis_units[_dim],
            )

    def define_additional_choices(self, choices: str):
        """
        Define additional choices for the display selection.

        Multiple choices must be separated by a double semicolon `;;`.

        Parameters
        ----------
        choices : str
            The additional choices.
        """
        self._additional_choices_str = choices
        self._additional_choices = choices.split(";;")
        for _dim in self._axwidgets:
            self._axwidgets[_dim].define_additional_choices(choices)
        if choices == "":
            return
        for _choice in self._additional_choices:
            if _choice in self.current_display_selection:
                continue
            for _axwidget in self._axwidgets.values():
                if _axwidget.display_choice not in self._additional_choices:
                    _axwidget.display_choice = _choice
                    break

    @QtCore.Slot(int, str)
    def _process_new_display_choice(self, axis: int, choice: str):
        """
        Process a new display choice for an axis.

        Parameters
        ----------
        axis : int
            The axis index.
        choice : str
            The new display choice.
        """
        if choice in self._additional_choices:
            for _dim, _axwidget in self._axwidgets.items():
                if _dim != axis and _axwidget.display_choice == choice:
                    with QtCore.QSignalBlocker(_axwidget):
                        _axwidget.reset_to_slicing()
        for _choice in self._additional_choices:
            if _choice in self.current_display_selection:
                continue
            for _dim, _axwidget in self._axwidgets.items():
                if _dim != axis and _axwidget.display_choice in _GENERIC_CHOICES:
                    with QtCore.QSignalBlocker(_axwidget):
                        _axwidget.display_choice = _choice
                    break
        self.process_new_slicing()

    def process_new_slicing(self):
        """
        Process the new slicing and emit a string representation as a signal.
        """
        self._current_slice_strings = {
            _dim: self._axwidgets[_dim].current_slice_str
            for _dim in range(self._data_ndim)
        }
        self._current_slice = [
            self._axwidgets[_dim].current_slice for _dim in range(self._data_ndim)
        ]
        self.sig_new_slicing.emit()
        self.sig_new_slicing_str_repr.emit(self.current_slice_str)

    @QtCore.Slot(int, str)
    def _update_ax_slicing(self, axis: int, slicing: str):
        """
        Update the slicing for an axis.

        Parameters
        ----------
        axis : int
            The axis index.
        slicing : str
            The slicing string.
        """
        self._current_slice_strings[axis] = slicing
        self._current_slice[axis] = self._axwidgets[axis].current_slice
        self.sig_new_slicing.emit()
        self.sig_new_slicing_str_repr.emit(self.current_slice_str)

    def closeEvent(self, event: QtCore.QEvent):
        """Close the widget and delete Children"""
        for _dim in self._axwidgets:
            self._axwidgets[_dim].deleteLater()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys

    import pydidas_qtcore
    from pydidas.gui import gui_excepthook
    from pydidas.unittest_objects import create_dataset

    class Printer(QtCore.QObject):
        @QtCore.Slot(str)
        def print_slicing(self, slicing: str):
            print(slicing)

        @QtCore.Slot()
        def slice_update(self):
            print("Slicing updated")

    sys.excepthook = gui_excepthook
    printer = Printer()
    data = create_dataset(5, float)
    app = pydidas_qtcore.PydidasQApplication([])
    window = AxesSelector(multiline_layout=True)
    window.set_data_shape((3, 4, 6, 7, 5, 6, 8))
    window.sig_new_slicing_str_repr.connect(printer.print_slicing)
    window.sig_new_slicing.connect(printer.slice_update)
    window.set_metadata_from_dataset(data)
    window.define_additional_choices("window x;;window y")
    # window.set_data_shape((3, 4, 6))
    # window.set_axis_metadata(1, 0.6 * np.arange(7), "axis 1", "unit 1")
    # window._axwidgets[1].define_additional_choices("window x;;window y")
    window.show()
    app.exec_()
