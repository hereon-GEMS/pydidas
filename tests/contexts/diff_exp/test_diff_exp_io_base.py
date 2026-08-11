# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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

"""Unit tests for DiffractionExperimentIoBase."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest  # pyright: ignore[reportMissingImports]

from pydidas.contexts.diff_exp import (
    DiffractionExperiment,
    DiffractionExperimentContext,
)
from pydidas.contexts.diff_exp.diff_exp_io_base import DiffractionExperimentIoBase
from pydidas.core import UserConfigError


EXP = DiffractionExperimentContext()


@pytest.fixture
def exp_context():
    """Provide a fresh DiffractionExperimentContext for each test."""
    _exp = DiffractionExperimentContext()
    _exp.restore_all_defaults(True)
    return _exp


@pytest.fixture
def complete_params_dict(exp_context):
    """Provide a dictionary with all required parameters."""
    _params = {}
    for param in exp_context.params:
        _params[param] = exp_context.get_param_value(param)
    return _params


def test_verify_all_entries_present__correct(complete_params_dict):
    _reply = DiffractionExperimentIoBase.verify_all_entries_present(
        complete_params_dict
    )
    assert _reply is None  # i.e. check that no Exception was raised


def test_verify_all_entries_present__missing_keys(complete_params_dict):
    del complete_params_dict["detector_name"]
    with pytest.raises(UserConfigError):
        DiffractionExperimentIoBase.verify_all_entries_present(complete_params_dict)


def test_verify_all_entries_present__exclude_det_mask(complete_params_dict):
    del complete_params_dict["detector_mask_file"]
    _reply = DiffractionExperimentIoBase.verify_all_entries_present(
        complete_params_dict, exclude_det_mask=True
    )
    assert _reply is None  # i.e. check that no Exception was raised


def test_update_diffraction_exp__w_global_context(exp_context, complete_params_dict):
    _det_name = "Test Detector"
    _energy = 123.45
    complete_params_dict["detector_name"] = _det_name
    complete_params_dict["xray_energy"] = _energy
    DiffractionExperimentIoBase.update_diffraction_exp(complete_params_dict)
    assert exp_context.get_param_value("detector_name") == _det_name
    assert exp_context.get_param_value("xray_energy") == _energy


def test_update_diffraction_exp__with_instance(complete_params_dict):
    _exp = DiffractionExperiment()
    _exp.restore_all_defaults(True)
    _det_name = "Test Detector"
    _energy = 123.45
    complete_params_dict["detector_name"] = _det_name
    complete_params_dict["xray_energy"] = _energy
    DiffractionExperimentIoBase.update_diffraction_exp(
        complete_params_dict, diffraction_exp=_exp
    )
    assert _exp.get_param_value("detector_name") == _det_name
    assert _exp.get_param_value("xray_energy") == _energy
    assert EXP.get_param_value("detector_name") != _det_name
    assert EXP.get_param_value("xray_energy") != _energy


if __name__ == "__main__":
    pytest.main([__file__])
