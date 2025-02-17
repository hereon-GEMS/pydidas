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
from pydidas.widgets.data_viewer.data_axis_selector import DataAxisSelector
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class AxesSelector(WidgetWithParameterCollection):
    sig_new_slicing = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, parent=parent, **kwargs)
        self._axwidgets = {}
        self._data_shape = ()
        self._data_ndim = 0
        self._additional_choices = ""
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
                    DataAxisSelector(_dim),
                    gridPos=(_dim, 0, 1, 1),
                    sizePolicy=POLICY_EXP_FIX,
                )
                self._axwidgets[_dim] = self._widgets[f"axis_{_dim}"]
                self._axwidgets[_dim].define_additional_choices(
                    self._additional_choices
                )
        for _key in self._axwidgets:
            self._axwidgets[_key].setVisible(_key < self._data_ndim)
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
        self.set_data_shape(dataset.data.shape)
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
        self._additional_choices = choices
        for _dim in self._axwidgets:
            self._axwidgets[_dim].define_additional_choices(choices)
        if choices == "":
            return
        _extra_choices = choices.split(";;")
        for _choice in _extra_choices:
            if _choice in self.current_display_selection:
                pass
            for _dim, _axwidget in self._axwidgets.items():
                if _axwidget.display_choice not in _extra_choices:
                    _axwidget.display_choice = _choice
                    break

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

    sys.excepthook = gui_excepthook

    data = create_dataset(5, float)
    app = pydidas_qtcore.PydidasQApplication([])
    window = AxesSelector()
    window.set_metadata_from_dataset(data)
    window.define_additional_choices("window x;;window y")
    # window.set_data_shape((3, 4, 6))
    # window.set_axis_metadata(1, 0.6 * np.arange(7), "axis 1", "unit 1")
    # window._axwidgets[1].define_additional_choices("window x;;window y")
    window.show()
    app.exec_()
