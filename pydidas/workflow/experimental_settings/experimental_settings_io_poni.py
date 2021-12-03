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
"""
Module with the ExperimentalSettingsYamlIo class which is used to import
ExperimentalSettings metadata from a pyFAI poni file.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSettingsIoPoni']


import pyFAI

from pydidas.constants import LAMBDA_TO_E
from .experimental_settings_io_base import ExperimentalSettingsIoBase
from .experimental_settings import ExperimentalSettings

EXP_SETTINGS = ExperimentalSettings()


class ExperimentalSettingsIoPoni(ExperimentalSettingsIoBase):
    """
    Base class for WorkflowTree exporters.
    """
    extensions = ['.poni']
    format_name = 'PONI'

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        """
        Write the ExperimentalTree to a pyFAI style poni file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        cls.check_for_existing_file(filename, **kwargs)
        _pdata = {}
        for key in ['rot1', 'rot2', 'rot3', 'poni1', 'poni2']:
            _pdata[key] = EXP_SETTINGS.get_param_value(f'detector_{key}')
        _pdata['detector'] = EXP_SETTINGS.get_param_value('detector_name')
        _pdata['distance'] = EXP_SETTINGS.get_param_value('detector_dist')
        if (_pdata['detector'] in pyFAI.detectors.Detector.registry.keys()
                and _pdata['detector'] != 'detector'):
            _pdata['detector_config'] = {}
        else:
            _pdata['detector_config'] = dict(
                pixel1=EXP_SETTINGS.get_param_value('detector_sizey'),
                pixel2=EXP_SETTINGS.get_param_value('detector_sizex'),
                max_shape=(EXP_SETTINGS.get_param_value('detector_npixy'),
                           EXP_SETTINGS.get_param_value('detector_npixx')))
        _pdata['wavelength'] = (EXP_SETTINGS.get_param_value('xray_wavelength')
                                * 1e-10)
        pfile = pyFAI.io.ponifile.PoniFile()
        pfile.read_from_dict(_pdata)
        with open(filename, 'w') as stream:
            pfile.write(stream)

    @classmethod
    def import_from_file(cls, filename):
        """
        Restore the ExperimentalSettings from a YAML file.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        """
        geo = pyFAI.geometry.Geometry().load(filename)
        cls.imported_params = {}
        cls._update_detector_from_pyFAI(geo.detector)
        cls._update_geometry_from_pyFAI(geo)
        cls._verify_all_entries_present()
        cls._write_to_exp_settings()

    @classmethod
    def _update_detector_from_pyFAI(cls, det):
        """Update the detector information from a pyFAI Detector instance. """
        if not isinstance(det, pyFAI.detectors.Detector):
            raise TypeError(f'Object "{det} (type {type(det)} is not a '
                            'pyFAI.detectors.Detector instance.')
        for key, value in [['detector_name', det.name],
                           ['detector_npixx', det.shape[1]],
                           ['detector_npixy', det.shape[0]],
                           ['detector_sizex', det.pixel2],
                           ['detector_sizey', det.pixel1]]:
            cls.imported_params[key] = value

    @classmethod
    def _update_geometry_from_pyFAI(cls, geo):
        """Update the geometry information from a pyFAI Geometry instance. """
        if not isinstance(geo, pyFAI.geometry.Geometry):
            raise TypeError(f'Object "{geo} (type {type(geo)} is not a '
                            'pyFAI.geometry.Geometry instance.')
        cls.imported_params['xray_wavelength'] = geo.wavelength * 1e10
        cls.imported_params['xray_energy'] = (LAMBDA_TO_E / geo.wavelength)
        _geodict = geo.getPyFAI()
        for key in ['detector_dist', 'detector_poni1', 'detector_poni2',
                    'detector_rot1', 'detector_rot2', 'detector_rot3']:
            cls.imported_params[key] = _geodict[key.split('_')[1]]
