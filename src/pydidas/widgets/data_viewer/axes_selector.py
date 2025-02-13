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

from pydidas.core import UserConfigError
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
                    f"axis_{_dim}", DataAxisSelector(_dim), gridPos=(-1, 0, 1, 1)
                )
                self._axwidgets[_dim] = self._widgets[f"axis_{_dim}"]
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


if __name__ == "__main__":
    import sys

    import pydidas_qtcore
    from pydidas.gui import gui_excepthook

    sys.excepthook = gui_excepthook

    app = pydidas_qtcore.PydidasQApplication([])
    window = AxesSelector()
    window.set_data_shape((3, 4, 5, 6))
    window.set_data_shape((3, 4, 6))
    window.show()
    app.exec_()
