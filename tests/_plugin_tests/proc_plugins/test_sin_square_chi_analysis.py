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
    np.tile(
        40 * np.exp(-0.5 * (np.arange(_RANGE_2THETA_RAD.size) - 75) ** 2 / 5**2),
        _CHI.size,
    ).reshape(_CHI.size, -1),
    axis_ranges=[_CHI, _RANGE_2THETA_RAD],
    axis_labels=["chi", "2theta"],
    axis_units=["deg", "rad"],
)


def test_prepare_data(plugin, fitted_data, d_spacing_unit, input_range):
    plugin.set_param_value("d_spacing_unit", d_spacing_unit)
    plugin.pre_execute()


@pytest.fixture
def fitted_data(request):
    input_range = request.param
    _FIT_PLUGIN = _REGISTRY.get_plugin_by_name("FitSinglePeak")()
    _FIT_PLUGIN.set_param_value("fit_output", "position; amplitude; FWHM")
    _FIT_PLUGIN.pre_execute()
    _label, _unit = input_range[0].split("_")
    _data = _RAW_DATA.copy()
    _data.update_axis_unit(1, _unit)
    _data.update_axis_label(1, _label)
    _data.update_axis_range(1, _RANGES[input_range[0]])
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
    _plugin.set_param_value("d_spacing_unit", "nm")
    _plugin.node_id = 42
    yield _plugin


def test_init(plugin):
    assert isinstance(plugin, ProcPlugin)


@pytest.mark.parametrize("d_spacing_unit", ["nm", "Angstrom"])
def test_pre_execute(plugin, d_spacing_unit):
    plugin.set_param_value("d_spacing_unit", d_spacing_unit)
    plugin.pre_execute()
    assert isinstance(plugin._base_name, str)
    assert (
        plugin._convert_to_d_spacing._config["unit"] == "nm"
        if d_spacing_unit == "nm"
        else "A"
    )
    for _key in ["ax_index", "new_range", "ax_indices"]:
        assert plugin._convert_to_d_spacing._config[_key] is None


@pytest.mark.parametrize("d_spacing_unit", ["nm", "Angstrom"])
@pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
def test_prepare_data(plugin, fitted_data, d_spacing_unit):
    # _label, _unit = input_range[0].split("_")
    # print(fitted_data)
    plugin.set_param_value("d_spacing_unit", d_spacing_unit)
    plugin.pre_execute()
    # fitted_data.update_axis_unit(1, _unit)
    # fitted_data.update_axis_label(1, _label)
    # fitted_data.update_axis_range(1, _RANGES[input_range[0]])
    # new_data = plugin._prepare_data(fitted_data)
    # _ref = fitted_data.axis_ranges[1] if _unit in ["nm", "A"] else _RANGES["d-spacing_" + ("nm" if d_spacing_unit == "nm" else "A")]
    # assert new_data.axis_labels[1] == "d-spacing"
    # if _unit not in ["nm", "A"]:
    #     assert new_data.axis_units[1] == "nm" if d_spacing_unit == "nm" else "A"
    # assert np.allclose(new_data.axis_ranges[1], _ref)


def test_prepare_data__invalid_data_dim(plugin):
    data = create_dataset(3)
    plugin.pre_execute()
    with pytest.raises(UserConfigError):
        plugin._prepare_data(data)


@pytest.mark.parametrize("modifier", [[0, "omega"], [1, "invalid_label"]])
def test_prepare_data__invalid_labels(plugin, fitted_data, modifier):
    fitted_data.update_axis_label(*modifier)
    plugin.pre_execute()
    with pytest.raises(UserConfigError):
        plugin._prepare_data(fitted_data)


@pytest.mark.parametrize("fitted_data", list(_RANGES.items()), indirect=True)
def test_execute(plugin, fitted_data):
    plugin.pre_execute()
    _new_data, _ = plugin.execute(fitted_data)
    print(_new_data)


if __name__ == "__main__":
    pytest.main()
