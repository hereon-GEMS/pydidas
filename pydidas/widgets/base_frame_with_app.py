# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the BaseFrame, the main window widget from which all
main frames should inherit."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BaseFrameWithApp']

import copy

from PyQt5 import QtCore

from ..apps import BaseApp
from .base_frame import BaseFrame


class BaseFrameWithApp(BaseFrame):
    """
    The BaseFrameWithApp is a subclassed BaseFrame and should be used as the
    base class for all Frames with an associated Application in the pydidas
    suite.
    It adds a name attribute and registration routines with the
    CentralWidgetStack.

    By default, a QGridLayout is applied with an alignment of left/top.
    """
    status_msg = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, name=None, **kwargs):
        """
        Initialize the BaseFrame instance.

                Parameters
        ----------
        parent : Union[QWidget, None], optional
            The parent widget. The default is None.
        name : Union[str, None], optional
            The reference name of the widget for the CentralWidgetStack.
            The default is None.
        initLayout : bool
            Flag to initialize the frame layout with a QtWidgets.QVBoxLayout.
            If False, no layout will be initialized and the subclass is
            responsible for setting up the layout. The default is True.
        **kwargs : object
            Any additional keyword arguments.
        """
        init_layout = kwargs.get('initLayout', True)
        super().__init__(parent=parent, initLayout=init_layout)
        self._app = None
        self._runner = None
        self._app_attributes_to_update = []

    @QtCore.pyqtSlot(object)
    def _set_app(self, app):
        """
        Update the local copy of the App after the AppRunner computations.

        Parameters
        ----------
        app : pydidas.apps.BaseApp
            Any App instance
        """
        if not isinstance(app, BaseApp):
            raise TypeError('The passed object must be a BaseApp instance.')
        if not isinstance(self._app, BaseApp):
            self._app = copy.copy(app)
            return
        for param_key in app.params:
            self._app.set_param_value(param_key,
                                      app.get_param_value(param_key))
        self._app._config.update(app._config)
        for att in self._app_attributes_to_update:
            _att_val = getattr(app, att)
            setattr(self._app, att, _att_val)

    @QtCore.pyqtSlot(float)
    def _apprunner_update_progress(self, progress):
        """
        Update the progress of the AppRunner.

        Parameters
        ----------
        progress : float
            The progress, given as numbers 0..1
        """
        if 'progress' in self._widgets:
            _progress = round(progress * 100)
            self._widgets['progress'].setValue(_progress)

    @QtCore.pyqtSlot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        if self._runner is not None:
            self._runner = None
