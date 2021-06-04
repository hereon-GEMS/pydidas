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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScanSettingsFrame']

import sys
from functools import partial
from PyQt5 import QtWidgets, QtCore


from .toplevel_frame import ToplevelFrame
from ..core import ScanSettings
from ..widgets.utilities import excepthook
from ..widgets.param_config import ParamConfigMixIn

SCAN_SETTINGS = ScanSettings()




class ScanSettingsFrame(ToplevelFrame, ParamConfigMixIn):

    # need to redefine the signal because of the multiple inheritance
    # status_msg = QtCore.pyqtSignal(str)

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        super().__init__(parent=parent, name=name, initLayout=False)
        _layout = QtWidgets.QGridLayout()
        _layout.setContentsMargins(5, 5, 0, 0)
        _layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setLayout(_layout)
        self.layout_meta = dict(set=True, grid=True)
        self.param_titlewidgets = {1: None, 2: None, 3: None, 4: None}
        self.initWidgets()
        self.toggle_dims()

    def initWidgets(self):
        self.add_text_widget('Scan settings\n', fontsize=14, bold=True,
                         underline=True, gridPos=(0, 0, 1, 0))
        _but = QtWidgets.QPushButton('Load scan parameters from file')
        _but.setIcon(self.style().standardIcon(42))
        self.layout().addWidget(_but, self.next_row(), 0, 1, 2)
        _but = QtWidgets.QPushButton('Open scan parameter import dialogue')
        _but.setIcon(self.style().standardIcon(42))
        self.layout().addWidget(_but, self.next_row(), 0, 1, 2)

        self.add_text_widget('\nScan dimensionality:', fontsize=11,
                         bold=True, gridPos=(self.next_row(), 0, 1, 2))

        param = SCAN_SETTINGS.get_param('scan_dim')
        self.add_param_widget(param, textwidth = 180)
        self.param_widgets['scan_dim'].currentTextChanged.connect(
            self.toggle_dims)
        _rowoffset = self.next_row()
        _prefixes = ['scan_dir_', 'n_points_', 'delta_', 'unit_', 'offset_']
        for i_dim in range(4):
            _gridPos = (_rowoffset + 6 * (i_dim % 2), 3 * (i_dim // 2), 1, 2)
            _box = self.add_text_widget(f'\nScan dimension {i_dim+1}:',
                                    fontsize=11, bold=True, gridPos= _gridPos)
            self.param_titlewidgets[i_dim + 1] = _box
            for i_item, basename in enumerate(_prefixes):
                _row = i_item + _rowoffset + 1 + 6 * (i_dim % 2)
                _column = 3 * (i_dim // 2)
                pname = f'{basename}{i_dim+1}'
                param = SCAN_SETTINGS.get_param(pname)
                self.add_param_widget(param, row=_row, textwidth = 180, column=_column)

        _spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Minimum)
        self.layout().addItem(_spacer, _rowoffset + 1, 2, 1, 1)


    def toggle_dims(self):
        _prefixes = ['scan_dir_{n}', 'n_points_{n}', 'delta_{n}',
                     'unit_{n}', 'offset_{n}']
        _dim = int(self.param_widgets['scan_dim'].currentText())
        for i in range(1, 5):
            _toggle = True if i <= _dim else False
            self.param_titlewidgets[i].setVisible(_toggle)
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


