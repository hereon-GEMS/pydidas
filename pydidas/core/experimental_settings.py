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

"""Module with the GlobalSettings class which is used to manage global
information independant from the individual frames."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSettings']

import scipy.constants

from .global_settings import _GlobalSettings
from .parameter import Parameter

LAMBDA_TO_E = scipy.constants.h * scipy.constants.c / scipy.constants.e * 1e-3

_tooltips = {
    'xray_wavelength': ('The X-ray wavelength (in Angstrom). Any changes to '
                        'the wavelength will also update the X-ray energy '
                        'setting.'),
    'xray_energy': ('The X-ray energy (in keV). Changing this parameter will '
                    'also update the X-ray wavelength setting.'),
    'detector_name': 'The detector name in pyFAI nomenclature.',
    'detector_npixx': ('The number of detector pixels in x direction '
                       '(horizontal).'),
    'detector_npixy': ('The number of detector pixels in y direction '
                       '(vertical).'),
    'detector_dx': 'The detector pixel size in X-direction in micrometer.',
    'detector_dy': 'The detector pixel size in Y-direction in micrometer.',
    'detector_dist': 'The sample-detector distance (in m).',
    'detector_poni1': ('The detector PONI1 (point of normal incidence; '
                       'in y direction). This is measured in meters from the'
                       'detector origin.'),
    'detector_poni2': ('The detector PONI2 (point of normal incidence; '
                       'in x direction). This is measured in meters from the'
                       'detector origin.'),
    'detector_rot1': ('The detector rotation 1 (lefthanded around the '
                      '"up"-axis), given in rad.'),
    'detector_rot2': ('The detector rotation 2 (pitching the detector; '
                      'positive direction is tilting the detector towards the'
                      ' floor, i.e. left-handed), given in rad.'),
    'detector_rot3': ('The detector rotation 3 (around the beam axis; '
                      'right-handed when looking downstream with the beam.'
                      'Given in rad.'),
    }

_params = {
     'xray_wavelength': Parameter('X-ray wavelength', float, default=1,
                                  unit='A', refkey='xray_wavelength',
                                  tooltip=_tooltips['xray_wavelength']),
    'xray_energy':  Parameter('X-ray energy', float, default=12.398, unit='keV', refkey='xray_energy',
                              tooltip=_tooltips['xray_energy']),
    'detector_name': Parameter('Detector name', str, default='', refkey='detector_name',
                          unit='', tooltip=_tooltips['detector_name']),
    'detector_npixx': Parameter('Detector size X', int, default=0, refkey='detector_npixx',
                          unit='px', tooltip=_tooltips['detector_npixx']),
    'detector_npixy': Parameter('Detector size Y', int, default=0, refkey='detector_npixy',
                          unit='px', tooltip=_tooltips['detector_npixy']),
    'detector_dx': Parameter('Detector pixel size X', float,
                             default=-1, unit='um', refkey='detector_dx',
                             tooltip=_tooltips['detector_dx']),
    'detector_dy': Parameter('Detector pixel size Y', float,
                             default=-1, unit='um', refkey='detector_dy',
                             tooltip=_tooltips['detector_dy']),
    'detector_dist': Parameter('Sample-detector distance', float, default=0, refkey='detector_dist',
                               unit='m', tooltip=_tooltips['detector_dist']),
    'detector_poni1': Parameter('Detector PONI1', float, default=0, unit='m', refkey='detector_poni1',
                                tooltip=_tooltips['detector_poni1']),
    'detector_poni2': Parameter('Detector PONI2', float, default=0, unit='m', refkey='detector_poni2',
                                tooltip=_tooltips['detector_poni2']),
    'detector_rot1': Parameter('Detector Rot1', float, default=0, unit='rad', refkey='detector_rot1',
                               tooltip=_tooltips['detector_rot1']),
    'detector_rot2': Parameter('Detector Rot2', float, default=0, unit='rad', refkey='detector_rot2',
                               tooltip=_tooltips['detector_rot2']),
    'detector_rot3': Parameter('Detector Rot3', float, default=0, unit='rad', refkey='detector_rot3',
                               tooltip=_tooltips['detector_rot3']),
    }

class _ExpSettings(_GlobalSettings):
    """
    Class which holds experimental settings. This class must only be
    instanciated through its factory, therefore guaranteeing that only a
    single instance exists.
    """
    def __init__(self, **kwargs):
        """Setup method"""
        self._params = kwargs.get('params', {})
        for key in _params:
            if not self.key_exists(key):
                self.register_param(key, default_entry=_params[key])

    def set(self, key, value):
        """
        Set a parameter value.

        This method overloads the inherited set method to update the linked
        parameters of X-ray energy and wavelength.

        Parameters
        ----------
        key : str
            The parameter identifier key.
        value : object
            The new value for the parameter. Depending upon the parameter,
            value can take any form (number, string, object, ...).

        Raises
        ------
        KeyError
            If the key does not exist.

        Returns
        -------
        None.
        """
        if key not in self._params:
            raise KeyError(f'The key {key} is not registered with '
                           'GlobalSettings!')
        if key == 'xray_energy':
            self._params['xray_wavelength'].value = LAMBDA_TO_E / value
            self._params['xray_energy'].value = value
        elif key == 'xray_wavelength':
            self._params['xray_wavelength'].value = value * 1e-10
            self._params['xray_energy'].value = LAMBDA_TO_E / (value * 1e-10)
        else:
            super().set(key, value)



class _ExpSettingsFactory:
    """
    Factory to create a Singleton.
    """
    def __init__(self):
        """
        Setup method.
        """
        self._instance = None

    def __call__(self):
        """
        Get the instance of ExperimentalSettings

        Returns
        -------
        ExperimentalSettings
            The instance of the ExperimentalSettings class.
        """
        if not self._instance:
            self._instance = _ExpSettings()
        return self._instance


ExperimentalSettings = _ExpSettingsFactory()
