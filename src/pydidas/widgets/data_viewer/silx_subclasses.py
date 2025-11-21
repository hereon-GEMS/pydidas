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
Module with subclasses of silx widgets to allow direct access without data views.
"""

from typing import Any

import h5py
import numpy as np
import silx
from silx.gui.data.ArrayTableWidget import ArrayTableWidget
from silx.gui.data.Hdf5TableView import Hdf5TableView


class PydidasHdf5TableView(Hdf5TableView):
    """
    A subclass of the silx Hdf5TableView to allow direct access without data views.
    """

    def display_data(
        self,
        data: h5py.Dataset | h5py.File | h5py.Group | silx.gui.hdf5.H5Node,
        **kwargs: Any,  # noqa ARG001
    ) -> None:
        """
        Display the data in the view.

        Parameters
        ----------
        data : h5py.Dataset | h5py.File | h5py.Group | silx.gui.hdf5.H5Node
            The data to display.
        kwargs : Any
            Additional keyword arguments. These are not used but included in
            the function signature for compatibility with other data views.
        """
        self.setData(data)

    def clear(self):
        """Clear the data reference."""
        self.setData(None)

    def setGraphTitle(self, title: str) -> None:  # noqa ARG001
        """
        Set the graph title.

        Parameters
        ----------
        title : str
            The new title.
        """
        pass


class PydidasArrayTableWidget(ArrayTableWidget):
    """
    A subclass of the silx ArrayTableWidget to allow direct access without data views.
    """

    def display_data(
        self,
        data: np.ndarray | silx.gui.hdf5.H5Node,
        **kwargs: Any,  # noqa ARG001
    ) -> None:
        """
        Display the data in the view.

        Parameters
        ----------
        data : np.ndarray | silx.gui.hdf5.H5Node
            The data to display.
        kwargs : Any
            Additional keyword arguments. These are not used but included in
            the function signature for compatibility with other data views.
        """
        if data.ndim == 1:
            data = data[:, np.newaxis]
        self.setArrayData(data)
        self.displayAxesSelector(False)

    def clear(self):
        """Clear the table."""
        self.setArrayData(np.array([]))

    def setGraphTitle(self, title: str) -> None:  # noqa ARG001
        """
        Set the graph title.

        Parameters
        ----------
        title : str
            The new title.
        """
        pass
