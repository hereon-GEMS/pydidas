# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PydidasWindow class which is a QMainWindow widget and is used
in pydidas to display stand-alone windows.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasWindow"]

from qtpy import QtCore

from ...core.utils import get_pydidas_icon_w_bg
from ...widgets import BaseFrame


class PydidasWindowMixIn:
    """
    MixIn class to extend PydidasWindow functionality to other classes also derived
    from a QObject.
    """

    def __init__(self):
        self._geometry = None

    def closeEvent(self, event):
        """
        Overload the closeEvent to store the window's geometry.

        Parameters
        ----------
        event : QtCore.QEvent
            The closing event.
        """
        self._geometry = self.geometry()
        self.sig_closed.emit()
        super().closeEvent(event)

    def show(self):
        """
        Overload the show method to update the geometry.
        """
        if self._geometry is not None:
            self.setGeometry(self._geometry)
        super().show()

    def export_window_state(self):
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

    def restore_window_state(self, state):
        """
        Restore the window state from saved information.

        Parameters
        ----------
        state : dict
            The dictionary with the state information.
        """
        self.setGeometry(*state["geometry"])
        self.setVisible(state["visible"])


class PydidasWindow(BaseFrame, PydidasWindowMixIn):
    """
    The PydidasWindow is a standalone BaseFrame with a persistent geometry
    upon closing and showing.
    """

    show_frame = False
    sig_closed = QtCore.Signal()

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent, **kwargs)
        PydidasWindowMixIn.__init__(self)
        self.set_default_params()
        self.frame_activated(self.frame_index)
        self.setWindowIcon(get_pydidas_icon_w_bg())
        if "title" in kwargs:
            self.setWindowTitle(kwargs.get("title"))
