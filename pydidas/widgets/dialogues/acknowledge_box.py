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
Module with AcknowledgeBox class for handling  dialogues with an 'acknowledge' tick
box to hide this dialogue in the future.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AcknowledgeBox"]


from qtpy import QtCore, QtWidgets

from ...core.constants import POLICY_EXP_EXP
from ...core.utils import apply_qt_properties, format_input_to_multiline_str
from ...resources import icons
from ..factory import CreateWidgetsMixIn
from ..scroll_area import ScrollArea


class AcknowledgeBox(QtWidgets.QDialog, CreateWidgetsMixIn):
    """
    Show a dialogue box with information to be acknowledged.

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
        self.setWindowTitle("Notice")
        self.setWindowIcon(icons.pydidas_icon())
        _layout = QtWidgets.QGridLayout()
        self.setLayout(_layout)

        self.create_label(
            "title",
            "Notice:",
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
        self.add_any_widget(
            "acknowledge",
            QtWidgets.QCheckBox("Do not show this notice again"),
            gridPos=(2, 0, 1, 2),
        )
        self.create_button("button_okay", "Acknowledge", gridPos=(2, 3, 1, 1))

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
