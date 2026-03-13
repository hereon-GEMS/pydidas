# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
The PydidasCheckBox is a QCheckBox with font formatting and sizeHint adjustment.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasCheckBox"]


from typing import Any

from qtpy import QtCore, QtWidgets

from pydidas.core.utils import IS_QT6
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin


class PydidasCheckBox(PydidasWidgetMixin, QtWidgets.QCheckBox):
    """
    Create a QCheckBox with automatic font formatting.

    Note that this class is not intended to be used with tri-state checkboxes.
    """

    sig_new_check_state = QtCore.Signal(int)
    sig_check_state_changed = QtCore.Signal()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the PydidasCheckBox.

        Parameters
        ----------
        *args : Any
            Positional arguments for QCheckBox.
        **kwargs : Any
            Keyword arguments for font formatting and widget initialization.
        """
        kwargs["font_metric_height_factor"] = kwargs.get("font_metric_height_factor", 1)
        QtWidgets.QCheckBox.__init__(self, *args)
        PydidasWidgetMixin.__init__(self, **kwargs)
        if IS_QT6:
            self.checkStateChanged.connect(self._emit_signal_in_qt6)
        else:
            self.stateChanged.connect(self._emit_signal_in_qt5)

    def _emit_signal_in_qt6(self, state: QtCore.Qt.CheckState) -> None:
        """
        Handle the signal emission in Qt6.

        Parameters
        ----------
        state : QtCore.Qt.CheckState
            The new check state.
        """
        if state == QtCore.Qt.CheckState.Checked:
            self.sig_new_check_state.emit(1)
        elif state == QtCore.Qt.CheckState.Unchecked:
            self.sig_new_check_state.emit(0)
        elif state == QtCore.Qt.CheckState.PartiallyChecked:
            self.sig_new_check_state.emit(-1)
        self.sig_check_state_changed.emit()

    def _emit_signal_in_qt5(self, state: int) -> None:
        """
        Handle the signal emission in Qt5.

        Parameters
        ----------
        state : int
            The new check state.
        """
        self.sig_new_check_state.emit(int(self.isChecked()))
        self.sig_check_state_changed.emit()
