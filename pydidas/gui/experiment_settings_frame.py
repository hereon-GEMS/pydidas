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

"""Module with the WorkflowPluginWidget which is used to create the workflow
tree."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentSettingsFrame']

from functools import partial

from PyQt5 import QtWidgets
from pyFAI.gui.CalibrationContext import CalibrationContext

from ..core import ParameterCollectionMixIn
from ..core.experimental_settings import (
    ExperimentalSettings, ExperimentalSettingsIoMeta)

from ..widgets import BaseFrame
from ..widgets.parameter_config import ParameterWidgetsMixIn
from ..widgets.dialogues import CriticalWarning
from .builders.experiment_settings_frame_builder import (
    create_experiment_settings_frame_widgets_and_layout)

EXP_SETTINGS = ExperimentalSettings()

## TODO : Restore default function

class ExperimentSettingsFrame(BaseFrame, ParameterWidgetsMixIn,
                              ParameterCollectionMixIn):

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        BaseFrame.__init__(self, parent, name=name)
        ParameterWidgetsMixIn.__init__(self)
        self.params = EXP_SETTINGS.params
        create_experiment_settings_frame_widgets_and_layout(self)
        self.connect_signals()

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

    def update_param_value(self, key, value):
        """
        Update a Parameter value both in the widget and ParameterCollection.

        This method overloads the ParameterConfigWidgetMixin.update_param_value
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
        _formats = ExperimentalSettingsIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Name of file', None, _formats)[0]
        if fname != '':
            EXP_SETTINGS.import_from_file(fname)
            for param in EXP_SETTINGS.params.values():
                self.param_widgets[param.refkey].set_value(param.value)

    def __save_to_file(self):
        _formats = ExperimentalSettingsIoMeta.get_string_of_formats()
        fname =  QtWidgets.QFileDialog.getSaveFileName(
            self, 'Name of file', None, _formats)[0]
        if fname != '':
            EXP_SETTINGS.export_to_file(fname)
