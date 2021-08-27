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
__all__ = ['LoadExperimentSettingsFromFile']

import os

import yaml
import pyFAI

from ...config import YAML_EXTENSIONS, LAMBDA_TO_E
from ..object_with_parameter_collection import ObjectWithParameterCollection
from .experimental_settings import ExperimentalSettings

EXP_SETTINGS = ExperimentalSettings()


class LoadExperimentSettingsFromFile(ObjectWithParameterCollection):
    """
    The LoadExperimentSettingsFromFile class allows to read Xray wavelength,
    detector and geometry information from a file and store them internally
    in the ExperimentalSettings object.
    """
    def __init__(self, fname=None):
        """Create new instance."""
        self.fname = fname
        ObjectWithParameterCollection.__init__(self)
        self.params = EXP_SETTINGS.params
        self.tmp_params = {}
        if fname not in [None, '']:
            self.load_from_file(fname)

    def load_from_file(self, fname):
        """
        Load ExperimentalSettings from a file.

        Parameters
        ----------
        fname : str
            The full path of the file with the ExperimentalSettings
            configuration.

        Raises
        ------
        FileNotFoundError
            If the file does not exits.
        KeyError
            If the file extension is not recognized.
        """
        if not os.path.exists(fname):
            raise FileNotFoundError(f'No file with the name "{fname}" exists.')

        _ext = os.path.splitext(self.fname)[1]
        if _ext in YAML_EXTENSIONS:
            self.__load_yaml_file()
        elif _ext == '.poni':
            self.__load_poni_file()
        else:
            raise KeyError('No interpreter found for file extension '
                           f'"{_ext}". Please try with a different file or'
                           ' rename the current file. Expected extensions '
                           'for poni files: .poni and for yaml files: '
                           f'{YAML_EXTENSIONS}.')

    def __load_yaml_file(self):
        """
        Load ExperimentalSettings from a YAML file.
        """
        self.__parse_yaml_file()
        self.__verify_all_entries_present()
        self.__write_to_exp_settings()

    def __parse_yaml_file(self):
        """Parse the YAML file and store the contents as dictionary."""
        with open(self.fname, 'r') as stream:
            try:
                self.tmp_params = yaml.safe_load(stream)
            except yaml.YAMLError as yerr:
                self.tmp_params = {}
                raise yaml.YAMLError from yerr
        self.tmp_params['xray_energy'] = (LAMBDA_TO_E
                                          / self.tmp_params['xray_wavelength'])

    def __verify_all_entries_present(self):
        """
        Verify that the tmp_params dictionary holds all keys from the
        ExperimentalSettings.
        """
        for key in self.params:
            if key not in self.tmp_params:
                raise KeyError(f'The setting for "{key}" is missing.')

    def __write_to_exp_settings(self):
        """
        Write the loaded (temporary) Parameters to the ExperimentalSettings.
        """
        for key in self.tmp_params:
            self.set_param_value(key, self.tmp_params[key])
        self.tmp_params = {}

    def __load_poni_file(self):
        """
        Loada pyFAI type file with geometry information.
        """
        geo = pyFAI.geometry.Geometry().load(self.fname)
        self.tmp_params = {}
        self.__update_detector_from_pyFAI(geo.detector)
        self.__update_geometry_from_pyFAI(geo)
        self.__verify_all_entries_present()
        self.__write_to_exp_settings()

    def __update_detector_from_pyFAI(self, det):
        """Update the detector information from a pyFAI Detector instance. """
        if not isinstance(det, pyFAI.detectors.Detector):
            raise TypeError(f'Object "{det} (type {type(det)} is not a '
                            'pyFAI.detectors.Detector instance.')
        for key, value in [['detector_name', det.name],
                           ['detector_npixx', det.shape[1]],
                           ['detector_npixy', det.shape[0]],
                           ['detector_sizex', det.pixel2],
                           ['detector_sizey', det.pixel1]]:
            self.tmp_params[key] = value

    def __update_geometry_from_pyFAI(self, geo):
        """Update the geometry information from a pyFAI Geometry instance. """
        if not isinstance(geo, pyFAI.geometry.Geometry):
            raise TypeError(f'Object "{geo} (type {type(geo)} is not a '
                            'pyFAI.geometry.Geometry instance.')
        self.tmp_params['xray_wavelength'] = geo.wavelength * 1e10
        self.tmp_params['xray_energy'] = (LAMBDA_TO_E
                                          / self.tmp_params['xray_wavelength'])

        _geodict = geo.getPyFAI()
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            self.tmp_params[key] = _geodict[key.split('_')[1]]
