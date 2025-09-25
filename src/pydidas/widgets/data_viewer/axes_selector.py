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


from typing import Any

import h5py
import numpy as np
from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import Dataset, UserConfigError
from pydidas.core.constants import POLICY_EXP_FIX
from pydidas.widgets.data_viewer.data_axis_selector import (
    GENERIC_AXIS_SELECTOR_CHOICES,
    DataAxisSelector,
)
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class AxesSelector(WidgetWithParameterCollection):
    """
    The AxesSelector is a widget to select slicing for a given Dataset.

    The AxesSelector allows to select slicing for a dataset based on indexing
    or on metadata.

    Supported signals:

        - sig_new_slicing: emitted when the slicing has been updated.
        - sig_new_slicing_str_repr[str, str]:
            emitted when the slicing has been updated. The signal content
            is the string representation of the slicing and the order of the axes.
    """

    sig_new_slicing = QtCore.Signal()
    sig_new_slicing_str_repr = QtCore.Signal(str, str)

    def __init__(self, parent: QtWidgets.QWidget | None = None, **kwargs: Any):
        WidgetWithParameterCollection.__init__(self, parent=parent, **kwargs)
        self._axis_widgets = {}
        self._data_shape = ()
        self._data_ndim = 0
        self._additional_choices_str = ""
        self._additional_choices = []
        self._current_slice_strings = {}
        self._current_slice = []
        self._current_transpose_required = None

        self._multiline_layout = kwargs.get("multiline_layout", False)
        self._allow_fewer_dims = kwargs.get("allow_fewer_dims", False)
        self.layout().setColumnStretch(0, 1)
        self.create_spacer("final_spacer", gridPos=(0, 1, 1, 1), fixedWidth=5)

    @property
    def filtered_data_ndim(self) -> int:
        """The number of dimensions of the data that are greater than 1."""
        return sum(i > 1 for i in self._data_shape)

    @property
    def current_display_selection(self) -> list[str]:
        """
        Get the current display selection.

        Returns
        -------
        list[str]
            The current display selection.
        """
        return [
            self._axis_widgets[_dim].display_choice for _dim in range(self._data_ndim)
        ]

    @property
    def transpose_required(self) -> bool:
        """
        Check if a transpose is required for the slicing.

        If the current display selection differs in order from the default
        selection order, a transpose is required.

        Returns
        -------
        bool
            True if a transpose is required, False otherwise.
        """
        if self._current_transpose_required is None:
            _default_selection = [
                _choice
                for _choice in self.current_display_selection
                if _choice not in GENERIC_AXIS_SELECTOR_CHOICES
            ]
            self._current_transpose_required = (
                _default_selection != self._additional_choices
            )
        return self._current_transpose_required

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

    @property
    def additional_choices(self) -> list[str]:
        """The additional choices defined for the display selection."""
        return self._additional_choices[:]

    @property
    def n_choices(self) -> int:
        """The number of additional choices defined for the display selection."""
        return len(self._additional_choices)

    @property
    def allow_fewer_dims(self) -> bool:
        """Flag to allow fewer dimensions in the data than additional choices."""
        return self._allow_fewer_dims

    @allow_fewer_dims.setter
    def allow_fewer_dims(self, value: bool):
        """Set the flag to allow fewer dimensions in the data than additional choices."""
        self._allow_fewer_dims = value

    def set_data_shape(self, shape: tuple[int], update_axwidgets: bool = True):
        """
        Set the shape of the data to be sliced.

        Parameters
        ----------
        shape : tuple[int]
            The shape of the data to be sliced.
        update_axwidgets : bool, optional
            Flag to update the axis widgets. This is not required in the case
            of setting metadata from a Dataset. Default is True.
        """
        if not isinstance(shape, tuple):
            raise UserConfigError(
                f"Invalid data shape `{shape}`. Please provide a tuple."
            )
        self._data_shape = shape
        self._data_ndim = len(shape)
        self._create_data_axis_selectors()
        if not update_axwidgets:
            return
        with QtCore.QSignalBlocker(self):
            for _dim, _npoints in enumerate(shape):
                self._axis_widgets[_dim].set_axis_metadata(
                    None, "", "", npoints=_npoints, ndim=self.filtered_data_ndim
                )

    def _create_data_axis_selectors(self):
        """
        Create the DataAxisSelector widgets for the axes.
        """
        for _dim in range(self._data_ndim):
            if _dim in self._axis_widgets:
                continue
            if self._multiline_layout and _dim > 0:
                self.create_line(f"line_{_dim}", gridPos=(-1, 0, 1, 1))
            self.add_any_widget(
                f"axis_{_dim}",
                DataAxisSelector(_dim, multiline=self._multiline_layout),
                gridPos=(-1, 0, 1, 1),
                sizePolicy=POLICY_EXP_FIX,
            )
            self._current_slice.append(slice(None))
            self._axis_widgets[_dim] = self._widgets[f"axis_{_dim}"]
            self._axis_widgets[_dim].define_additional_choices(
                self._additional_choices_str
            )
            self._axis_widgets[_dim].sig_display_choice_changed.connect(
                self._process_new_display_choice
            )
            self._axis_widgets[_dim].sig_new_slicing.connect(self._update_ax_slicing)
        for _dim in self._axis_widgets:
            self._axis_widgets[_dim].setVisible(_dim < self._data_ndim)
            if self._multiline_layout and _dim > 0:
                self._widgets[f"line_{_dim}"].setVisible(_dim < self._data_ndim)

    def set_axis_metadata(
        self,
        axis: int,
        data_range: np.ndarray | None,
        label: str = "",
        unit: str = "",
        npoints: int | None = None,
    ):
        """
        Set the metadata for an axis.

        Parameters
        ----------
        axis : int
            The axis index.
        data_range : np.ndarray | None
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
        if axis not in self._axis_widgets:
            raise UserConfigError(
                f"The axis `{axis}` not defined in the AxesSelector. Please update "
                "the data shape first."
            )
        self._axis_widgets[axis].set_axis_metadata(
            data_range, label, unit, npoints=npoints, ndim=self.filtered_data_ndim
        )

    def set_metadata_from_dataset(self, dataset: Dataset | h5py.Dataset):
        """
        Set the metadata from a pydidas Dataset.

        Parameters
        ----------
        dataset : Dataset | h5py.Dataset
            The dataset to get the metadata from.
        """
        if not isinstance(dataset, (Dataset, h5py.Dataset)):
            try:
                _type = f"`<{dataset.__module__}.{dataset.__class__.__name__}>`"
            except AttributeError:
                _type = f"`<{dataset.__class__.__name__}>`"
            raise UserConfigError(
                "Invalid dataset: The given object is not a pydidas Dataset but "
                f"{_type}.\nAlternatively, please set the metadata manually using the "
                "`set_axis_metadata` method."
            )
        if dataset.ndim < len(self._additional_choices) and not self._allow_fewer_dims:
            raise UserConfigError(
                "The dataset has less dimensions than required for the display. "
                "Please change the dataset or how to display the dataset."
            )
        self.set_data_shape(dataset.shape, update_axwidgets=False)
        for _dim in range(self._data_ndim):
            if isinstance(dataset, h5py.Dataset):
                _args = (np.arange(dataset.shape[_dim]), "", "")
            elif isinstance(dataset, Dataset):
                _args = (
                    dataset.axis_ranges[_dim],
                    dataset.axis_labels[_dim],
                    dataset.axis_units[_dim],
                )
            with QtCore.QSignalBlocker(self._axis_widgets[_dim]):
                self._axis_widgets[_dim].set_axis_metadata(
                    *_args,  # noqa -- args is always set due to isinstance check above
                    ndim=self.filtered_data_ndim,
                )
        self._verify_additional_choices_selected(-1, block_signals=True)
        self.process_new_slicing(block_signals=True)

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
        self._additional_choices = choices.split(";;") if choices else []
        for _dim, _axwidget in self._axis_widgets.items():
            with QtCore.QSignalBlocker(_axwidget):
                _axwidget.define_additional_choices(choices)
        if choices == "":
            return
        self._verify_additional_choices_selected(-1, block_signals=True)

    def _verify_additional_choices_selected(
        self, ignore_ax: int, block_signals: bool = False
    ):
        """
        Verify that the additional choices are selected for all axes.

        Parameters
        ----------
        ignore_ax : int
            The axis index to ignore.
        block_signals : bool, optional
            Flag to block signals during the verification.
        """
        for _choice in self._additional_choices:
            if self.current_display_selection.count(_choice) > 1:
                self._change_duplicate_choices(_choice, ignore_ax)
            elif self.current_display_selection.count(_choice) == 0:
                self._assign_choice_to_first_available_axis(_choice, ignore_ax)
        self._current_transpose_required = None
        self.process_new_slicing(block_signals)

    def _change_duplicate_choices(self, choice: str, ignore_ax: int):
        """
        Change duplicate choices in the current display selection.

        Parameters
        ----------
        choice : str
            The current choice to be replaced.
        ignore_ax : int
            The axis dimension to be ignored.
        """
        _dim_where_selected = [
            _dim
            for _dim, _key in enumerate(self.current_display_selection)
            if _key == choice
        ]
        if ignore_ax in _dim_where_selected:
            _dim_where_selected.remove(ignore_ax)
        elif self._additional_choices.index(choice) in _dim_where_selected:
            _dim_where_selected.remove(self._additional_choices.index(choice))
        else:
            _dim_where_selected = _dim_where_selected[:-1]
        _other_choices = [
            _c
            for _c in self._additional_choices
            if (_c != choice and _c not in self.current_display_selection)
        ]
        if len(_other_choices) < len(_dim_where_selected):
            if self._data_ndim == len(self._additional_choices):
                raise ValueError("Cannot set the additional choices for all axes.")
            _other_choices = _other_choices + ["slice at index"] * (
                len(_dim_where_selected) - len(_other_choices)
            )
        for _i, _dim in enumerate(_dim_where_selected):
            with QtCore.QSignalBlocker(self._axis_widgets[_dim]):
                self._axis_widgets[_dim].display_choice = _other_choices[_i]

    def _assign_choice_to_first_available_axis(self, choice: str, ignore_ax: int = -1):
        """
        Assign a choice to the first available axis that is not the ignored axis.
        """
        for _dim, _axwidget in self._axis_widgets.items():
            if (
                _dim != ignore_ax
                and _axwidget.display_choice in GENERIC_AXIS_SELECTOR_CHOICES
                and _dim < self._data_ndim
                and self._data_shape[_dim] > 1
            ):
                with QtCore.QSignalBlocker(_axwidget):
                    _axwidget.display_choice = choice
                break

    def assign_index_use_to_dims(self, dims: list[int]):
        """
        Assign the "slice at index" choice to the given dimensions.

        Parameters
        ----------
        dims : list[int]
            The dimensions to assign the "slice at index" choice to.
        """
        if len(dims) + len(self._additional_choices) != self.filtered_data_ndim:
            raise UserConfigError(
                "The number of given dimensions and additional choices does not match "
                "the number of dimensions in the data."
            )
        _choices_to_use = self._additional_choices[:]
        for _dim in range(self.filtered_data_ndim):
            if _dim in self._axis_widgets:
                with QtCore.QSignalBlocker(self._axis_widgets[_dim]):
                    if _dim in dims:
                        self._axis_widgets[_dim].display_choice = "slice at index"
                    else:
                        self._axis_widgets[_dim].display_choice = _choices_to_use.pop(0)
        self.process_new_slicing(block_signals=True)

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
            for _dim, _axwidget in self._axis_widgets.items():
                if _dim != axis and _axwidget.display_choice == choice:
                    with QtCore.QSignalBlocker(_axwidget):
                        _axwidget.reset_to_slicing()
        self._verify_additional_choices_selected(axis)

    def process_new_slicing(self, block_signals: bool = False):
        """
        Process the new slicing and emit a string representation as a signal.

        Parameters
        ----------
        block_signals : bool, optional
            Flag to block signals during the processing.
        """
        self._current_slice_strings = {
            _dim: self._axis_widgets[_dim].current_slice_str
            for _dim in range(self._data_ndim)
        }
        self._current_slice = [
            self._axis_widgets[_dim].current_slice for _dim in range(self._data_ndim)
        ]
        _curr_selection = ";;".join(self.current_display_selection)
        if not block_signals:
            self.sig_new_slicing.emit()
            self.sig_new_slicing_str_repr.emit(self.current_slice_str, _curr_selection)

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
        self._current_slice[axis] = self._axis_widgets[axis].current_slice
        _curr_selection = ";;".join(self.current_display_selection)
        self.sig_new_slicing.emit()
        self.sig_new_slicing_str_repr.emit(self.current_slice_str, _curr_selection)

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Close the widget and delete Children"""
        for _dim in self._axis_widgets:
            self._axis_widgets[_dim].deleteLater()
        super().closeEvent(event)
