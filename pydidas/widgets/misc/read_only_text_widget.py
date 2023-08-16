# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the ReadOnlyTextWidget which is a subclassed QTextEdit and can
be used to display scrollable text.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ReadOnlyTextWidget"]


from typing import Union

from qtpy import QtCore, QtWidgets

from ...core.utils import apply_qt_properties


class ReadOnlyTextWidget(QtWidgets.QTextEdit):
    """
    A QTextEdit widget with some layout settings in setup and a more advanced setText.

    Parameters
    ----------
    parent : QWidget, optional
        The Qt parent widget. The default is None.
    **kwargs : Any supported Qt arguments
        Any arguments which have an associated setArgName method in Qt can be used
        at creation.
    """

    def __init__(self, parent=None, **params):
        QtWidgets.QTextEdit.__init__(self, parent)
        params["minimumWidth"] = params.get("minimumWidth", 300)
        params["readOnly"] = params.get("readOnly", True)
        params["acceptRichText"] = params.get("acceptRichText", True)

        # if fixed settings are given, overwrite the minimum size settings
        # because the minimumSize take precedence in Qt:
        if "fixedWidth" in params and "minimumWidth" in params:
            del params["minimumWidth"]
        if "fixedHeight" in params and "minimumHeight" in params:
            del params["minimumHeight"]
        apply_qt_properties(self, **params)
        self.__qtapp = QtWidgets.QApplication.instance()
        self.__qtapp.sig_fontsize_changed.connect(self.reprint)
        self.__text = ""
        self.__title = None

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
        QtWidgets.QTextEdit.setText(self, "")
        self.__text = text
        self.__add_title(title)
        self.append(text)
        self.verticalScrollBar().triggerAction(QtWidgets.QScrollBar.SliderToMinimum)

    def __add_title(self, title: Union[str, None]):
        """
        Add the title to the box, if given.

        Parameters
        ----------
        title : Union[str, None]
            The title. If None, this method will be skipped.
        """
        self.__title = title
        if title is None:
            return
        self.setFontPointSize(self.__qtapp.standard_fontsize + 3)
        self.setFontWeight(75)
        self.append(f"{title}")
        self.setFontPointSize(self.__qtapp.standard_fontsize + 1)

    def setTextFromDict(
        self,
        text_dict: dict,
        title: Union[str, None] = None,
        one_line_entries: bool = False,
        indent: int = 4,
    ):
        """
        Set the widget's text.

        This widget accepts both a single text entry and a list of entries
        for the text. A list of entries will be converted to a single text
        according to a <key: entry> scheme.

        Parameters
        ----------
        text_dict : dict
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
        self.__text = ""
        for _key, _value in text_dict.items():
            if one_line_entries:
                self.__text += f"{_key}: {_value}\n"
            else:
                _items = _value.split("\n")
                self.setFontWeight(75)
                self.__text += f"\n{_key}:\n"
                self.setFontWeight(50)
                for item in _items:
                    _indent = " " * indent if item[:indent] != " " * indent else ""
                    self.__text += _indent + item + "\n"
        self.setText(self.__text, title=title)

    @QtCore.Slot()
    def reprint(self):
        """
        Reprint the latest text with the updated font settings.
        """
        self.setFontPointSize(self.__qtapp.standard_fontsize + 1)
        self.setText(self.__text, title=self.__title)
