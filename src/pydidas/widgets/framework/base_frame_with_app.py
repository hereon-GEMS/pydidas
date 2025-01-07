# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
The BaseFrameWithApp extends the BaseFrame with a pydidas Application.

All frames with an associated app should interit BaseFrameWithApp instead of
the BaseFrame. This subclass includes methods for using a pydidas App in
parallel processing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["BaseFrameWithApp"]


from typing import Tuple

from qtpy import QtCore

from pydidas.core import BaseApp
from pydidas.widgets.framework.base_frame import BaseFrame


class BaseFrameWithApp(BaseFrame):
    """
    The BaseFrameWithApp is a subclassed BaseFrame with an associated pydidas App.

    It should be used as the base class for all Frames with an associated
    Application in the pydidas suite.

    It adds (internal) methods required for running a pydidas app to the
    BaseFrame.

    Parameters
    ----------
    parent : Union[QWidget, None], optional
        The parent widget. The default is None.
    **kwargs : dict
        Any additional keyword arguments.
    **init_layout : bool
        Flag to initialize the frame layout with a QtWidgets.QVBoxLayout.
        If False, no layout will be initialized and the subclass is
        responsible for setting up the layout. The default is True.
    """

    status_msg = QtCore.Signal(str)

    def __init__(self, parent=None, **kwargs):
        BaseFrame.__init__(self, parent=parent, **kwargs)
        self._app = None
        self._runner = None
        self._app_attributes_to_update = []

    @QtCore.Slot(object)
    def _set_app(self, app: BaseApp):
        """
        Update the local copy of the App after the AppRunner computations.

        Parameters
        ----------
        app : pydidas.apps.BaseApp
            Any App instance.
        """
        if not isinstance(app, BaseApp):
            raise TypeError("The passed object must be a BaseApp instance.")
        if not isinstance(self._app, BaseApp):
            self._app = app.copy()
            self._app.clone_mode = False
            return
        for param_key in app.params:
            self._app.set_param_value(param_key, app.get_param_value(param_key))
        self._app._config.update(app._config)
        for att in self._app_attributes_to_update:
            _att_val = getattr(app, att)
            setattr(self._app, att, _att_val)

    @QtCore.Slot(float)
    def _apprunner_update_progress(self, progress: float):
        """
        Update the progress of the AppRunner.

        Parameters
        ----------
        progress : float
            The progress, given as numbers 0..1
        """
        if "progress" in self._widgets:
            _progress = round(progress * 100)
            self._widgets["progress"].setValue(_progress)

    @QtCore.Slot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        if self._runner is not None:
            self._runner.exit()
            self._runner = None

    def export_state(self) -> Tuple[int, dict]:
        """
        Export the state of the Frame for saving.

        This method adds an export for the frame's app.

        Returns
        -------
        frame_index : int
            The frame index which can be used as key for referencing the state.
        information : dict
            A dictionary with all the information required to export the
            frame's state.
        """
        _index, _state = super().export_state()
        _state["app"] = self._app.export_state()
        return _index, _state

    def restore_state(self, state: dict):
        """
        Restore the frame's state from stored information.

        The BaseFrameWithApp implementation will update the associated App
        and then call the BaseFrame's method.

        Parameters
        ----------
        state : dict
            A dictionary with 'params', 'app' and 'visibility' keys and the
            respective information for all.
        """
        self._app.import_state(state["app"])
        super().restore_state(state)
