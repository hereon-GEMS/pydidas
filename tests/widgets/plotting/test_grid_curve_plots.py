# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

from copy import copy
from numbers import Integral

import numpy as np
import pytest

from pydidas.contexts import Scan
from pydidas.core import Dataset, UserConfigError
from pydidas.widgets.plotting import GridCurvePlot


_DATASETS = {
    "test1": Dataset(np.random.random((140, 3, 12))),
    "test2": Dataset(np.random.random((140, 5, 12))),
}


@pytest.fixture
def grid_plot():
    _grid_plot = GridCurvePlot()
    _grid_plot._local_scan.set_param_value("scan_dim0_n_points", 140)
    yield _grid_plot
    _grid_plot.deleteLater()


@pytest.fixture
def datasets():
    return {_k: copy(_val) for _k, _val in _DATASETS.items()}


def test_init(grid_plot):
    assert isinstance(grid_plot._local_scan, Scan)
    assert grid_plot._datasets == dict()
    assert grid_plot._yscaling == dict()
    assert grid_plot._xscaling == dict()
    assert isinstance(grid_plot._config, dict)


@pytest.mark.slow
@pytest.mark.parametrize("n_plots_hor", [2, 3, 5])
@pytest.mark.parametrize("n_plots_vert", [3, 4, 5])
def test_set_n_plots(grid_plot, n_plots_hor, n_plots_vert):
    grid_plot.n_plots_vert = n_plots_vert
    grid_plot.n_plots_hor = n_plots_hor
    assert grid_plot._config["n_hor"] == n_plots_hor
    assert grid_plot._config["n_vert"] == n_plots_vert
    assert grid_plot.n_plots == n_plots_hor * n_plots_vert


@pytest.mark.slow
@pytest.mark.parametrize("n_plots_hor", [2, 3, 5])
@pytest.mark.parametrize("n_plots_vert", [3, 4, 5])
def test_set_n_plots__w_data(grid_plot, datasets, n_plots_hor, n_plots_vert):
    grid_plot.n_plots_vert = n_plots_vert
    grid_plot.n_plots_hor = n_plots_hor
    grid_plot.set_datasets(**datasets)
    assert grid_plot._config["n_hor"] == n_plots_hor
    assert grid_plot._config["n_vert"] == n_plots_vert
    assert grid_plot.n_plots == n_plots_hor * n_plots_vert
    for _i_hor in range(n_plots_hor):
        for _i_vert in range(n_plots_vert):
            _key = f"plot_{_i_vert}_{_i_hor}"
            assert _key in grid_plot._widgets


@pytest.mark.slow
def test_set_scan(grid_plot):
    _scan = Scan()
    _scan.set_param_value("scan_title", "dummy")
    grid_plot.set_scan(_scan)
    assert id(grid_plot._local_scan) != id(_scan)
    for _key, _val in _scan.param_values.items():
        assert grid_plot._local_scan.get_param_value(_key) == _val


@pytest.mark.slow
def test_clear(grid_plot):
    grid_plot._datasets = {"test1": None, "test2": [1, 2]}
    grid_plot._yscaling = {"test1": 1, "test2": 2}
    grid_plot._xscaling = {"test1": 1, "test2": 2}
    grid_plot._config["max_index"] = 42
    grid_plot.clear()
    for _key in ["_datasets", "_yscaling", "_xscaling"]:
        assert getattr(grid_plot, _key) == {}
    assert grid_plot._config["max_index"] is None


@pytest.mark.slow
def test_set_datasets(grid_plot, datasets):
    grid_plot.set_datasets(**datasets)
    assert grid_plot._datasets == datasets
    assert grid_plot._yscaling == {k: (None, None) for k in datasets.keys()}
    assert grid_plot._xscaling == {k: (None, None) for k in datasets.keys()}
    assert grid_plot._config["max_index"] == datasets["test1"].shape[0] - 1


def test_set_datasets__no_datasets(grid_plot):
    with pytest.raises(UserConfigError):
        grid_plot.set_datasets()


def test_set_datasets__wrong_shape(grid_plot):
    with pytest.raises(UserConfigError):
        grid_plot.set_datasets(
            test1=Dataset(np.zeros((140, 3, 12))),
            test2=Dataset(np.zeros((135, 5, 10))),
        )


def test_set_datasets__wrong_dim(grid_plot):
    with pytest.raises(UserConfigError):
        grid_plot.set_datasets(
            test1=Dataset(np.zeros((140, 3, 12, 4))),
        )


@pytest.mark.slow
@pytest.mark.parametrize("direction", ["x", "y"])
def test_set_scaling(grid_plot, datasets, direction):
    grid_plot.set_datasets(**datasets)
    _setter = getattr(grid_plot, f"set_{direction}scaling")
    _values = getattr(grid_plot, f"_{direction}scaling")
    _setter("test1", (0.5, 1.5))
    assert _values["test1"] == (0.5, 1.5)
    assert _values["test2"] == (None, None)


@pytest.mark.parametrize("direction", ["x", "y"])
def test_set_scaling__missing_key(grid_plot, datasets, direction):
    grid_plot.set_datasets(**datasets)
    _setter = getattr(grid_plot, f"set_{direction}scaling")
    with pytest.raises(UserConfigError):
        _setter("test3", (0.5, 1.5))


@pytest.mark.parametrize("direction", ["x", "y"])
def test_set_scaling__wrong_scaling(grid_plot, datasets, direction):
    grid_plot.set_datasets(**datasets)
    _setter = getattr(grid_plot, f"set_{direction}scaling")
    with pytest.raises(UserConfigError):
        _setter("test1", (0.5, 1.5, 2.0))


@pytest.mark.slow
@pytest.mark.parametrize("direction", ["x", "y"])
def test_set_autoscaling(grid_plot, datasets, direction):
    grid_plot.set_datasets(**datasets)
    grid_plot._xscaling = {"test1": (1, 2), "test2": (1, 2)}
    grid_plot._yscaling = {"test1": (1, 2), "test2": (1, 2)}
    _setter = getattr(grid_plot, f"set_{direction}_autoscaling")
    _values = getattr(grid_plot, f"_{direction}scaling")
    _setter("test1")
    assert _values["test1"] == (None, None)
    assert _values["test2"] == (1, 2)


@pytest.mark.slow
@pytest.mark.parametrize(
    "start_value", ["::start::", "::end::", "::page+::", "::page-::", 1, -1, 4, -4]
)
@pytest.mark.parametrize("direction", ["vert", "hor"])
def test_change_start_index(grid_plot, datasets, start_value, direction):
    _index0 = 22
    grid_plot.set_datasets(**datasets)
    grid_plot.n_plots_hor = 3 if direction == "hor" else 2
    grid_plot.n_plots_vert = 3 if direction == "vert" else 2
    grid_plot._current_index = _index0
    grid_plot._change_start_index(start_value)
    if isinstance(start_value, Integral):
        assert grid_plot._current_index == _index0 + start_value
    else:
        if start_value == "::start::":
            assert grid_plot._current_index == 0
        elif start_value == "::end::":
            assert (
                grid_plot._current_index
                == datasets["test1"].shape[0] - grid_plot.n_plots
            )
        elif start_value == "::page+::":
            assert grid_plot._current_index == _index0 + grid_plot.n_plots
        elif start_value == "::page-::":
            assert grid_plot._current_index == _index0 - grid_plot.n_plots


if __name__ == "__main__":
    pytest.main()
