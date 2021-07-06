# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the BaseFrame, the main window widget from which all
main frames should inherit."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BaseFrame']

from PyQt5 import QtWidgets, QtCore
from ..widgets import CreateWidgetsMixIn

class BaseFrame(QtWidgets.QFrame, CreateWidgetsMixIn):
    """
    The BaseFrame is a subclassed QFrame and should be used as the
    base class for all Frames in the pySALADD suite.
    It adds a name attribute and registration routines with the
    CentralWidgetStack.

    By default, a QGridLayout is applied with an alignment of left/top.
    """
    status_msg = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, name=None, **kwargs):
        """
        Initialize the BaseFrame instance.

                Parameters
        ----------
        parent : Union[QWidget, None], optional
            The parent widget. The default is None.
        name : Union[str, None], optional
            The reference name of the widget for the CentralWidgetStack.
            The default is None.
        initLayout : bool
            Flag to initialize the frame layout with a QtWidgets.QVBoxLayout.
            If False, no layout will be initialized and the subclass is
            responsible for setting up the layout. The default is True.
        **kwargs : object
            Any additional keyword arguments.
        """
        initLayout = kwargs.get('initLayout', True)
        super().__init__(parent=parent)
        self.font = QtWidgets.QApplication.font()
        if initLayout:
            _layout = QtWidgets.QGridLayout(self)
            _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            _layout.setContentsMargins(5, 5, 0, 0)
            self.setLayout(_layout)
        self.initialized = False

    def setParent(self, parent):
        """
        Overloaded setParent method which also calls the _initialize
        method if this has not yet happened.

        Parameters
        ----------
        parent : Union[QWidget, None]
            The parent widget.

        Returns
        -------
        None.
        """
        super().setParent(parent)
        if self.parent() and not self.initialized:
            self._initialize()
            self.initialized = True

    @QtCore.pyqtSlot(int)
    def frame_activated(self, index):
        """
        Received signal that frame has been activated.

        This method is called when this frame becomes activated by the
        central widget. By default, this method will perform no actions.
        If specific frames require any actions, they will need to overwrite
        this method.

        Parameters
        ----------
        index : int
            The index of the activated frame.

        Returns
        -------
        None.
        """

    def _initialize(self):
        """
        Initialize the frame once parent and name have been set.

        This method needs to be overloaded by the subclass implementations.

        Returns
        -------
        None.

        """
        self.initialized = True

    def set_status(self, text):
        """
        Emit a status message to the main window.

        Parameters
        ----------
        text : str
            The status message to be emitted.

        Returns
        -------
        None.
        """
        self.status_msg.emit(text)

    def next_row(self):
        """
        Get the next empty row in the grid layout.

        Returns
        -------
        int
            The next empty row.
        """
        return self.layout().rowCount() + 1
