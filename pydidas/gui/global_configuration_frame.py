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

"""Module with the GlobalSettingsFrame which is used for administrating
global settings."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['GlobalConfigurationFrame']

import sys
from numbers import Integral, Real
from functools import partial
from PyQt5 import QtWidgets, QtCore, QtGui


from pydidas.widgets import BaseFrame
from pydidas.core import (ParameterCollectionMixIn,
                          get_generic_parameter, ParameterCollection)
from pydidas.widgets import excepthook
from pydidas.widgets.parameter_config import ParameterConfigWidgetsMixIn


DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('mp_n_workers'),
    get_generic_parameter('det_mask'),
    get_generic_parameter('mosaic_border_width'),
    get_generic_parameter('mosaic_border_value'),
    get_generic_parameter('mosaic_max_size'),
    )


class GlobalConfigurationFrame(BaseFrame, ParameterConfigWidgetsMixIn):
    """
    Frame which manages global configuration items.
    """
    TEXT_WIDTH = 180
    default_params = DEFAULT_PARAMS
    value_changed_signal = QtCore.pyqtSignal(str, object)

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        BaseFrame.__init__(self, parent,name=name)
        ParameterConfigWidgetsMixIn.__init__(self)
        self.set_default_params()

        self._widgets = {}
        self.init_widgets()

        self.connect_signals()

        self.frame_activated(self.frame_index)

    def init_widgets(self):
        """
        Create the widgets required for GlobalConfigurationFrame.
        """
        _twoline_options = dict(width_text=self.TEXT_WIDTH, width=240,
                                linebreak=True, n_columns=2,
                                halign_text=QtCore.Qt.AlignLeft,
                                valign_text=QtCore.Qt.AlignBottom)
        _options = dict(width_text=self.TEXT_WIDTH, width=60)
        _section_options = dict(fontsize=13, bold=True,
                                gridPos=(-1, 0, 2, 0))

        self._widgets['title'] = self.create_label(
            'Global settings\n', fontsize=14, bold=True, gridPos=(0, 0, 2, 0))

        self._widgets['but_reset'] = self.create_button(
            'Restore defaults', icon=self.style().standardIcon(59),
            gridPos=(-1, 0, 2, 0), alignment=None)

        self._widgets['section_multiprocessing'] = self.create_label(
            'Multiprocessing settings', **_section_options)
        self.create_param_widget(self.params.get_param('mp_n_workers'),
                                 **_options)
        self.create_spacer()

        self._widgets['section_detector'] = self.create_label(
            'Detector settings', **_section_options)
        self.create_param_widget(self.params.get_param('det_mask'),
                                 **_twoline_options)
        self.create_spacer()

        self._widgets['section_mosaic'] = self.create_label(
            'Composite creator settings', **_section_options)
        self.create_param_widget(self.params.get_param('mosaic_border_width'),
                                 **_options)
        self.create_param_widget(self.params.get_param('mosaic_border_value'),
                                 **_options)
        self.create_param_widget(self.params.get_param('mosaic_max_size'),
                                 **_options)
        self.create_spacer()

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
            _value = self.qsetting_get_global_value(_param_key)
            self.update_param_value(_param_key, _value)

    def __reset(self):
        qm = QtGui.QMessageBox
        answer = qm.question(self,'', "Are you sure to reset all the values?",
                             qm.Yes | qm.No)
        if answer == qm.Yes:
            self.restore_all_defaults(True)
            for _param_key in self.params:
                _value = self.get_param_value(_param_key)
                self.param_widgets[_param_key].set_value(_value)
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
    STANDARD_FONT_SIZE = pydidas.config.STANDARD_FONT_SIZE

    _font = app.font()
    _font.setPointSize(STANDARD_FONT_SIZE)
    app.setFont(_font)
    gui = MainWindow()

    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()
