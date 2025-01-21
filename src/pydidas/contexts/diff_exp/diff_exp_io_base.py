# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the DiffractionExperimentIoBase class which exporters / importers for
DiffractionExperiment(Context) should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DiffractionExperimentIoBase"]


from typing import Union

from pydidas.contexts.diff_exp.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_context import DiffractionExperimentContext
from pydidas.contexts.diff_exp.diff_exp_io import DiffractionExperimentIo
from pydidas.core import UserConfigError
from pydidas.core.io_registry import GenericIoBase


EXP = DiffractionExperimentContext()


class DiffractionExperimentIoBase(GenericIoBase, metaclass=DiffractionExperimentIo):
    """
    Base class for DiffractionExperimentContext importer/exporters.
    """

    extensions = []
    format_name = "unknown"
    imported_params = {}

    @classmethod
    def _verify_all_entries_present(cls, exclude_det_mask: bool = False):
        """
        Verify that the tmp_params dictionary holds all required keys.

        Parameters
        ----------
        exclude_det_mask : bool, optional
            Flag to skip checking for the detector_mask_file Parameter. Used for
            example when importing .poni files which do not support a detector mask.
            The default is False.
        """
        _missing_entries = []
        for _key in EXP.params:
            if _key not in cls.imported_params:
                _missing_entries.append(_key)
        if exclude_det_mask and "detector_mask_file" in _missing_entries:
            _missing_entries.remove("detector_mask_file")
        if len(_missing_entries) > 0:
            _text = (
                "The following DiffractionExperimentContext Parameters are missing:\n- "
                + "\n- ".join(_missing_entries)
            )
            raise UserConfigError(_text)

    @classmethod
    def _write_to_exp_settings(
        cls, diffraction_exp: Union[DiffractionExperiment, None] = None
    ):
        """
        Write the loaded (temporary) Parameters to a Diffraction.

        Parameters
        ----------
        diffraction_exp : Union[DiffractionExperiment, None], optional
            The instance to be updated. If None, the generic
            DiffractionExperimentContext will be used. The default is None.
        """
        _exp = EXP if diffraction_exp is None else diffraction_exp
        for _key, _value in cls.imported_params.items():
            _exp.set_param_value(_key, _value)
        cls.imported_params = {}
