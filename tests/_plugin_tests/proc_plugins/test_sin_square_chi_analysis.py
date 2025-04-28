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
from pathlib import Path

import numpy as np
import pytest

from pydidas_plugins.proc_plugins.sin_square_chi_analysis import (
    _filter_nan_from_1d_dataset,
)

import pydidas
from pydidas.core import Dataset, UserConfigError, get_generic_parameter
from pydidas.core.utils.scattering_geometry import convert_integration_result
from pydidas.plugins import ProcPlugin
from pydidas.unittest_objects import create_dataset


_OUTPUT_UNIT_PARAM = get_generic_parameter("output_type")
_EXP = pydidas.contexts.DiffractionExperimentContext()
_REGISTRY = pydidas.plugins.PluginCollection()
_SCAN = pydidas.contexts.ScanContext()

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
_RANGE_ONLY_2THETA_RAD = [("2theta_deg", np.rad2deg(_RANGE_2THETA_RAD))]
_CHI = np.linspace(5, 355, 36)

_RAW_DATA = Dataset(
    [
        40
        * np.exp(
            -0.5
            * (np.arange(_RANGE_2THETA_RAD.size) - 75 + 10 * np.sin(2 * _DELTA)) ** 2
            / 5**2
        )
        for _DELTA in np.deg2rad(_CHI + 20)
    ],
    axis_ranges=[_CHI, _RANGE_2THETA_RAD],
    axis_labels=["chi", "2theta"],
    axis_units=["deg", "rad"],
)


@pytest.fixture(scope="module")
def sin_square_plugin():
    _plugin_class = _REGISTRY.get_plugin_by_name("SinSquareChiGrouping")
    _plugin = _plugin_class()
    _plugin.node_id = 42
    yield _plugin


@pytest.fixture(scope="module")
def sin_2chi_plugin():
    _plugin_class = _REGISTRY.get_plugin_by_name("Sin_2chiGrouping")
    _plugin = _plugin_class()
    _plugin.node_id = 41
    yield _plugin


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
    _data[1, :] = np.nan
    return _data


@pytest.fixture(scope="module")
def temp_dir():
    _SCAN.set_param_value("scan_dim0_n_points", 42)
    _SCAN.set_param_value("scan_dim", 1)
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


@pytest.fixture
def grouped_sin_square_chi_data(fitted_data, sin_square_plugin) -> Dataset:
    _plugin = sin_square_plugin.copy()
    _plugin.pre_execute()
    _sin_square_chi_data = _plugin.execute(fitted_data)
    return _sin_square_chi_data


def test_init(plugin):
    assert isinstance(plugin, ProcPlugin)


def test_pre_execute(plugin):
    plugin._converter = lambda x: x
    plugin.pre_execute()
    assert not plugin._config["flag_input_data_check"]
    assert not plugin._config["flag_conversion_set_up"]
    assert plugin._converter is None


def test_pre_execute__w_invalid_limits(plugin):
    plugin.set_param_value("sin_square_chi_low_fit_limit", 0.5)
    plugin.set_param_value("sin_square_chi_high_fit_limit", 0.1)
    with pytest.raises(UserConfigError):
        plugin.pre_execute()


@pytest.mark.parametrize("ndim", [1, 3])
def test_check_input_data__invalid_ndim(plugin, ndim):
    fitted_data = create_dataset(ndim)
    plugin.pre_execute()
    with pytest.raises(UserConfigError, match="The input data must be two-dimensional"):
        plugin._check_input_data(fitted_data)


@pytest.mark.parametrize("fitted_data", _RANGE_ONLY_2THETA_RAD, indirect=True)
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
@pytest.mark.parametrize("output_type", _OUTPUT_UNIT_PARAM.choices)
def test_set_up_converter(plugin, fitted_data, output_type):
    plugin.set_param_value("output_type", output_type)
    plugin.pre_execute()
    plugin._set_up_converter(fitted_data)
    assert plugin._config["flag_conversion_set_up"]
    assert isinstance(plugin._config["converter_args"], tuple)
    assert callable(plugin._converter)


@pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
@pytest.mark.parametrize("output_type", _OUTPUT_UNIT_PARAM.choices)
def test_regroup_data_w_sin_chi(plugin, fitted_data, output_type, sin_square_plugin):
    plugin.set_param_value("output_type", output_type)
    input_type = (
        fitted_data.metadata.get("fitted_axis_label")
        + " / "
        + fitted_data.metadata.get("fitted_axis_unit")
    )
    if output_type == "Same as input":
        output_type = input_type
    plugin.pre_execute()
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    _ref_sin_square_chi_data = convert_integration_result(
        sin_square_plugin.execute(fitted_data)[0],
        input_type,
        output_type,
        _EXP.xray_wavelength_in_m,
        _EXP.det_dist_in_m,
    )
    assert np.allclose(_sin_square_chi_data.data, _ref_sin_square_chi_data.data)


@pytest.mark.parametrize("fitted_data", _RANGE_ONLY_2THETA_RAD, indirect=True)
@pytest.mark.parametrize("output_type", [_OUTPUT_UNIT_PARAM.choices[0]])
@pytest.mark.parametrize("non_nan_values", list(np.arange(10)))
def test_fit_sin_square_chi_data__w_nan_values(
    plugin, fitted_data, output_type, non_nan_values
):
    plugin.set_param_value("output_type", output_type)
    plugin.pre_execute()
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    _sin_square_chi_data[2, non_nan_values:] = np.nan
    _fitted_slope_and_errors = plugin._fit_sin_square_chi_data(_sin_square_chi_data)
    if non_nan_values in [0, 1]:
        assert np.all(np.isnan(_fitted_slope_and_errors))
    else:
        _x, _y = _filter_nan_from_1d_dataset(_sin_square_chi_data[2])
        _slope_estimate = np.mean(np.diff(_y) / np.diff(_x))
        _intercept_estimate = np.mean(_y - _slope_estimate * _x)
        assert np.allclose(_fitted_slope_and_errors[0], _slope_estimate, atol=0.1)
        assert np.allclose(_fitted_slope_and_errors[2], _intercept_estimate, atol=0.1)
        if non_nan_values in [2, 3, 4]:
            assert np.isnan(_fitted_slope_and_errors[1])
            assert np.isnan(_fitted_slope_and_errors[3])


@pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
@pytest.mark.parametrize("output_type", _OUTPUT_UNIT_PARAM.choices)
def test_fit_sin_square_chi_data(plugin, fitted_data, output_type):
    plugin.set_param_value("output_type", output_type)
    plugin.pre_execute()
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    _sin_square_chi_data[2, 4] = np.nan
    _fitted_slope_and_errors = plugin._fit_sin_square_chi_data(_sin_square_chi_data)
    _x, _y = _filter_nan_from_1d_dataset(_sin_square_chi_data[2])
    _slope_estimate = np.mean(np.diff(_y) / np.diff(_x))
    _intercept_estimate = np.mean(_y - _slope_estimate * _x)
    assert np.allclose(_fitted_slope_and_errors[0], _slope_estimate, atol=0.1)
    assert np.allclose(_fitted_slope_and_errors[2], _intercept_estimate, atol=0.1)


@pytest.mark.parametrize("fitted_data", _RANGE_ONLY_2THETA_RAD, indirect=True)
@pytest.mark.parametrize("output_type", [_OUTPUT_UNIT_PARAM.choices[0]])
def test_fit_sin_2chi_data__w_all_nan(
    plugin,
    fitted_data,
    output_type,
):
    plugin.set_param_value("output_type", output_type)
    plugin.pre_execute()
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    _sin_2chi_data[2, :] = np.nan
    _fitted_slope_and_error = plugin._fit_sin_2chi_data(_sin_2chi_data)
    assert np.isnan(_fitted_slope_and_error[0])
    assert np.isnan(_fitted_slope_and_error[1])


@pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
@pytest.mark.parametrize("output_type", _OUTPUT_UNIT_PARAM.choices)
def test_fit_sin_2chi_data(
    plugin,
    fitted_data,
    output_type,
):
    plugin.set_param_value("output_type", output_type)
    plugin.pre_execute()
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    _sin_2chi_data[2, 2] = np.nan
    _fitted_slope_and_error = plugin._fit_sin_2chi_data(_sin_2chi_data)
    _slope_estimate = np.nanmean(_sin_2chi_data[2] / _sin_2chi_data.axis_ranges[1])
    assert np.allclose(_fitted_slope_and_error[0], _slope_estimate, atol=0.1)
    assert np.allclose(_fitted_slope_and_error[1], 0, atol=0.2)


@pytest.mark.parametrize("limit_low", [0, 0.1, 0.2, 0.3, 0.5])
@pytest.mark.parametrize("limit_high", [0.6, 0.75, 0.9, 1])
def test_calculate_fit_slice(plugin, limit_low, limit_high):
    plugin.set_param_value("sin_square_chi_low_fit_limit", limit_low)
    plugin.set_param_value("sin_square_chi_high_fit_limit", limit_high)
    _x = np.linspace(0, 1, 101)
    _y = Dataset(np.ones(_x.size), axis_ranges=[_x], axis_labels=["x"])
    _valid_indices = np.where((_x >= limit_low) & (_x <= limit_high))[0]
    plugin._calculate_fit_slice(_y)
    assert plugin._fit_slice.start == _valid_indices[0]
    assert plugin._fit_slice.stop == _valid_indices[-1] + 1


@pytest.mark.parametrize("fitted_data", _RANGE_ONLY_2THETA_RAD, indirect=True)
def test_create_detailed_results(plugin, fitted_data):
    plugin.pre_execute()
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    _fit_sin_square_res = plugin._fit_sin_square_chi_data(_sin_square_chi_data)
    _fit_sin_2chi_res = plugin._fit_sin_2chi_data(_sin_2chi_data)
    plugin.create_detailed_results(
        _sin_square_chi_data,
        _sin_2chi_data,
        _fit_sin_square_res,
        _fit_sin_2chi_res,
    )
    assert None in plugin._details
    assert plugin._details[None]["n_plots"] == 2
    assert plugin._details[None]["plot_titles"] == {
        0: "sin^2(chi)",
        1: "sin(2*chi)",
    }
    assert plugin._details[None]["plot_ylabels"] == {
        0: _sin_square_chi_data.data_description,
        1: _sin_2chi_data.data_description,
    }
    assert "items" in plugin._details[None]


@pytest.mark.parametrize("fitted_data", _RANGE_ONLY_2THETA_RAD, indirect=True)
def test_write_results(plugin, fitted_data):
    plugin.set_param_value("output_export_images_flag", True)
    plugin._config["global_index"] = 2
    plugin.pre_execute()
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    _fit_sin_square_res = plugin._fit_sin_square_chi_data(_sin_square_chi_data)
    _fit_sin_2chi_res = plugin._fit_sin_2chi_data(_sin_2chi_data)
    plugin.create_detailed_results(
        _sin_square_chi_data,
        _sin_2chi_data,
        _fit_sin_square_res,
        _fit_sin_2chi_res,
    )
    plugin._write_results()
    _fname = plugin.get_output_filename("png")
    assert Path(_fname).is_file()


@pytest.mark.parametrize("fitted_data", _RANGE_ONLY_2THETA_RAD, indirect=True)
def test_write_results__all_nan(plugin, fitted_data):
    plugin.set_param_value("output_export_images_flag", True)
    plugin._config["global_index"] = 2
    plugin.pre_execute()
    fitted_data[:] = np.nan
    _sin_square_chi_data, _sin_2chi_data = plugin._regroup_data_w_sin_chi(fitted_data)
    _fit_sin_square_res = plugin._fit_sin_square_chi_data(_sin_square_chi_data)
    _fit_sin_2chi_res = plugin._fit_sin_2chi_data(_sin_2chi_data)
    plugin.create_detailed_results(
        _sin_square_chi_data,
        _sin_2chi_data,
        _fit_sin_square_res,
        _fit_sin_2chi_res,
    )
    plugin._write_results()
    _fname = plugin.get_output_filename("png")
    assert Path(_fname).is_file()


if __name__ == "__main__":
    pytest.main()
