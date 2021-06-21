# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the BaseFrame, the main window widget from which all
main frames should inherit."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BaseFrame']

from PyQt5 import QtWidgets, QtCore


class BaseFrame(QtWidgets.QFrame):
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

        Returns
        -------
        None.
        """
        initLayout = kwargs.get('initLayout', True)
        super().__init__(parent=parent)
        self.font = QtWidgets.QApplication.font()
        if initLayout:
            _layout = QtWidgets.QGridLayout(self)
            _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.setLayout(_layout)
        self._initialized = False
        self.name = name if name else ''

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
        if self.parent() and not self._initialized:
            self._initialize()
            self._initialized = True

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
