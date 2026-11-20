# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
#
# An AI tool has been used to migrate the content of this file from
# using unittest to pytest.

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import itertools

import numpy as np
import pytest
from qtpy import QtCore

from pydidas_plugins.proc_plugins.fit_triple_peak import FitTriplePeak
from tests.plugins.test_base_fit_plugin import BaseFitPluginTestSuite

from pydidas.core import Dataset
from pydidas.core.fitting.gaussian import Gaussian
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()
PEAK_INDICES = (42, 48, 62)
AMPLITUDES = (25, 37, 28)
SIGMA = 1.25
FIT_OUTPUT_SHAPES = [
    ("area", (3, 1)),
    ("position", (3, 1)),
    ("FWHM", (3, 1)),
    ("position; area", (3, 2)),
    ("position; area; FWHM", (3, 3)),
]
FIT_FUNCTION_CASES = [
    pytest.param("Triple Gaussian", None, {"check_amplitudes": False}, id="g-no_bg"),
    pytest.param("Triple Gaussian", 0, {}, id="gaussian-bg0"),
    pytest.param("Triple Gaussian", 1, {}, id="gaussian-bg1"),
    pytest.param(
        "Triple Lorentzian", None, {"amplitude_tolerance": 25}, id="lorentzian-no_bg"
    ),
    pytest.param("Triple Lorentzian", 0, {}, id="lorentzian-bg0"),
    pytest.param("Triple Lorentzian", 1, {}, id="lorentzian-bg1"),
    pytest.param("Triple Voigt", None, {"amplitude_tolerance": 25}, id="voigt-no_bg"),
    pytest.param("Triple Voigt", 0, {}, id="voigt-bg0"),
    pytest.param("Triple Voigt", 1, {}, id="voigt-bg1"),
]


@pytest.fixture(scope="module", autouse=True)
def _remove_unittesting_settings():
    yield
    QtCore.QSettings("Hereon", "pydidas").remove("unittesting")


@pytest.fixture
def data() -> Dataset:
    _x = np.arange(150) * 0.5
    _data = Dataset(
        np.ones(150), data_unit="data unit", axis_units=["ax_unit"], axis_ranges=[_x]
    )
    for _index, _amp in zip(PEAK_INDICES, AMPLITUDES):
        _data += Gaussian.func((_amp, SIGMA, _x[_index]), _x)
    return _data


def create_plugin(func: str = "Triple Gaussian", **params) -> FitTriplePeak:
    _plugin = PLUGIN_COLLECTION.get_plugin_by_name("FitTriplePeak")()
    _plugin.set_param_value("fit_func", func)
    _plugin.set_param_value("fit_lower_limit", 5)
    _plugin.set_param_value("fit_upper_limit", 45)
    _plugin.set_param_value("fit_output", "position")
    _plugin.set_param_value("fit_peak0_xstart", 20.2)
    _plugin.set_param_value("fit_peak1_xstart", 25)
    for _key, _value in params.items():
        _plugin.set_param_value(_key, _value)
    return _plugin


def create_plugin_with_dummy_fit(data: Dataset, output: str) -> FitTriplePeak:
    _plugin = create_plugin(fit_output=output)
    _plugin.pre_execute()
    _plugin.prepare_input_data(data)
    _startguess = _plugin._fitter.guess_fit_start_params(
        _plugin._data_x, _plugin._data, bg_order=_plugin.get_param_value("fit_bg_order")
    )
    _plugin._fit_params = dict(zip(_plugin.config["param_labels"], _startguess))
    _plugin._data.metadata = _plugin._data.metadata | {"test_meta": 123}
    return _plugin


def create_multidim_input_data(data: Dataset, data_dim: int) -> Dataset:
    _indices = {0: [2, 0, 1], 1: [0, 2, 1], 2: [0, 1, 2]}[data_dim]
    return Dataset(
        np.rollaxis(np.tile(data.array, (5, 4, 1)), 2, data_dim),
        axis_labels=[("a", "b", "data")[i] for i in _indices],
        axis_ranges=[
            [np.array((0, 2, 4, 7, 10)), np.array((1, 5, 9, 14)), data.axis_ranges[0]][
                i
            ]
            for i in _indices
        ],
        axis_units=[("u0", "u1", "u2")[i] for i in _indices],
    )


def assert_fit_results_okay(
    result: Dataset,
    params: dict,
    bg_order: int | None,
    check_amplitudes: bool = True,
    amplitude_tolerance: float | None = None,
) -> None:
    assert result.shape == (3, len(result.data_label.split(";")))
    if amplitude_tolerance is None:
        amplitude_tolerance = (
            2 if result.metadata["fit_func"] == "Triple Gaussian" else 15
        )
    assert "fit_params" in result.metadata
    assert "fit_func" in result.metadata
    assert "fit_residual_std" in result.metadata
    for _i, _amp in enumerate(AMPLITUDES):
        if check_amplitudes:
            assert abs(params[f"amplitude{_i}"] - _amp) <= amplitude_tolerance
        if "sigma" in params:
            assert abs(params[f"sigma{_i}"] - SIGMA) < 0.5
        if "gamma" in params:
            assert abs(params[f"gamma{_i}"] - SIGMA) < 0.5
        assert abs(params[f"center{_i}"] - PEAK_INDICES[_i] * 0.5) < 2
    if bg_order in [0, 1]:
        assert abs(params["background_p0"] - 1) < 1
    if bg_order == 1:
        assert abs(params["background_p1"]) < 1


@pytest.mark.parametrize("output, shape", FIT_OUTPUT_SHAPES)
def test_create_result_dataset__valid(data, output, shape):
    _plugin = create_plugin_with_dummy_fit(data, output)
    _result = _plugin.create_result_dataset()
    for _key in ["fit_params", "fit_func", "fit_residual_std", "test_meta"]:
        assert _key in _result.metadata
    assert _result.shape == shape


def test_create_result_dataset__peak_outside_array(data):
    _plugin = create_plugin_with_dummy_fit(data, "position")
    _plugin._fit_params["center0"] = 0
    _result = _plugin.create_result_dataset()
    assert "test_meta" in _result.metadata
    assert np.all(np.isnan(_result.array))


def test_create_result_dataset__high_std(data):
    _plugin = create_plugin_with_dummy_fit(data, "position")
    _plugin._fit_params["amplitude0"] = 1e6
    _result = _plugin.create_result_dataset()
    assert "test_meta" in _result.metadata
    assert np.all(np.isnan(_result.array))
    assert _result.shape == (3, 1)


def test_execute__gaussian_no_bg__axis_unit_in_label(data):
    _plugin = create_plugin(fit_bg_order=None)
    _plugin.pre_execute()
    _result, _ = _plugin.execute(data)
    assert data.axis_units[0] in _result.data_label


def test_execute__gaussian_no_bg_all_outputs(data):
    _plugin = create_plugin(fit_bg_order=None, fit_output="position; area; FWHM")
    _plugin.pre_execute()
    _result, _ = _plugin.execute(data)
    assert _result.shape == (3, 3)


@pytest.mark.parametrize("func, bg_order, check_kwargs", FIT_FUNCTION_CASES)
def test_execute__fit_functions(data, func, bg_order, check_kwargs):
    _plugin = create_plugin(func, fit_bg_order=bg_order)
    _plugin.pre_execute()
    _result, _kwargs = _plugin.execute(data)
    assert_fit_results_okay(_result, _kwargs["fit_params"], bg_order, **check_kwargs)


def test_execute__gaussian_w_steep_1d_bg(data):
    _plugin = create_plugin(fit_bg_order=1)
    _plugin.pre_execute()
    _result, _kwargs = _plugin.execute(data + 3 * np.arange(data.size))
    assert_fit_results_okay(_result, _kwargs["fit_params"], None)
    assert abs(_kwargs["fit_params"]["background_p1"] - 6) < 0.5


def test_execute__gaussian_w_only_background_and_min_peak(data):
    _plugin = create_plugin(fit_bg_order=1, fit_min_peak_height=10)
    _plugin.pre_execute()
    _result, _ = _plugin.execute(Dataset(3 * np.arange(data.size)))
    assert np.all(np.isnan(_result))


@pytest.mark.parametrize("data_dim", [0, 1, 2])
@pytest.mark.parametrize("output", ["position", "position; area; FWHM"])
def test_execute__w_multidim_input(data, data_dim, output):
    _data = create_multidim_input_data(data, data_dim)
    _plugin = create_plugin(fit_output=output, process_data_dim=data_dim)
    _plugin.pre_execute()
    _result, _kwargs = _plugin.execute(_data)
    _slice = [0] * data_dim + [slice(None), slice(None)] + [0] * (2 - data_dim)
    assert_fit_results_okay(_result[*_slice], _kwargs["fit_params"], None)


def test_detailed_results(data):
    _plugin = create_plugin()
    _plugin.pre_execute()
    _plugin.execute(data, store_details=True)
    assert set(_plugin.detailed_results) == {None}


def test_detailed_results__multidim(data):
    _data = create_multidim_input_data(data, 2)
    _plugin = create_plugin()
    _plugin.pre_execute()
    _plugin.execute(_data, store_details=True)
    _details = _plugin.detailed_results
    for _indices in itertools.product(range(5), range(4)):
        assert _data.get_description_of_point(_indices + (None,)) in _details
    assert None not in _details


class TestFitTriplePeakGeneric(BaseFitPluginTestSuite):
    plugin_class = FitTriplePeak
    fit_func = "Triple Gaussian"
    num_peaks = 3


if __name__ == "__main__":
    pytest.main([__file__])
