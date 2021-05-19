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
        self.layout_meta = dict(set=True, grid=True, row=0)
        self.initWidgets()

    def initWidgets(self):
        _pnames = ['scan_dir_', 'n_points_',
                   'delta_', 'unit_', 'offset_']
        self.add_label('Scan settings\n', fontsize=14, bold=True,
                       underline=True, gridPos=(0, 0, 1, 0))
        _but = QtWidgets.QPushButton('Load scan parameters from file')
        _but.setIcon(self.style().standardIcon(42))
        self.layout().addWidget(_but, 1, 0, 1, 2)
        _but = QtWidgets.QPushButton('Open scan parameter import dialogue')
        _but.setIcon(self.style().standardIcon(42))
        self.layout().addWidget(_but, 2, 0, 1, 2)

        self.add_label('\nScan dimensionality:', fontsize=11,
                       bold=True, gridPos=(3, 0, 1, 2))

        param = SCAN_SETTINGS.get_param('scan_dim')
        self.add_param(param, 4 , width = 180, column=0)
        _rowoffset = 5
        for i in range(4):
            self.add_label(f'\nScan dimension {i+1}:', fontsize=11,
                           bold=True,
                           gridPos=(_rowoffset + 6 * (i % 2), 3 * (i // 2), 1, 2))
            for iitem, basename in enumerate(_pnames):
                _row = iitem + _rowoffset + 1 + 6 * (i % 2)
                _column = 3 * (i // 2)
                pname = f'{basename}{i+1}'
                param = SCAN_SETTINGS.get_param(pname)
                self.add_param(param, _row , width = 180, column=_column)

        _spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Minimum)
        self.layout().addItem(_spacer, _rowoffset + 1, 2, 1, 1)


        #     _w.setFixedWidth(150)
        #     self.add_label(param.unit, gridPos=(row + _rowoffset, 2, 1, 1), width=24)
        # _row = self.layout().getItemPosition(self.layout().indexOf(_w))[0] + 2
        # _spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum,
        #                                 QtWidgets.QSizePolicy.Expanding)
        # self.layout().addItem(_spacer, _row, 0, 1, 3)
        # _but = QtWidgets.QPushButton('Save experimental parameters to file')
        # _but.setIcon(self.style().standardIcon(43))
        # self.layout().addWidget(_but, _row + 1, 0, 1, 3)

    def update_param(self, pname, widget):
        try:
            SCAN_SETTINGS.set(pname, widget.get_value())
        except Exception:
            widget.set_value(SCAN_SETTINGS.get(pname))
            excepthook(*sys.exc_info())
        # explicitly call update fo wavelength and energy
        if pname == 'xray_wavelength':
            _w = self.param_links['X-ray energy']
            _w.set_value(SCAN_SETTINGS.get('xray_energy'))
        elif pname == 'xray_energy':
            _w = self.param_links['X-ray wavelength']
            _w.set_value(SCAN_SETTINGS.get('xray_wavelength') * 1e10)


