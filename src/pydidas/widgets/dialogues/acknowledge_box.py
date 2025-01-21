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
Module with AcknowledgeBox class for handling dialogues with an 'acknowledge' tick
box to hide this dialogue in the future.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AcknowledgeBox"]


from qtpy import QtCore, QtWidgets

from pydidas.core.constants import (
    FONT_METRIC_CONSOLE_WIDTH,
    FONT_METRIC_MEDIUM_BUTTON_WIDTH,
    FONT_METRIC_WIDE_CONFIG_WIDTH,
    POLICY_EXP_EXP,
)
from pydidas.core.utils import format_input_to_multiline_str
from pydidas.resources import icons
from pydidas.widgets.factory import CreateWidgetsMixIn


class AcknowledgeBox(QtWidgets.QDialog, CreateWidgetsMixIn):
    """
    Show a dialogue box with information to be acknowledged.

    Parameters
    ----------
    *args : tuple
        Arguments passed to QtWidgets.QDialogue instanciation.
    **kwargs : dict
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

    def __init__(self, *args: tuple, **kwargs: dict):
        _text = kwargs.pop("text", "")
        _text_preformatted = kwargs.pop("text_preformatted", False)
        _title = kwargs.pop("title", "Notice")
        _show_checkbox = kwargs.pop("show_checkbox", True)
        _qtapp = QtWidgets.QApplication.instance()
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        self.setWindowTitle(_title)
        self.setWindowIcon(icons.pydidas_icon())
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
            gridPos=(1, 0, 1, 2),
            indent=8,
            sizePolicy=POLICY_EXP_EXP,
            textInteractionFlags=QtCore.Qt.TextSelectableByMouse,
        )

        self.add_any_widget(
            "acknowledge",
            QtWidgets.QCheckBox("Do not show this notice again"),
            gridPos=(2, 0, 1, 1),
            visible=_show_checkbox,
        )
        self.create_button(
            "button_okay",
            "Acknowledge",
            clicked=self.close,
            font_metric_width_factor=FONT_METRIC_MEDIUM_BUTTON_WIDTH,
            gridPos=(2, 2, 1, 1),
        )
        self.set_text(_text, pre_formatted=_text_preformatted)

        self.setFixedWidth(
            int(_qtapp.font_char_width * (FONT_METRIC_CONSOLE_WIDTH + 10))
        )

    def set_text(self, text: str, pre_formatted: bool = False):
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.
        pre_formatted : bool, optional
            Flag to keep the text formatting. The default is False.
        """
        if not pre_formatted:
            text = format_input_to_multiline_str(text, max_line_length=60)
        self._widgets["label"].setText(text)
        self._widgets["label"].font_metric_height_factor = len(text.split("\n"))

    @QtCore.Slot()
    def close(self):
        """
        Close the widget and store the acknowledge state.
        """
        super().close()
        if self._widgets["acknowledge"].isChecked():
            self.setResult(QtWidgets.QDialog.Accepted)
        else:
            self.setResult(QtWidgets.QDialog.Rejected)
