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
__all__ = ['SaveExperimentSettingsToFileMixIn']

import os

import yaml
import pyFAI

from ...config import YAML_EXTENSIONS


class SaveExperimentSettingsToFileMixIn:
    """
    The LoadExperimentSettingsFromFile class allows to read Xray wavelength,
    detector and geometry information from a file and store them internally
    in the ExperimentalSettings object.
    """
    def save_to_file(self, fname):
        """
        Save ExperimentalSettings to a file.

        Parameters
        ----------
        fname : str
            The full path of the file with the ExperimentalSettings
            configuration.

        Raises
        ------
        KeyError
            If the file extension is not recognized.
        """
        self.fname = fname
        _ext = os.path.splitext(self.fname)[1]
        if _ext == '.poni':
            self.__save_poni_file()
        elif _ext in YAML_EXTENSIONS:
            self.__save_yaml_file()
        else:
            raise KeyError('No interpreter found for file extension '
                           f'"{_ext}". Please try with a different file or'
                           ' change the current file extension. Expected '
                           'extensions for poni files: .poni and for yaml '
                           f'files: {YAML_EXTENSIONS}.')

    def __save_poni_file(self):
        """
        Loada pyFAI type file with geometry information.
        """
        _pdata = {}
        for key in ['rot1', 'rot2', 'rot3', 'poni1', 'poni2']:
            _pdata[key] = self.get_param_value(f'detector_{key}')
        _pdata['detector'] = self.get_param_value('detector_name')
        _pdata['distance'] = self.get_param_value('detector_dist')
        if (_pdata['detector'] in pyFAI.detectors.Detector.registry.keys()
                and _pdata['detector'] != 'detector'):
            _pdata['detector_config'] = {}
        else:
            _pdata['detector_config'] = dict(
                pixel1=self.get_param_value('detector_sizey'),
                pixel2=self.get_param_value('detector_sizex'),
                max_shape=(self.get_param_value('detector_npixy'),
                           self.get_param_value('detector_npixx')))
        _pdata['wavelength'] = (self.get_param_value('xray_wavelength')
                                  * 1e-10)
        pfile = pyFAI.io.ponifile.PoniFile()
        pfile.read_from_dict(_pdata)
        with open(self.fname, 'w') as stream:
            pfile.write(stream)

    def __save_yaml_file(self):
        """
        Load ExperimentalSettings from a YAML file.
        """
        tmp_params = self.get_param_values_as_dict()
        del tmp_params['xray_energy']
        with open(self.fname, 'w') as stream:
            yaml.safe_dump(tmp_params, stream)
