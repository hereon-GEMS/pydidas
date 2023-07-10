# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with QuestionBox class which shows a dialog with a yes/no reply.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["QuestionBox"]


from qtpy import QtWidgets

from ..utilities import get_pyqt_icon_from_str


class QuestionBox(QtWidgets.QMessageBox):
    """
    Show a dialogue box with a yes/no question.

    Parameters
    ----------
    title : str
        The QuestionBox title.
    question : str
        The question text.
    explanation : str, optional
        An explanatory text to amend the question text.
    parent : Union[None, QtWidgets.QWidget], optional
        The parent widget. The default is None.
    default : QtWidgets.QMessageBox.StandardButton, optional
        The default pre-selected button. The default is No.
    tooltip : str, optional
        The tooltip text for the dialog. The default is an empty string.
    """

    def __init__(
        self,
        title,
        question,
        explanation="",
        parent=None,
        default=QtWidgets.QMessageBox.No,
        tooltip="",
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(get_pyqt_icon_from_str("qt-std::SP_MessageBoxQuestion"))
        self.setText(question)
        if len(explanation) > 0:
            self.setInformativeText(explanation)
        if len(tooltip) > 0:
            self.setToolTip(tooltip)
        self.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        self.setDefaultButton(default)

    def exec_(self):
        """
        Show the box.

        This method will show the QuestionBox
        """
        _res = super().exec_()
        if _res == QtWidgets.QMessageBox.Yes:
            return True
        return False
