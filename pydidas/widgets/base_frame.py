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

"""Module with the BaseFrame, the main window widget from which all
main frames should inherit."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BaseFrame']

from PyQt5 import QtWidgets, QtCore

from .create_widgets_mixin import CreateWidgetsMixIn
from ..core import (ParameterCollection, PydidasQsettingsMixin,
                    ParameterCollectionMixIn)


class BaseFrame(QtWidgets.QFrame,
                ParameterCollectionMixIn,
                PydidasQsettingsMixin,
                CreateWidgetsMixIn):
    """
    Inherits from :py:class:`PyQt5.QtWidgets.QFrame`,
    :py:class:`pydidas.core.ParameterCollectionMixIn`,
    :py:class:`pydidas.core.PydidasQsettingsMixin`,
    :py:class:`pydidas.widgets.CreateWidgetsMixIn`.

    The BaseFrame is a subclassed QFrame and should be used as the
    base class for all Frames in pydidas.

    By default, a QGridLayout is applied with an alignment of left/top.
    """
    status_msg = QtCore.pyqtSignal(str)
    default_params = ParameterCollection()

    def __init__(self, parent=None, **kwargs):
        """
        Initialize the BaseFrame instance.

        Parameters
        ----------
        parent : Union[QWidget, None], optional
            The parent widget. The default is None.
        initLayout : bool, optional
            Flag to initialize the frame layout with a QtWidgets.QGridLayout
            and left / top alignment. If False, no layout will be initialized
            and the subclass is responsible for setting up the layout. The
            default is True.
        **kwargs : object
            Any additional keyword arguments which might be used by
            subclasses.
        """
        CreateWidgetsMixIn.__init__(self)
        QtWidgets.QFrame.__init__(self, parent=parent)
        PydidasQsettingsMixin.__init__(self)

        self.font = QtWidgets.QApplication.font()
        self.params = ParameterCollection()

        init_layout = kwargs.get('initLayout', True)
        if init_layout:
            _layout = QtWidgets.QGridLayout()
            _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.setLayout(_layout)
        self.frame_index = -1

    @QtCore.pyqtSlot(int)
    def frame_activated(self, index):
        """
        Received signal that frame has been activated.

        This method is called when this frame becomes activated by the
        central widget. By default, this method will perform no actions.
        If specific frames require any actions, they will need to overwrite
        this method.

        Parameters
        ----------
        index : int
            The index of the activated frame.
        """

    def set_status(self, text):
        """
        Emit a status message to the main window.

        Parameters
        ----------
        text : str
            The status message to be emitted.
        """
        self.status_msg.emit(text)

    def next_row(self):
        """
        Get the next empty row in the grid layout.

        Returns
        -------
        int
            The next empty row.
        """
        if self .layout().count() == 0:
            return 0
        return self.layout().rowCount()
