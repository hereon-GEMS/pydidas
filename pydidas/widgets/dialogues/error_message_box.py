# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with ErrorMessageBox class for exception output."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ErrorMessageBox']

from PyQt5 import QtCore, QtWidgets

class ErrorMessageBox(QtWidgets.QDialog):
    """
    Show a dialogue box with exception information.

    Methods
    -------
    setText(str) :
        Set the message box text to the input string.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the message box.

        Parameters
        ----------
        *args : TYPE
            Arguments passed to QtWidgets.QDialogue instantiation.
        **kwargs : TYPE
            Keyword arguments passed to QtWidgets.QDialogue instantiation.

        Returns
        -------
        None.
        """
        _text = None
        if 'text' in kwargs:
            _text = kwargs['text']
            del kwargs['text']
        super().__init__(*args, **kwargs)
        self.setWindowTitle("An exception has occured")

        self._label = QtWidgets.QLabel()
        self._label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._label.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        _scroll_area = QtWidgets.QScrollArea()

        _scroll_area.setWidget(self._label)
        _scroll_area.setWidgetResizable(True)
        _scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        _ok_button = QtWidgets.QPushButton('OK')

        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(_scroll_area)
        _layout.addWidget(_ok_button, 1, QtCore.Qt.AlignRight)

        self.setLayout(_layout)
        _ok_button.clicked.connect(self.close)
        self.resize(800, self.height())
        if _text:
            self.set_text(_text)

    # def __exec__(self):
    #     """
    #     Show the box.

    #     This method will show the ErrorMessageBox
    #     """
    #     self.exec_()

    def set_text(self, text):
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.
        """
        self._label.setText(text)
