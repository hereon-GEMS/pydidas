# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the PydidasWindow class which can be used to subclass BaseFrames
to stand-alone Qt windows.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasWindow"]


import os
from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core.utils import (
    DOC_HOME_QURL,
    doc_filename_for_window_manual,
    doc_qurl_for_window_manual,
)
from pydidas.resources import icons
from pydidas.widgets.framework.base_frame import BaseFrame
from pydidas_qtcore import PydidasQApplication


class PydidasWindow(BaseFrame):
    """The PydidasWindow is a standalone BaseFrame with a persistent geometry."""

    show_frame = False
    sig_closed = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseFrame.__init__(self, **kwargs)
        self._geometry = None
        self.set_default_params()
        if kwargs.get("activate_frame", True):
            self.frame_activated(self.frame_index)
        self.setWindowIcon(icons.pydidas_icon_with_bg())
        if "title" in kwargs:
            self.setWindowTitle(kwargs.get("title"))
        self._help_shortcut = QtWidgets.QShortcut(QtCore.Qt.Key_F1, self)
        self._help_shortcut.activated.connect(self.open_help)
        PydidasQApplication.instance().sig_exit_pydidas.connect(self.deleteLater)

    @QtCore.Slot()
    def open_help(self):
        """
        Open the help in a browser.

        This slot will check whether a helpfile exists for the current frame and open
        the respective helpfile if it exits or the main documentation if it does not.
        """
        _window_class = self.__class__.__name__
        _doc_file = doc_filename_for_window_manual(_window_class)

        if os.path.exists(_doc_file):
            _url = doc_qurl_for_window_manual(_window_class)
        else:
            _url = DOC_HOME_QURL
        _ = QtGui.QDesktopServices.openUrl(_url)

    def show(self):
        """
        Overload the generic show method.

        This makes sure that any show calls will have a fully built window.
        """
        if not self._config.get("built", False):
            self.frame_activated(self.frame_index)
        if self._geometry is not None:
            self.setGeometry(self._geometry)
        super().show()

    def closeEvent(self, event: QtGui.QCloseEvent):  # noqa
        """
        Overload the closeEvent to store the window's geometry.

        Parameters
        ----------
        event : QtGui.QCloseEvent
            The closing event.
        """
        self._geometry = self.geometry()
        self.sig_closed.emit()
        super().closeEvent(event)

    def export_window_state(self) -> dict:
        """
        Get the state of the window for exporting.

        The generic PydidasWindow method will return the geometry and
        visibility. If windows need to export more information, they need
        to reimplement this method.

        Returns
        -------
        dict
            The dictionary with the window state.
        """
        return {"geometry": self.geometry().getRect(), "visible": self.isVisible()}

    def restore_window_state(self, state: dict):
        """
        Restore the window state from saved information.

        Parameters
        ----------
        state : dict
            The dictionary with the state information.
        """
        self.setGeometry(*state["geometry"])
        self.setVisible(state["visible"])
