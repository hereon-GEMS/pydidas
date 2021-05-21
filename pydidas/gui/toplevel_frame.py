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

from ..config import STANDARD_FONT_SIZE

class ToplevelFrame(QtWidgets.QFrame):
    """
    The ToplevelFrame is a subclassed QFrame and should be used as the
    base class for all Frames in the pySALADD suite.
    It adds a name attribute and registration routines with the
    CentralWidgetStack.

    By default, a QGridLayout is applied with an alignment
    """
    status_msg = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, name=None, **kwargs):
        """
        Initialize the ToplevelFrame instance.

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
            self.layout_meta = dict(set=True, grid=True, row=0)
        self.initialized = False
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
        pass

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

    def add_textbox(self, text, fontsize=STANDARD_FONT_SIZE, underline=False,
                    bold=False, gridPos=None, width=400):
        """
        Add a label textbox to the frame.



        Parameters
        ----------
        text : str
            The text to be printed.
        fontsize : int, optional
            The size of the font. The default is STANDARD_FONT_SIZE.
        underline : bool, optional
            Flag to highlight the text with an underline. The default is
            False.
        bold : bool, optional
            Flag to print the text in bold. The default is False.
        gridPos : Union[tuple, list, None], optional
            If a tuple or list is given for the grid position, the label is
            added to the layout at the specified location. If None, the layout
            will decide where to add the label (typically, the next free cell).
            The default is None.
        width : int, optional
            The width of the textbox in pixel. The default is 400.

        Returns
        -------
        None.
        """
        _l = QtWidgets.QLabel(text)
        self.font.setPointSize(fontsize)
        self.font.setBold(bold)
        self.font.setUnderline(underline)
        _l.setFont(self.font)
        _l.setFixedWidth(width)
        _l.setWordWrap(True)
        if gridPos:
            self.layout().addWidget(_l, *gridPos)
        else:
            self.layout().addWidget(_l)
        return _l

    def add_button(self, text, **kwargs):
        """
        Create a button and add it to the layout.

        Parameters
        ----------
        text : str
            The button text.
        icon : Union[QtWidgets.QIcon, None], optional
            The button icon. If None, no icon is added to the button.
            The default is None.
        gridPos : Union[tuple, None], optional
            The grid position of the widget in the layout. If None, the widget
            is added to the layout and the layout selects the widget's
            position. The default is None.
        width : Union[int, None], optional
            If not None, the fixed width of the button. The default is None.
        height : Union[int, None], optional
            If not None, the fixed height of the button. The default is None.
        enabled : bool, optional
            Flag to create the button enabled or disabled. The default is True.

        Returns
        -------
        _button : QtWidgets.QPushButton
            The instantiated button widget.
        """
        _cfg = {'icon': kwargs.get('icon', None),
                'gridPos': kwargs.get('gridPos', None),
                'width': kwargs.get('width', None),
                'height': kwargs.get('height', None),
                'enabled': kwargs.get('enabled', True),
                }
        if _cfg['icon'] is not None:
            _button = QtWidgets.QPushButton(text, _cfg['icon'])
        else:
            _button = QtWidgets.QPushButton(text)
        _button.setEnabled(_cfg['enabled'])
        if _cfg['width'] is not None:
            _button.setFixedWidth(_cfg['width'])
        if _cfg['height'] is not None:
            _button.setFixedHeight(_cfg['height'])
        if _cfg['gridPos']:
            self.layout().addWidget(_button, *_cfg['gridPos'])
        else:
            self.layout().addWidget(_button)
        return _button

    def add_spacer(self, height=20, width=20, gridPos=None):
        """
        Add a spacer to the Frame layout.

        A QSpacerItem will be created and added to the layout. Its size policy
        is "Minimal".

        Parameters
        ----------
        height : int, optional
            The height of the spacer in pixel. The default is 20.
        width : int, optional
            The width of the spacer in pixel. The default is 20.
        gridPos : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        _spacer = QtWidgets.QSpacerItem(width, height,
                                        QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Minimum)
        if gridPos:
            self.layout().addItem(_spacer, *gridPos)
        else:
            self.layout().addItem(_spacer)

    def next_row(self):
        """
        Get the next empty row in the grid layout.

        Returns
        -------
        int
            The next empty row.
        """
        return self.layout().rowCount() + 1
