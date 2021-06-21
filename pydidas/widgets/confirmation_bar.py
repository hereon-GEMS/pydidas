# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with the Confirmation bar."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ConfirmationBar']

from functools import partial

from PyQt5 import QtCore, QtWidgets

from pydidas.config.qt_presets import STYLES

class _Metadata(QtCore.QObject):
    """Metadata class to connect signals between different widgets."""
    checked_state = QtCore.pyqtSignal(bool, bool, bool)

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


    @QtCore.pyqtSlot(bool, bool, bool)
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
