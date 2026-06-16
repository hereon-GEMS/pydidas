# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ReadOnlyTextWidget"]


from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core.exceptions import UserConfigError
from pydidas.widgets.factory.pydidas_widget_mixin import PydidasWidgetMixin


class ReadOnlyTextWidget(PydidasWidgetMixin, QtWidgets.QTextEdit):
    """
    A QTextEdit widget with advanced text display and formatting support.

    The ReadOnlyTextWidget is a subclass of QTextEdit and is used to
    display scrollable text. It allows four formatters for text.

    - 'plain' : No indent and regular text
    - 'header' : No indent and bold font
    - 'section' : A single indent level and regular text
    - 'subsection' : Two indent levels and regular text

    The formats can be specified in the :py:meth:`set_text` or
    :py:meth:`append_text` method or by supplying a list of items.

    Parameters
    ----------
    parent : QWidget, optional
        The Qt parent widget. The default is None.
    **kwargs : Any
        Any arguments which have an associated setArgName method in Qt can
        be used at creation.
    """

    init_kwargs = PydidasWidgetMixin.init_kwargs + ["line_wrap_width"]

    # Class-level formatter objects (shared across all instances)
    _BLOCK_FORMAT_STANDARD = QtGui.QTextBlockFormat()
    _BLOCK_FORMAT_STANDARD.setIndent(0)
    _BLOCK_FORMAT_SECTION = QtGui.QTextBlockFormat()
    _BLOCK_FORMAT_SECTION.setIndent(1)
    _BLOCK_FORMAT_SUBSECTION = QtGui.QTextBlockFormat()
    _BLOCK_FORMAT_SUBSECTION.setIndent(2)
    _CHAR_FORMAT_NORMAL = QtGui.QTextCharFormat()
    _CHAR_FORMAT_NORMAL.setFontWeight(QtGui.QFont.Normal)
    _CHAR_FORMAT_BOLD = QtGui.QTextCharFormat()
    _CHAR_FORMAT_BOLD.setFontWeight(QtGui.QFont.Bold)

    def __init__(self, parent: QtWidgets.QWidget | None = None, **kwargs: Any):
        """
        Initialize the ReadOnlyTextWidget.

        Parameters
        ----------
        parent : QWidget, optional
            The Qt parent widget. The default is None.
        **kwargs : Any
            Additional keyword arguments passed to PydidasWidgetMixin.
        """
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
        self._current_content: list[tuple[str, str]] = self.default_text
        self._title: str = ""
        self.setLineWrapMode(QtWidgets.QTextEdit.FixedColumnWidth)
        self.setLineWrapColumnOrWidth(kwargs.get("line_wrap_width", 80))
        self.setWordWrapMode(QtGui.QTextOption.WordWrap)

    # Re-implemented Qt methods:

    def setText(self, text: str, title: str = "") -> None:
        """
        Set the widget's text.

        Parameters
        ----------
        text : str
            The text to be displayed.
        title : str
            The title. If an empty string, no title will be printed.
            The default is ''.
        """
        self._title = title
        self._current_content = [("plain", text)]
        self._print_contents()

    @QtCore.Slot()
    def reprint(self) -> None:
        """Reprint the latest text with the updated font settings."""
        self._print_contents()

    @QtCore.Slot()
    def clear(self) -> None:
        """Clear the widget and reset the content tracking."""
        super().clear()
        self._current_content = self.default_text

    # New public methods:

    # Set an alias for setText in Python style
    set_text = setText

    @property
    def default_text(self) -> list[tuple[str, str]]:
        """Get the default text (the first entry in the content list)."""
        return [("plain", "")]

    def append_text(self, text: str, formatter: str = "plain") -> None:
        """
        Append text to the widget with a specified formatter.

        Parameters
        ----------
        text : str
            The text to be appended.
        formatter : str
            The formatter of the text. Can be 'plain', 'header', 'section',
            or 'subsection'. The default is 'plain'.
        """
        _entry = (formatter, text)
        if self._current_content == self.default_text:
            self._current_content = [_entry]
        else:
            self._current_content.append(_entry)
        self._print_contents()

    def prepend_text(self, text: str, formatter: str = "plain") -> None:
        """
        Prepend text to the widget with a specified formatter.

        Parameters
        ----------
        text : str
            The text to be appended.
        formatter : str
            The formatter of the text. Can be 'plain', 'header', 'section',
            or 'subsection'. The default is 'plain'.
        """
        _entry = (formatter, text)
        if self._current_content == self.default_text:
            self._current_content = [_entry]
        else:
            self._current_content.insert(0, _entry)
        self._print_contents()

    def set_title(self, title: str) -> None:
        """
        Update the displayed title without changing the text.

        Parameters
        ----------
        title : str
            The new title.
        """
        self._title = title
        self._print_contents()

    # TODO: Rename set_text_from_list to reasonable name
    def set_text_from_list(
        self, text_list: list[tuple[str, str]], title: str = ""
    ) -> None:
        """
        Set the widget's text from a list of entries.

        Each entry in the list is a tuple with the first element being the
        `type` of the entry (header, section, subsection) and the second
        element being the value. The type will determine the formatting of
        the entry.

        Parameters
        ----------
        text_list: list[tuple[str, str]]
            The list of entries. Each entry is a tuple with the formatter key
            and text entries to be displayed.
        title : str
            The title. If an empty string, no title will be printed.
            The default is ''.
        """
        self._current_content = text_list
        self._title = title
        self._print_contents()

        # Private methods:

    def _print_contents(self) -> None:
        """Print the currently stored content."""
        super().clear()
        self._print_title()
        self.setFontPointSize(self._qtapp.font_size + 1)
        _cursor = self.textCursor()
        for _format, _text in self._current_content:
            if _text == "":
                continue
            if _format == "header":
                _block_format = self._BLOCK_FORMAT_STANDARD
                _char_format = self._CHAR_FORMAT_BOLD
                _text = f"\n{_text}:"
            elif _format == "section":
                _block_format = self._BLOCK_FORMAT_SECTION
                _char_format = self._CHAR_FORMAT_NORMAL
            elif _format == "subsection":
                _block_format = self._BLOCK_FORMAT_SUBSECTION
                _char_format = self._CHAR_FORMAT_NORMAL
            elif _format == "plain":
                _block_format = self._BLOCK_FORMAT_STANDARD
                _char_format = self._CHAR_FORMAT_NORMAL
            else:
                raise UserConfigError(
                    f"Unsupported formatter type: {_format} in ReadOnlyTextWidget. "
                    "Supported types are `plain`, `header`, `section`, and "
                    "`subsection`."
                )
            if not _text.endswith("\n"):
                _text += "\n"
            _cursor.setBlockFormat(_block_format)
            _cursor.setCharFormat(_char_format)
            _cursor.insertText(_text)
        self.verticalScrollBar().triggerAction(QtWidgets.QScrollBar.SliderToMinimum)

    def _print_title(self) -> None:
        """Print the box title, if set."""
        if self._title:
            self.setFontPointSize(self._qtapp.font_size + 3)
            self.setFontWeight(QtGui.QFont.Bold)
            self.append(f"{self._title}\n")
            self.setFontPointSize(self._qtapp.font_size + 1)
            self.setFontWeight(QtGui.QFont.Normal)
