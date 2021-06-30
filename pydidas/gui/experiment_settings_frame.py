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
__all__ = ['ExperimentSettingsFrame']

import os
from functools import partial

from PyQt5 import QtWidgets
from pyFAI.gui.CalibrationContext import CalibrationContext
from pyFAI.geometry import Geometry

from .base_frame import BaseFrame
from ..config import YAML_EXTENSIONS
from ..core import ParameterCollectionMixIn
from ..core.experimental_settings import (ExperimentalSettings,
                                          LoadExperimentSettingsFromFile,
                                          SaveExperimentSettingsToFile)

from ..widgets.parameter_config import ParameterConfigMixIn
from ..widgets.dialogues import CriticalWarning

EXP_SETTINGS = ExperimentalSettings()


## TODO : Restore default function

class ExperimentSettingsFrame(BaseFrame, ParameterConfigMixIn,
                              ParameterCollectionMixIn):

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        BaseFrame.__init__(self, parent, name=name)
        ParameterConfigMixIn.__init__(self)
        self.params = EXP_SETTINGS.params
        self.initWidgets()
        self.connect_signals()

    def initWidgets(self):
        self._widgets = {}
        self.layout().setContentsMargins(5, 5, 0, 0)

        self.__create_global_header()
        for _param_key in self.params.keys():
            if _param_key == 'xray_wavelength':
                self.__create_xray_header()
            if _param_key == 'detector_name':
                self.__create_detector_header()
            if _param_key == 'detector_dist':
                self.__create_geometry_header()
            self.__create_param_widgets(_param_key)

        self.create_spacer(gridPos=(-1, 0, 1, 3))
        self._widgets['but_save_to_file'] = self.create_button(
            'Save experimental parameters to file', gridPos=(-1, 0, 1, 3),
            alignment=None,
            icon=self.style().standardIcon(43))

    def connect_signals(self):
        self._widgets['but_load_from_file'].clicked.connect(
            self.load_parameters_from_file)
        self._widgets['but_copy_from_pyfai'].clicked.connect(
            self.copy_all_from_pyfai)
        self._widgets['but_select_detector'].clicked.connect(
            self.select_detector)
        self._widgets['but_copy_det_from_pyfai'].clicked.connect(
            partial(self.copy_detector_from_pyFAI, True))
        self._widgets['but_copy_geo_from_pyfai'].clicked.connect(
            partial(self.copy_geometry_from_pyFAI, True))
        self._widgets['but_copy_energy_from_pyfai'].clicked.connect(
            partial(self.copy_energy_from_pyFAI, True))
        self._widgets['but_save_to_file'].clicked.connect(
            self.__save_to_file)
        for _param_key in self.params.keys():
            param = self.get_param(_param_key)
            #disconnect directly setting the parameters and route
            # through EXP_SETTINGS to catch wavelength/energy
            _w = self.param_widgets[param.refkey]
            _w.io_edited.disconnect()
            _w.io_edited.connect(partial(self.update_param, _param_key, _w))

    def __create_xray_header(self):
        """Create header items (label / buttons) for X-ray energy settings."""
        self.create_label('\nBeamline X-ray energy:', fontsize=11,
                          bold=True, gridPos=(self.next_row(), 0, 1, 3))
        self._widgets['but_copy_energy_from_pyfai'] = self.create_button(
            'Copy X-ray energy from pyFAI calibration',
            gridPos=(-1, 0, 1, 3), alignment=None)

    def __create_detector_header(self):
        """Create header items (label / buttons) for the detector."""
        self.create_label('\nX-ray detector:', fontsize=11, bold=True,
                          gridPos=(-1, 0, 1, 3))
        self._widgets['but_select_detector'] = self.create_button(
            'Select X-ray detector', gridPos=(-1, 0, 1, 3),
            alignment=None)
        self._widgets['but_copy_det_from_pyfai'] = self.create_button(
            'Copy X-ray detector from pyFAI calibration',
            gridPos=(-1, 0, 1, 3), alignment=None)

    def __create_geometry_header(self):
        """Create header items (label / buttons) for the detector."""
        self.create_label('\nDetector geometry:', fontsize=11,
                         bold=True, gridPos=(-1, 0, 1, 3))
        self._widgets['but_copy_geo_from_pyfai'] = self.create_button(
            'Copy X-ray detector geometry from pyFAI calibration',
            gridPos=(-1, 0, 1, 3))

    def __create_global_header(self):
        """Create global header items (label / buttons). """
        self.create_label('Experimental settings\n', fontsize=14, bold=True,
                          underline=True, gridPos=(0, 0, 1, 0))
        self._widgets['but_load_from_file'] = self.create_button(
            'Load experimental parameters from file',
            icon=self.style().standardIcon(42),
            gridPos=(-1, 0, 1, 3), alignment=None)
        self._widgets['but_copy_from_pyfai'] = self.create_button(
            'Copy all experimental parameters from calibration',
            gridPos=(-1, 0, 1, 3), alignment=None)

    def __create_param_widgets(self, param_key):
        """Create widgets for a Parameter."""
        _row = self.next_row()
        _param = self.get_param(param_key)
        self.create_param_widget(_param, row=_row, textwidth = 180,
                                 width=150)
        self.create_label(_param.unit, gridPos=(_row, 2, 1, 1),
                          fixedWidth=24)

    def update_param_value(self, key, value):
        """
        Update a Parameter value both in the widget and ParameterCollection.

        This method overloads the ParamConfigMixin.update_param_value
        method to process the linked energy / wavelength parameters.

        Parameters
        ----------
        key : str
            The Parameter reference key.
        value : object
            The new Parameter value. The datatype is determined by the
            Parameter.
        """
        EXP_SETTINGS.set_param_value(key, value)
        if key in ['xray_energy', 'xray_wavelength']:
            _energy = self.get_param_value('xray_energy')
            _lambda = self.get_param_value('xray_wavelength')
            self.param_widgets['xray_energy'].set_value(_energy)
            self.param_widgets['xray_wavelength'].set_value(_lambda)
        else:
            self.param_widgets[key].set_value(value)

    def update_param(self, param_key, widget):
        EXP_SETTINGS.set_param_value(param_key,  widget.get_value())
        # explicitly call update fo wavelength and energy
        if param_key == 'xray_wavelength':
            _w = self.param_widgets['xray_energy']
            _w.set_value(EXP_SETTINGS.get_param_value('xray_energy'))
        elif param_key == 'xray_energy':
            _w = self.param_widgets['xray_wavelength']
            _w.set_value(EXP_SETTINGS.get_param_value('xray_wavelength'))

    def select_detector(self):
        from pyFAI.gui.dialog.DetectorSelectorDialog import DetectorSelectorDialog
        dialog = DetectorSelectorDialog()
        dialog.exec_()
        _det = dialog.selectedDetector()
        self.update_detector_params(_det, show_warning=False)

    def copy_all_from_pyfai(self):
        self.copy_detector_from_pyFAI()
        self.copy_energy_from_pyFAI(show_warning=False)
        self.copy_geometry_from_pyFAI()

    def copy_detector_from_pyFAI(self, show_warning=True):
        context = CalibrationContext.instance()
        model = context.getCalibrationModel()
        _det = model.experimentSettingsModel().detector()
        self.update_detector_params(_det, show_warning)

    def update_detector_params(self, det, show_warning=True):
        if det is not None:
            for key, value in [['detector_name', det.name],
                               ['detector_npixx', det.shape[1]],
                               ['detector_npixy', det.shape[0]],
                               ['detector_sizex', det.pixel2],
                               ['detector_sizey', det.pixel1]]:
                self.update_param_value(key, value)
        elif show_warning:
            CriticalWarning('No pyFAI Detector',
                            'No detector selected in pyFAI. Cannot copy '
                            'information.')

    def copy_geometry_from_pyFAI(self, show_warning=True):
        model = CalibrationContext.instance().getCalibrationModel()
        _geo = model.fittedGeometry()
        if _geo.isValid():
            for key, value in [['detector_dist', _geo.distance().value()],
                               ['detector_poni1', _geo.poni1().value()],
                               ['detector_poni2', _geo.poni2().value()],
                               ['detector_rot1', _geo.rotation1().value()],
                               ['detector_rot2', _geo.rotation2().value()],
                               ['detector_rot3', _geo.rotation3().value()]]:
                self.update_param_value(key, value)
        elif show_warning:
            CriticalWarning('pyFAI geometry invalid',
                            'The pyFAI geometry is not valid and cannot be '
                            'copied. This is probably due to either:\n'
                            '1. No fit has been performed.\nor\n'
                            '2. The fit did not succeed.')


    def copy_energy_from_pyFAI(self, show_warning=True):
        model = CalibrationContext.instance().getCalibrationModel()
        _geo = model.fittedGeometry()
        if _geo.isValid():
            _wavelength = _geo.wavelength().value() * 1e10
            self.update_param_value('xray_wavelength', _wavelength)
        elif show_warning:
            CriticalWarning('pyFAI geometry invalid',
                            'The X-ray energy / wavelength cannot be set '
                            'because the pyFAI geometry is not valid. '
                            'This is probably due to either:\n'
                            '1. No fit has been performed.\nor\n'
                            '2. The fit did not succeed.')

    def load_parameters_from_file(self):
        _func = QtWidgets.QFileDialog.getOpenFileName
        fname = _func(self, 'Name of file', None,
                      'PONI files (*.poni);;All files (*.*)')[0]
        LoadExperimentSettingsFromFile(fname)

    def __save_to_file(self):
        _func = QtWidgets.QFileDialog.getSaveFileName
        _files = 'YAML files (*.yml);;PONI files (*.poni);;All files (*.*)'
        fname = _func(self, 'Name of file', None, _files)[0]
        SaveExperimentSettingsToFile(fname)
