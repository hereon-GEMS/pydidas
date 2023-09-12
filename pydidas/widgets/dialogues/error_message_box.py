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
Module with ErrorMessageBox class for exception output.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ErrorMessageBox"]


import os

from qtpy import QtCore, QtGui, QtWidgets

from ...core.constants import ALIGN_TOP_RIGHT, POLICY_EXP_EXP, PYDIDAS_FEEDBACK_URL
from ...core.utils import (
    copy_text_to_system_clipbord,
    get_logging_dir,
    update_size_policy,
)
from ...resources import icons, logos
from ..factory import CreateWidgetsMixIn
from ..scroll_area import ScrollArea


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

    def __init__(self, *args, **kwargs):
        self._text = kwargs.pop("text", "")
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        self.setWindowTitle("Unhandled exception")
        self.setWindowIcon(icons.pydidas_error_icon_with_bg())
        _layout = QtWidgets.QGridLayout()
        self.setLayout(_layout)
        _font_height_metric = QtWidgets.QApplication.instance().standard_font_height

        self.create_label(
            "title",
            "An unhandled exception has occurred",
            bold=True,
            fontsize_offset=2,
            font_metric_width_factor=40,
            gridPos=(0, 0, 1, 2),
        )
        self.create_label(
            "label",
            "",
            parent_widget=None,
            sizePolicy=POLICY_EXP_EXP,
            textInteractionFlags=QtCore.Qt.TextSelectableByMouse,
        )

        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            gridPos=(1, 0, 2, 2),
            widget=self._widgets["label"],
        )
        update_size_policy(self._widgets["scroll_area"], horizontalStretch=1)
        self.create_button(
            "button_copy",
            "Copy to clipboard and open webpage",
            font_metric_width_factor=18,
            gridPos=(3, 0, 1, 1),
        )

        self.add_any_widget(
            "icon",
            logos.pydidas_error_svg(),
            fixedHeight=_font_height_metric * 9,
            fixedWidth=_font_height_metric * 9,
            gridPos=(0, 2, 2, 1),
            layout_kwargs={"alignment": ALIGN_TOP_RIGHT},
        )
        self.create_button(
            "button_okay",
            "Acknowledge",
            font_metric_width_factor=9,
            gridPos=(3, 2, 1, 1),
        )

        self._widgets["button_okay"].clicked.connect(self.close)
        self._widgets["button_copy"].clicked.connect(
            self.copy_to_clipboard_and_open_webpage
        )
        self.resize(_font_height_metric * 50, _font_height_metric * 30)
        self.set_text(self._text)
        for _name in ["icon", "label", "scroll_area", "title"]:
            self._widgets[_name].setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        for _name in ["button_okay", "button_copy"]:
            self._widgets[_name].setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
        self.setTabOrder(self._widgets["button_copy"], self._widgets["button_okay"])

    def set_text(self, text):
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.
        """
        _logfile = os.path.join(get_logging_dir(), "pydidas_exception.log")
        _note = (
            "Please report the bug online using the following form:\n"
            "\thttps://ms.hereon.de/pydidas\n\n"
            "You can simply use the button on the bottom left to open the\n"
            "Webpage in your default browser. The exception trace has been \n"
            "copied to your clipboard."
            f"\n\nA log has been written to:\n\t{_logfile}\n\n"
            + "-" * 20
            + "\n"
            + "Exception trace:\n\n"
        )
        self._text = text
        copy_text_to_system_clipbord(self._text)
        self._widgets["label"].setText(_note + text)

    def copy_to_clipboard_and_open_webpage(self):
        """
        Copy the trace to the clipboard and open the URL for the pydidas
        feedback form.
        """
        copy_text_to_system_clipbord(self._text)
        QtGui.QDesktopServices.openUrl(PYDIDAS_FEEDBACK_URL)
