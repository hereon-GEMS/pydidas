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
Module with UserConfigErrorMessageBox class for handling user config exceptions in a
lighter way.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["UserConfigErrorMessageBox"]


from qtpy import QtCore, QtWidgets

from ...core.constants import POLICY_EXP_EXP
from ...core.utils import apply_qt_properties, format_input_to_multiline_str
from ...resources import icons, logos
from ..factory import CreateWidgetsMixIn
from ..scroll_area import ScrollArea


class UserConfigErrorMessageBox(QtWidgets.QDialog, CreateWidgetsMixIn):
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
        _text = kwargs.pop("text", "")
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        self.setWindowTitle("Configuration error")
        self.setWindowIcon(icons.pydidas_error_icon_with_bg())
        _layout = QtWidgets.QGridLayout()
        self.setLayout(_layout)
        self.create_label(
            "title",
            "Configuration error:",
            fontsize=12,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self._widgets["label"] = QtWidgets.QLabel()
        apply_qt_properties(
            self._widgets["label"],
            textInteractionFlags=QtCore.Qt.TextSelectableByMouse,
            sizePolicy=POLICY_EXP_EXP,
            indent=8,
            fixedWidth=500,
        )

        self.create_any_widget(
            "scroll_area",
            ScrollArea,
            widget=self._widgets["label"],
            gridPos=(1, 0, 1, 2),
        )
        self.create_button("button_okay", "Acknowledge", gridPos=(2, 3, 1, 1))

        self.add_any_widget(
            "icon",
            logos.pydidas_error_svg(),
            fixedHeight=100,
            fixedWidth=100,
            autoDefault=True,
            default=True,
            layout_kwargs={"alignment": (QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)},
            gridPos=(0, 2, 2, 2),
        )

        self._widgets["button_okay"].clicked.connect(self.close)
        self.set_text(_text)

    def set_text(self, text):
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.
        """
        _new_text = format_input_to_multiline_str(text, max_line_length=60)
        self._widgets["label"].setText(_new_text)
