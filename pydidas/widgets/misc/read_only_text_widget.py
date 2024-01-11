# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ReadOnlyTextWidget"]


from typing import Union

from qtpy import QtCore, QtGui, QtWidgets

from ..factory.pydidas_widget_mixin import PydidasWidgetMixin


class ReadOnlyTextWidget(PydidasWidgetMixin, QtWidgets.QTextEdit):
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

    def __init__(self, parent: Union[None, QtWidgets.QWidget] = None, **kwargs: dict):
        QtWidgets.QTextEdit.__init__(self, parent)
        kwargs["minimumWidth"] = kwargs.get("minimumWidth", 300)
        kwargs["readOnly"] = kwargs.get("readOnly", True)
        kwargs["acceptRichText"] = kwargs.get("acceptRichText", True)
        # if fixed settings are given, overwrite the minimum size settings
        # because the minimumSize take precedence in Qt:
        if "fixedWidth" in kwargs and "minimumWidth" in kwargs:
            del kwargs["minimumWidth"]
        if "fixedHeight" in kwargs and "minimumHeight" in kwargs:
            del kwargs["minimumHeight"]
        PydidasWidgetMixin.__init__(self, **kwargs)
        if hasattr(self._qtapp, "sig_font_size_changed"):
            self._qtapp.sig_font_size_changed.connect(self.reprint)
        self.__text = ""
        self.__title = None

    def setText(self, text: str, title: str = ""):
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
        self.__add_title(title)
        self.__text = text
        if isinstance(text, list):
            for _weight, _txt in text:
                self.setFontWeight(_weight)
                self.append(_txt)
        else:
            self.append(text)
        self.verticalScrollBar().triggerAction(QtWidgets.QScrollBar.SliderToMinimum)

    def __add_title(self, title: str):
        """
        Add the title to the box, if given.

        Parameters
        ----------
        title : str
            The title to be added. Use an empty string to skip the title.
        """
        self.__title = title
        if title == "":
            return
        self.setFontPointSize(self._qtapp.font_size + 3)
        self.setFontWeight(QtGui.QFont.Bold)
        self.append(f"{title}")
        self.setFontPointSize(self._qtapp.font_size + 1)
        self.setFontWeight(QtGui.QFont.Normal)

    def set_text_from_dict(
        self,
        text_dict: dict,
        title: str = "",
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
        self.__text = []
        for _key, _value in text_dict.items():
            if one_line_entries:
                self.__text.append([QtGui.QFont.Normal, f"{_key}: {_value}"])
            else:
                _items = _value.split("\n")
                self.__text.append([QtGui.QFont.Bold, f"\n{_key}:"])
                for item in _items:
                    _indent = " " * indent if item[:indent] != " " * indent else ""
                    self.__text.append([QtGui.QFont.Normal, _indent + item])
        self.setText(self.__text, title=title)

    @QtCore.Slot()
    def reprint(self):
        """
        Reprint the latest text with the updated font settings.
        """
        self.setFontPointSize(self._qtapp.font_size + 1)
        self.setText(self.__text, title=self.__title)
