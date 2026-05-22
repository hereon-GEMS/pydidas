# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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
Module utility function for the file browser widgets and models.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ChangeFilter"]


from typing import Any

from qtpy.QtCore import QSortFilterProxyModel

from pydidas import IS_QT6


class ChangeFilter:
    """
    Context manager that wraps the Qt5/Qt6 filter-change API differences.

    In Qt6 the filter model exposes ``beginFilterChange`` /
    ``endFilterChange`` to batch invalidation; in Qt5 only
    ``invalidateFilter`` is available.

    Parameters
    ----------
    model : QSortFilterProxyModel
        The proxy model whose filter is about to be changed.
    """

    def __init__(self, model: QSortFilterProxyModel) -> None:
        """
        Initialize the context manager.

        Parameters
        ----------
        model : QSortFilterProxyModel
            The proxy model whose filter is about to be changed.
        """
        self._model: QSortFilterProxyModel = model

    def __enter__(self) -> "ChangeFilter":
        """Begin the filter-change block."""
        if IS_QT6:
            self._model.beginFilterChange()
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: Any,
    ) -> None:
        """End the filter-change block and invalidate the filter."""
        if IS_QT6:
            self._model.endFilterChange()
        else:
            self._model.invalidateFilter()
