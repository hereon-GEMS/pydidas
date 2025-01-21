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
Module with ErrorMessageBox class for exception output.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ErrorMessageBox"]


import os

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core.constants import (
    ALIGN_TOP_RIGHT,
    FONT_METRIC_CONSOLE_WIDTH,
    FONT_METRIC_HALF_CONSOLE_WIDTH,
    FONT_METRIC_MEDIUM_BUTTON_WIDTH,
    POLICY_EXP_EXP,
    PYDIDAS_FEEDBACK_URL,
)
from pydidas.core.utils import copy_text_to_system_clipbord, get_logging_dir
from pydidas.resources import icons, logos
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.scroll_area import ScrollArea


class ErrorMessageBox(QtWidgets.QDialog, CreateWidgetsMixIn):
    """
    Show a dialogue box with exception information.

    Parameters
    ----------
    *args : tuple
        Arguments passed to QtWidgets.QDialogue instanciation.
    **kwargs : dict
        Keyword arguments passed to QtWidgets.QDialogue instanciation.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        self._text = kwargs.pop("text", "")
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        self.setWindowTitle("Unhandled exception")
        self.setWindowIcon(icons.pydidas_error_icon_with_bg())
        _layout = QtWidgets.QGridLayout()
        self.setLayout(_layout)
        _char_width, _char_height = QtWidgets.QApplication.instance().font_metrics

        self.create_label(
            "title",
            "An unhandled exception has occurred",
            bold=True,
            fontsize_offset=2,
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
            gridPos=(0, 0, 1, 2),
        )
        self.create_label(
            "label",
            "",
            font_metric_width_factor=FONT_METRIC_CONSOLE_WIDTH,
            parent_widget=None,
            sizePolicy=POLICY_EXP_EXP,
            textInteractionFlags=QtCore.Qt.TextSelectableByMouse,
        )

        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            gridPos=(1, 0, 2, 2),
            resize_to_widget_width=True,
            widget=self._widgets["label"],
        )
        self.create_button(
            "button_copy",
            "Copy to clipboard and open webpage",
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            gridPos=(3, 0, 1, 1),
        )

        self.add_any_widget(
            "icon",
            logos.pydidas_error_svg(),
            fixedHeight=_char_height * 9,
            fixedWidth=_char_height * 9,
            gridPos=(0, 2, 2, 1),
            layout_kwargs={"alignment": ALIGN_TOP_RIGHT},
        )
        self.create_button(
            "button_okay",
            "Acknowledge",
            font_metric_width_factor=FONT_METRIC_MEDIUM_BUTTON_WIDTH,
            gridPos=(3, 2, 1, 1),
        )

        self._widgets["button_okay"].clicked.connect(self.close)
        self._widgets["button_copy"].clicked.connect(
            self.copy_to_clipboard_and_open_webpage
        )
        self.set_text(self._text)
        self.resize(
            int(
                _char_width * self._widgets["label"].font_metric_width_factor
                + 10 * _char_height
                + 20
            ),
            int(_char_height * 30 + 20),
        )
        for _name in ["icon", "label", "scroll_area", "title"]:
            self._widgets[_name].setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        for _name in ["button_okay", "button_copy"]:
            self._widgets[_name].setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
        self.setTabOrder(self._widgets["button_copy"], self._widgets["button_okay"])

    def set_text(self, text: str):
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.
        """
        _logfile = os.path.join(get_logging_dir(), "pydidas_exception.log")
        _note = (
            "Please report the bug online using the form available on:\n"
            "\thttps://pydidas.hereon.de/\n\n"
            "You can simply use the button on the bottom left to coyy the\n"
            "exception trace to your clipboard and open the webpage in your"
            " default browser."
            f"\n\nA log has been written to:\n\t{_logfile}\n\n"
            + "-" * 20
            + "\n"
            + "Exception trace:\n\n"
        )
        self._text = text
        self._widgets["label"].setText(_note + text)
        _lines = (_note + text).split("\n")
        _max_len = max(len(_line) for _line in _lines)
        self._widgets["label"].font_metric_height_factor = len(_lines)
        self._widgets["label"].font_metric_width_factor = _max_len + 5

    def copy_to_clipboard_and_open_webpage(self):
        """
        Copy the trace to the clipboard and open the URL for the pydidas
        feedback form.
        """
        copy_text_to_system_clipbord(self._text)
        QtGui.QDesktopServices.openUrl(PYDIDAS_FEEDBACK_URL)

    def exec(self):
        """
        Execute the dialogue box.
        """
        self.show()
        self.activateWindow()
        return QtWidgets.QDialog.exec(self)

    def exec_(self):
        """
        Execute the dialogue box.
        """
        return self.exec()
