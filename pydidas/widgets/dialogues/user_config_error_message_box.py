# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["UserConfigErrorMessageBox"]

import os

from qtpy import QtCore, QtWidgets, QtSvg

from ...core.utils import get_pydidas_error_icon_w_bg, get_pydidas_icon_path
from ...core.constants import EXP_EXP_POLICY
from ...core.utils import format_input_to_multiline_str, apply_qt_properties
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
        self.setWindowIcon(get_pydidas_error_icon_w_bg())
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
            sizePolicy=EXP_EXP_POLICY,
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

        _icon_fname = os.path.join(get_pydidas_icon_path(), "pydidas_error.svg")
        self.add_any_widget(
            "icon",
            QtSvg.QSvgWidget(_icon_fname),
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
