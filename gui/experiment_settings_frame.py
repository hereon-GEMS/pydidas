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
__all__ = ['ExperimentSettingsFrame']

import sys
from functools import partial
from PyQt5 import QtWidgets, QtCore

import qtawesome as qta
from pyFAI.gui.CalibrationContext import CalibrationContext

from .toplevel_frame import ToplevelFrame
from ..core import ExperimentalSettings
from ..widgets.utilities import excepthook
from ..widgets.param_config import ParamConfigMixIn

EXP_SETTINGS = ExperimentalSettings()


class ExperimentSettingsFrame(ToplevelFrame, ParamConfigMixIn):

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
        _pnames = ['xray_wavelength', 'xray_energy', 'detector_name',
                   'detector_npixx', 'detector_npixy', 'detector_dx',
                   'detector_dy', 'detector_dist', 'detector_poni1',
                   'detector_poni2', 'detector_rot1', 'detector_rot2',
                   'detector_rot3']
        self.add_label('Experimental settings\n', fontsize=14, bold=True,
                       underline=True, gridPos=(0, 0, 1, 0))
        _but = QtWidgets.QPushButton('Load experimental parameters from file')
        _but.setIcon(self.style().standardIcon(42))
        self.layout().addWidget(_but, 1, 0, 1, 3)
        _but = QtWidgets.QPushButton('Copy all experimental parameters from calibration')
        self.layout().addWidget(_but, 2, 0, 1, 3)

        _rowoffset = 3
        for row, pname in enumerate(_pnames):
            if pname == 'xray_wavelength':
                self.add_label('\nBeamline X-ray energy:', fontsize=11,
                               bold=True, gridPos=(_rowoffset + row, 0, 1, 3))
                _but2 = QtWidgets.QPushButton('Copy X-ray energy from calibration')
                self.layout().addWidget(_but2, _rowoffset + 1 + row, 0, 1, 3)
                _rowoffset += 2
            if pname == 'detector_name':
                self.add_label('\nX-ray detector:', fontsize=11,
                               bold=True, gridPos=(_rowoffset + row, 0, 1, 3))
                _but = QtWidgets.QPushButton('Select X-ray detector')
                _but2 = QtWidgets.QPushButton('Copy X-ray detector from calibration')
                _but.clicked.connect(self.select_detector)
                _but2.clicked.connect(self.copy_detector)
                self.layout().addWidget(_but, _rowoffset + 1 + row, 0, 1, 3)
                self.layout().addWidget(_but2, _rowoffset + 2 + row, 0, 1, 3)
                _rowoffset += 3
            if pname == 'detector_dist':
                self.add_label('\nDetector position:', fontsize=11,
                               bold=True, gridPos=(_rowoffset + row, 0, 1, 3))
                _but = QtWidgets.QPushButton('Copy detector position from calibration')
                self.layout().addWidget(_but, _rowoffset + 1 + row, 0, 1, 3)
                _rowoffset += 2
            param = EXP_SETTINGS.get_param(pname)
            self.add_param(param, row + _rowoffset, width = 180)

            #disconnect directly setting the parameters and route
            # through EXP_SETTINGS to catch wavelength/energy
            _w = self.param_links[param.name]
            _w.io_edited.disconnect()
            _w.io_edited.connect(partial(self.update_param, pname, _w))

            _w.setFixedWidth(150)
            self.add_label(param.unit, gridPos=(row + _rowoffset, 2, 1, 1), width=24)
        _row = self.layout().getItemPosition(self.layout().indexOf(_w))[0] + 2
        _spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Expanding)
        self.layout().addItem(_spacer, _row, 0, 1, 3)
        _but = QtWidgets.QPushButton('Save experimental parameters to file')
        _but.setIcon(self.style().standardIcon(43))
        self.layout().addWidget(_but, _row + 1, 0, 1, 3)

    def update_param(self, pname, widget):
        try:
            EXP_SETTINGS.set(pname, widget.get_value())
        except Exception:
            widget.set_value(EXP_SETTINGS.get(pname))
            excepthook(*sys.exc_info())
        # explicitly call update fo wavelength and energy
        if pname == 'xray_wavelength':
            _w = self.param_links['X-ray energy']
            _w.set_value(EXP_SETTINGS.get('xray_energy'))
        elif pname == 'xray_energy':
            _w = self.param_links['X-ray wavelength']
            _w.set_value(EXP_SETTINGS.get('xray_wavelength') * 1e10)

    def select_detector(self, name):
        from pyFAI.gui.dialog.DetectorSelectorDialog import DetectorSelectorDialog
        dialog = DetectorSelectorDialog()
        dialog.exec_()

        _det = dialog.selectedDetector()
        if _det is not None:
            self.update_detector_params(_det)

    def copy_detector(self):
        context = CalibrationContext.instance()
        model = context.getCalibrationModel()
        _det = model.experimentSettingsModel().detector()
        self.update_detector_params(_det)

    def update_detector_params(self, detector):
        ...

    def update_model_from_pyFAI(self):
        ...

