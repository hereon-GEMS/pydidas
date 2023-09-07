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
Module with the RadioButtonGroup widget which can hold multiple QRadioButtons.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["RadioButtonGroup"]


from qtpy import QtCore, QtWidgets


class RadioButtonGroup(QtWidgets.QWidget):
    """
    The RadioButtonGroup holds a number of QRadioButtons in a QButtonGroup.

    Creation is automated based on the entries.
    """

    new_button_index = QtCore.Signal(int)
    new_button_label = QtCore.Signal(str)
    init_kwargs = ["entries", "title", "rows", "columns"]

    def __init__(self, entries, **kwargs):
        """
        Create a new RadioButtonGroup.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments. Supported kwargs are "entries" with a list of
            labels for the butttons; "rows" and "columns" to control the layout of
            the buttons and "title" to add a header label.
        """
        QtWidgets.QWidget.__init__(self, kwargs.get("parent", None))
        self._title = kwargs.get("title", None)
        for _key, _default in [["rows", 1], ["columns", -1]]:
            _val = kwargs.get(_key, _default)
            _val = _val if _val != -1 else len(entries)
            setattr(self, f"_{_key}", _val)
        self._active_index = 0
        self._emit_signal = True
        self._buttons = {}
        self._button_indices = {}
        self._button_label = {}
        if entries is not None:
            self.__create_widgets(entries)
            self._active_label = self._buttons[0].text()
        else:
            self._active_label = ""
        self._qtapp = QtWidgets.QApplication.instance()
        self._qtapp.sig_new_font_height.connect(self.set_dynamic_height_from_font)
        self.set_dynamic_height_from_font(self._qtapp.standard_font_height)

    def __create_widgets(self, entries):
        """
        Initialize the user interface with Widgets and Layout.

        Parameters
        ----------
        entries : list
            The list of entries as passed from __init__.
        """
        _yoffset = self._title is not None

        self.q_button_group = QtWidgets.QButtonGroup(self)
        _layout = QtWidgets.QGridLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(0)
        if self._title is not None:
            _label = QtWidgets.QLabel(self._title)
            _layout.addWidget(_label, 0, 0, 1, self._columns, QtCore.Qt.AlignBottom)

        for _index, _entry in enumerate(entries):
            _currx = _index % self._columns
            _curry = _index // self._columns
            _button = QtWidgets.QRadioButton(_entry, self)
            _button.toggled.connect(self.__toggled)
            self._button_indices[id(_button)] = _index
            self._button_label[_entry] = _index
            self._buttons[_index] = _button
            self.q_button_group.addButton(_button)
            _layout.addWidget(
                _button, _yoffset + _curry, _currx, 1, 1, QtCore.Qt.AlignTop
            )
        self._buttons[0].setChecked(True)
        self.setLayout(_layout)

    @property
    def emit_signal(self):
        """
        Query whether a signal will be emitted on change.

        Returns
        -------
        bool
            Flag whether a signal will be emitted.
        """
        return self._emit_signal

    @emit_signal.setter
    def emit_signal(self, value):
        """
        Change the stored value for emit_signal.

        Parameters
        ----------
        value : bool
            The new value.
        """
        if value is True:
            self._emit_signal = True
        elif value is False:
            self._emit_signal = False
        raise ValueError("The new value must be boolean.")

    @QtCore.Slot()
    def __toggled(self):
        """
        Perform action after a button was toggled.

        This method stores the index of the active button and emits the
        signal if the "emit_signal" property is True.
        """
        _button = self.sender()
        if _button.isChecked():
            _index = self._button_indices[id(_button)]
            _entry = _button.text()
            self._active_index = _index
            self._active_label = _entry
            if self._emit_signal:
                self.new_button_index.emit(_index)
                self.new_button_label.emit(_entry)

    def which_is_checked(self):
        """
        Return the information about which index is checked.

        Returns
        -------
        int
            The active RadioButton's index.
        """
        return self._active_index

    @property
    def active_label(self):
        """
        Return the label name of the currently selected button.

        Returns
        -------
        str
            The label.
        """
        return self._active_label

    def select_by_index(self, index):
        """
        Select and activate a new RadioButton based on the index.

        Parameters
        ----------
        index : int
            The new RadioButton's index.
        """
        _button = self._buttons[index]
        self.__select_new_button(_button)

    def select_by_label(self, label):
        """
        Select and activate a new RadioButton based on the text label.

        Parameters
        ----------
        label : str
            The new RadioButton's label.
        """
        _button = self._buttons[self._button_label[label]]
        self.__select_new_button(_button)

    def __select_new_button(self, button):
        """
        Toggle a new RadioButton without emitting a signal.

        Parameters
        ----------
        button : QtWidgets.QRadioButton
            The RadioButton to be checked.
        """
        _emit_enabled = self._emit_signal
        try:
            self._emit_signal = False
            button.setChecked(True)
        finally:
            self._emit_signal = _emit_enabled

    @QtCore.Slot(float)
    def set_dynamic_height_from_font(self, new_height: float):
        """
        Adjust the widget height based on the font metrics.

        Parameters
        ----------
        new_height : float
            The new font height metrics in pixels.
        """
        self.setFixedHeight((self._rows + (self._title is not None)) * (new_height + 6))
