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
# An AI tool has been used to migrate the content of this file from
# using unittest to pytest.

"""
Unit tests for the BaseFitPlugin and the generic test suite for all its subclasses.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from typing import Any, ClassVar

import numpy as np
import pytest

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.core.fitting import FitFuncMeta
from pydidas.core.fitting.gaussian import Gaussian
from pydidas.core.generic_params import FIT_OUTPUT_OPTIONS, fit_multi_peak_params
from pydidas.plugins import BaseFitPlugin, BasePlugin
from pydidas.widgets.plugin_config_widgets import FitPluginConfigWidget


AMPLITUDE = 25
SIGMA = 1.25
ALL_OUTPUTS = "; ".join(FIT_OUTPUT_OPTIONS)
PEAK_INDICES = {1: (42,), 2: (12, 42), 3: (12, 42, 72)}


def create_data(peak_indices: tuple[int, ...]) -> Dataset:
    """Create a Dataset with Gaussian peaks centered at the given indices."""
    _x = np.arange(150) * 0.5
    _data = Dataset(
        np.ones(150), data_unit="data unit", axis_units=["ax_unit"], axis_ranges=[_x]
    )
    _peak = AMPLITUDE * Gaussian.func((1, SIGMA, 0), np.linspace(-4, 4, 15))
    for _index in peak_indices:
        _data[_index - 7 : _index + 8] += _peak
    return _data


class BaseFitPluginTestSuite:
    """
    Generic tests for the BaseFitPlugin and all its subclasses.

    Subclasses must set the `plugin_class` and the `fit_func` and, if the
    plugin fits more than one peak, `num_peaks`.
    """

    plugin_class: ClassVar[type[BaseFitPlugin]] = BaseFitPlugin
    fit_func: ClassVar[str] = "Gaussian"
    num_peaks: ClassVar[int] = 1

    @property
    def peak_indices(self) -> tuple[int, ...]:
        return PEAK_INDICES[self.num_peaks]

    @property
    def fitter(self) -> type:
        return FitFuncMeta.get_fitter(self.fit_func)

    @property
    def center_labels(self) -> list[str]:
        return [_l for _l in self.fitter.param_labels if _l.startswith("center")]

    def make_plugin(self, **params: Any) -> BaseFitPlugin:
        _plugin = self.plugin_class()
        _plugin.set_param_value("fit_func", self.fit_func)
        for _key, _value in params.items():
            _plugin.set_param_value(_key, _value)
        return _plugin

    def result_shape(self, n_outputs: int) -> tuple[int, ...]:
        if self.num_peaks == 1:
            return (n_outputs,)
        return (self.num_peaks, n_outputs)

    def peak_param(self, suffix: str, peak_index: int = 0) -> str:
        if self.num_peaks == 1:
            return f"fit_peak_{suffix}"
        return f"fit_peak{peak_index}_{suffix}"

    def add_missing_peak_params(self, plugin: BaseFitPlugin) -> None:
        _names = (
            ["fit_peak_xlow", "fit_peak_xhigh", "fit_peak_xstart", "fit_peak_width"]
            if self.num_peaks == 1
            else fit_multi_peak_params(self.num_peaks)
        )
        if _names[0] not in plugin.params:
            plugin.add_params(get_generic_param_collection(*_names))

    @pytest.fixture
    def data(self) -> Dataset:
        return create_data(self.peak_indices)

    @pytest.fixture
    def x(self, data) -> np.ndarray:
        return data.axis_ranges[0]

    @pytest.fixture
    def prepared_plugin(self, data) -> BaseFitPlugin:
        _plugin = self.make_plugin(fit_output="position")
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

    def test_creation(self):
        assert isinstance(self.make_plugin(), BasePlugin)

    def test_detailed_results__empty_at_start(self):
        assert self.make_plugin().detailed_results == {}

    @pytest.mark.parametrize(
        "output, expected",
        [
            ("position", ["position"]),
            ("position; area; FWHM", ["position", "area", "FWHM"]),
            ("position; amplitude", ["position", "amplitude"]),
        ],
    )
    def test_fit_outputs(self, output, expected):
        assert self.make_plugin(fit_output=output).fit_outputs == expected

    def test_get_parameter_config_widget(self):
        assert self.make_plugin().get_parameter_config_widget() is FitPluginConfigWidget

    def test_pre_execute(self):
        _plugin = self.make_plugin(
            fit_min_peak_height=12.4, fit_sigma_threshold=0.42, fit_bg_order=None
        )
        _plugin.pre_execute()
        assert _plugin.config["sigma_threshold"] == 0.42
        assert _plugin.config["min_peak_height"] == 12.4
        assert _plugin.config["param_labels"] == self.fitter.param_labels
        assert _plugin.config["param_bounds_low"] == self.fitter.param_bounds_low
        assert _plugin.config["param_bounds_high"] == self.fitter.param_bounds_high
        assert _plugin.config["result_shape"] == (self.num_peaks, 3)

    @pytest.mark.parametrize(
        "bg_order, bg_labels",
        [(None, []), (0, ["background_p0"]), (1, ["background_p0", "background_p1"])],
    )
    def test_pre_execute__bg_order(self, bg_order, bg_labels):
        _plugin = self.make_plugin(fit_bg_order=bg_order)
        _plugin.pre_execute()
        _n_fit_params = len(self.fitter.param_labels)
        _n_total = _n_fit_params + len(bg_labels)
        assert _plugin.config["param_labels"][_n_fit_params:] == bg_labels
        assert len(_plugin.config["param_bounds_low"]) == _n_total
        assert len(_plugin.config["param_bounds_high"]) == _n_total

    def test_pre_execute__peak_bounds_from_params(self, x):
        _low, _high = x[12], x[-17]
        _plugin = self.make_plugin()
        self.add_missing_peak_params(_plugin)
        _plugin.set_param_value(self.peak_param("xlow"), _low)
        _plugin.set_param_value(self.peak_param("xhigh"), _high)
        _plugin.pre_execute()
        _index = self.fitter.param_labels.index(self.center_labels[0])
        assert _plugin.config["param_bounds_low"][_index] == _low
        assert _plugin.config["param_bounds_high"][_index] == _high

    def test_pre_execute__peak_bounds_params_not_set(self):
        _plugin = self.make_plugin()
        self.add_missing_peak_params(_plugin)
        _plugin.pre_execute()
        _expected_low = self.fitter.param_bounds_low + [-np.inf]
        _expected_high = self.fitter.param_bounds_high + [np.inf]
        assert _plugin.config["param_bounds_low"] == _expected_low
        assert _plugin.config["param_bounds_high"] == _expected_high

    def test_pre_execute__fit_start_params(self, data, x):
        _plugin = self.make_plugin()
        self.add_missing_peak_params(_plugin)
        _plugin.set_param_value(self.peak_param("xstart"), x[self.peak_indices[0]])
        _plugin.set_param_value(self.peak_param("width"), SIGMA)
        _plugin.pre_execute()
        _result, _ = _plugin.execute(data)
        assert _result.shape == self.result_shape(3)
        assert np.all(np.isfinite(_result))

    def test_pre_execute__fit_start_params_not_set(self, data):
        _plugin = self.make_plugin()
        self.add_missing_peak_params(_plugin)
        _plugin.pre_execute()
        _result, _ = _plugin.execute(data)
        assert np.all(np.isfinite(_result))

    @pytest.mark.parametrize(
        "limits, slice_",
        [
            ((None, None), slice(0, 150)),
            ((12, 25), slice(24, 51)),
            ((12, None), slice(24, 150)),
            ((None, 25), slice(0, 51)),
        ],
    )
    def test_prepare_input_data__w_limits(self, data, x, limits, slice_):
        _plugin = self.make_plugin(fit_lower_limit=limits[0], fit_upper_limit=limits[1])
        _plugin.config["settings_updated_from_data"] = True
        _plugin.prepare_input_data(data)
        assert np.all(_plugin._data == data[slice_])
        assert np.all(_plugin._data_x == x[slice_])

    def test_prepare_input_data__range_too_small(self, data):
        _plugin = self.make_plugin(fit_lower_limit=10, fit_upper_limit=11)
        with pytest.raises(UserConfigError):
            _plugin.prepare_input_data(data)

    def test_prepare_input_data__repeated_call_with_same_x(self, data):
        _plugin = self.make_plugin(fit_lower_limit=12, fit_upper_limit=25)
        _plugin.pre_execute()
        _plugin.prepare_input_data(data)
        _slice = _plugin.config.range_slice
        _plugin.prepare_input_data(data)
        assert _plugin.config.range_slice is _slice
        assert _plugin._data.size == 27

    def test_prepare_input_data__updates_output_labels(self, data):
        _plugin = self.make_plugin(fit_output=ALL_OUTPUTS)
        _plugin.pre_execute()
        _plugin.prepare_input_data(data)
        assert _plugin.output_data_label == (
            "position / ax_unit; amplitude / cts; area / (cts * ax_unit); "
            "FWHM / ax_unit; background at peak / cts; total count intensity / cts"
        )
        assert _plugin.config["settings_updated_from_data"]

    def test_prepare_input_data__updates_peak_bounds(self, data, x):
        _plugin = self.make_plugin()
        _plugin.pre_execute()
        _plugin.prepare_input_data(data)
        for _label in self.center_labels:
            _index = self.fitter.param_labels.index(_label)
            assert _plugin.config["param_bounds_low"][_index] == np.amin(x)
            assert _plugin.config["param_bounds_high"][_index] == np.amax(x)

    def test_prepare_input_data__bounds_already_set(self, data, x):
        _low, _high = x[4], x[-7]
        _plugin = self.make_plugin()
        _plugin.pre_execute()
        _index = self.fitter.param_labels.index(self.center_labels[0])
        _plugin.config["param_bounds_low"][_index] = _low
        _plugin.config["param_bounds_high"][_index] = _high
        _plugin.prepare_input_data(data)
        assert _plugin.config["param_bounds_low"][_index] == _low
        assert _plugin.config["param_bounds_high"][_index] == _high

    @pytest.mark.parametrize(
        "min_height, expected_valid", [(None, True), (5, True), (50, False)]
    )
    def test_execute__min_peak_height(self, data, min_height, expected_valid):
        _plugin = self.make_plugin(fit_min_peak_height=min_height)
        _plugin.pre_execute()
        _result, _ = _plugin.execute(data)
        assert np.all(np.isfinite(_result)) == expected_valid
        assert np.all(np.isnan(_result)) != expected_valid

    @pytest.mark.parametrize("bg_order", [None, 0, 1])
    def test_execute__valid_fit(self, data, x, bg_order):
        _plugin = self.make_plugin(
            fit_bg_order=bg_order, fit_output="position; area; FWHM"
        )
        _plugin.pre_execute()
        _result, _kwargs = _plugin.execute(data, test_kwarg=12)
        _params = _kwargs["fit_params"]
        assert _result.shape == self.result_shape(3)
        assert _kwargs["test_kwarg"] == 12
        assert _kwargs["fit_func"] == self.fit_func
        assert _kwargs["fitted_axis_unit"] == "ax_unit"
        assert "fitted_axis_label" in _kwargs
        for _label, _index in zip(self.center_labels, self.peak_indices):
            assert abs(_params[_label] - x[_index]) < 1
        for _key in _params:
            if _key.startswith("amplitude"):
                assert abs(_params[_key] - AMPLITUDE) < 20
        assert _result.metadata["fit_func"] == self.fit_func
        assert "fit_residual_std" in _result.metadata
        assert ("background_p0" in _params) == (bg_order is not None)
        assert ("background_p1" in _params) == (bg_order == 1)
        assert _plugin.detailed_results == {}

    def test_execute__axis_labels(self, data):
        _plugin = self.make_plugin(fit_output=ALL_OUTPUTS)
        _plugin.pre_execute()
        _result, _ = _plugin.execute(data)
        _output_label = "; ".join(
            f"{_k}: {_v}" for _k, _v in enumerate(FIT_OUTPUT_OPTIONS)
        )
        if self.num_peaks == 1:
            assert _result.axis_labels == {0: _output_label}
        else:
            assert _result.axis_labels == {0: "Peak number", 1: _output_label}

    def test_execute__repeated_calls_with_different_data(self, data):
        _plugin = self.make_plugin()
        _plugin.pre_execute()
        _res1, _ = _plugin.execute(data)
        _res2, _ = _plugin.execute(data * 2)
        assert np.all(np.isfinite(_res1))
        assert np.all(np.isfinite(_res2))

    @pytest.mark.parametrize("bg_order", [None, 0, 1])
    def test_execute__store_details(self, data, bg_order):
        _plugin = self.make_plugin(fit_bg_order=bg_order)
        _plugin.pre_execute()
        _plugin.execute(data, store_details=True)
        _details = _plugin.detailed_results[None]
        _labels = [_item["label"] for _item in _details["items"]]
        assert _details["n_plots"] == 4
        assert {_item["plot"] for _item in _details["items"]} == {0, 1, 2, 3}
        assert f"fit_func: {self.fit_func}" in _details["metadata"]
        assert sum(_label.startswith("peak") for _label in _labels) == self.num_peaks
        assert ("background" in _labels) == (bg_order is not None)

    def test_execute__store_details_w_multidim_input(self, data):
        _data = Dataset(
            np.tile(data.array, (3, 1)),
            axis_ranges=[np.arange(3), data.axis_ranges[0]],
            axis_labels=["index", "x"],
            axis_units=["", "ax_unit"],
        )
        _plugin = self.make_plugin()
        _plugin.set_param_value("process_data_dim", 1)
        _plugin.pre_execute()
        _result, _ = _plugin.execute(_data, store_details=True)
        assert _result.shape == (3,) + self.result_shape(3)
        assert len(_plugin.detailed_results) == 3

    @pytest.mark.parametrize("bg_order, n_plots", [(None, 1), (0, 2), (1, 2)])
    def test_execute__invalid_peak_details(self, data, bg_order, n_plots):
        _plugin = self.make_plugin(fit_min_peak_height=500, fit_bg_order=bg_order)
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

    def test_execute__details_are_reset_after_invalid_peak(self, data):
        _plugin = self.make_plugin(fit_min_peak_height=500)
        _plugin.pre_execute()
        _plugin.execute(data, store_details=True)
        assert None in _plugin.detailed_results
        _plugin.config["min_peak_height"] = None
        _plugin.execute(data)
        assert _plugin.detailed_results == {}

    def test_execute__invalid_peak_without_store_details(self, data):
        _plugin = self.make_plugin(fit_min_peak_height=500)
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
    def test_create_result_dataset__valid(self, data, output):
        _plugin = self.make_plugin(fit_output=output)
        _plugin.pre_execute()
        _result, _ = _plugin.execute(data)
        assert _result.shape == self.result_shape(len(output.split(";")))
        assert np.all(np.isfinite(_result))

    def test_create_result_dataset__no_output(self, data):
        _plugin = self.make_plugin(fit_output="no output")
        _plugin.pre_execute()
        _result, _kwargs = _plugin.execute(data)
        assert _result.shape == self.result_shape(1)
        assert "fit_params" in _kwargs

    def test_create_result_dataset__metadata(self, prepared_plugin):
        prepared_plugin._data.metadata = prepared_plugin._data.metadata | {"meta": 123}
        _result = prepared_plugin.create_result_dataset()
        assert _result.metadata["meta"] == 123
        assert _result.metadata["fit_func"] == self.fit_func
        assert _result.metadata["fit_params"] == prepared_plugin._fit_params
        assert _result.metadata["fitted_axis_unit"] == "ax_unit"

    def test_create_result_dataset__invalid_flag(self, prepared_plugin):
        _result = prepared_plugin.create_result_dataset(valid=False)
        assert np.all(np.isnan(_result))
        assert np.isnan(_result.metadata["fit_residual_std"])

    def test_create_result_dataset__center_outside_range(self, prepared_plugin):
        _label = self.center_labels[0]
        prepared_plugin._fit_params[_label] = prepared_plugin._data_x[-1] + 10
        _result = prepared_plugin.create_result_dataset()
        assert np.all(np.isnan(_result))

    def test_create_result_dataset__residual_above_threshold(self, prepared_plugin):
        prepared_plugin.config["sigma_threshold"] = 1e-12
        _result = prepared_plugin.create_result_dataset()
        assert np.all(np.isnan(_result))
        assert _result.metadata["fit_residual_std"] > 1e-12

    def test_create_detailed_results__no_data(self):
        with pytest.raises(ValueError, match="without input data"):
            self.make_plugin().create_detailed_results(Dataset(np.ones(3)), (1, 1, 1))

    def test_create_detailed_results__content(self, prepared_plugin):
        _results = prepared_plugin.create_result_dataset()
        _start = tuple(prepared_plugin._fit_params.values())
        _details = prepared_plugin.create_detailed_results(_results, _start)
        assert _details["n_plots"] == 4
        assert set(_details["plot_titles"]) == {0, 1, 2, 3}
        assert set(_details["plot_ylabels"]) == {0, 1, 2, 3}
        assert "fit params" in _details["metadata"]
        assert any(_item["label"] == "background" for _item in _details["items"])


class TestBaseFitPlugin(BaseFitPluginTestSuite):
    plugin_class = BaseFitPlugin
    fit_func = "Gaussian"
    num_peaks = 1


class TestBaseFitPluginSubclassWithMultiplePeaks(BaseFitPluginTestSuite):
    class MultiPeakFitPlugin(BaseFitPlugin):
        num_peaks = 2

    plugin_class = MultiPeakFitPlugin
    fit_func = "Double Gaussian"
    num_peaks = 2


def test_is_basic_plugin__baseclass():
    assert BaseFitPlugin.is_basic_plugin()
    assert BaseFitPlugin().is_basic_plugin()


def test_is_basic_plugin__subclass():
    class TestPlugin(BaseFitPlugin):
        pass

    assert not TestPlugin.is_basic_plugin()
    assert not TestPlugin().is_basic_plugin()


if __name__ == "__main__":
    pytest.main([__file__])
