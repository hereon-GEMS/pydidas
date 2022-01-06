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
Module with the ReadOnlyTextWidget which is a subclassed QTextEdit and can
be used to display scrollable text.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ReadOnlyTextWidget']

from PyQt5 import QtWidgets

from .utilities import apply_widget_properties


class ReadOnlyTextWidget(QtWidgets.QTextEdit):
    """
    A read only QTextEdit widget with some layout settings in setup and a
    more advanced setText method.

    Parameters
    ----------
    parent : QWidget, optional
        The Qt parent widget. The default is None.
    **kwargs : Any supported Qt arguments
        Any arguments which have an associated setArgName method in
        Qt can be defined at creation.
    **readOnly : bool, optional
        Flag to set the field to read only. The default is True.
    **minimumWidth : Union[int, None], optional
        The minimum width of the widget. If None, no minimum width will be
        set for the widget. The default is 500.
    **fixedWidth : Union[int, None], optional
        A fixed width for the widget. If None, no fixedWidth will be set.
        The default is None.
    **minimumHeight : Union[int, None], optional
        The minimum Height of the widget. If None, no minimum height will
        be set for the widget. The default is None.
    **fixedHeight : Union[int, None], optional
        A fixed height for the widget. If None, no fixedHeight will be set.
        The default is None.
    **visible : bool, optional
        Flag to set widget visibility at startup. The default is True.
    """

    def __init__(self, parent=None, **params):
        super().__init__(parent)
        params['minimumWidth'] = params.get('minimumWidth', 500)
        params['readOnly'] = params.get('readOnly', True)
        params['acceptRichText'] = params.get('acceptRichText', True)

        # if fixed settings are given, overwrite the minimum size settings
        # because the minimumSize take precedence in Qt:
        if 'fixedWidth' in params and 'minimumWidth' in params:
            del params['minimumWidth']
        if 'fixedHeight' in params and 'minimumHeight' in params:
            del params['minimumHeight']
        apply_widget_properties(self, **params)

    def setText(self, text, title=None):
        """
        Set the widget's text.

        Parameters
        ----------
        text : str
            The text to be displayed.
        title : str, optional
            The title. If None, no title will be printed. The default is None.
        """
        super().setText('')
        if title is not None:
            self.__add_title(title)
        self.append(text)
        self.verticalScrollBar().triggerAction(
            QtWidgets.QScrollBar.SliderToMinimum)

    def __add_title(self, title):
        """
        Add the title to the box, if given.

        Parameters
        ----------
        title : Union[str, None]
            The title. If None, this method will be skipped.
        """
        self.setFontPointSize(14)
        self.setFontWeight(75)
        self.append(f'{title}')
        self.setFontPointSize(10)

    def setTextFromDict(self, text_dict, title=None, one_line_entries=False,
                        indent=4):
        """
        Set the widget's text.

        This widget accepts both a single text entry and a list of entries
        for the text. A list of entries will be converted to a single text
        according to a <key: entry> scheme.

        Parameters
        ----------
        text : dict
            The dictionnary of the text to be displayed. The dictionary will
            be processed with keys as item titles and values as corresponding
            items.
        title : str, optional
            The title. If None, no title will be printed. The default is None.
        one_line_entries : bool, optional
            Flag to force printing of keys and entries in one line instead
            of two lines with an indent. The default is False.
        indent : int, optional
            The indent depth for list entries. The default is 4.
        """
        super().setText('')
        self.__add_title(title)
        for _key, _value in text_dict.items():
            if one_line_entries:
                self.append(f'{_key}: {_value}')
            else:
                _items = _value.split('\n')
                self.setFontWeight(75)
                self.append(f'\n{_key}:')
                self.setFontWeight(50)
                for item in _items:
                    _indent = (' ' * indent if item[:indent] != ' ' * indent
                               else '')
                    self.append(_indent + item)
        self.verticalScrollBar().triggerAction(
            QtWidgets.QScrollBar.SliderToMinimum)
