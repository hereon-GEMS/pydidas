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

"""Module with the Confirmation bar."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ConfirmationBar']

from functools import partial

from qtpy import QtCore, QtWidgets

from ...core.constants import QT_STYLES

class _Metadata(QtCore.QObject):
    """Metadata class to connect signals between different widgets."""
    checked_state = QtCore.Signal(bool, bool, bool)

    def __init__(self):
        """
        Setup method.

        This will create an instance of the _Metadata class.

        Returns
        -------
        None.
        """
        super().__init__()
        self.checked = [False, False, False]

    def update_checks(self, i):
        """
        Check a box.

        This method will change the checked state of the box with the index i.

        Parameters
        ----------
        i : int
            The index of the checked box.

        Returns
        -------
        None.
        """
        self.checked[i] = not self.checked[i]
        self.checked_state.emit(*self.checked)


class _MetadataFactory:
    """
    Factory method for the Metadata class.
    """
    def __init__(self):
        """
        Setup method for the factory.

        Returns
        -------
        None.
        """
        self._instance = None

    def __call__(self):
        """
        Get a unique instance of the _Metadata class.

        Returns
        -------
        _Metadata
            The unique instance of the _Metadata class.

        """
        if not self._instance:
            self._instance = _Metadata()
        return self._instance


Metadata = _MetadataFactory()


class ConfirmationBar(QtWidgets.QFrame):
    """
    Confirmation bar is a setup-spanning bar to confirm the various inputs.
    """

    def __init__(self, parent=None):
        """
        Create a ConfirmationBar.

        The setup method will create the confirmation bar and set the Qt parent
        widget.

        Parameters
        ----------
        parent : QWidget, optional
            The parent QWidget. The default is None.

        Returns
        -------
        None.
        """
        super().__init__(parent)
        self.parent = parent

        self.setFixedHeight(70)

        self.label = QtWidgets.QLabel('Confirm\nConfiguration: ', self)
        self.label.setStyleSheet(STYLES['subtitle'])
        self.check_experiment = QtWidgets.QCheckBox('Experiment description', self)
        self.check_scan = QtWidgets.QCheckBox('Scan description', self)
        self.check_workflow = QtWidgets.QCheckBox('Workflow configuration', self)


        _layout = QtWidgets.QHBoxLayout(self)
        _layout.addWidget(self.label, 0, QtCore.Qt.AlignLeft)
        _layout1 = QtWidgets.QVBoxLayout(self)
        _layout1.setContentsMargins(20, 0, 0, 0)
        _layout1.addWidget(self.check_experiment)
        _layout1.addWidget(self.check_scan)
        _layout1.addWidget(self.check_workflow)
        _layout.addLayout(_layout1)
        _layout.setAlignment(QtCore.Qt.AlignLeft)
        _layout.setContentsMargins(5, 2, 0, 0)
        self.setLayout(_layout)

        self.check_experiment.clicked.connect(partial(Metadata().update_checks, 0))
        self.check_scan.clicked.connect(partial(Metadata().update_checks, 1))
        self.check_workflow.clicked.connect(partial(Metadata().update_checks, 2))

        Metadata().checked_state.connect(self.set_buttons)

    def update_references(self, parent=None):
        """
        Update the reference to the Qt parent.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget. The default is None.

        Returns
        -------
        None.
        """
        if parent:
            self.setParent(parent)


    @QtCore.Slot(bool, bool, bool)
    def set_buttons(self, state0, state1, state2):
        """
        Set the button ticks with new information from the metadata class.

        Parameters
        ----------
        state0 : bool
            The experiment config flag.
        state1 : bool
            The scan config flag.
        state2 : bool
            The workflow config flag.

        Returns
        -------
        None.
        """
        self.check_experiment.setChecked(state0)
        self.check_scan.setChecked(state1)
        self.check_workflow.setChecked(state2)
