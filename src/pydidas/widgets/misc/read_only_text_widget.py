# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ReadOnlyTextWidget"]

from typing import Optional, Union

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin


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
        self._current_content = ""
        self.__title = ""
        self.__block_format_header = QtGui.QTextBlockFormat()
        self.__block_format_header.setIndent(0)
        self.__block_format_section = QtGui.QTextBlockFormat()
        self.__block_format_section.setIndent(1)
        self.__block_format_subsection = QtGui.QTextBlockFormat()
        self.__block_format_subsection.setIndent(2)
        self.__char_format_normal = QtGui.QTextCharFormat()
        self.__char_format_normal.setFontWeight(QtGui.QFont.Normal)
        self.__char_format_bold = QtGui.QTextCharFormat()
        self.__char_format_bold.setFontWeight(QtGui.QFont.Bold)
        self.setLineWrapMode(QtWidgets.QTextEdit.FixedColumnWidth)
        self.setLineWrapColumnOrWidth(80)
        self.setWordWrapMode(QtGui.QTextOption.WordWrap)

    def setText(
        self,
        text: str,
        title: str = "",
    ):
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
        self._add_title(title)
        self._current_content = text
        self.append(self._current_content)
        self.verticalScrollBar().triggerAction(QtWidgets.QScrollBar.SliderToMinimum)

    def _add_title(self, title: str):
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
        self.append(f"{title}\n")
        self.setFontPointSize(self._qtapp.font_size + 1)
        self.setFontWeight(QtGui.QFont.Normal)

    def set_text_from_list(
        self,
        text_list: list[str, str],
        title: Optional[str] = None,
    ):
        """
        Set the widget's text from a list of entries.

        Each entry in the list is a tuple with the first element being the
        `type` of the entry (header, section, subsection) and the second
        element being the value. The type will determine the formatting of
        the entry.

        Parameters
        ----------
        text_list: list[str, str]
            The list of the type keys and /text entries to be displayed.
            The list will be processed with type keys used for formatting
            the entries.
        title : str, optional
            The title. If None, no title will be printed. The default is None.
        """
        self._current_content = text_list
        QtWidgets.QTextEdit.setText(self, "")
        if title is not None:
            self._add_title(title)
        cursor = self.textCursor()

        for _type, _value in text_list:
            if _type == "header":
                cursor.setBlockFormat(self.__block_format_header)
                cursor.setCharFormat(self.__char_format_bold)
                cursor.insertText(f"\n{_value}:\n")
            elif _type == "section":
                cursor.setBlockFormat(self.__block_format_section)
                cursor.setCharFormat(self.__char_format_normal)
                self.setFontWeight(QtGui.QFont.Normal)
                cursor.insertText(f"{_value}\n")
            elif _type == "subsection":
                cursor.setBlockFormat(self.__block_format_subsection)
                cursor.setCharFormat(self.__char_format_normal)
                cursor.insertText(f"{_value}\n")

    @QtCore.Slot()
    def reprint(self):
        """
        Reprint the latest text with the updated font settings.
        """
        self.setFontPointSize(self._qtapp.font_size + 1)
        if isinstance(self._current_content, list):
            self.set_text_from_list(self._current_content, title=self.__title)
        else:
            self.setText(self._current_content, title=self.__title)
