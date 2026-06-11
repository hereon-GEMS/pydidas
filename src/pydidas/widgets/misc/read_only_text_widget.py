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

from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin

raise AttributeError("Must continue work here to finish _print_contents")

class ReadOnlyTextWidget(PydidasWidgetMixin, QtWidgets.QTextEdit):
    """
    A QTextEdit widget with some layout settings in setup and a more advanced setText.

    The ReadOnlyTextWidget is a subclass of QTextEdit and is used to
    display scrollable text. It allows four formatters for text.

    - 'plain' : No indent and regular text
    - 'header' : No indent and bold font
    - 'section' : A single indent level and regular text
    - 'subsection' : Two indent levels and regular text

    The formas can be specified in the :py:meth:`ReadOnlyTextWidget.append_text'
    or specified if giving a list of items.

    Parameters
    ----------
    parent : QWidget, optional
        The Qt parent widget. The default is None.
    **kwargs : Any supported Qt arguments
        Any arguments which have an associated setArgName method in Qt can be used
        at creation.
    """

    init_kwargs = PydidasWidgetMixin.init_kwargs + ["line_wrap_width"]

    # Class-level formatter objects (shared across all instances)
    _BLOCK_FORMAT_HEADER = QtGui.QTextBlockFormat()
    _BLOCK_FORMAT_HEADER.setIndent(0)
    _BLOCK_FORMAT_SECTION = QtGui.QTextBlockFormat()
    _BLOCK_FORMAT_SECTION.setIndent(1)
    _BLOCK_FORMAT_SUBSECTION = QtGui.QTextBlockFormat()
    _BLOCK_FORMAT_SUBSECTION.setIndent(2)
    _CHAR_FORMAT_NORMAL = QtGui.QTextCharFormat()
    _CHAR_FORMAT_NORMAL.setFontWeight(QtGui.QFont.Normal)
    _CHAR_FORMAT_BOLD = QtGui.QTextCharFormat()
    _CHAR_FORMAT_BOLD.setFontWeight(QtGui.QFont.Bold)

    def __init__(self, parent: QtWidgets.QWidget | None = None, **kwargs: Any):
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
        self._current_content : list[tuple[str, str]] = [("simple", "")]
        self.self._title : str = ""
        self.setLineWrapMode(QtWidgets.QTextEdit.FixedColumnWidth)
        self.setLineWrapColumnOrWidth(kwargs.get("line_wrap_width", 80))
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
            The title. If an empty string, no title will be printed.
            The default is ''.
        """
        self._title = title
        self._current_content = [("plain", text)]
        self._print_contents()

    # define an alias in Python style
    set_text = setText

    def append_text(self, text: str, formatter: str="plain"):
        """

        Parameters
        ----------
        text : str
            The text to be appended.
        formatter : str, optional
            The formatter of the text. Can be 'plain', 'header', 'section',
            or 'subsection'. The default is 'plain'.
        """
        self._current_content.append((formatter, text))

    # TODO: Rename set_text_from_list to reasonable name
    def set_text_from_list(self, ):

    def update_title(self, title: str):
        """
        Update the displayed title without changing the text.

        Parameters
        ----------
        title : str
            The new title.
        """
        self._title = title
        self._print_contents()


    def _print_contents(self) -> None:
        """Print the current content."""
        self.clear()

        self.verticalScrollBar().triggerAction(QtWidgets.QScrollBar.SliderToMinimum)

    def _add_title(self, title: str):
        """
        Add the title to the box, if given.

        Parameters
        ----------
        title : str
            The title to be added. Use an empty string to skip the title.
        """
        self.self._title = title
        if title == "":
            return
        self.setFontPointSize(self._qtapp.font_size + 3)
        self.setFontWeight(QtGui.QFont.Bold)
        self.append(f"{title}\n")
        self.setFontPointSize(self._qtapp.font_size + 1)
        self.setFontWeight(QtGui.QFont.Normal)

    def set_text_from_list(
        self,
        text_list: list[tuple[str, str]],
        title: str  | None = ""
    ):
        """
        Set the widget's text from a list of entries.

        Each entry in the list is a tuple with the first element being the
        `type` of the entry (header, section, subsection) and the second
        element being the value. The type will determine the formatterting of
        the entry.

        Parameters
        ----------
        text_list: list[tuple[str, str]]
            The list of entries. Each entry is a tuple with the formatter key
            and text entries to be displayed.
        title : str or None, optional
            The title. If None, the current title will be kept. If an empty
            string, no title will be printed. The default is ''.
        """
        self._current_content = text_list
        if title is not None:
            self._title = title


            self._add_title(title)
        cursor = self.textCursor()

        for _type, _value in text_list:
            if _type == "header":
                cursor.setBlockFormat(self._BLOCK_FORMAT_HEADER)
                cursor.setCharFormat(self._CHAR_FORMAT_BOLD)
                cursor.insertText(f"\n{_value}:\n")
            elif _type == "section":
                cursor.setBlockFormat(self._BLOCK_FORMAT_SECTION)
                cursor.setCharFormat(self._CHAR_FORMAT_NORMAL)
                self.setFontWeight(QtGui.QFont.Normal)
                cursor.insertText(f"{_value}\n")
            elif _type == "subsection":
                cursor.setBlockFormat(self._BLOCK_FORMAT_SUBSECTION)
                cursor.setCharFormat(self._CHAR_FORMAT_NORMAL)
                cursor.insertText(f"{_value}\n")

    @QtCore.Slot()
    def reprint(self):
        """
        Reprint the latest text with the updated font settings.
        """
        self.setFontPointSize(self._qtapp.font_size + 1)
        if isinstance(self._current_content, list):
            self.set_text_from_list(self._current_content, title=self.self._title)
        else:
            self.setText(self._current_content, title=self.self._title)
