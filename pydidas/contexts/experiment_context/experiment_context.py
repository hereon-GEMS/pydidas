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
Module with the ExperimentContext singleton which is used to manage
global information about the experiment independant from the individual frames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ExperimentContext"]

import pyFAI

from ...core.constants import LAMBDA_IN_A_TO_E
from ...core import (
    SingletonFactory,
    get_generic_param_collection,
    ObjectWithParameterCollection,
)
from .experiment_context_io_meta import ExperimentContextIoMeta


class _ExperimentContext(ObjectWithParameterCollection):
    """
    Class which holds experimental settings. This class must only be
    instanciated through its factory, therefore guaranteeing that only a
    single instance exists.

    The singleton factory will allow access to the single instance through
    :py:class:`pydidas.contexts.experiment_context.ExperimentContext`.
    """

    default_params = get_generic_param_collection(
        "xray_wavelength",
        "xray_energy",
        "detector_name",
        "detector_npixx",
        "detector_npixy",
        "detector_pxsizex",
        "detector_pxsizey",
        "detector_mask_file",
        "detector_dist",
        "detector_poni1",
        "detector_poni2",
        "detector_rot1",
        "detector_rot2",
        "detector_rot3",
    )

    def __init__(self, *args, **kwargs):
        ObjectWithParameterCollection.__init__(self)
        self.add_params(*args)
        self.set_default_params()
        self.update_param_values_from_kwargs(**kwargs)

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
        if param_key == "xray_energy":
            self.params["xray_energy"].value = value
            self.params["xray_wavelength"].value = LAMBDA_IN_A_TO_E / value
        elif param_key == "xray_wavelength":
            self.params["xray_wavelength"].value = value
            self.params["xray_energy"].value = LAMBDA_IN_A_TO_E / value
        else:
            self.params.set_value(param_key, value)

    def get_detector(self):
        """
        Get the pyFAI detector object.

        If a pyFAI detector can be instantiated from the "detector" Parameter
        value, this object will be used. Otherwise, a new detector is created
        and values from the ExperimentContext are copied.

        Returns
        -------
        det : pyFAI.detectors.Detector
            The detector object.
        """
        _name = self.get_param_value("detector_name")
        try:
            _det = pyFAI.detector_factory(_name)
        except RuntimeError:
            _det = pyFAI.detectors.Detector()
        for key, value in [
            ["pixel1", self.get_param_value("detector_pxsizey") * 1e-6],
            ["pixel2", self.get_param_value("detector_pxsizex") * 1e-6],
            [
                "max_shape",
                (
                    self.get_param_value("detector_npixy"),
                    self.get_param_value("detector_npixx"),
                ),
            ],
        ]:
            setattr(_det, key, value)
        return _det

    def set_detector_params_from_name(self, det_name):
        """
        Set the detector parameters based on a detector name.

        This method will query the pyFAI library for the detector parameters
        and update the internal Parameters.

        Parameters
        ----------
        det_name : str
            The pyFAI name for the detector.

        Raises
        ------
        NameError
            If the specified detector name is unknown by pyFAI.
        """
        try:
            _det = pyFAI.detector_factory(det_name)
        except RuntimeError:
            raise NameError(f'The detector name "{det_name}"is unknown to ' "pyFAI.")
        self.set_param_value("detector_pxsizey", _det.pixel1 * 1e6)
        self.set_param_value("detector_pxsizex", _det.pixel2 * 1e6)
        self.set_param_value("detector_npixy", _det.max_shape[0]),
        self.set_param_value("detector_npixx", _det.max_shape[1])
        self.set_param_value("detector_name", _det.name)

    @staticmethod
    def import_from_file(filename):
        """
        Import ExperimentContext from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        """
        ExperimentContextIoMeta.import_from_file(filename)

    @staticmethod
    def export_to_file(filename, overwrite=False):
        """
        Import ExperimentContext from a file.

        Parameters
        ----------
        filename : Union[str, pathlib.Path]
            The full filename.
        overwrite : bool, optional
            Keyword to allow overwriting of existing files.
        """
        ExperimentContextIoMeta.export_to_file(filename, overwrite=overwrite)

    def __copy__(self):
        """
        Overload copy to return self.
        """
        return self


ExperimentContext = SingletonFactory(_ExperimentContext)
