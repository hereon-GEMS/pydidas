# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with PydidasExceptionMessageBox class for handling user config exceptions in a
lighter way.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasExceptionMessageBox"]


from qtpy import QtCore, QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_SMALL_BUTTON_WIDTH,
    FONT_METRIC_WIDE_CONFIG_WIDTH,
    POLICY_EXP_EXP,
)
from pydidas.core.utils import format_input_to_multiline_str
from pydidas.resources import icons, logos
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.scroll_area import ScrollArea


class PydidasExceptionMessageBox(QtWidgets.QDialog, CreateWidgetsMixIn):
    """
    Show a dialogue box with exception information.

    Parameters
    ----------
    *args : tuple
        Arguments passed to QtWidgets.QDialogue instanciation.
    **kwargs : dict
        Supported keyword arguments are:

        text : str, optional
            The error string. The default is an empty string.
        title : str, optional
            The window title. The default is "Configuration error".
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        _text = kwargs.pop("text", "")
        _title = kwargs.pop("title", "Configuration error")
        _font_height = QtWidgets.QApplication.instance().font_height
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        self.setWindowTitle(_title)
        self.setWindowIcon(icons.pydidas_error_icon_with_bg())
        _layout = QtWidgets.QGridLayout()
        self.setLayout(_layout)
        self.create_label(
            "title",
            f"{_title}:",
            bold=True,
            fontsize_offset=2,
        )
        self.create_label(
            "label",
            "",
            font_metric_width_factor=FONT_METRIC_WIDE_CONFIG_WIDTH,
            indent=8,
            sizePolicy=POLICY_EXP_EXP,
            textInteractionFlags=QtCore.Qt.TextSelectableByMouse,
        )
        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            gridPos=(1, 0, 1, 2),
            widget=self._widgets["label"],
        )
        self.create_button(
            "button_okay",
            "Acknowledge",
            gridPos=(2, 3, 1, 1),
            font_metric_width_factor=FONT_METRIC_SMALL_BUTTON_WIDTH,
        )

        self.add_any_widget(
            "icon",
            logos.pydidas_error_svg(),
            fixedHeight=_font_height * 6,
            fixedWidth=_font_height * 6,
            autoDefault=True,
            default=True,
            gridPos=(0, 2, 2, 2),
            layout_kwargs={"alignment": (QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)},
        )
        self._widgets["button_okay"].clicked.connect(self.close)
        self.set_text(_text)

    def set_text(self, text: str):
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.
        """
        _new_text = format_input_to_multiline_str(text, max_line_length=60)
        self._widgets["label"].font_metric_height_factor = _new_text.count("\n") + 1
        self._widgets["label"].setText(_new_text)
