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

"""
Module with the GlobalConfigurationFrame which is used for administrating
global settings.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GlobalConfigurationFrame']

import sys
from functools import partial

from PyQt5 import QtWidgets, QtCore

from pydidas.widgets import BaseFrame
from pydidas.core import (get_generic_parameter, ParameterCollection)
from pydidas.widgets.parameter_config import ParameterWidgetsMixIn
from pydidas.gui.builders.global_configuration_frame_builder import (
    create_global_configuratation_frame_widgets_and_layout)


DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('mp_n_workers'),
    get_generic_parameter('shared_buffer_size'),
    get_generic_parameter('shared_buffer_max_n'),
    get_generic_parameter('det_mask'),
    get_generic_parameter('det_mask_val'),
    get_generic_parameter('mosaic_border_width'),
    get_generic_parameter('mosaic_border_value'),
    get_generic_parameter('mosaic_max_size'),
    get_generic_parameter('plot_update_time')
    )


class GlobalConfigurationFrame(BaseFrame, ParameterWidgetsMixIn):
    """
    Frame which manages global configuration items.
    """
    TEXT_WIDTH = 180
    default_params = DEFAULT_PARAMS
    value_changed_signal = QtCore.pyqtSignal(str, object)

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        BaseFrame.__init__(self, parent, name=name)
        ParameterWidgetsMixIn.__init__(self)
        self.set_default_params()
        create_global_configuratation_frame_widgets_and_layout(self)
        self.connect_signals()
        self.frame_activated(self.frame_index)

    def connect_signals(self):
        """
        Connect the signals for Parameter updates.
        """
        for _param_key in self.params:
            self.param_widgets[_param_key].io_edited.connect(
                partial(self.update_qsetting, _param_key))
        self._widgets['but_reset'].clicked.connect(self.__reset)

    def update_qsetting(self, param_key, value):
        """
        Update a QSetting value

        Parameters
        ----------
        param_key : str
            The QSetting reference key. A "global/" prefix will be applied
            to it.
        value : object
            The new value.
        """
        self.q_settings.setValue(f'global/{param_key}', value)
        self.value_changed_signal.emit(param_key, value)

    @QtCore.pyqtSlot(int)
    def frame_activated(self, index):
        """
        Update the frame.

        The frame_activated slot is called every time a frame is activated.
        The index is the frame_index of the newly activated frame in case any
        cross-options need to be taken.

        Parameters
        ----------
        index : int
            The index of the activated frame.
        """
        if index != self.frame_index:
            return
        for _param_key in self.params:
            _value = self.q_settings_get_global_value(_param_key)
            self.update_param_value(_param_key, _value)

    def __reset(self):
        qm = QtWidgets.QMessageBox
        answer = qm.question(self,'', "Are you sure to reset all the values?",
                             qm.Yes | qm.No)
        if answer == qm.Yes:
            self.restore_all_defaults(True)
            for _param_key in self.params:
                _value = self.get_param_value(_param_key)
                self.update_widget_value(_param_key, _value)
                self.value_changed_signal.emit(_param_key, _value)

    @QtCore.pyqtSlot(str, object)
    def external_update(self, param_key, value):
        """
        Perform an update after a Parameter has changed externally.

        Parameters
        ----------
        param_key : str
            The Parameter reference key.
        value : object
            The new value which was set externally.
        """
        value = self._qsettings_convert_value_type(param_key, value)
        self.update_param_value(param_key, value)


if __name__ == '__main__':
    import pydidas
    from pydidas.gui.main_window import MainWindow
    import sys
    import qtawesome as qta
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Fusion')

    # needs to be initialized after the app has been created.
    # sys.excepthook = pydidas.widgets.excepthook
    CENTRAL_WIDGET_STACK = pydidas.widgets.CentralWidgetStack()
    STANDARD_FONT_SIZE = pydidas.constants.STANDARD_FONT_SIZE

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()
