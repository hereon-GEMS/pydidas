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
Module with the ExperimentalSetup singleton which is used to manage
global information about the experiment independant from the individual frames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ExperimentalSetup']

import pyFAI

from ...core.constants import LAMBDA_TO_E
from ...core import (SingletonFactory, get_generic_param_collection, #
                     ObjectWithParameterCollection)
from .experimental_setup_io_meta import ExperimentalSetupIoMeta


class _ExpSetup(ObjectWithParameterCollection):
    """
    Class which holds experimental settings. This class must only be
    instanciated through its factory, therefore guaranteeing that only a
    single instance exists.

    The singleton factory will allow access to the single instance through
    :py:class:`pydidas.experiment.experimental_setup.ExperimentalSetup`.
    """
    default_params = get_generic_param_collection(
        'xray_wavelength', 'xray_energy', 'detector_name', 'detector_npixx',
        'detector_npixy', 'detector_sizex', 'detector_sizey', 'detector_dist',
        'detector_poni1', 'detector_poni2', 'detector_rot1', 'detector_rot2',
        'detector_rot3')

    def __init__(self, *args, **kwargs):
        ObjectWithParameterCollection.__init__(self)
        self.add_params(*args, **kwargs)
        self.set_default_params()

    def set_param_value(self, param_key, value):
        """
        Set a Parameter value.

        This method overloads the inherited set_param_value method to update
        the linked parameters of X-ray energy and wavelength.

        Parameters
        ----------
        key : str
            The Parameter identifier key.
        value : object
            The new value for the parameter. Depending upon the parameter,
            value can take any form (number, string, object, ...).

        Raises
        ------
        KeyError
            If the key does not exist.
        """
        self._check_key(param_key)
        if param_key == 'xray_energy':
            self.params['xray_wavelength'].value = (
                LAMBDA_TO_E / (value * 1e-10))
            self.params['xray_energy'].value = value
        elif param_key == 'xray_wavelength':
            self.params['xray_wavelength'].value = value
            self.params['xray_energy'].value = LAMBDA_TO_E / (value * 1e-10)
        else:
            self.params.set_value(param_key, value)

    def get_detector(self):
        """
        Get the pyFAI detector object.

        If a pyFAI detector can be instantiated from the "detector" Parameter
        value, this object will be used. Otherwise, a new detector is created
        and values from the ExperimentalSetup are copied.

        Returns
        -------
        det : pyFAI.detectors.Detector
            The detector object.
        """
        _name = self.get_param_value('detector_name')
        try:
            _det = pyFAI.detector_factory(_name)
        except RuntimeError:
            _det = pyFAI.detectors.Detector()
        for key, value in [
                ['pixel1', self.get_param_value('detector_sizey')],
                ['pixel2', self.get_param_value('detector_sizex')],
                ['max_shape', (self.get_param_value('detector_npixy'),
                               self.get_param_value('detector_npixx'))]
                ]:
            if getattr(_det, key) != value:
                setattr(_det, key, value)
        return _det

    @staticmethod
    def import_from_file(filename):
        """
        Import ExperimentalSetup from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ExperimentalSetupIoMeta.import_from_file(filename)

    @staticmethod
    def export_to_file(filename):
        """
        Import ExperimentalSetup from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ExperimentalSetupIoMeta.export_to_file(filename)

    def __copy__(self):
        """
        Overload copy to return self.
        """
        return self


ExperimentalSetup = SingletonFactory(_ExpSetup)
