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
#
# This file was modified (migrated from unittest to pytest) using
# an AI tool.


"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from typing import Any

import numpy as np
import pytest

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.core.fitting.gaussian import Gaussian
from pydidas.core.generic_params import FIT_OUTPUT_OPTIONS
from pydidas.plugins import BaseFitPlugin, BasePlugin
from pydidas.widgets.plugin_config_widgets import FitPluginConfigWidget


PEAK_INDEX = 42
SIGMA = 1.25
AMPLITUDE = 25
ALL_OUTPUTS = "; ".join(FIT_OUTPUT_OPTIONS)


def make_plugin(
    plugin_class: type[BaseFitPlugin] = BaseFitPlugin, **params: Any
) -> BaseFitPlugin:
    _plugin = plugin_class()
    for _key, _value in params.items():
        _plugin.set_param_value(_key, _value)
    return _plugin


def create_data(peak_indices: tuple[int, ...] = (PEAK_INDEX,)) -> Dataset:
    _x = np.arange(150) * 0.5
    _data = Dataset(
        np.ones(150), data_unit="data unit", axis_units=["ax_unit"], axis_ranges=[_x]
    )
    _peak = AMPLITUDE * Gaussian.func((1, SIGMA, 0), np.linspace(-4, 4, 15))
    for _index in peak_indices:
        _data[_index - 7 : _index + 8] += _peak
    return _data


@pytest.fixture
def data() -> Dataset:
    return create_data()


@pytest.fixture
def x(data) -> np.ndarray:
    return data.axis_ranges[0]


@pytest.fixture
def prepared_plugin(data) -> BaseFitPlugin:
    _plugin = make_plugin(fit_output="position")
    _plugin.pre_execute()
    _plugin.prepare_input_data(data)
    _plugin._fit_params = dict(
        zip(
            _plugin.config["param_labels"],
            _plugin._fitter.guess_fit_start_params(
                _plugin._data_x, _plugin._data, bg_order=0
            ),
        )
    )
    return _plugin


def test_creation():
    plugin = BaseFitPlugin()
    assert isinstance(plugin, BasePlugin)


def test_is_basic_plugin__baseclass():
    plugin = BaseFitPlugin()
    assert BaseFitPlugin.is_basic_plugin()
    assert plugin.is_basic_plugin()


def test_is_basic_plugin__subclass():
    class TestPlugin(BaseFitPlugin):
        pass

    assert not TestPlugin.is_basic_plugin()
    assert not TestPlugin().is_basic_plugin()


def test_detailed_results__empty_at_start():
    plugin = BaseFitPlugin()
    assert plugin.detailed_results == {}


@pytest.mark.parametrize(
    "output, expected",
    [
        ("position", ["position"]),
        ("position; area; FWHM", ["position", "area", "FWHM"]),
        ("position; amplitude", ["position", "amplitude"]),
    ],
)
def test_fit_outputs(output, expected):
    assert make_plugin(fit_output=output).fit_outputs == expected


def test_pre_execute():
    _plugin = make_plugin(
        fit_min_peak_height=12.4, fit_sigma_threshold=0.42, fit_bg_order=None
    )
    _plugin.pre_execute()
    assert _plugin.config["sigma_threshold"] == 0.42
    assert _plugin.config["min_peak_height"] == 12.4
    assert _plugin.config["param_labels"] == Gaussian.param_labels
    assert _plugin.config["param_bounds_low"] == Gaussian.param_bounds_low
    assert _plugin.config["param_bounds_high"] == Gaussian.param_bounds_high
    assert _plugin.config["result_shape"] == (1, 3)


@pytest.mark.parametrize(
    "bg_order, bg_labels",
    [(None, []), (0, ["background_p0"]), (1, ["background_p0", "background_p1"])],
)
def test_pre_execute__bg_order(bg_order, bg_labels):
    _plugin = make_plugin(fit_bg_order=bg_order)
    _plugin.pre_execute()
    _n_params = len(Gaussian.param_labels) + len(bg_labels)
    assert _plugin.config["param_labels"][len(Gaussian.param_labels) :] == bg_labels
    assert len(_plugin.config["param_bounds_low"]) == _n_params
    assert len(_plugin.config["param_bounds_high"]) == _n_params


@pytest.mark.parametrize(
    "limits, slice_",
    [
        ((None, None), slice(0, 150)),
        ((12, 25), slice(24, 51)),
        ((12, None), slice(24, 150)),
        ((None, 25), slice(0, 51)),
    ],
)
def test_prepare_input_data__w_limits(data, x, limits, slice_):
    _plugin = make_plugin(fit_lower_limit=limits[0], fit_upper_limit=limits[1])
    _plugin.config["settings_updated_from_data"] = True
    _plugin.prepare_input_data(data)
    assert np.all(_plugin._data == data[slice_])
    assert np.all(_plugin._data_x == x[slice_])


def test_prepare_input_data__range_too_small(data):
    _plugin = make_plugin(fit_lower_limit=10, fit_upper_limit=11)
    with pytest.raises(UserConfigError):
        _plugin.prepare_input_data(data)


def test_prepare_input_data__repeated_call_with_same_x(data):
    _plugin = make_plugin(fit_lower_limit=12, fit_upper_limit=25)
    _plugin.pre_execute()
    _plugin.prepare_input_data(data)
    _slice = _plugin.config.range_slice
    _plugin.prepare_input_data(data)
    assert _plugin.config.range_slice is _slice
    assert _plugin._data.size == 27


def test_prepare_input_data__updates_output_labels(data):
    _plugin = make_plugin(fit_output=ALL_OUTPUTS)
    _plugin.pre_execute()
    _plugin.prepare_input_data(data)
    assert _plugin.output_data_label == (
        "position / ax_unit; amplitude / cts; area / (cts * ax_unit); "
        "FWHM / ax_unit; background at peak / cts; total count intensity / cts"
    )
    assert _plugin.config["settings_updated_from_data"]


def test_prepare_input_data__updates_peak_bounds(data, x):
    plugin = BaseFitPlugin()
    plugin.pre_execute()
    plugin.prepare_input_data(data)
    assert plugin.config["param_bounds_low"][2] == np.amin(x)
    assert plugin.config["param_bounds_high"][2] == np.amax(x)


def test_prepare_input_data__bounds_already_set(data, x):
    plugin = BaseFitPlugin()
    _low, _high = x[4], x[-7]
    plugin.pre_execute()
    plugin.config["param_bounds_low"][2] = _low
    plugin.config["param_bounds_high"][2] = _high
    plugin.prepare_input_data(data)
    assert plugin.config["param_bounds_low"][2] == _low
    assert plugin.config["param_bounds_high"][2] == _high


def test_pre_execute__peak_bounds_from_params(x):
    plugin = BaseFitPlugin()
    _low, _high = x[12], x[-17]
    plugin.add_params(get_generic_param_collection("fit_peak_xlow", "fit_peak_xhigh"))
    plugin.set_param_value("fit_peak_xlow", _low)
    plugin.set_param_value("fit_peak_xhigh", _high)
    plugin.pre_execute()
    assert plugin.config["param_bounds_low"][2] == _low
    assert plugin.config["param_bounds_high"][2] == _high


def test_pre_execute__peak_bounds_params_not_set():
    plugin = BaseFitPlugin()
    plugin.add_params(get_generic_param_collection("fit_peak_xlow", "fit_peak_xhigh"))
    plugin.pre_execute()
    assert plugin.config["param_bounds_low"] == Gaussian.param_bounds_low + [-np.inf]
    assert plugin.config["param_bounds_high"] == Gaussian.param_bounds_high + [np.inf]


def test_pre_execute__fit_start_params(data):
    plugin = BaseFitPlugin()
    plugin.add_params(get_generic_param_collection("fit_peak_xstart", "fit_peak_width"))
    plugin.set_param_value("fit_peak_xstart", 12)
    plugin.set_param_value("fit_peak_width", 2.0)
    plugin.pre_execute()
    _result, _ = plugin.execute(data)
    assert _result.shape == (3,)


def test_pre_execute__fit_start_params_not_set(data):
    plugin = BaseFitPlugin()
    plugin.add_params(get_generic_param_collection("fit_peak_xstart", "fit_peak_width"))
    plugin.pre_execute()
    _result, _ = plugin.execute(data)
    assert np.all(np.isfinite(_result))


@pytest.mark.parametrize(
    "min_height, expected_valid", [(None, True), (5, True), (50, False)]
)
def test_execute__min_peak_height(data, min_height, expected_valid):
    _plugin = make_plugin(fit_min_peak_height=min_height)
    _plugin.pre_execute()
    _result, _ = _plugin.execute(data)
    assert np.all(np.isfinite(_result)) == expected_valid
    assert np.all(np.isnan(_result)) != expected_valid


@pytest.mark.parametrize("bg_order", [None, 0, 1])
def test_execute__valid_fit(data, x, bg_order):
    _plugin = make_plugin(fit_bg_order=bg_order, fit_output="position; area; FWHM")
    _plugin.pre_execute()
    _result, _kwargs = _plugin.execute(data, test_kwarg=12)
    assert _result.shape == (3,)
    assert _kwargs["test_kwarg"] == 12
    assert _kwargs["fit_func"] == "Gaussian"
    assert _kwargs["fitted_axis_unit"] == "ax_unit"
    assert "fitted_axis_label" in _kwargs
    assert abs(_kwargs["fit_params"]["center"] - x[PEAK_INDEX]) < 1
    assert abs(_kwargs["fit_params"]["amplitude"] - AMPLITUDE) < 20
    assert _result.metadata["fit_func"] == "Gaussian"
    assert "fit_residual_std" in _result.metadata
    assert ("background_p0" in _kwargs["fit_params"]) == (bg_order is not None)
    assert ("background_p1" in _kwargs["fit_params"]) == (bg_order == 1)
    assert _plugin.detailed_results == {}


def test_execute__repeated_calls_with_different_data(data):
    plugin = BaseFitPlugin()
    plugin.pre_execute()
    _res1, _ = plugin.execute(data)
    _res2, _ = plugin.execute(data * 2)
    assert np.all(np.isfinite(_res1))
    assert np.all(np.isfinite(_res2))


@pytest.mark.parametrize("bg_order", [None, 0, 1])
def test_execute__store_details(data, bg_order):
    _plugin = make_plugin(fit_bg_order=bg_order)
    _plugin.pre_execute()
    _plugin.execute(data, store_details=True)
    _details = _plugin.detailed_results[None]
    assert _details["n_plots"] == 4
    assert {_item["plot"] for _item in _details["items"]} == {0, 1, 2, 3}
    assert "fit_func: Gaussian" in _details["metadata"]
    _labels = [_item["label"] for _item in _details["items"]]
    assert ("background" in _labels) == (bg_order is not None)


def test_execute__store_details_w_multidim_input(data):
    plugin = BaseFitPlugin()
    _data = Dataset(
        np.tile(data.array, (3, 1)),
        axis_ranges=[np.arange(3), data.axis_ranges[0]],
        axis_labels=["index", "x"],
        axis_units=["", "ax_unit"],
    )
    plugin.set_param_value("process_data_dim", 1)
    plugin.pre_execute()
    _result, _ = plugin.execute(_data, store_details=True)
    assert _result.shape == (3, 3)
    assert len(plugin.detailed_results) == 3


@pytest.mark.parametrize("bg_order, n_plots", [(None, 1), (0, 2), (1, 2)])
def test_execute__invalid_peak_details(data, bg_order, n_plots):
    _plugin = make_plugin(fit_min_peak_height=500, fit_bg_order=bg_order)
    _plugin.pre_execute()
    _result, _ = _plugin.execute(data, store_details=True)
    _details = _plugin.detailed_results[None]
    assert np.all(np.isnan(_result))
    assert _details["n_plots"] == n_plots
    assert len(_details["plot_titles"]) == n_plots
    assert len(_details["plot_ylabels"]) == n_plots
    assert {_item["plot"] for _item in _details["items"]} == set(range(n_plots))
    assert any(_item["label"] == "background" for _item in _details["items"]) == (
        bg_order is not None
    )


def test_execute__details_are_reset_after_invalid_peak(data):
    _plugin = make_plugin(fit_min_peak_height=500)
    _plugin.pre_execute()
    _plugin.execute(data, store_details=True)
    assert None in _plugin.detailed_results
    _plugin.config["min_peak_height"] = None
    _plugin.execute(data)
    assert _plugin.detailed_results == {}


def test_execute__invalid_peak_without_store_details(data):
    _plugin = make_plugin(fit_min_peak_height=500)
    _plugin.pre_execute()
    _plugin.execute(data)
    assert _plugin.detailed_results == {}


@pytest.mark.parametrize(
    "output",
    [
        "position",
        "amplitude",
        "area",
        "FWHM",
        "total count intensity",
        "background at peak",
        ALL_OUTPUTS,
    ],
)
def test_create_result_dataset__valid(data, output):
    _plugin = make_plugin(fit_output=output)
    _plugin.pre_execute()
    _result, _ = _plugin.execute(data)
    assert _result.shape == (len(output.split(";")),)
    assert np.all(np.isfinite(_result))
    assert _result.axis_labels[0].startswith("0: ")


def test_create_result_dataset__no_output(data):
    _plugin = make_plugin(fit_output="no output")
    _plugin.pre_execute()
    _result, _kwargs = _plugin.execute(data)
    assert _result.shape == (1,)
    assert "fit_params" in _kwargs


def test_create_result_dataset__metadata(prepared_plugin):
    prepared_plugin._data.metadata = prepared_plugin._data.metadata | {"meta": 123}
    _result = prepared_plugin.create_result_dataset()
    assert _result.metadata["meta"] == 123
    assert _result.metadata["fit_func"] == "Gaussian"
    assert _result.metadata["fit_params"] == prepared_plugin._fit_params
    assert _result.metadata["fitted_axis_unit"] == "ax_unit"


def test_create_result_dataset__invalid_flag(prepared_plugin):
    _result = prepared_plugin.create_result_dataset(valid=False)
    assert np.all(np.isnan(_result))
    assert np.isnan(_result.metadata["fit_residual_std"])


def test_create_result_dataset__center_outside_range(prepared_plugin):
    prepared_plugin._fit_params["center"] = prepared_plugin._data_x[-1] + 10
    _result = prepared_plugin.create_result_dataset()
    assert np.all(np.isnan(_result))


def test_create_result_dataset__residual_above_threshold(prepared_plugin):
    prepared_plugin.config["sigma_threshold"] = 1e-12
    _result = prepared_plugin.create_result_dataset()
    assert np.all(np.isnan(_result))
    assert _result.metadata["fit_residual_std"] > 1e-12


def test_create_detailed_results__no_data():
    plugin = BaseFitPlugin()
    with pytest.raises(ValueError, match="without input data"):
        plugin.create_detailed_results(Dataset(np.ones(3)), (1, 1, 1))


def test_create_detailed_results__content(prepared_plugin):
    _results = prepared_plugin.create_result_dataset()
    _start = tuple(prepared_plugin._fit_params.values())
    _details = prepared_plugin.create_detailed_results(_results, _start)
    assert _details["n_plots"] == 4
    assert set(_details["plot_titles"]) == {0, 1, 2, 3}
    assert set(_details["plot_ylabels"]) == {0, 1, 2, 3}
    assert "fit params" in _details["metadata"]
    assert any(_item["label"] == "background" for _item in _details["items"])


@pytest.mark.parametrize("n_peak", [1, 2, 3])
def test_base_fit_plugin__w_diff_peaks__execute(n_peak):
    class TestPlugin(BaseFitPlugin):
        num_peaks = n_peak

    _peak_pos = (12, 42, 72)[:n_peak]
    _data = create_data(_peak_pos)
    match n_peak:
        case 1:
            _fit_func_name = "Gaussian"
        case 2:
            _fit_func_name = "Double Gaussian"
        case 3:
            _fit_func_name = "Triple Gaussian"
    _plugin = make_plugin(
        TestPlugin,
        fit_func=_fit_func_name,
        fit_output=ALL_OUTPUTS,
    )
    _plugin.pre_execute()
    _result, _kwargs = _plugin.execute(_data, store_details=True)
    if n_peak == 1:
        assert _result.axis_labels[0] == "; ".join(
            f"{_k}: {_v}" for _k, _v in enumerate(FIT_OUTPUT_OPTIONS)
        )
        assert _result.shape == (len(FIT_OUTPUT_OPTIONS),)
    else:
        assert _result.axis_labels[0] == "Peak number"
        assert _result.shape == (n_peak, len(FIT_OUTPUT_OPTIONS))
    assert np.all(np.isfinite(_result))
    assert _plugin.detailed_results[None]["n_plots"] == 4
    assert (
        sum(
            _item["label"].startswith("peak")
            for _item in _plugin.detailed_results[None]["items"]
        )
        == n_peak
    )


def test_get_parameter_config_widget():
    plugin = BaseFitPlugin()
    assert plugin.get_parameter_config_widget() is FitPluginConfigWidget


if __name__ == "__main__":
    pytest.main([__file__])
