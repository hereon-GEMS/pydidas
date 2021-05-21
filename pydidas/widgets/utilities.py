#!/usr/bin/env python

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

"""Module with various utility functions for widgets."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['deleteItemsOfLayout', 'excepthook', 'QtaIconButton']

from io import StringIO
import os
import time
import traceback

from PyQt5 import QtWidgets, QtCore
import qtawesome

from .dialogues import ErrorMessageBox


def deleteItemsOfLayout(layout):
    """
    Function to recursively delete items in a QLayout.

    Parameters
    ----------
    layout : QLayout
        The layout to be cleard.

    Returns
    -------
    None.
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                deleteItemsOfLayout(item.layout())


class QtaIconButton(QtWidgets.QPushButton):
    """
    A QPushButton with a reference to an qtawesome icon to be used as
    icon.
    """
    def __init__(self, icon, text='', parent=None, size=None):
        """


        Parameters
        ----------
        icon: Union[str, QtIcon]
            The icon to be used for the button. If a string is passed, this is
            interpreted as icon name for a qtawesome icon. If a QtIcon is
            passed, this is used as it is.
        text : str, optional
            The button text. The default is ''.
        parent : Union[QtWidget, None], optional
            The parent widget. The default is None.
        size : Union[int, list, tuple, None], optional
            The button size. If an integer is passed, this is interpreted as
            both height and width. A list or tuple of length 2 is interpreted
            as the (width, height). If None, the size is not set and the
            button defaults to its sizeHint size. The default is None.

        Raises
        ------
        ValueError
            If the size cannot be interpreted (ie. not an integer or a tuple
            or list of length 2), a value error is raised.

        Returns
        -------
        None.
        """
        import numbers
        if isinstance(icon, str):
            _icon = qtawesome.icon(icon)
        elif not isinstance(icon, QtCore.QIcon):
            raise ValueError('icon is neither a QIcon nor a String')
        super().__init__(_icon, text, parent)
        if size:
            if isinstance(size, numbers.Integral):
                size = (size, size)
            elif (isinstance(size, (list, tuple))
                  and len(size) == 2
                  and isinstance(size[0], numbers.Integral)
                  and isinstance(size[1], numbers.Integral)):
                ...
            else:
                raise ValueError(f'Cannot interprete size "{size}".')
            self.setIconSize(QtCore.QSize(*size))
            self.setFixedSize(*size)



def excepthook(exc_type, exception, trace):
    """
    Catch global exceptions.

    This global function is used to replace the generic sys.excepthook
    to handle exceptions. It will open a popup window with the exception
    text.

    Parameters
    ----------
    exc_type : type
        The exception type
    exception : Exception
        The exception itself.
    trace : traceback object
        The trace of where the exception occured.

    Returns
    -------
    None
    """
    _sep = '\n' + '-' * 80 + '\n'
    _traceback_info = StringIO()
    traceback.print_tb(trace, None, _traceback_info)
    _traceback_info.seek(0)
    _trace = _traceback_info.read()
    _logfile = os.path.join(os.path.dirname(__file__), 'error.log')
    _note = ('An unhandled exception occurred. Please report the bug to:'
             '\n\tmalte.storm@hereon.de\nor'
             '\n\thttps://github.com/malte-storm/pydidas/issues'
             f'\n\nA log has been written to:\n\t{_logfile}.'
             '\n\nError information:\n')
    _time = time.strftime('%Y-%m-%d %H:%M:%S')
    _msg = _sep.join([_time, f'{exc_type}: {exception}', _trace ])
    try:
        with open(_logfile, 'w') as f:
            f.write(_msg)
    except IOError:
        pass
    errorbox = ErrorMessageBox()
    errorbox.set_text(_note + _msg)
    errorbox.exec_()