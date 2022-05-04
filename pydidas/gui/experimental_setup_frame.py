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
Module with the ExperimentalSetupFrame which is used to define or modify the
global experimental settings like detector, geometry and energy.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSetupFrame']

from functools import partial

import numpy as np
from qtpy import QtWidgets
from pyFAI.gui.CalibrationContext import CalibrationContext
from pyFAI.gui.dialog.DetectorSelectorDialog import DetectorSelectorDialog

from ..experiment import ExperimentalSetup, ExperimentalSetupIoMeta
from ..widgets.dialogues import critical_warning
from .builders import ExperimentalSetupFrameBuilder


EXP_SETUP = ExperimentalSetup()

_GEO_INVALID = ('The pyFAI geometry is not valid and cannot be copied. '
                'This is probably due to either:\n'
                '1. No fit has been performed.\nor\n'
                '2. The fit did not succeed.')

_ENERGY_INVALID = ('The X-ray energy / wavelength cannot be set because the '
                   'pyFAI geometry is not valid. This is probably due to '
                   'either:\n'
                   '1. No fit has been performed.\nor\n'
                   '2. The fit did not succeed.')


class ExperimentalSetupFrame(ExperimentalSetupFrameBuilder):
    """
    The ExperimentalSetupFrame is the main frame for reading, editing and
    saving the ExperimentalSettings in the GUI.
    """
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        ExperimentalSetupFrameBuilder.__init__(self, parent)
        self.params = EXP_SETUP.params
        self.build_frame()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect all signals and slots in the frame.
        """
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
            # disconnect directly setting the parameters and route
            # through update_param method to catch wavelength/energy
            _w = self.param_widgets[param.refkey]
            _w.io_edited.disconnect()
            _w.io_edited.connect(partial(self.update_param, _param_key, _w))

    def set_param_value_and_widget(self, key, value):
        """
        Update a Parameter value both in the widget and ParameterCollection.

        This method overloads the
        ParameterConfigWidgetMixin.set_param_value_and_widget method to
        process the linked energy / wavelength parameters.

        Parameters
        ----------
        key : str
            The Parameter reference key.
        value : object
            The new Parameter value. The datatype is determined by the
            Parameter.
        """
        EXP_SETUP.set_param_value(key, value)
        if key in ['xray_energy', 'xray_wavelength']:
            _energy = self.get_param_value('xray_energy')
            _lambda = self.get_param_value('xray_wavelength')
            self.param_widgets['xray_energy'].set_value(_energy)
            self.param_widgets['xray_wavelength'].set_value(_lambda)
        else:
            self.param_widgets[key].set_value(value)

    def update_param(self, param_key, widget):
        """
        Update a value in both the Parameter and the corresponding widget.

        Parameters
        ----------
        param_key : str
            The reference key.
        widget : pydidas.widgets.parameter_config.BaseParamIoWidget
            The Parameter editing widget.
        """
        EXP_SETUP.set_param_value(param_key,  widget.get_value())
        # explicitly call update fo wavelength and energy
        if param_key == 'xray_wavelength':
            _w = self.param_widgets['xray_energy']
            _w.set_value(EXP_SETUP.get_param_value('xray_energy'))
        elif param_key == 'xray_energy':
            _w = self.param_widgets['xray_wavelength']
            _w.set_value(EXP_SETUP.get_param_value('xray_wavelength'))

    def select_detector(self):
        """
        Open a dialog to select a detector.
        """
        dialog = DetectorSelectorDialog()
        dialog.exec_()
        _det = dialog.selectedDetector()
        self.update_detector_params(_det, show_warning=False)

    def copy_all_from_pyfai(self):
        """
        Copy all settings (i.e. detector, energy and geometry) from pyFAI.
        """
        self.copy_detector_from_pyFAI()
        self.copy_energy_from_pyFAI(show_warning=False)
        self.copy_geometry_from_pyFAI()

    def copy_detector_from_pyFAI(self, show_warning=True):
        """
        Copy the detector from the pyFAI CalibrationContext instance.

        Parameters
        ----------
        show_warning : bool, optional
            Flag to show a warning if the detector cannot be found or simply
            to ignore. True will show the warning. The default is True.
        """
        context = CalibrationContext.instance()
        model = context.getCalibrationModel()
        _det = model.experimentSettingsModel().detector()
        self.update_detector_params(_det, show_warning)

    def update_detector_params(self, det, show_warning=True):
        """
        Update the pydidas detector Parameters based on the selected pyFAI
        detector.

        Parameters
        ----------
        det : pyFAI.detectors.Detector
            The detector instance.
        show_warning : bool, optional
            Flag to show a warning if the detector cannot be found or simply
            to ignore. True will show the warning. The default is True.
        """
        if det is not None:
            self.set_param_value_and_widget('detector_name', det.name)
            self.set_param_value_and_widget('detector_npixx', det.shape[1])
            self.set_param_value_and_widget('detector_npixy', det.shape[0])
            self.set_param_value_and_widget('detector_pxsizex',
                                            1e6 * det.pixel2)
            self.set_param_value_and_widget('detector_pxsizey',
                                            1e6 * det.pixel1)
        elif show_warning:
            critical_warning('No pyFAI Detector',
                             'No detector selected in pyFAI. Cannot copy '
                             'information.')

    def copy_geometry_from_pyFAI(self, show_warning=True):
        """
        Copy the geometry from the pyFAI CalibrationContext instance.

        Parameters
        ----------
        show_warning : bool, optional
            Flag to show a warning if the geometry cannot be found or simply
            to ignore. True will show the warning. The default is True.
        """
        model = CalibrationContext.instance().getCalibrationModel()
        _geo = model.fittedGeometry()
        if _geo.isValid():
            for key, value in [['detector_dist', _geo.distance().value()],
                               ['detector_poni1', _geo.poni1().value()],
                               ['detector_poni2', _geo.poni2().value()],
                               ['detector_rot1', _geo.rotation1().value()],
                               ['detector_rot2', _geo.rotation2().value()],
                               ['detector_rot3', _geo.rotation3().value()]]:
                self.set_param_value_and_widget(key, np.round(value, 12))
        elif show_warning:
            critical_warning('pyFAI geometry invalid', _GEO_INVALID)

    def copy_energy_from_pyFAI(self, show_warning=True):
        """
        Copy the energy setting from pyFAI and store it in the
        ExperimentalSetup.

        Parameters
        ----------
        show_warning : TYPE, optional
            Flag to show a warning if the energy/wavelength cannot be found
            or simply to ignore the missing value. True will show the warning.
            The default is True.
        """
        model = CalibrationContext.instance().getCalibrationModel()
        _geo = model.fittedGeometry()
        if _geo.isValid():
            _wavelength = np.round(_geo.wavelength().value() * 1e10, 12)
            self.set_param_value_and_widget('xray_wavelength', _wavelength)
        elif show_warning:
            critical_warning('pyFAI geometry invalid', _ENERGY_INVALID)

    def load_parameters_from_file(self):
        """
        Open a dialog to select a filename and load ExperimentalSetup from
        the selected file.

        Note: This method will overwrite all current settings.
        """
        _formats = ExperimentalSetupIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Name of file', None, _formats)[0]
        if fname != '':
            EXP_SETUP.import_from_file(fname)
            for param in EXP_SETUP.params.values():
                self.param_widgets[param.refkey].set_value(param.value)

    def __save_to_file(self):
        """
        Open a dialog to select a filename and write all currrent settings
        for the ExperimentalSetup to file.
        """
        _formats = ExperimentalSetupIoMeta.get_string_of_formats()
        fname = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Name of file', None, _formats)[0]
        if fname != '':
            EXP_SETUP.export_to_file(fname, overwrite=True)
