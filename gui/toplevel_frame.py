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

"""Module with the ToplevelFrame, the main window widget from which all
main frames should inherit."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ToplevelFrame']

from PyQt5 import QtWidgets, QtCore

from ..widgets import CENTRAL_WIDGET_STACK
from ..config import STANDARD_FONT_SIZE

class ToplevelFrame(QtWidgets.QFrame):
    """
    The ToplevelFrame is a subclassed QFrame and should be used as the
    base class for all Frames in the pySALADD suite.
    It adds a name attribute and registration routines with the
    CENTRAL_WIDGET_STACK.

    By default, a QVBoxLayout is applied with an alignment
    """
    def __init__(self, parent=None, name=None, initLayout=True):
        """
        Initialize the ToplevelFrame instance.

                Parameters
        ----------
        parent : Union[QWidget, None], optional
            The parent widget. The default is None.
        name : Union[str, None], optional
            The reference name of the widget for the CENTRAL_WIDGET_STACK.
            The default is None.
        initLayout : bool
            Flag to initialize the frame layout with a QtWidgets.QVBoxLayout.
            If False, no layout will be initialized and the subclass is
            responsible for setting up the layout. The default is True.

        Returns
        -------
        None.
        """
        super().__init__(parent)
        self.font = QtWidgets.QApplication.font()
        if initLayout:
            _layout = QtWidgets.QVBoxLayout(self)
            _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.setLayout(_layout)
        self.initialized = False
        self.name = name if name else ''
        if name:
            CENTRAL_WIDGET_STACK.register_widget(self.name, self)
            self._initialize()
            self.initialized = True

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

    def set_name(self, name):
        """
        Set the reference name of the frame.

        This method will store the reference name of the widget and also
        update the frame's reference in the CENTRAL_WIDGET_STACK or register
        it there if it is not yet registered.

        Parameters
        ----------
        name : str
            The reference name of the frame.

        Returns
        -------
        None.
        """
        self.name = name
        if not CENTRAL_WIDGET_STACK.is_registered(self.name, self):
            CENTRAL_WIDGET_STACK.register_widget(name, self)
        else:
            CENTRAL_WIDGET_STACK.change_reference_name(name, self)

    def _initialize(self):
        """
        Initialize the frame once parent and name have been set.

        This method needs to be overloaded by the subclass implementations.

        Returns
        -------
        None.

        """
        self.initialized = True

    def add_label(self, text, fontsize=STANDARD_FONT_SIZE, underline=False,
                  bold=False):
        """


        Parameters
        ----------
        text : TYPE
            DESCRIPTION.
        fontsize : TYPE, optional
            DESCRIPTION. The default is STANDARD_FONT_SIZE.
        underline : TYPE, optional
            DESCRIPTION. The default is False.
        bold : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None.

        """
        _l = QtWidgets.QLabel(text)
        self.font.setPointSize(fontsize)
        self.font.setBold(bold)
        self.font.setUnderline(underline)
        _l.setFont(self.font)
        _l.setFixedWidth(400)
        _l.setWordWrap(True)
        self.layout().addWidget(_l)