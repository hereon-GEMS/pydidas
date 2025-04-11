# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import shutil
import tempfile

import numpy as np
import pytest

from pydidas_plugins.proc_plugins.sin_square_chi_analysis import OUTPUT_UNIT_PARAM

import pydidas
from pydidas.core import Dataset, UserConfigError
from pydidas.plugins import ProcPlugin
from pydidas.unittest_objects import create_dataset
from pydidas_qtcore import PydidasQApplication


_EXP = pydidas.contexts.DiffractionExperimentContext()
_REGISTRY = pydidas.plugins.PluginCollection()

_LAMBDA_in_A = 1.0
_DET_DIST_in_m = 0.421
_RANGE_2THETA_RAD = np.linspace(0.035, 0.733, 200)
_RANGES = {
    "2theta_deg": np.rad2deg(_RANGE_2THETA_RAD),
    "2theta_rad": _RANGE_2THETA_RAD,
    "d-spacing_nm": (0.1 * _LAMBDA_in_A) / (2 * np.sin(_RANGE_2THETA_RAD[::-1] / 2)),
    "d-spacing_A": _LAMBDA_in_A / (2 * np.sin(_RANGE_2THETA_RAD[::-1] / 2)),
    "Q_nm^-1": (4 * np.pi) / (0.1 * _LAMBDA_in_A) * np.sin(_RANGE_2THETA_RAD / 2),
    "Q_A^-1": (4 * np.pi) / _LAMBDA_in_A * (np.sin(_RANGE_2THETA_RAD / 2)),
    "r_mm": (_DET_DIST_in_m * 1000) * np.tan(_RANGE_2THETA_RAD),
}
_CHI = np.linspace(5, 355, 36)

_RAW_DATA = Dataset(
    [
        40
        * np.exp(
            -0.5
            * (np.arange(_RANGE_2THETA_RAD.size) - 75 + 10 * np.sin(_DELTA)) ** 2
            / 5**2
        )
        for _DELTA in np.deg2rad(_CHI)
    ],
    axis_ranges=[_CHI, _RANGE_2THETA_RAD],
    axis_labels=["chi", "2theta"],
    axis_units=["deg", "rad"],
)


@pytest.fixture
def fitted_data(request):
    _input = request.param
    _output = _input[2] if len(_input) == 3 else "position; amplitude; FWHM"
    _FIT_PLUGIN = _REGISTRY.get_plugin_by_name("FitSinglePeak")()
    _FIT_PLUGIN.set_param_value("fit_output", _output)
    _FIT_PLUGIN.pre_execute()
    _label, _unit = _input[0].split("_")
    _data = _RAW_DATA.copy()
    _data.update_axis_unit(1, _unit)
    _data.update_axis_label(1, _label)
    _data.update_axis_range(1, _RANGES[_input[0]])
    _data, _ = _FIT_PLUGIN.execute(_data)
    return _data


@pytest.fixture(scope="module")
def app():
    app = PydidasQApplication([])
    yield app
    app.quit()


@pytest.fixture(scope="module")
def temp_dir():
    _dir = tempfile.mkdtemp()
    yield _dir
    shutil.rmtree(_dir)


@pytest.fixture
def plugin(temp_dir):
    _EXP.set_param_value("xray_wavelength", _LAMBDA_in_A)
    _EXP.set_param_value("detector_dist", _DET_DIST_in_m)
    _plugin_class = _REGISTRY.get_plugin_by_name("SinSquareChiAnalysis")
    _plugin = _plugin_class()
    _plugin.set_param_value("directory_path", temp_dir)
    _plugin.set_param_value("enable_overwrite", True)
    _plugin.node_id = 42
    yield _plugin


def test_init(plugin):
    assert isinstance(plugin, ProcPlugin)


def test_pre_execute(plugin):
    plugin._converter = lambda x: x
    plugin.pre_execute()
    assert not plugin._config["flag_input_data_check"]
    assert not plugin._config["flag_conversion_set_up"]
    assert plugin._converter is None


@pytest.mark.parametrize("ndim", [1, 3])
def test_check_input_data__invalid_ndim(plugin, ndim):
    fitted_data = create_dataset(ndim)
    plugin.pre_execute()
    with pytest.raises(UserConfigError, match="The input data must be two-dimensional"):
        plugin._check_input_data(fitted_data)


@pytest.mark.parametrize(
    "fitted_data",
    [("2theta_deg", np.rad2deg(_RANGE_2THETA_RAD))],
    indirect=True,
)
def test_check_input_data__invalid_ax0_label(plugin, fitted_data):
    fitted_data.update_axis_label(0, "not chi")
    plugin.pre_execute()
    with pytest.raises(UserConfigError, match="The data does not appear to be "):
        plugin._check_input_data(fitted_data)


@pytest.mark.parametrize(
    "fitted_data",
    [("2theta_deg", np.rad2deg(_RANGE_2THETA_RAD), "FWHM")],
    indirect=True,
)
def test_check_input_data__invalid_fit_output(plugin, fitted_data):
    plugin.pre_execute()
    with pytest.raises(UserConfigError, match="The data does not appear to be "):
        plugin._check_input_data(fitted_data)


@pytest.mark.parametrize(
    "fitted_data",
    [("2theta_deg", np.rad2deg(_RANGE_2THETA_RAD), "position")],
    indirect=True,
)
def test_check_input_data__fit_only_position(plugin, fitted_data):
    plugin.pre_execute()
    plugin._check_input_data(fitted_data)
    assert plugin._config["flag_input_data_check"]


@pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
def test_check_input_data__valid(plugin, fitted_data):
    plugin.pre_execute()
    plugin._check_input_data(fitted_data)
    assert plugin._config["flag_input_data_check"]


@pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
@pytest.mark.parametrize("output_type", OUTPUT_UNIT_PARAM.choices)
def test_set_up_converter(plugin, fitted_data, output_type):
    plugin.set_param_value("output_type", output_type)
    plugin.pre_execute()
    plugin._set_up_converter(fitted_data)
    assert plugin._config["flag_conversion_set_up"]
    assert isinstance(plugin._config["converter_args"], tuple)
    assert callable(plugin._converter)


# @pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
@pytest.mark.parametrize(
    "fitted_data",
    [("2theta_deg", np.rad2deg(_RANGE_2THETA_RAD), "position")],
    indirect=True,
)
# @pytest.mark.parametrize("output_type", OUTPUT_UNIT_PARAM.choices)
@pytest.mark.parametrize("output_type", ["d-spacing / A"])
def test_regroup_data_w_sin_chi(plugin, fitted_data, output_type):
    plugin.set_param_value("output_type", output_type)
    plugin.pre_execute()
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    print(_sin_square_chi_data)
    print(_sin_2chi_data)

#
# @pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
# def test_execute(plugin, fitted_data):
#     plugin.pre_execute()
#     _new_data, _ = plugin.execute(fitted_data)
#     print(_new_data)


if __name__ == "__main__":
    pytest.main()
