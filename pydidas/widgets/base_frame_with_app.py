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
Module with the BaseFrameWithApp, a subclass of the BaseFrame from which all
main pydidas frames should inherit. This subclass includes some methods for
using a pydidas App in multiprocessing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['BaseFrameWithApp']

from qtpy import QtCore

from ..core import BaseApp
from .base_frame import BaseFrame


class BaseFrameWithApp(BaseFrame):
    """
    The BaseFrameWithApp is a subclassed BaseFrame and should be used as the
    base class for all Frames with an associated Application in the pydidas
    suite.

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
        init_layout = kwargs.get('init_layout', True)
        BaseFrame.__init__(self, parent=parent, init_layout=init_layout)
        self._app = None
        self._runner = None
        self._app_attributes_to_update = []

    @QtCore.Slot(object)
    def _set_app(self, app):
        """
        Update the local copy of the App after the AppRunner computations.

        Parameters
        ----------
        app : pydidas.apps.BaseApp
            Any App instance.
        """
        if not isinstance(app, BaseApp):
            raise TypeError('The passed object must be a BaseApp instance.')
        if not isinstance(self._app, BaseApp):
            self._app = app.get_copy()
            self._app.slave_mode = False
            return
        for param_key in app.params:
            self._app.set_param_value(
                param_key, app.get_param_value(param_key))
        self._app._config.update(app._config)
        for att in self._app_attributes_to_update:
            _att_val = getattr(app, att)
            setattr(self._app, att, _att_val)

    @QtCore.Slot(float)
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

    @QtCore.Slot()
    def _apprunner_finished(self):
        """
        Clean up after AppRunner is done.
        """
        if self._runner is not None:
            self._runner = None

    def export_state(self):
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
        _app_params = self._app.get_param_values_as_dict(
            filter_types_for_export=True)
        _app_state = {'params': _app_params,
                      'config': self.__get_app_config_for_saving()}
        _state['app'] = _app_state
        return _index, _state

    def __get_app_config_for_saving(self):
        """
        Get the Application config for saving.

        This method sanitized the config for saving and is responsible for
        conversions to yaml-dumpable formats.

        Returns
        -------
        dict
            The Application config in processed form.
        """
        _cfg = self._app._config.copy()
        _newcfg = {}
        for _key, _item in _cfg.items():
            if isinstance(_item, range):
                _newcfg[_key] = (f'::range::{_item.start}::{_item.stop}'
                                 f'::{_item.step}')
        _cfg.update(_newcfg)
        return _cfg

    def restore_state(self, state):
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
        for _key, _val in state['app']['params'].items():
            self._app.set_param_value(_key, _val)
        self._app._config = self.__process_app_config_from_import(
            state['app']['config'].copy())
        super().restore_state(state)

    def __process_app_config_from_import(self, config):
        """
        Process settings which have been modified for export and restore
        the original values.

        Parameters
        ----------
        config : dict
            The input config dictionary.

        Returns
        -------
        config : dict
            The updated config dictionary
        """
        _newcfg = {}
        for _key, _item in config.items():
            if isinstance(_item, str) and _item.startswith('::range::'):
                _, _, _start, _stop, _step = _item.split('::')
                _start = None if _start == 'None' else int(_start)
                _stop = None if _stop == 'None' else int(_stop)
                _step = None if _step == 'None' else int(_step)
                _newcfg[_key] = range(_start, _stop, _step)
        config.update(_newcfg)
        return config
