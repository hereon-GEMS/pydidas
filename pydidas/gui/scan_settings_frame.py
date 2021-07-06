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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScanSettingsFrame']

import sys
from functools import partial
from PyQt5 import QtWidgets, QtCore


from pydidas.gui import BaseFrame
from pydidas.core import ScanSettings
from pydidas.widgets import CreateWidgetsMixIn, excepthook
from pydidas.widgets.parameter_config import ParameterConfigMixIn

SCAN_SETTINGS = ScanSettings()


class ScanSettingsFrame(BaseFrame, ParameterConfigMixIn, CreateWidgetsMixIn):
    """
    Frame for
    """
    TEXT_WIDTH = 180

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        BaseFrame.__init__(self, parent,name=name)
        ParameterConfigMixIn.__init__(self)
        self._widgets = {}
        self.initWidgets()
        self.toggle_dims()

    def initWidgets(self):
        self._widgets['title'] = self.create_label(
            'Scan settings\n', fontsize=14, bold=True, underline=True,
            gridPos=(0, 0, 1, 0))
        self._widgets['but_load']  = self.create_button(
            'Load scan parameters from file', gridPos=(-1, 0, 1, 2),
            icon=self.style().standardIcon(42), alignment=None)
        self._widgets['but_import']  = self.create_button(
            'Open scan parameter import dialogue', gridPos=(-1, 0, 1, 2),
            icon=self.style().standardIcon(42), alignment=None)

        self.create_label('\nScan dimensionality:', fontsize=11,
                         bold=True, gridPos=(self.next_row(), 0, 1, 2))

        param = SCAN_SETTINGS.get_param('scan_dim')
        self.create_param_widget(param, width_text = self.TEXT_WIDTH)
        self.param_widgets['scan_dim'].currentTextChanged.connect(
            self.toggle_dims)

        _rowoffset = self.next_row()
        _prefixes = ['scan_dir_', 'n_points_', 'delta_', 'unit_', 'offset_']
        for i_dim in range(4):
            self._widgets[f'title_{i_dim + 1}'] =  self.create_label(
                f'\nScan dimension {i_dim+1}:',fontsize=11, bold=True,
                gridPos=(_rowoffset + 6 * (i_dim % 2), 3 * (i_dim // 2), 1, 2))
            for i_item, basename in enumerate(_prefixes):
                _row = i_item + _rowoffset + 1 + 6 * (i_dim % 2)
                _column = 3 * (i_dim // 2)
                pname = f'{basename}{i_dim+1}'
                param = SCAN_SETTINGS.get_param(pname)
                self.create_param_widget(param, row=_row, column=_column,
                                         width_text=self.TEXT_WIDTH)
        self.create_spacer(gridPos=(_rowoffset + 1, 2, 1, 1))

    def toggle_dims(self):
        _prefixes = ['scan_dir_{n}', 'n_points_{n}', 'delta_{n}',
                     'unit_{n}', 'offset_{n}']
        _dim = int(self.param_widgets['scan_dim'].currentText())
        for i in range(1, 5):
            _toggle = True if i <= _dim else False
            self._widgets[f'title_{i}'].setVisible(_toggle)
            for _pre in _prefixes:
                self.param_widgets[_pre.format(n=i)].setVisible(_toggle)
                self.param_textwidgets[_pre.format(n=i)].setVisible(_toggle)

    def update_param(self, pname, widget):
        try:
            SCAN_SETTINGS.set(pname, widget.get_value())
        except Exception:
            widget.set_value(SCAN_SETTINGS.get(pname))
            excepthook(*sys.exc_info())
        # explicitly call update fo wavelength and energy
        if pname == 'xray_wavelength':
            _w = self.param_widgets['xray_energy']
            _w.set_value(SCAN_SETTINGS.get('xray_energy'))
        elif pname == 'xray_energy':
            _w = self.param_widgets['xray_wavelength']
            _w.set_value(SCAN_SETTINGS.get('xray_wavelength') * 1e10)


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

    gui.register_frame('Test', 'Test', qta.icon('mdi.clipboard-flow-outline'),
                       ScanSettingsFrame)
    gui.create_toolbars()

    gui.show()
    sys.exit(app.exec_())
    app.deleteLater()
