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
Module with the FeedbackWindow class which allows users to create a quick feedback
form which they can copy and pasteto submit feedback.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FeedbackWindow"]

from qtpy import QtCore, QtWidgets, QtGui

from ...core import Parameter, ParameterCollection
from ...core.constants import PYDIDAS_FEEDBACK_URL
from ...core.utils import copy_text_to_system_clipbord
from .pydidas_window import PydidasWindow


INFO_TEXT = (
    "Please enter information about the problem/suggestion below and fill out "
    "the form. \nUsing the button at the bottom of the window will copy the "
    "given information to the clipboard. Please paste the information in the "
    "field on the webpage and submit the feedback on the webpage.\n"
    "(You can use only the 'detailed feedback' field, all information will be "
    "encoded in the detailed feedback.)"
)


class FeedbackWindow(PydidasWindow):
    """
    Create all widgets and initialize their state.

    Parameters
    ----------
    self : pydidas.gui.ScanSetupFrame
        The ScanSetupFrame instance.
    """

    show_frame = False
    default_params = ParameterCollection(
        Parameter("email", str, "", name="E-mail address (optional)")
    )

    def __init__(self, parent=None, **kwargs):
        PydidasWindow.__init__(self, parent, title="pydidas feedback", **kwargs)

    def build_frame(self):
        """
        Create all widgets for the frame and place them in the layout.
        """
        self.setFixedWidth(400)

        self.create_label(
            "label_title",
            "pydidas Feedback",
            fontsize=12,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self.create_label(
            "label_title",
            INFO_TEXT,
            gridPos=(-1, 0, 1, 1),
        )

        self.create_line(None)
        self.create_label(
            "label_title",
            "type of feedback",
            fontsize=10,
            bold=True,
            gridPos=(-1, 0, 1, 1),
        )
        self.create_radio_button_group(
            "type",
            ["Bug report", "Improvement suggestion", "Usage question"],
            gridPos=(-1, 0, 1, 1),
        )
        self.create_line(None)
        self.create_spacer(None)
        self.create_label(
            "label_title",
            "feedback information",
            fontsize=10,
            bold=True,
            gridPos=(-1, 0, 1, 1),
        )
        self.create_param_widget(self.get_param("email"), width_text=170, width_io=200)
        self.create_label(
            "label_details",
            "details:",
            gridPos=(-1, 0, 1, 1),
        )
        self.add_any_widget(
            "details", QtWidgets.QPlainTextEdit(), fixedWidth=380, fixedHeight=500
        )
        self.create_button(
            "button_copy", "Copy to clipboard and open feedback webpage."
        )

    def connect_signals(self):
        """
        Connect the signals.
        """
        self._widgets["button_copy"].clicked.connect(self._submit_feedback)

    @QtCore.Slot()
    def _submit_feedback(self):
        _text = (
            f"Sender: {self.get_param_value('email')}\n\n"
            f"Type: {self._widgets['type'].active_label}\n\n"
            f"Details: \n{self._widgets['details'].toPlainText()}"
        )
        copy_text_to_system_clipbord(_text)
        QtGui.QDesktopServices.openUrl(PYDIDAS_FEEDBACK_URL)
