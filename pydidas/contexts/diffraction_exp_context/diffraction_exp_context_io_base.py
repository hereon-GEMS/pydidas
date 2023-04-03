# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the DiffractionExperimentContextIoBase class which exporters/importers for
DiffractionExperimentContext should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["DiffractionExperimentContextIoBase"]


from ...core import UserConfigError
from ...core.io_registry import GenericIoBase
from .diffraction_exp_context import DiffractionExperimentContext
from .diffraction_exp_context_io_meta import DiffractionExperimentContextIoMeta


EXP = DiffractionExperimentContext()


class DiffractionExperimentContextIoBase(
    GenericIoBase, metaclass=DiffractionExperimentContextIoMeta
):
    """
    Base class for DiffractionExperimentContext importer/exporters.
    """

    extensions = []
    format_name = "unknown"
    imported_params = {}

    @classmethod
    def _verify_all_entries_present(cls, exclude_det_mask=False):
        """
        Verify that the tmp_params dictionary holds all keys from the
        DiffractionExperimentContext.
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
    def _write_to_exp_settings(cls, diffraction_exp=None):
        """
        Write the loaded (temporary) Parameters to a Diffraction.

        Parameters
        ----------
        diffraction_exp : Union[DiffractionExperiment, None], optional
            The instance to be updated. If None, the generic
            DiffractionExperimentContext will be used. The default is None.
        """
        _exp = EXP if diffraction_exp is None else diffraction_exp
        for key in cls.imported_params:
            _exp.set_param_value(key, cls.imported_params[key])
        cls.imported_params = {}
