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

"""Module with various utility functions for widgets."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['deleteItemsOfLayout', 'excepthook', 'QtaIconButton',
           'apply_widget_properties', 'apply_font_properties',
           'create_default_grid_layout']

from io import StringIO
import os
import time
import traceback

from PyQt5 import QtWidgets, QtCore
import qtawesome

from .dialogues import ErrorMessageBox
from ..config import STANDARD_FONT_SIZE

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


def get_args_as_list(args):
    """
    Format the input arguments to an interable list to be passed as *args.

    Parameters
    ----------
    args : object
        Any input

    Returns
    -------
    args : Union[tuple, list, set]
        The input arguments formatted to a iterable list.
    """
    if not isinstance(args, (tuple, list, set)):
        args = [args]
    return args


def apply_widget_properties(obj, **kwargs):
    """
    Set Qt widget properties from a supplied dict.

    This function takes a dictionary (ie. keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the widget has a "setProperty"
    method and will then call "widget.setProperty(12)". The verificiation that
    methods exist allows this function to take the full kwargs of any
    object without the need to filter out non-related keys.

    Parameters
    ----------
    widget : QObject
        Any QObject
    **kwargs : dict
        A dictionary with properties to be set.
    """
    for _key in kwargs:
        _name = f'set{_key[0].upper()}{_key[1:]}'
        if hasattr(obj, _name):
            _func = getattr(obj, _name)
            _func(*get_args_as_list(kwargs.get(_key)))


def apply_font_properties(fontobj, **kwargs):
    """
    Set font properties from a supplied dict.

    This function takes a dictionary (ie. keyword arguments) and iterates
    through all keys. Keys will be interpreted in Qt style: A "property: 12"
    entry in the dictionary will verify that the font object  has a
    "setProperty" method and will then call "fontobj.setProperty(12)". The
    verificiation that methods exist allows this function to take the full
    kwargs of any object without the need to filter out non-related keys.

    Parameters
    ----------
    fontobj : QObject
        Any QFont
    **kwargs : dict
        A dictionary with properties to be set.
    """
    if 'fontsize' in kwargs and not 'pointSize' in kwargs:
        kwargs['pointSize'] = kwargs.get('fontsize', STANDARD_FONT_SIZE)
    for _key in kwargs:
        _name = f'set{_key[0].upper()}{_key[1:]}'
        if hasattr(fontobj, _name):
            _func = getattr(fontobj, _name)
            _func(*get_args_as_list(kwargs.get(_key)))


def create_default_grid_layout():
    """
    Create a QGridLayout with default parameters.

    The default parameters are

        - vertical spacing : 5
        - horizontal spacing : 5
        - alignment : left | top

    Returns
    -------
    layout : QGridLayout
        The layout.
    """
    _layout = QtWidgets.QGridLayout()
    _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    _layout.setHorizontalSpacing(5)
    _layout.setVerticalSpacing(5)
    return _layout


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
