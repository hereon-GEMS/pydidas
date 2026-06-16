# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with AcknowledgeBox class for handling dialogues with an 'acknowledge' tick
box to hide this dialogue in the future.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AcknowledgeBox"]


from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_MEDIUM_BUTTON_WIDTH,
    FONT_METRIC_WIDE_CONFIG_WIDTH,
    POLICY_EXP_EXP,
)
from pydidas.core.utils import format_input_to_multiline_str
from pydidas.resources import icons, logos
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.scroll_area import ScrollArea
from pydidas_qtcore.pydidas_qapp import PydidasQApplication


class AcknowledgeBox(QtWidgets.QDialog, CreateWidgetsMixIn):
    """
    Show a dialogue box with information to be acknowledged.

    Parameters
    ----------
    *args : Any
        Arguments passed to QtWidgets.QDialog instantiation.
    **kwargs : Any
        Supported keywords are:

        text : str, optional
            The notice text to be displayed. The text will be formatted to a
            line length of a maximum of 60 characters.
        text_preformatted : bool, optional
            Flag to keep the text formatting and not to auto-format the text
            to keep a width of < 60 characters.
        title : str, optional
            The title of the box. The default is "Notice"
    """

    default_title = "Notice"
    add_error_icon = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _text = kwargs.pop("text", "")
        _title = kwargs.pop("title", self.default_title)
        _text_preformatted = kwargs.pop("text_preformatted", False)
        _show_checkbox = kwargs.pop("show_checkbox", True)
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        self.__qtapp = PydidasQApplication.instance()
        self.setWindowTitle(_title)
        self.setWindowIcon(self.default_icon)
        _layout = QtWidgets.QGridLayout()
        self.setLayout(_layout)

        self.create_label(
            "title",
            f"{_title}:",
            bold=True,
            fontsize_offset=2,
            gridPos=(0, 0, 1, 2),
        )
        self.create_label(
            "label",
            "",
            font_metric_width_factor=FONT_METRIC_WIDE_CONFIG_WIDTH,
            font_metric_height_factor=3,
            indent=8,
            sizePolicy=POLICY_EXP_EXP,
            textInteractionFlags=QtCore.Qt.TextSelectableByMouse,
            parent_widget=None,
        )
        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            gridPos=(1, 0, 1, 2),
            widget=self._widgets["label"],
        )
        self.add_any_widget(
            "acknowledge",
            QtWidgets.QCheckBox("Do not show this notice again"),
            gridPos=(2, 0, 1, 1),
            visible=_show_checkbox,
        )
        if self.add_error_icon:
            self.add_any_widget(
                "icon",
                logos.pydidas_error_svg(),
                fixedHeight=self.__qtapp.font_height * 6,
                fixedWidth=self.__qtapp.font_height * 6,
                autoDefault=True,
                default=True,
                gridPos=(0, 2, 2, 1),
                layout_kwargs={
                    "alignment": (QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
                },
            )
        self.create_button(
            "button_okay",
            "Acknowledge",
            clicked=self.close,
            font_metric_width_factor=FONT_METRIC_MEDIUM_BUTTON_WIDTH,
            gridPos=(2, 2, 1, 1),
        )
        self.set_text(_text, pre_formatted=_text_preformatted)

    @property
    def default_icon(self) -> QtGui.QIcon:
        """
        The default icon for the acknowledgment box.

        Returns
        -------
        QtGui.QIcon
            The default icon.
        """
        return icons.pydidas_icon()

    def set_text(self, text: str, pre_formatted: bool = False) -> None:
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.
        pre_formatted : bool, optional
            Flag to keep the text formatting. The default is False.
        """
        _font_width = self.__qtapp.font_char_width
        if not pre_formatted:
            text = format_input_to_multiline_str(text, max_line_length=60)
        _line_len = max(len(_line) for _line in text.split("\n"))
        _n_lines = text.count("\n")
        self._widgets["label"].setText(text)
        self._widgets["label"].font_metric_height_factor = _n_lines + 2
        self._widgets["label"].font_metric_width_factor = _line_len + 5
        _scroll_width = max(
            50, min(120, self._widgets["label"].font_metric_width_factor)
        )
        self._widgets["scroll_area"].setFixedWidth(_scroll_width * _font_width)
        self._widgets["scroll_area"].setFixedHeight(
            self.__qtapp.font_height * (_n_lines + 4)
        )
        self.setFixedWidth(int(_font_width * (_scroll_width + 25)))

    @QtCore.Slot()
    def close(self) -> None:
        """
        Close the widget and store the acknowledgment state.
        """
        super().close()
        if self._widgets["acknowledge"].isChecked():
            self.setResult(QtWidgets.QDialog.Accepted)
        else:
            self.setResult(QtWidgets.QDialog.Rejected)
