# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Tests for the DspacingSin2chiGrouping class / plugin.
"""

__author__ = "Gudrun Lotze"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"

import pytest

import numpy as np
import numpy.testing as npt
from typing import Callable
from numbers import Real
from dataclasses import dataclass

from pydidas.plugins import PluginCollection
from pydidas.plugins import ProcPlugin
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_STRESS_STRAIN

from pydidas.core import Dataset, UserConfigError

from pydidas_plugins.proc_plugins.sin2chi_grouping import ( PARAMETER_KEEP_RESULTS, 
    LABELS_SIN2CHI, LABELS_CHI, LABELS_POSITION, UNITS_NANOMETER, UNITS_ANGSTROM, UNITS_DEGREE,
    NPT_AZIM_LIMIT, S2C_TOLERANCE)

@pytest.fixture
def plugin_fixture():
    return PluginCollection().get_plugin_by_name('DspacingSin2chiGrouping')()


def test_plugin_initialization(plugin_fixture):
    # Test if the plugin is initialized correctly
    plugin = plugin_fixture
      
    assert plugin.plugin_name == "Group d-spacing according to sin^2(chi) method"
    assert plugin.basic_plugin == False
    assert plugin.plugin_type == PROC_PLUGIN
    assert plugin.plugin_subtype == PROC_PLUGIN_STRESS_STRAIN
    assert plugin.input_data_dim == -1
    assert plugin.output_data_dim == 2
    assert plugin.output_data_label == "0: position_neg, 1: position_pos, 2: Mean of 0: position_neg, 1: position_pos"
    assert plugin.new_dataset == True
    
    #check plugin is initialised with autosave option (True or 1)
    assert plugin.params.get_value(PARAMETER_KEEP_RESULTS) == True
    assert plugin.generic_params[PARAMETER_KEEP_RESULTS].value == 1
    
    
def test_plugin_inheritance():  
    plugin_obj =  PluginCollection().get_plugin_by_name('DspacingSin2chiGrouping')
    assert issubclass(plugin_obj, ProcPlugin), "Plugin is not a subclass of ProcPlugin"
    
    
@pytest.mark.parametrize(
    "input_shape, result_shape",
    [
        ((10, 20), (3, 10)),   # Test case 1
        ((20, 40), (3, 20)),  # Test case 2
        ((15, 30), (3, 15)),   # Test case 3
    ]
)



# Testing of remaining methods

def chi_gen(chi_start, chi_stop, delta_chi):
    if chi_start >= chi_stop:
        raise ValueError("chi_start has to be smaller than chi_stop")
    return np.arange(chi_start, chi_stop, delta_chi)


def predefined_metric_calculation(metric_name, chi, x, y, d0, spatial_var, phase_shift):
    """Calculate predefined metric based on name, applying spatial variation even if x is not provided."""
    # Handle spatial variation by introducing a default or random x if none is provided
    if x is None and spatial_var:
        x = np.random.uniform(0, 1)  # A random x between 0 and 5
    if metric_name == "LABELS_POSITION":
        return (
            0.2832 * np.sin(np.deg2rad(chi + phase_shift)) ** 2
            + d0
            + (0.01 * x if spatial_var else 0)
        )
    if metric_name == "area":
        return np.random.uniform(6, 37, size=len(chi)) + 0.1 * y
    if metric_name == "FWHM":
        return np.random.uniform(0.35, 0.75, size=len(chi))
    if metric_name == "background at peak":
        return np.random.uniform(2.3, 5.3, size=len(chi))
    if metric_name == "total count intensity":
        return np.random.uniform(80, 800, size=len(chi))
    return np.random.uniform(
        1.5708, 3.141, size=len(chi)
    )  # Fallback for unknown metrics


def generate_spatial_fit_res(
    y_range,
    x_range=None,
    chi_start=-175,
    chi_stop=180,
    delta_chi=10,
    fit_labels=None,
    spatial_var=True,
    phase_shift=0,
):
    """
    chi [degree]
    phase_shift [degree]
    """

    if fit_labels is None:
        fit_labels = "0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity"
    fit_labels_dict = {
        int(k.split(":")[0].strip()): k.split(":")[1].strip()
        for k in fit_labels.replace(", ", ";").split(";")
    }

    chi = chi_gen(chi_start, chi_stop, delta_chi)
    d0 = 25  # in nm

    # Determine the dimensions based on x_range
    if x_range is not None:
        result_array = np.empty(
            (len(y_range), len(x_range), len(chi), len(fit_labels_dict))
        )
    else:
        result_array = np.empty((len(y_range), len(chi), len(fit_labels_dict)))
        x_range = [None]  # Simulate the absence of x values

    # Perform calculations for each y and x, and across all metrics
    for j, y in enumerate(y_range):
        for i, x in enumerate(x_range):
            fit_results = []
            for idx in sorted(fit_labels_dict.keys()):
                metric_name = fit_labels_dict[idx]
                result = predefined_metric_calculation(
                    metric_name, chi, x, y, d0, spatial_var, phase_shift
                )
                fit_results.append(result)

            fit_results = np.array(fit_results)
            # Adjust how results are stored based on the presence of x_range
            if x is not None:
                result_array[j, i, :, :] = fit_results.T
            else:
                result_array[j, :, :] = (
                    fit_results.T
                )  # Ensure dimensionality matches expected (len(chi), len(fit_labels_dict))

    return result_array


def generate_result_array_spatial(x=np.arange(0, 5), fit_labels=None):
    y = np.arange(2, 8)  # y-range is always given

    if fit_labels == None:
        fit_labels = "0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity"

    return generate_spatial_fit_res(
        y,
        x,
        chi_start=-175,
        chi_stop=180,
        delta_chi=10,
        fit_labels=fit_labels,
        spatial_var=True,
    )
    
    
def nan_allclose(arr1, arr2, atol=1e-08):
    # Check if shapes are equal
    if arr1.shape != arr2.shape:
        return False
    # Create masks for nan values
    nan_mask1 = np.isnan(arr1)
    nan_mask2 = np.isnan(arr2)
    # Compare non-nan parts of the arrays and nan masks
    non_nan_equal = np.allclose(arr1[~nan_mask1], arr2[~nan_mask2], atol=atol)
    nan_mask_equal = np.array_equal(nan_mask1, nan_mask2)
    return non_nan_equal and nan_mask_equal


def d_spacing_simple(chi):
    return np.arange(0, len(chi))


def d_spacing_simple_nan(chi):
    d_spacing = np.arange(0, len(chi), dtype=float)
    d_spacing[1::2] = np.nan
    return d_spacing


def d_spacing_simu(chi):
    d0 = 25
    phase_shift = 70
    return 0.2832 * np.sin(np.deg2rad(chi + phase_shift)) ** 2 + d0


def d_spacing_simu_noise(chi):
    d0 = 25
    phase_shift = 70
    d_spacing = 0.2832 * np.sin(np.deg2rad(chi + phase_shift)) ** 2 + d0

    mean_value = 1
    # Define the scale parameter for the Laplace distribution
    scale = 0.03
    # Generate Laplace noise centered around the mean value
    d_spacing_noise = np.random.default_rng(seed=10).laplace(
        mean_value, scale, size=d_spacing.shape
    )
     
    return d_spacing + d_spacing_noise    


@dataclass
class S2cTestConfig:
    delta_chi: Real
    chi_start: Real
    chi_stop: Real
    d_spacing_func: Callable
    d_mean_pos: np.ndarray
    d_mean_neg: np.ndarray
    s2c_range: np.ndarray
    description: str = ""


case1 = S2cTestConfig(
    delta_chi=22.5,
    chi_start=-180,
    chi_stop=180,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array([4, 5, 6, 7, 8]),
    d_mean_neg=np.array([8, 11, 10, 9, 8]),
    s2c_range=np.array([0.0, 0.14645, 0.5, 0.85355, 1]),
)

case2 = S2cTestConfig(
    delta_chi=10,
    chi_start=0,
    chi_stop=45,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
    d_mean_neg=np.array([np.nan, np.nan, np.nan, np.nan, np.nan]),
    s2c_range=np.array([0.0, 0.03015, 0.11698, 0.25, 0.41318]),
    description="Few chi values",
)

case3 = S2cTestConfig(
    delta_chi=10,
    chi_start=-180,
    chi_stop=181,
    d_spacing_func=d_spacing_simple_nan,
    d_mean_pos=np.array(
        [9.0, np.nan, 11.0, np.nan, 13.0, np.nan, 15.0, np.nan, 17.0, np.nan]
    ),
    d_mean_neg=np.array(
        [27.0, np.nan, 25.0, np.nan, 23.0, np.nan, 21.0, np.nan, 19.0, np.nan]
    ),
    s2c_range=np.array(
        [0.0, 0.03015, 0.11698, 0.25, 0.41318, 0.58682, 0.75, 0.88302, 0.96985, 1.0]
    ),
    description="Some nan values",
)

case4 = S2cTestConfig(
    delta_chi=10,
    chi_start=-90,
    chi_stop=11,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array(
        [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 10.0, 9.0]
    ),
    d_mean_neg=np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]),
    s2c_range=np.array(
        [1.0, 0.96985, 0.88302, 0.75, 0.58682, 0.41318, 0.25, 0.11698, 0.03015, 0.0]
    ),
    description="Few values in positive slope",
)

case5 = S2cTestConfig(
    delta_chi=10,
    chi_start=-10,
    chi_stop=91,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array([2.0, 1, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]),
    d_mean_neg=np.array(
        [0.0, 1, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    ),
    s2c_range=np.array(
        [0.03015, 0.0, 0.11698, 0.25, 0.41318, 0.58682, 0.75, 0.88302, 0.96985, 1.0]
    ),
    description="Few values in negative slope",
)

case6 = S2cTestConfig(
    delta_chi=10,
    chi_start=-30,
    chi_stop=181,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array([6.0, 5.0, 4.0, 3.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]),
    d_mean_neg=np.array([9.0, 10.0, 11.0, 12.0, 17.0, 16.0, 15.0, 14.0, 13.0, 12.0]),
    s2c_range=np.array(
        [0.25, 0.11698, 0.03015, 0.0, 0.41318, 0.58682, 0.75, 0.88302, 0.96985, 1.0]
    ),
    description="Less values in negative slope",
)

case7 = S2cTestConfig(
    delta_chi=22.5,
    chi_start=-180,
    chi_stop=180,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array([4, 5, 6, 7, 8]),
    d_mean_neg=np.array([8, 11, 10, 9, 8]),
    s2c_range=np.array([0.0, 0.14645, 0.5, 0.85355, 1]),
    description="Simple case",
)

case8 = S2cTestConfig(
    delta_chi=10,
    chi_start=-180,
    chi_stop=181,
    d_spacing_func=d_spacing_simu,
    d_mean_pos=np.array(
        [
            25.25007189,
            25.27466048,
            25.2832,
            25.27466048,
            25.25007189,
            25.2124,
            25.16618858,
            25.11701142,
            25.0708,
            25.03312811,
        ]
    ),
    d_mean_neg=np.array(
        [
            25.25007189,
            25.2124,
            25.16618858,
            25.11701142,
            25.0708,
            25.03312811,
            25.00853952,
            25.0,
            25.00853952,
            25.03312811,
        ]
    ),
    s2c_range=np.array(
        [0.0, 0.03015, 0.11698, 0.25, 0.41318, 0.58682, 0.75, 0.88302, 0.96985, 1.0]
    ),
    description="A more realistic case",
)

case9 = S2cTestConfig(
    delta_chi=10,
    chi_start=0,
    chi_stop=361,
    d_spacing_func=d_spacing_simu,
    d_mean_pos=np.array(
        [
            25.25007,
            25.27466,
            25.2832,
            25.27466,
            25.25007,
            25.2124,
            25.16619,
            25.11701,
            25.0708,
            25.03313,
        ]
    ),
    d_mean_neg=np.array(  
        [
            25.25007,
            25.2124,
            25.16619,
            25.11701,
            25.0708,
            25.03313,
            25.00854,
            25.0,
            25.00854,
            25.03313,
        ]
    ),
    s2c_range=np.array(
        [0.0, 0.03015, 0.11698, 0.25, 0.41318, 0.58682, 0.75, 0.88302, 0.96985, 1.0]
    ),
    description="A more realistic case with chi ranging from 0 to 360",
)

case10 = S2cTestConfig(
    delta_chi=10,
    chi_start=0,
    chi_stop=361,
    d_spacing_func=d_spacing_simu_noise,
    d_mean_pos=np.array(
        [
            26.267365,
            26.286636,
            26.287342,
            26.274916,
            26.243111,
            26.234978,
            26.173857,
            26.127689,
            26.059813,
            26.073472,
        ]
    ),
    d_mean_neg=np.array(
        [
            26.211465,
            26.204416,
            26.137925,
            26.15062,
            26.106923,
            26.033314,
            25.993381,
            26.000767,
            26.018253,
            26.073472,
        ]
    ),
    s2c_range=np.array(
        [
            0.0,
            0.030154,
            0.116978,
            0.25,
            0.413176,
            0.586824,
            0.75,
            0.883022,
            0.969846,
            1.0,
        ]
    ),
    description="A more realistic case with chi ranging from 0 to 360 and noise added",
)


test_cases = [case1, case2, case3, case4, case5, case6, case7, case8, case9, case10]
@pytest.mark.parametrize("case", test_cases)
def test__group_d_spacing_by_chi_result(plugin_fixture, case):
    plugin = plugin_fixture
    
    chi = chi_gen(case.chi_start, case.chi_stop, case.delta_chi)
    d_spacing = Dataset(
        case.d_spacing_func(chi),
        axis_ranges={0: np.arange(0, len(chi))},
        axis_labels={0: "d_spacing"},
    )

    (d_spacing_pos, d_spacing_neg) = plugin._group_d_spacing_by_chi(
        d_spacing, chi, tolerance=S2C_TOLERANCE
    )

    assert nan_allclose(d_spacing_pos.array, case.d_mean_pos, atol=1e-8)
    assert nan_allclose(d_spacing_neg.array, case.d_mean_neg, atol=1e-8)
    assert nan_allclose(d_spacing_pos.axis_ranges[0], case.s2c_range, atol=1e-5)
    assert nan_allclose(d_spacing_neg.axis_ranges[0], case.s2c_range, atol=1e-5)
    assert d_spacing_pos.array.size == case.d_mean_pos.size
    assert d_spacing_neg.array.size == case.d_mean_neg.size
    assert (
        np.sum(np.isnan(d_spacing_pos.array)) == np.sum(np.isnan(case.d_mean_pos))
    ), f"Expected {np.sum(np.isnan(case.d_mean_pos))} NaN values, but got {np.sum(np.isnan(d_spacing_pos.array))}"
    assert (
        np.sum(np.isnan(d_spacing_neg.array)) == np.sum(np.isnan(case.d_mean_neg))
    ), f"Expected {np.sum(np.isnan(case.d_mean_neg))} NaN values, but got {np.sum(np.isnan(d_spacing_neg.array))}"
    assert (
        d_spacing_pos.array.shape == case.d_mean_pos.shape
    ), f"Expected shapes to match: {d_spacing_pos.array.shape} != {case.d_mean_pos.shape}"
    assert (
        d_spacing_neg.array.shape == case.d_mean_neg.shape
    ), f"Expected shapes to match: {d_spacing_neg.array.shape} != {case.d_mean_neg.shape}"
    

@pytest.fixture()
def base_dataset_one_fit_parameter_factory():
    def factory(unit):
        return Dataset(
            np.random.default_rng(seed=42).random((5,)),
            axis_labels={0: LABELS_CHI},
            axis_ranges={0: np.arange(5)},
            axis_units={0: UNITS_DEGREE},
            data_label=f'{LABELS_POSITION} / {unit}'
        )
    return factory
    
@pytest.mark.parametrize("unit, expected_unit", [
    (UNITS_ANGSTROM, UNITS_ANGSTROM),
    (UNITS_NANOMETER, UNITS_NANOMETER)
])    
def test__extract_and_verify_units_validation(plugin_fixture, base_dataset_one_fit_parameter_factory,
                                              unit, expected_unit):
    plugin = plugin_fixture
    test_ds = base_dataset_one_fit_parameter_factory(unit)
    
    plugin._extract_and_verify_units(test_ds)
    
    assert test_ds.axis_units[0] == UNITS_DEGREE
    assert test_ds.data_label == LABELS_POSITION
    assert test_ds.data_unit == expected_unit
    assert test_ds.axis_labels[0] == LABELS_CHI
    
    
def test__extract_and_verify_units_chi_missing(plugin_fixture, base_dataset_one_fit_parameter_factory):
    plugin = plugin_fixture
    test_ds = base_dataset_one_fit_parameter_factory(UNITS_ANGSTROM)
    test_ds.update_axis_label(0, 'delta')

    # Check that UserConfigError is raised when 'chi' is missing
    with pytest.raises(UserConfigError) as excinfo:
        plugin._extract_and_verify_units(test_ds)
    
    assert "The input dataset does not contain chi values in the axis and/or" in str(excinfo.value)
    
def test__extract_and_verify_units_chi_unit_wrong(plugin_fixture, base_dataset_one_fit_parameter_factory):
    plugin = plugin_fixture
    test_ds = base_dataset_one_fit_parameter_factory(UNITS_ANGSTROM)
    test_ds.update_axis_unit(0, 'rad')

    # Check that UserConfigError is raised when unit of 'chi' is not allowes
    with pytest.raises(UserConfigError) as excinfo:
        plugin._extract_and_verify_units(test_ds)
    
    assert "The input dataset does not contain chi values in the axis and/or" in str(excinfo.value)
    
def test__extract_and_verify_units_position_missing(plugin_fixture, base_dataset_one_fit_parameter_factory):
    plugin = plugin_fixture
    test_ds = base_dataset_one_fit_parameter_factory(UNITS_ANGSTROM)
    test_ds.data_label=f'length / {UNITS_ANGSTROM}'

    # Check that UserConfigError is raised when 'position' is missing
    with pytest.raises(UserConfigError) as excinfo:
        plugin._extract_and_verify_units(test_ds)
    
    assert f"Key '{LABELS_POSITION}' not found in data_label." in str(excinfo.value)    
    
    
def test__extract_and_verify_units_position_unit_wrong(plugin_fixture, base_dataset_one_fit_parameter_factory):
    plugin = plugin_fixture
    test_ds = base_dataset_one_fit_parameter_factory(UNITS_ANGSTROM)
    test_ds.data_label = f'{LABELS_POSITION} / m'  # Set an invalid unit for position

    # Check that ValueError is raised when the unit for 'position' is not allowed
    with pytest.raises(UserConfigError) as excinfo:
        plugin._extract_and_verify_units(test_ds)
    
    assert f"Unit 'm' is not allowed for key '{LABELS_POSITION}." in str(excinfo.value)    
    
    
    
def test__ds_slicing_1d_validation(plugin_fixture, base_dataset_one_fit_parameter_factory):
    plugin = plugin_fixture
    test_ds = base_dataset_one_fit_parameter_factory(UNITS_ANGSTROM)
    
    chi, ds = plugin._ds_slicing_1d(test_ds)
    
    np.testing.assert_array_equal(chi, np.arange(5))
    assert ds.shape == (5, )
    assert ds.axis_labels[0] == LABELS_CHI
    assert ds.axis_units[0] == UNITS_DEGREE
    assert ds.data_label == LABELS_POSITION
    assert ds.data_unit == UNITS_ANGSTROM
    assert len(ds.axis_labels) == 1
    

@pytest.mark.parametrize("chi, should_raise_error", [
    (np.arange(3000), False),  # Valid case, exactly at the limit
    (np.arange(2999), False),  # Valid case, below the limit
    (np.arange(3001), True),   # Invalid case, above the limit
])
def test__ensure_npt_azim_limit(plugin_fixture, chi, should_raise_error):
    if should_raise_error:
        with pytest.raises(UserConfigError, match=f"Number of azimuthal angles exceeds the limit of {NPT_AZIM_LIMIT}."):
            plugin_fixture._ensure_npt_azim_limit(chi)
    else:
        plugin_fixture._ensure_npt_azim_limit(chi)  # Should not raise an error
      

@pytest.fixture
def base_dataset_with_fit_labels_factory():
    def _create_dataset(fit_labels):
        y_range = np.arange(2, 7)
        result_array = generate_spatial_fit_res(y_range=y_range, fit_labels=fit_labels, phase_shift=70)
        chi = chi_gen(-175, 180, 10)
        
        return Dataset(result_array, 
                axis_labels={0: "y", 1: "chi", 2: fit_labels},
                axis_ranges={0: y_range, 1: chi, 2: np.arange(result_array.shape[-1])}
                )
    return _create_dataset

@pytest.mark.parametrize("fit_label_input, expected_chi_pos_values",
    [
        ('0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity', (1, (2,0))),
      ('0: position', (1, (2,0))),  
      ('0: area; 1: FWHM; 2: background at peak; 3: total count intensity; 4: position', (1, (2,4)))                 
  ])    
def test__chi_pos_verification_success(plugin_fixture, base_dataset_with_fit_labels_factory, fit_label_input, expected_chi_pos_values):
    plugin = plugin_fixture
    test_ds = base_dataset_with_fit_labels_factory(fit_label_input)
    
    print(test_ds.shape)
    
    (chi_pos_res, (pos_idx_res, pos_key_res)) = plugin._chi_pos_verification(test_ds)
    
    assert chi_pos_res == expected_chi_pos_values[0]
    assert pos_idx_res == expected_chi_pos_values[1][0]
    assert pos_key_res == expected_chi_pos_values[1][1]
    assert (chi_pos_res, (pos_idx_res, pos_key_res)) == expected_chi_pos_values
   
    
def test__chi_pos_verification_success_4d_array(plugin_fixture):
    plugin = plugin_fixture
    
    fit_labels = (
        "0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity"
    )

    result_array_spatial = generate_result_array_spatial()

    axis_labels = ["y", "x", "chi", fit_labels]

    ds = Dataset(result_array_spatial, axis_labels=axis_labels)
    
    chi_key, (pos_key, pos_idx) = plugin._chi_pos_verification(ds)
    
    assert chi_key == 2
    assert pos_key == 3
    assert pos_idx == 0 
    
    
def test__chi_pos_verification_missing_position(plugin_fixture):
    
    plugin = plugin_fixture
    
    fit_labels = (
        "0: energy; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity"
    )

    result_array_spatial = generate_result_array_spatial(fit_labels=fit_labels)

    axis_labels = ["y", "x", "chi", fit_labels]

    ds = Dataset(result_array_spatial, axis_labels=axis_labels)
    with pytest.raises(UserConfigError) as excinfo:
        plugin._chi_pos_verification(ds)
    assert 'Key containing "position" is missing' in str(excinfo.value)
    
def test_chi_pos_verification_wrong_input_type(plugin_fixture):
    
    plugin = plugin_fixture
    
    with pytest.raises(UserConfigError) as excinfo:
        plugin._chi_pos_verification([])  # Pass a list instead of a Dataset
    assert "Input must be an instance of Dataset." in str(excinfo.value), "Error message should indicate wrong type for Dataset."

    
def test__chi_pos_verification_all_labels_missing(plugin_fixture):
    
    plugin = plugin_fixture
    
    result_array_spatial = generate_result_array_spatial()

    # labels are missing while creating a Dataset
    ds = Dataset(result_array_spatial)
    with pytest.raises(UserConfigError) as excinfo:
        plugin._chi_pos_verification(ds)
    assert "chi is missing" in str(excinfo.value)


def test__multiple_chis_in_labels(plugin_fixture):
    plugin = plugin_fixture
    
    fit_labels = (
        "0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity"
    )
    result_array_spatial = generate_result_array_spatial()
    axis_labels = {
        0: "y",
        1: "chi",
        2: "chi",
        3: fit_labels,
    }  # 'chi' appears twice, simulated by the same value at different keys
    data_labels = "position / nm; area / (cts * nm-1); FWHM / nm; background at peak / cts; total count intensity / cts"

    ds = Dataset(result_array_spatial, axis_labels=axis_labels, data_label=data_labels)

    with pytest.raises(UserConfigError) as excinfo:
        plugin._chi_pos_verification(ds)

    assert 'Multiple "chi" found' in str(
        excinfo.value
    ), "Error message should indicate multiple 'chi' were found"


def test__position_not_at_zero(plugin_fixture):
    plugin = plugin_fixture
    
    fit_labels = (
        "1: area; 2: position; 3: FWHM; 4: background at peak; 0: total count intensity"
    )
    data_labels = "area / (cts * nm-1); position / nm; FWHM / nm; background at peak / cts; total count intensity / cts"

    result_array_spatial = generate_result_array_spatial(fit_labels=fit_labels)
    axis_labels = {0: "y", 1: "x", 2: "chi", 3: fit_labels}
    ds = Dataset(result_array_spatial, axis_labels=axis_labels, data_label=data_labels)

    _, position_key = plugin._chi_pos_verification(ds)
    assert position_key == (3, 2), "Expected position key to be (3, 2)"

def test__position_not_at_zero_3d(plugin_fixture):
    
    plugin = plugin_fixture
    
    fit_labels = (
        "1: area; 2: position; 3: FWHM; 4: background at peak; 0: total count intensity"
    )
    data_labels = "area / (cts * nm-1); position / nm; FWHM / nm; background at peak / cts; total count intensity / cts"

    results_array_spatial_3d = generate_result_array_spatial(
        None, fit_labels=fit_labels
    )
    axis_labels = {0: "y", 1: "chi", 2: fit_labels}
    ds = Dataset(
        results_array_spatial_3d, axis_labels=axis_labels, data_label=data_labels
    )
    _, position_key = plugin._chi_pos_verification(ds)
    assert position_key == (2, 2), "Expected position key to be (2, 2)"


def test__ds_slicing_type_error(plugin_fixture):
    plugin = plugin_fixture
    
    with pytest.raises(UserConfigError) as excinfo:
        plugin._ds_slicing([])  # Pass an empty list instead of a Dataset
    assert "Input must be an instance of Dataset." in str(
        excinfo.value
    ), "Error message should indicate wrong type for Dataset."
    
def test__ds_slicing_valid(plugin_fixture):
    
    plugin = plugin_fixture
    
    fit_labels = (
        "0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity"
    )
    data_labels = "position / nm; area / (cts * nm-1); FWHM / nm; background at peak / cts; total count intensity / cts"

    result_array_spatial = generate_result_array_spatial()
    axis_labels = {0: "y", 1: "x", 2: "chi", 3: fit_labels}
    axis_units = ["um", "um", "deg", ""]

    ds = Dataset(
        result_array_spatial,
        axis_labels=axis_labels,
        data_label=data_labels,
        axis_units=axis_units,
    )
    ds = ds[0, 0]
    chi, d_spacing = plugin._ds_slicing(ds)

    assert isinstance(chi, np.ndarray) and isinstance(d_spacing, Dataset)
    
    
def test__ds_slicing_beyond_bounds_v2(plugin_fixture):
    plugin = plugin_fixture
    
    """fit_label is 5: position. Shape of Dataset is 5 in the last dimension. Expected error: "Array is empty, slicing out of bounds." because 5 is out of range.
    Slice: slices [slice(None, None, None), slice(None, None, None), slice(None, None, None), slice(5, 6, None)]
    Allowed incides in last dimension range from 0 to 4.
    """
    ones_array = np.ones((3, 2, 1, 5))
    # Create the arange array and reshape it to (1, 1, 1, 5)
    arange_array = np.arange(5).reshape(1, 1, 1, 5)
    # Multiply using broadcasting
    result_array = ones_array * arange_array
    axis_units = ["um", "um", "deg", ""]
    data_label = "area / (cts * nm); FWHM / nm; background at peak / cts; total count intensity / cts; position / nm"
    axis_labels = ["y", "x", "chi", "fit_labels"]
    fit_labels = (
        "1: area; 2: FWHM; 3: background at peak; 4: total count intensity; 5: position"
    )
    ds2 = Dataset(
        result_array,
        axis_labels=axis_labels,
        data_label=data_label,
        axis_units=axis_units,
    )
    ds2.update_axis_label(3, fit_labels)

    chi_key, (pos_key, pos_idx) = plugin._chi_pos_verification(ds2)
    # Position has a key of 5
    assert pos_idx == 5
    
    with pytest.raises(ValueError) as excinfo:
        plugin._ds_slicing(ds2)
    assert "Array is empty, slicing out of bounds." in str(
        excinfo.value
    ), "Error message should indicate that slicing beyond bounds."
    

def test__ds_slicing_dimension_mismatch(plugin_fixture):
    
    plugin = plugin_fixture
    
    fit_labels = (
        "0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity"
    )
    data_labels = "position / nm; area / (cts * nm-1); FWHM / nm; background at peak / cts; total count intensity / cts"
    result_array_spatial = generate_result_array_spatial()
    axis_labels = {0: "y", 1: "x", 2: "chi", 3: fit_labels}
    axis_units = ["um", "um", "deg", ""]
    ds = Dataset(
        result_array_spatial,
        axis_labels=axis_labels,
        data_label=data_labels,
        axis_units=axis_units,
    )

    with pytest.raises(ValueError) as excinfo:
        test = plugin._ds_slicing(ds)
    assert "Dimension mismatch" in str(
        excinfo.value
    ), "Error message should indicate that d_spacing has a larger dimension."



def test__ds_slicing_dimension_mismatch_3d(plugin_fixture):
    plugin = plugin_fixture
    
    
    fit_labels = "0: position"
    data_labels = "position / nm"
    results_array_spatial_3d = generate_result_array_spatial(
        None, fit_labels=fit_labels
    )
    axis_labels = {0: "y", 1: "chi", 2: fit_labels}
    axis_units = ["um", "deg", ""]
    ds_3d = Dataset(
        results_array_spatial_3d,
        axis_labels=axis_labels,
        data_label=data_labels,
        axis_units=axis_units,
    )
    with pytest.raises(ValueError) as excinfo:
        plugin._ds_slicing(ds_3d)
    assert "Dimension mismatch" in str(
        excinfo.value
    ), "Error message should indicate that d_spacing has a larger dimension."

def test__extract_d_spacing_valid(plugin_fixture):
    plugin = plugin_fixture
    
    fit_labels = (
        "0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity"
    )
    data_labels = "position / nm; area / (cts * nm-1); FWHM / nm; background at peak / cts; total count intensity / cts"
    result_array_spatial = generate_result_array_spatial()
    axis_labels = {0: "y", 1: "x", 2: "chi", 3: fit_labels}
    axis_units = ["um", "um", "deg", ""]
    ds = Dataset(
        result_array_spatial,
        axis_labels=axis_labels,
        data_label=data_labels,
        axis_units=axis_units,
    )
    pos_key_exp = 3
    pos_idx_exp = 0
    ds_expected = ds[:, :, :, pos_idx_exp : pos_idx_exp + 1].squeeze()   
    
    assert np.array_equal(plugin._extract_d_spacing(ds, pos_key_exp, pos_idx_exp), ds_expected)
    
def test__idx_s2c_grouping_basic(plugin_fixture):
    plugin = plugin_fixture
    
    chi = np.arange(-175, 185, 10)
    n_components, s2c_labels = plugin._idx_s2c_grouping(chi, tolerance=1e-3)
    assert n_components > 0
    assert len(s2c_labels) == len(chi)
    
    
def test__idx_s2c_grouping_tolerance_effectiveness(plugin_fixture):
    plugin = plugin_fixture
    
    chi = np.array([0, 0.001, 0.002, 0.003])
    n_components, labels = plugin._idx_s2c_grouping(chi, tolerance=0.00001)
    assert (
        n_components == 1
    )  # All should be in one group due to small variation and tight tolerance

def test__idx_s2c_grouping_type_error(plugin_fixture):
    plugin = plugin_fixture
    
    with pytest.raises(TypeError):
        plugin._idx_s2c_grouping([0, 30, 60])  # Passing a list instead of np.ndarray


def test__idx_s2c_grouping_empty_array(plugin_fixture):
    plugin = plugin_fixture
    
    chi = np.array([])
    n_components, labels = plugin._idx_s2c_grouping(chi)
    assert n_components == 0  # No components should be found
    assert len(labels) == 0  # No labels should be assigned
    
def test__idx_s2c_grouping_extreme_values(plugin_fixture):
    plugin = plugin_fixture
    
    chi = np.array([-360, 360])
    n_components, labels = plugin._idx_s2c_grouping(chi)
    assert n_components == 1  # Extreme but equivalent values should be grouped together
    
    
def test__idx_s2c_grouping_very_small_array(plugin_fixture):
    plugin = plugin_fixture
    
    chi = np.array([0])
    n_components, labels = plugin._idx_s2c_grouping(chi)
    assert n_components == 1  # Single value should form one group
    assert len(labels) == 1  # One label for the one value


def test__group_d_spacing_by_chi_basic(plugin_fixture):
    plugin = plugin_fixture
    
    
    chi = np.arange(-175, 185, 10)
    d_spacing = Dataset(
        np.arange(0, len(chi)),
        axis_ranges={0: chi},
        axis_labels={0: "chi"},
        data_label="position",
    )
    d_spacing_pos, d_spacing_neg = plugin._group_d_spacing_by_chi(
        d_spacing, chi, tolerance=1e-3
    )
    assert d_spacing_pos.size == d_spacing_neg.size
    assert d_spacing_pos.size > 0
    assert d_spacing_neg.size > 0
    assert d_spacing_pos.axis_ranges[0].size == d_spacing_neg.axis_ranges[0].size
    assert d_spacing_pos.data_label == f"{ d_spacing.data_label}_pos"
    assert d_spacing_neg.data_label == f"{ d_spacing.data_label}_neg"
    assert d_spacing_pos.axis_labels[0] == LABELS_SIN2CHI
    assert d_spacing_neg.axis_labels[0] == LABELS_SIN2CHI


def test__group_d_spacing_by_chi_type_error(plugin_fixture):
    plugin = plugin_fixture
    
    
    chi = np.arange(-175, 185, 10)
    d_spacing = Dataset(
        np.arange(0, len(chi)), axis_ranges={0: chi}, axis_labels={0: "chi"}
    )
    with pytest.raises(TypeError) as excinfo:
        plugin._group_d_spacing_by_chi(d_spacing, [], tolerance=1e-4)
    assert "Chi has to be of type np.ndarray" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plugin._group_d_spacing_by_chi([], chi, tolerance=1e-4)
    assert "d_spacing has to be of type Pydidas Dataset" in str(excinfo.value)
    
def test__group_d_spacing_by_chi_len_unique_groups(plugin_fixture):
    plugin = plugin_fixture
    
    
    delta_chi = 10
    chi_start = -180
    chi_stop = 181
    chi = chi_gen(chi_start, chi_stop, delta_chi)
    d_spacing = Dataset(
        np.arange(0, len(chi), dtype=float),
        axis_ranges={0: np.arange(0, len(chi))},
        axis_labels={0: "chi"},
        data_label="d_spacing",
    )

    # unique groups:
    # dependent only on chi
    # idx_s2c_grouping is tested separately
    _, s2c_labels = plugin._idx_s2c_grouping(chi, tolerance=1e-4)
    s2c_unique_labels = np.unique(s2c_labels)

    (d_spacing_pos, d_spacing_neg) = plugin._group_d_spacing_by_chi(
        d_spacing, chi, tolerance=1e-4
    )

    # Check the lengths of the output arrays
    assert (
        len(s2c_unique_labels) == d_spacing_pos.size
    ), f"Expected {len(s2c_unique_labels)}, got {d_spacing_pos.size}"
    assert (
        len(s2c_unique_labels) == d_spacing_pos.axis_ranges[0].size
    ), f"Expected {len(s2c_unique_labels)}, got {d_spacing_pos.axis_ranges[0].size}"
    assert (
        len(s2c_unique_labels) == d_spacing_neg.size
    ), f"Expected {len(s2c_unique_labels)}, got {d_spacing_neg.size}"
    assert (
        len(s2c_unique_labels) == d_spacing_neg.axis_ranges[0].size
    ), f"Expected {len(s2c_unique_labels)}, got {d_spacing_neg.axis_ranges[0].size}"
    

test_cases = [case9]    
@pytest.mark.parametrize("case", test_cases)
def test__group_d_spacing_by_chi_second_validation_method(plugin_fixture, case):
    """
    A test function to validate the `group_d_spacing_by_chi` function via the via a different approach.

    This test performs the following steps:
    1. Initializes chi values and a Dataset instance for d_spacing using the provided case configuration.
    2. Uses the second validation method to calculate mean d_spacing values for positive and negative slopes.
    3. Uses the original `group_d_spacing_by_chi` function to calculate mean d_spacing values for positive and negative slopes.
    4. Compares the results from both methods with each other and with the expected mean values provided in the case configuration.
    5. Asserts that all elements in the comparisons are close within the specified tolerances.

    Parameters
    ----------
    case : S2cTestConfig
        The test configuration containing the parameters and expected values for the test case.

    Raises
    ------
    AssertionError
        If any of the comparisons fail, indicating that the methods do not produce close results.

    """

    def group_d_spacing_by_chi_second_validation(d_spacing, chi, tolerance=1e-4):
        """
        Group d_spacing values by chi using a secondary validation method.

        Parameters
        ----------
        d_spacing : Dataset
            The dataset containing d_spacing values.
        chi : np.ndarray
            The array of chi values.
        tolerance : float, optional
            The tolerance value for grouping by chi, by default 1e-4.

        Returns
        -------
        tuple
            A tuple containing two arrays: mean d_spacing values for positive slopes and negative slopes.

        Raises
        ------
        TypeError
            If chi is not an np.ndarray or d_spacing is not a Pydidas Dataset.
        """

        if not isinstance(chi, np.ndarray):
            raise TypeError("Chi has to be of type np.ndarray")

        if not isinstance(d_spacing, Dataset):
            raise TypeError("d_spacing has to be of type Pydidas Dataset.")

        n_components, s2c_labels = plugin._idx_s2c_grouping(chi, tolerance=tolerance)
        s2c = np.sin(np.deg2rad(chi)) ** 2
        s2c_unique_labels = np.unique(s2c_labels)
        unique_groups = np.unique(s2c_labels)

        # Calculate first derivative
        first_derivative = np.gradient(s2c, edge_order=2)

        # Define the threshold for being "close to zero", i.e. where is the slope=0
        zero_threshold = 1e-4
        # Categorize the values of the first_derivative
        # 1 is close to zero
        # 2 is positive
        # 0 is negative
        categories = np.zeros_like(first_derivative, dtype=int)
        categories[first_derivative > zero_threshold] = 2
        categories[first_derivative < -zero_threshold] = 0
        categories[
            (first_derivative >= -zero_threshold) & (first_derivative <= zero_threshold)
        ] = 1

        # Dynamic length of matrices
        max_len = 0
        for group in unique_groups:
            mask_pos = (s2c_labels == group) & ((categories == 2) | (categories == 1))
            mask_neg = (s2c_labels == group) & ((categories == 0) | (categories == 1))

            d_pos = d_spacing[mask_pos]
            d_neg = d_spacing[mask_neg]

            len_d_pos = len(d_pos)
            len_d_neg = len(d_neg)

            current_max = max(len_d_pos, len_d_neg)

            if current_max > max_len:
                max_len = current_max

        # array creation with initialization
        data_pos = np.full(
            (n_components, max_len + 2), np.nan
        )  # group, max value for d_spacing for pos slope, average = max_len+2
        data_neg = np.full((n_components, max_len + 2), np.nan)
        data = np.full((n_components, 2 * max_len + 1), np.nan)

        # Chi indices
        idx_chi = np.arange(0, len(chi), 1)

        for group in unique_groups:
            mask_pos = (s2c_labels == group) & ((categories == 2) | (categories == 1))
            mask_neg = (s2c_labels == group) & ((categories == 0) | (categories == 1))

            chi_combi_pos = chi[mask_pos]
            chi_combi_neg = chi[mask_neg]

            d_pos = d_spacing[mask_pos]
            d_neg = d_spacing[mask_neg]

            data_pos[group, 0] = group
            data_neg[group, 0] = group
            data[group, 0] = group

            # Check the length of d_pos to see if it should be assigned
            if len(d_pos) > 0:
                data_pos[group, 1 : len(d_pos) + 1] = d_pos
                # print(d_pos.array, np.nanmean(data_pos[group, 1:len(d_pos)+1]))
                data_pos[group, -1] = np.nanmean(data_pos[group, 1 : len(d_pos) + 1])
                data[group, 1 : len(d_pos) + 1] = d_pos

            # Check the length of d_neg to see if it should be assigned
            if len(d_neg) > 0:
                data_neg[group, 1 : len(d_neg) + 1] = d_neg
                data_neg[group, -1] = np.nanmean(data_neg[group, 1 : len(d_neg) + 1])
                data[group, -len(d_neg) :] = d_neg

        return (data_pos[:, -1].T, data_neg[:, -1].T)

    # Initialisation
    
    plugin = plugin_fixture
    
    
    chi = chi_gen(case.chi_start, case.chi_stop, case.delta_chi)
    d_spacing = Dataset(
        case.d_spacing_func(chi),
        axis_ranges={0: np.arange(0, len(chi))},
        axis_labels={0: "d_spacing"},
    )

    # Calculate the expected values
    (data_pos_mean, data_neg_mean) = group_d_spacing_by_chi_second_validation(
        d_spacing, chi, tolerance=1e-4
    )
    (d_spacing_pos, d_spacing_neg) = plugin._group_d_spacing_by_chi(
        d_spacing, chi, tolerance=1e-4
    )

    # Comparison of both calculation methods and, finally, with the expected values
    res_pos_1 = np.isclose(
        data_pos_mean, d_spacing_pos.array, equal_nan=True, atol=1e-8, rtol=1e-5
    )
    res_pos_2 = np.isclose(
        d_spacing_pos.array, case.d_mean_pos, equal_nan=True, atol=1e-8, rtol=1e-5
    )
    res_pos_combined = np.logical_and(res_pos_1, res_pos_2)

    # Assertions to ensure all elements are close
    assert np.all(
        res_pos_1
    ), f"data_pos_mean and d_spacing_pos are not close: {res_pos_1}"
    assert np.all(
        res_pos_2
    ), f"d_spacing_pos and case.d_mean_pos are not close: {res_pos_2}"
    # Assertions to ensure all elements are close
    assert np.all(
        res_pos_combined
    ), f"data_pos_mean, d_spacing_pos.array, and expected case.d_mean_pos are not close: {res_pos_combined}"

    # Same for negative slopes
    res_neg_1 = np.isclose(
        data_neg_mean, d_spacing_neg.array, equal_nan=True, atol=1e-8, rtol=1e-5
    )
    res_neg_2 = np.isclose(
        d_spacing_neg.array, case.d_mean_neg, equal_nan=True, atol=1e-8, rtol=1e-5
    )
    res_neg_combined = np.logical_and(res_neg_1, res_neg_2)

    assert np.all(
        res_neg_1
    ), f"data_neg_mean and d_spacing_neg are not close: {res_neg_1}"
    assert np.all(
        res_neg_2
    ), f"d_spacing_neg and case.d_mean_neg are not close: {res_neg_2}"
    assert np.all(
        res_neg_combined
    ), f"data_neg_mean, d_spacing_neg.array, and expected case.d_mean_neg are not close: {res_neg_combined}"
    
    
@dataclass
class DSpacingTestConfig:
    d_spacing_pos: Dataset
    d_spacing_neg: Dataset
    ds_expected: Dataset


ds_case1 = DSpacingTestConfig(
    d_spacing_pos=Dataset(
        np.array([1.0, 2.0, 3.0]),
        axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        axis_labels={0: LABELS_SIN2CHI},
    ),
    d_spacing_neg=Dataset(
        np.array([3.0, 2.0, 1.0]),
        axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        axis_labels={0: LABELS_SIN2CHI},
    ),
    ds_expected=Dataset(
        np.vstack((np.array([1.0, 2.0, 3.0]), np.array([3.0, 2.0, 1.0]))),
        axis_ranges={0: np.arange(2), 1: np.array([0.1, 0.2, 0.3])},
        axis_labels={0: "0: d-, 1: d+", 1:LABELS_SIN2CHI},
        data_label="d_spacing",
    ),
)



@pytest.mark.parametrize(
    "d_spacing_pos, d_spacing_neg, expect_error",
    [
        (np.arange(0, 10), np.arange(0, 10)[::-1], True),  # Both inputs are non-Dataset
        (ds_case1.d_spacing_pos, np.arange(0, 10), True),  # One input is non-Dataset
        (
            ds_case1.d_spacing_pos,
            ds_case1.d_spacing_neg,
            False,
        ),  # Both inputs are Dataset
        (ds_case1.d_spacing_pos, [], True),  # One input is empty list
        ([], ds_case1.d_spacing_pos, True),  # One input is empty list
    ],
)
def test__combine_sort_d_spacing_pos_neg_type_error(plugin_fixture,
    d_spacing_pos, d_spacing_neg, expect_error
):
    plugin=plugin_fixture    
    
    if expect_error:
        with pytest.raises(TypeError):
            plugin._combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg)
    else:
        result = plugin._combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg)
        assert isinstance(result, Dataset), "Expected Dataset object as output"
        
        
        
def test__combine_sort_d_spacing_pos_neg_axis_labels_mismatch(plugin_fixture):
    plugin= plugin_fixture
    
    d_spacing_pos = Dataset(
        np.array([1.0, 2.0, 3.0]),
        axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        axis_labels={0: LABELS_SIN2CHI},
    )
    d_spacing_neg = Dataset(
        np.array([3.0, 2.0, 1.0]),
        axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        axis_labels={0: "different_label"},
    )

    with pytest.raises(ValueError, match="Axis labels do not match."):
        plugin._combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg)


def test__combine_sort_d_spacing_pos_neg_axis_ranges_mismatch_shape(plugin_fixture):
    plugin= plugin_fixture
    
    d_spacing_pos = Dataset(
        np.array([1.0, 2.0, 3.0]),
        axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        axis_labels={0: LABELS_SIN2CHI},
    )
    d_spacing_neg = Dataset(
        np.array([3.0, 2.0, 1.0, 0.0]),
        axis_ranges={0: np.array([0.1, 0.2, 0.3, 0.4])},
        axis_labels={0: LABELS_SIN2CHI},
    )

    with pytest.raises(ValueError, match="Axis ranges do not have the same length."):
        plugin._combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg)
        
        
def test_combine_sort_d_spacing_pos_neg_valid(plugin_fixture):
    plugin= plugin_fixture
    
    d_spacing_pos = Dataset(
        np.array([1.0, 2.0, 3.0]),
        axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        axis_labels={0: LABELS_SIN2CHI},
        data_label="position_pos",
    )
    d_spacing_neg = Dataset(
        np.array([3.0, 2.0, 1.0]),
        axis_ranges={0: np.array([0.1, 0.2, 0.3])},
        axis_labels={0: LABELS_SIN2CHI},
        data_label="position_neg",
    )

    result = plugin._combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg)
    assert np.array_equal(result.array, np.array([[3.0, 2.0, 1.0], [1.0, 2.0, 3.0]]))
    assert np.array_equal(result.axis_ranges[1], np.array([0.1, 0.2, 0.3]))
    assert result.axis_labels == {0: "0: d-, 1: d+", 1: LABELS_SIN2CHI}
    assert result.data_label == "0: position_neg, 1: position_pos"

def test_combine_sort_d_spacing_pos_neg_stablesort(plugin_fixture):
    plugin= plugin_fixture
        
    # Create datasets with the same sin2chi values but in different unsorted order
    sin2chi_values = np.array([0.3, 0.1, 0.2])

    d_spacing_pos = Dataset(
        np.array([3.0, 1.0, 2.0]),
        axis_ranges={0: sin2chi_values},
        axis_labels={0: LABELS_SIN2CHI},
    )
    d_spacing_neg = Dataset(
        np.array([2.0, 3.0, 1.0]),
        axis_ranges={0: sin2chi_values},
        axis_labels={0: LABELS_SIN2CHI},
    )

    result = plugin._combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg)

    # Check that the sin2chi axis has been sorted
    expected_sin2chi_sorted = np.array([0.1, 0.2, 0.3])
    np.testing.assert_array_equal(
        result.axis_ranges[1],
        expected_sin2chi_sorted,
        err_msg="sin2chi values are not correctly sorted in ascending order.",
    )

    # Check that the d_spacing values have been sorted according to the sorted sin2chi values
    expected_d_spacing_combined = np.array([[3.0, 1.0, 2.0], [1.0, 2.0, 3.0]])
    np.testing.assert_array_equal(
        result.array,
        expected_d_spacing_combined,
        err_msg="d_spacing values are not correctly sorted according to sorted sin2chi values.",
    )
    
    
def test_combine_sort_d_spacing_pos_neg_with_nan(plugin_fixture):
    plugin= plugin_fixture
    
    # Create datasets with the same sin2chi values but with NaN values in d_spacing
    sin2chi_values = np.array([0.3, 0.1, 0.2])

    d_spacing_pos = Dataset(
        np.array([3.0, np.nan, 2.0]),
        axis_ranges={0: sin2chi_values},
        axis_labels={0: LABELS_SIN2CHI},
    )
    d_spacing_neg = Dataset(
        np.array([2.0, 3.0, np.nan]),
        axis_ranges={0: sin2chi_values},
        axis_labels={0: LABELS_SIN2CHI},
    )

    result = plugin._combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg)

    # Check that the sin2chi axis has been sorted
    expected_sin2chi_sorted = np.array([0.1, 0.2, 0.3])
    np.testing.assert_array_equal(
        result.axis_ranges[1],
        expected_sin2chi_sorted,
        err_msg="sin2chi values are not correctly sorted in ascending order.",
    )

    # Check that the d_spacing values have been sorted according to the sorted sin2chi values
    expected_d_spacing_combined = np.array([[3.0, np.nan, 2.0], [np.nan, 2.0, 3.0]])
    np.testing.assert_array_equal(
        result.array,
        expected_d_spacing_combined,
        err_msg="d_spacing values are not correctly sorted according to sorted sin2chi values, especially with NaN values.",
    )


@pytest.fixture
def d_spacing_datasets():
    d_spacing_pos = Dataset(
        axis_labels={0: LABELS_SIN2CHI},
        axis_ranges={
            0: np.array(
                [
                    0.75,
                    0.883022,
                    0.969846,
                    1.0,
                    0.586824,
                    0.413176,
                    0.25,
                    0.116978,
                    0.030154,
                    0.0,
                ]
            )
        },
        axis_units={0: ""},
        metadata={},
        data_unit="nm",
        data_label="position_pos",
        array=np.array(
            [
                26.201953,
                26.151003,
                26.102181,
                26.063213,
                26.249156,
                26.267693,
                26.324825,
                26.323819,
                26.311725,
                26.281715,
            ]
        ),
    )
    d_spacing_neg = Dataset(
        axis_labels={0: LABELS_SIN2CHI},
        axis_ranges={
            0: np.array(
                [
                    0.75,
                    0.883022,
                    0.969846,
                    1.0,
                    0.586824,
                    0.413176,
                    0.25,
                    0.116978,
                    0.030154,
                    0.0,
                ]
            )
        },
        axis_units={0: ""},
        metadata={},
        data_unit="nm",
        data_label="position_neg",
        array=np.array(
            [
                26.041096,
                26.037526,
                26.036219,
                26.063213,
                26.074632,
                26.099187,
                26.171528,
                26.206706,
                26.238491,
                26.281715,
            ]
        ),
    )

    d_spacing_combined = Dataset(
        axis_labels={0: "0: d-, 1: d+", 1: LABELS_SIN2CHI},
        axis_ranges={
            0: np.array([0, 1]),
            1: np.array(
                [
                    0.0,
                    0.030154,
                    0.116978,
                    0.25,
                    0.413176,
                    0.586824,
                    0.75,
                    0.883022,
                    0.969846,
                    1.0,
                ]
            ),
        },
        axis_units={0: "", 1: ""},
        metadata={},
        data_unit="nm",
        data_label="0: position_neg, 1: position_pos",
        array=np.array(
            [
                [
                    26.281715,
                    26.238491,
                    26.206706,
                    26.171528,
                    26.099187,
                    26.074632,
                    26.041096,
                    26.037526,
                    26.036219,
                    26.063213,
                ],
                [
                    26.281715,
                    26.311725,
                    26.323819,
                    26.324825,
                    26.267693,
                    26.249156,
                    26.201953,
                    26.151003,
                    26.102181,
                    26.063213,
                ],
            ]
        ),
    )
    return d_spacing_pos, d_spacing_neg, d_spacing_combined

def test_combine_sort_d_spacing_pos_neg_explicit(plugin_fixture, d_spacing_datasets):
    plugin=plugin_fixture
    
    
    d_spacing_pos, d_spacing_neg, d_spacing_combined = d_spacing_datasets
    d_spacing_combined_cal =plugin._combine_sort_d_spacing_pos_neg(
        d_spacing_pos, d_spacing_neg
    )

    assert np.allclose(d_spacing_combined_cal.array, d_spacing_combined.array)
    assert np.allclose(
        d_spacing_combined_cal.axis_ranges[1], d_spacing_combined.axis_ranges[1]
    )
    assert d_spacing_combined_cal.data_label == d_spacing_combined.data_label
    assert d_spacing_combined_cal.data_unit == d_spacing_combined.data_unit
    

# Parameterized test for TypeError with list and 2D numpy array inputs
@pytest.mark.parametrize(
    "invalid_input",
    [
        [1.0, 2.0],  # List input
        np.array([[1.0, 2.0]]),  # 2D numpy array input
    ],
)
def test__create_final_result_sin2chi_method_type_error(plugin_fixture, invalid_input):
    plugin = plugin_fixture
    
    with pytest.raises(
        TypeError, match="Input must be an instance of Dataset."
    ):
        plugin._create_final_result_sin2chi_method(invalid_input)


@pytest.fixture
def d_spacing_combined_fixture():
    # Mocking a Dataset instance with sample data
    data = np.array([[1, 2, np.nan], [4, 5, 6]])  # Example data
       
    d_spacing_combined = Dataset(data,
        axis_ranges={0:  np.arange(2) , 1: np.array([0.1, 0.2, 0.3])},  # Example sin^2(chi) values
        axis_labels={0: "0: d-, 1: d+", 1: LABELS_SIN2CHI},
        axis_units={0: "", 1: ""},
        data_unit="nm",
        data_label="d_spacing"
    )
    return d_spacing_combined


def test__create_final_result_sin2chi_method_valid_input(plugin_fixture, d_spacing_combined_fixture):
    
    plugin = plugin_fixture
    #dummy input shape: 3 chi-values and 5 fit results
    # This is currently required due to pre-allocation requirements in pydidas, dynamic allocation is not yet supported
    plugin._config["input_shape"] = (3, 5)
    
    
    # Calculation
    result = plugin._create_final_result_sin2chi_method(d_spacing_combined_fixture)

    # Verify the shape and content of the returned datasets
    assert result.shape == (3, 3), "Average dataset shape is incorrect"
    assert (result.axis_labels[0] == '0: d-, 1: d+, 2: d_mean'), "Expected axis_labels[0] is '0: d-, 1: d+, 2: d_mean'."
    
    assert (
        result.axis_labels[1] == LABELS_SIN2CHI
    ), f"Expected axis_labels[1] dataset axis label is {LABELS_SIN2CHI}."
    assert (
        result.data_unit == d_spacing_combined_fixture.data_unit
    ), f'Resulting dataset data unit is incorrect. Expected unit: {d_spacing_combined_fixture.data_unit}'
    assert (
        result.data_label == d_spacing_combined_fixture.data_label
    ), f'Resulting dataset data label is incorrect. Expected data label: {d_spacing_combined_fixture.data_label}'
    

def test__create_final_result_sin2chi_method_accuracy(plugin_fixture, d_spacing_combined_fixture):
    
    plugin = plugin_fixture
    # This is currently required due to pre-allocation requirements in pydidas, dynamic allocation is not yet supported
    plugin._config["input_shape"] = (3, 5)
    
    
    result = plugin._create_final_result_sin2chi_method(d_spacing_combined_fixture)

    expected_avg = np.vstack((d_spacing_combined_fixture.array, [2.5, 3.5, np.nan]))  # Assuming mean calculation ignores np.nan
    

    np.testing.assert_allclose(
        result.array,
        expected_avg,
        rtol=1e-6,
        atol=1e-8,
        equal_nan=True,
        err_msg="Result calculation is incorrect",
    )
    
def test__create_final_result_sin2chi_method_with_nan_explicit(plugin_fixture, d_spacing_combined_fixture):
    plugin = plugin_fixture
    # This is currently required due to pre-allocation requirements in pydidas, dynamic allocation is not yet supported
    plugin._config["input_shape"] = (3, 5)
    
        
    d_spacing_combined_fixture.array[0, 1] = np.nan
    result = plugin._create_final_result_sin2chi_method(d_spacing_combined_fixture)
    print(result.array)

    expected_avg = np.vstack((d_spacing_combined_fixture.array, [2.5, np.nan, np.nan]))  # Assuming mean calculation ignores np.nan
    
    
    np.testing.assert_array_equal(
        result.array, expected_avg, "Resulting calculation is incorrect"
    )
    
    
def test__create_final_result_sin2chi_method_precision(plugin_fixture, d_spacing_datasets):
    """ 
    Test to check the precision in create_final_result_sin2chi_method
    """
    
    _, _, d_spacing_combined = d_spacing_datasets
    
    plugin = plugin_fixture

    expected = Dataset(
        axis_ranges={
            0: np.arange(3),
            1: np.array(
                [
                    0.0,
                    0.030154,
                    0.116978,
                    0.25,
                    0.413176,
                    0.586824,
                    0.75,
                    0.883022,
                    0.969846,
                    1.0,
                ]
            )
        },
        axis_labels = {0: "0: d-, 1: d+, 2: d_mean", 1: LABELS_SIN2CHI},
        metadata={},
        data_unit="nm",
        data_label='d_spacing',
        array=np.vstack((d_spacing_combined, np.array(
            [
                26.281715,
                26.275108,
                26.265263,
                26.248177,
                26.18344,
                26.161894,
                26.121524,
                26.094265,
                26.0692,
                26.063213
            ]
            )
        )
    )
    )
        
    #Calculation for test
    result = plugin._create_final_result_sin2chi_method(d_spacing_combined)

    assert np.allclose(result.array, expected.array, atol=1e-8) 
    assert np.allclose(result.axis_ranges[1], expected.axis_ranges[1], atol=1e-8) 
    assert np.allclose(result.axis_ranges[0], expected.axis_ranges[0])
    assert result.data_label == expected.data_label
    assert result.data_unit == expected.data_unit
    
    
    
@pytest.fixture
def results_sin2chi_method_fixture():
    d_spacing_combined = Dataset(
        np.array([[1, 2, 3, 4], [5, 6, 7, 8]]), 
        axis_ranges={0: [0, 1], 1: [0, 1, 2, 3]}, 
        axis_labels={0: '0: d-, 1: d+', 1: LABELS_SIN2CHI}, 
        data_unit='nm', 
        data_label='0: position_neg, 1: position_pos'
    )
    
    d_spacing_result = Dataset(
        np.array([[1, 2, 3, 4], [5, 6, 7, 8], [3, 4, 5, 6]]),
        axis_ranges={0: [0, 1, 2], 1: [0, 1, 2, 3]}, 
        axis_labels={0: '0: d-, 1: d+, 2: d_mean', 1: LABELS_SIN2CHI},
        data_unit='nm', 
        data_label='d_spacing'
    )
    
    return d_spacing_combined, d_spacing_result

def test__create_final_result_sin2chi_method_validation(plugin_fixture, results_sin2chi_method_fixture):
    plugin = plugin_fixture
    plugin._config["input_shape"] = (4, 5) #chose 5 in position 0 to avoid padding as above
    
    
    d_spacing_combined, d_spacing_result = results_sin2chi_method_fixture
    
    result = plugin._create_final_result_sin2chi_method(d_spacing_combined)
    

    assert np.array_equal(result.array, d_spacing_result.array)
    # Compare each key-value pair in the axis_ranges
    for key, value in result.axis_ranges.items():
        assert key in d_spacing_result.axis_ranges.keys()
        assert np.array_equal(value, d_spacing_result.axis_ranges[key])
    assert result.axis_labels == d_spacing_result.axis_labels
    assert result.data_label == d_spacing_result.data_label
    assert result.data_unit == d_spacing_result.data_unit
    
    
def test__create_final_result_sin2chi_method_type_error(plugin_fixture, results_sin2chi_method_fixture):
    plugin = plugin_fixture    
    
    d_spacing_combined, d_spacing_result = results_sin2chi_method_fixture

    with pytest.raises(TypeError, match="Input must be an instance of Dataset"):
        plugin._create_final_result_sin2chi_method([])
        
def test__create_final_result_sin2chi_method_shape(plugin_fixture):
    plugin = plugin_fixture
    
    invalid_d_spacing_combined = Dataset(
        np.array([1, 2, 3, 4]), 
        axis_ranges={0: [0, 1, 2, 3]}, 
        axis_labels={0: LABELS_SIN2CHI}, 
        data_unit='nm', 
        data_label='0: position_neg'
    )
    with pytest.raises(ValueError, match=r"Dataset d_spacing_combined must have a shape of \(2, N\)."):
        plugin._create_final_result_sin2chi_method(invalid_d_spacing_combined)
    
def test__create_final_result_sin2chi_method_label_1(plugin_fixture, results_sin2chi_method_fixture):
    plugin = plugin_fixture
    
    d_spacing_combined, d_spacing_result = results_sin2chi_method_fixture
    d_spacing_combined.update_axis_label(0, 'blub')
    
    with pytest.raises(ValueError, match=r"axis_labels\[0\] does not match '0: d-, 1: d\+'."):
        plugin._create_final_result_sin2chi_method(d_spacing_combined)
        

def test__create_final_result_sin2chi_method_label_2(plugin_fixture, results_sin2chi_method_fixture):   
    plugin = plugin_fixture
     
    d_spacing_combined, d_spacing_avg = results_sin2chi_method_fixture
    d_spacing_combined.update_axis_label(1, 'blub')

    with pytest.raises(ValueError, match=r'axis_labels\[1\] does not match sin\^2\(chi\).'):
        plugin._create_final_result_sin2chi_method(d_spacing_combined)  
        
        
@dataclass 
class Ds2cTestConfig:
    delta_chi: Real
    chi_start: Real
    chi_stop: Real
    d_spacing_func: Callable
    s2c_range_sorted: np.array
    d_mean_pos: np.array
    d_mean_neg: np.array
    d_mean_avg: np.array
    azimuth_name: str = LABELS_CHI
    chi_unit: str = UNITS_DEGREE
    d_unit: str = UNITS_NANOMETER
    d_label: str = "d_spacing"
    description: str = ""
        
    def create_simple_input_ds(self):
        chi = chi_gen(self.chi_start, self.chi_stop, self.delta_chi) 
       
        input_ds =  Dataset(self.d_spacing_func(chi).reshape(-1, 1),
                        axis_ranges={0: chi, 1: np.array([0])},
                        axis_labels={0: self.azimuth_name, 1: '0: position'},
                        axis_units = {0: self.chi_unit, 1: ''},
                        data_label = f'position / {self.d_unit}')
    
        return input_ds
    
    def create_output_ds(self):
        expected_result = np.vstack([
        self.d_mean_neg,
        self.d_mean_pos,
        self.d_mean_avg
        ])    
        output_ds =  Dataset(expected_result, axis_ranges= {0: np.arange(expected_result.shape[0]), 1: self.s2c_range_sorted}, 
                             axis_labels = {0: '0: d-, 1: d+, 2: d_mean', 1: LABELS_SIN2CHI}, data_unit = f'{self.d_unit}', data_label='d_spacing')
        
        return output_ds
    
    def create_simple_input_ds_1d(self):
        chi = chi_gen(self.chi_start, self.chi_stop, self.delta_chi)
        input_ds = Dataset(self.d_spacing_func(chi), axis_ranges={0: chi}, axis_labels={0: self.azimuth_name}, axis_units={0: self.chi_unit}, data_label=f'position / {self.d_unit}')
        return input_ds
        
    
ds_case1_exe =  Ds2cTestConfig(
    delta_chi=22.5,
    chi_start=-180,
    chi_stop=180,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array([4, 5, 6, 7, 8] ),
    d_mean_neg=np.array([8, 11, 10, 9, 8]),
    d_mean_avg= np.array([6, 8, 8, 8, 8]),
    s2c_range_sorted=np.array([0.0, 0.14645, 0.5, 0.85355, 1] ),    
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,

    description= "A simple case"   
)   

ds_case2_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=0,
    chi_stop=45,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
    d_mean_neg=np.array([np.nan, np.nan, np.nan, np.nan, np.nan]),
    d_mean_avg= np.array([np.nan, np.nan, np.nan, np.nan, np.nan]),
    s2c_range_sorted=np.array([0.0, 0.03015, 0.11698, 0.25, 0.41318]),
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description= "Few chi values"   
) 

ds_case3_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=-180,
    chi_stop=181,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array(
         [ 9., 10., 11. ,12., 13., 14., 15., 16., 17. ,18.]
    ),
    d_mean_neg=np.array(
        [27. ,26., 25.,24., 23., 22. ,21, 20., 19., 18.]
    ),
    d_mean_avg= np.array([18. ,18., 18., 18., 18., 18., 18., 18., 18., 18.]),    
    s2c_range_sorted=np.array(
        [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]),
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description= "Some nan values"   
) 

ds_case4_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=-90,
    chi_stop=11,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array(
         [ 9. ,10.]+[np.nan]*8
    ),
    d_mean_neg=np.array([9., 8., 7., 6., 5. ,4.,3., 2., 1., 0.]),
    d_mean_avg= np.array([9. ,9.]+[np.nan]*8),    
    s2c_range_sorted=np.array(
       [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]    ),
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="Few values in positive slope",

)


ds_case5_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=-10,
    chi_stop=91,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array(
         [ 1.  ,2. , 3. , 4. , 5. , 6. , 7.,  8. , 9., 10.]
    ),
    d_mean_neg=np.array(
        [1., 0.]+[np.nan]*8
    ),
    d_mean_avg= np.array([1. ,1.]+[np.nan]*8),    
    s2c_range_sorted=np.array(
       [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]),
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="Few values in negative slope",

)

ds_case6_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=-30,
    chi_stop=181,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array(
         [ 3. , 4. , 5. , 6. , 7. , 8. , 9., 10., 11.,12.]    ),
    d_mean_neg=np.array(
        [12., 11., 10. , 9., 17., 16., 15., 14., 13., 12.]    ),
    d_mean_avg= np.array([ 7.5 , 7.5,  7.5 , 7.5 ,12. , 12.,  12. , 12.,  12., 12. ]),    
    s2c_range_sorted=np.array(
       [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]    ),
    azimuth_name = 'chi',
    chi_unit= 'deg',
    d_unit= "nm" ,
    description="Less values in negative slope"
)

ds_case7_exe =  Ds2cTestConfig(
    delta_chi=22.5,
    chi_start=-180,
    chi_stop=180,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array(
        [4., 5., 6.,7., 8.]    ),
    d_mean_neg=np.array(
       [ 8. ,11. ,10.,  9.,  8.]    ),
    d_mean_avg= np.array( [6., 8., 8., 8., 8.]),    
    s2c_range_sorted=np.array(
        [0.0000000, 0.1464466, 0.5000000, 0.8535534, 1.0000000]     ),
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="Simple case",
)


ds_case8_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=-180,
    chi_stop=181,
    d_spacing_func=d_spacing_simu, 
    d_mean_pos=np.array(
       [25.25007189, 25.27466048 ,25.2832  ,  25.27466048, 25.25007189, 25.2124,
 25.16618858, 25.11701142, 25.0708    , 25.03312811]    ),
    d_mean_neg=np.array(
      [25.25007189 ,25.2124  ,   25.16618858 ,25.11701142 ,25.0708   ,  25.03312811,
 25.00853952, 25.  ,       25.00853952 ,25.03312811]),
    d_mean_avg= np.array([25.25007189 ,25.24353024 ,25.22469429, 25.19583595, 25.16043595, 25.12276405,
 25.08736405, 25.05850571, 25.03966976, 25.03312811]),    
    s2c_range_sorted=np.array(
         [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000] ),
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="Simple case",
)

ds_case9_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=0,
    chi_stop=361,
    d_spacing_func=d_spacing_simu, 
    d_mean_pos=np.array(
       [25.25007189, 25.27466048 ,25.2832   ,  25.27466048 ,25.25007189 ,25.2124,
 25.16618858, 25.11701142 ,25.0708  ,   25.03312811]    ),
    d_mean_neg=np.array([25.25007189, 25.2124  ,   25.16618858, 25.11701142 ,25.0708  ,   25.03312811,
 25.00853952, 25.    ,     25.00853952, 25.03312811] ),
    d_mean_avg= np.array([25.25007189, 25.24353024 ,25.22469429, 25.19583595 ,25.16043595, 25.12276405,
 25.08736405 ,25.05850571, 25.03966976, 25.03312811]),    
    s2c_range_sorted=np.array(
        [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]  ),    
    azimuth_name = 'chi',
    chi_unit= 'deg',
    d_unit= "nm" ,
    description="A more realistic case with chi ranging from 0 to 360",
)

ds_case10_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=0,
    chi_stop=361,
    d_spacing_func=d_spacing_simu_noise, 
    d_mean_pos=np.array(
       [26.26736461, 26.28663577, 26.28734205 ,26.27491604, 26.24311126, 26.23497842,
 26.17385737 ,26.12768893 ,26.0598127 , 26.07347215]
    ),
    d_mean_neg=np.array([26.21146524 ,26.20441612 ,26.13792499, 26.15061959 ,26.10692267, 26.03331406,
 25.99338069, 26.00076722 ,26.01825283 ,26.07347215]    ),
    d_mean_avg= np.array([26.23941493, 26.24552595, 26.21263352, 26.21276782, 26.17501697 ,26.13414624,
 26.08361903 ,26.06422807 ,26.03903276 ,26.07347215]),    
    s2c_range_sorted=np.array(
        [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]     ),    
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="A more realistic case with chi ranging from 0 to 360 and noise added; noise with scale 0.03",
)

ds_case11_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=0,
    chi_stop=45,
    d_spacing_func=d_spacing_simu_noise, 
    d_mean_pos=np.array(
      [26.32298561, 26.24830245, 26.31529111, 26.23839737, 26.25085018]),
    d_mean_neg=np.array([np.nan, np.nan, np.nan, np.nan, np.nan]),
    d_mean_avg = np.array([np.nan, np.nan, np.nan, np.nan, np.nan]),    
    s2c_range_sorted=np.array(
        [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759]),    
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="Positive chi range between 0 and 45; noise with scale 0.03",
)

ds_case12_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=-90,
    chi_stop=272,
    d_spacing_func=d_spacing_simu_noise, 
    d_mean_pos=np.array([26.29041594 ,26.28437378 ,26.28396722, 26.25950164 ,26.25025785, 26.24852267,
 26.19979675, 26.08874783 ,26.06281612, 25.99452146]),
    d_mean_neg=np.array([26.29041594, 26.2014127 , 26.17686609 ,26.12468021, 26.09337842, 26.02616748,
 26.00879509, 26.00414205, 26.02051482, 26.05042083]),
    d_mean_avg= np.array([26.29041594 ,26.24289324 ,26.23041665 ,26.19209092, 26.17181813 ,26.13734507,
 26.10429592, 26.04644494 ,26.04166547 ,26.02247114]),
    s2c_range_sorted=np.array(
        [0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]),    
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="Positive chi range between 0 and 45; noise with scale 0.03",
)

ds_case13_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=-180,
    chi_stop=181,
    d_spacing_func=d_spacing_simu,
    d_mean_pos=np.array([25.25007189 ,25.27466048 ,25.2832   ,  25.27466048 ,25.25007189, 25.2124,
 25.16618858 ,25.11701142 ,25.0708    , 25.03312811] ),
    d_mean_neg=np.array([25.25007189 ,25.2124   ,  25.16618858, 25.11701142, 25.0708   ,  25.03312811,
 25.00853952, 25.     ,    25.00853952 ,25.03312811]),
    d_mean_avg = np.array([25.25007189, 25.24353024 ,25.22469429 ,25.19583595, 25.16043595, 25.12276405,
 25.08736405, 25.05850571 ,25.03966976 ,25.03312811]),
    s2c_range_sorted=np.array([0.0000000, 0.0301537, 0.1169778, 0.2500000,
                               0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]),
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="Simple case without noise"
)

ds_case14_exe =  Ds2cTestConfig(
    delta_chi=10,
    chi_start=0,
    chi_stop=181,
    d_spacing_func=d_spacing_simple,
    d_mean_pos=np.array([0., 1., 2., 3., 4., 5., 6., 7., 8., 9.]),    
    d_mean_neg=np.array([18., 17. ,16., 15. ,14, 13., 12,11. ,10. , 9.]),
    d_mean_avg=np.array([9., 9., 9., 9., 9., 9., 9. ,9., 9., 9.]),
    s2c_range_sorted=np.array([0.0000000, 0.0301537, 0.1169778, 0.2500000, 0.4131759, 0.5868241, 0.7500000, 0.8830222, 0.9698463, 1.0000000]),
    azimuth_name = LABELS_CHI,
    chi_unit= UNITS_DEGREE,
    d_unit= UNITS_NANOMETER ,
    description="Simple case without noise"
)
                                         
test_cases = [ds_case1_exe, ds_case2_exe, ds_case3_exe, ds_case4_exe, ds_case5_exe, ds_case6_exe,
              ds_case7_exe, ds_case8_exe, ds_case9_exe, ds_case10_exe, ds_case11_exe, ds_case12_exe]
#test_cases=[ds_case12_exe]
@pytest.mark.parametrize("case", test_cases)        
def test_execute_with_various_cases(plugin_fixture, case):    
    plugin = plugin_fixture
    
    ds_in = case.create_simple_input_ds()
    expected_ds = case.create_output_ds()
    
    result, _ = plugin.execute(ds_in)
    
    print("In the test")
    print(case.description)
    print('ds_in', ds_in)
    print('ds_out', result)
    

    npt.assert_allclose(result.array, expected_ds.array, rtol=5e-10, atol=1e-15, equal_nan=True, err_msg='Tolerance not matchend.', verbose=True)
    npt.assert_allclose(expected_ds.array[2,:], np.mean([case.d_mean_neg, case.d_mean_pos], axis=0), rtol=1e-5, atol=1e-8, equal_nan=True, err_msg='Tolerance not matchend.', verbose=True)
    npt.assert_allclose(result.axis_ranges[1], expected_ds.axis_ranges[1], rtol=1e-05, atol=1e-05, equal_nan=True, err_msg='Tolerance not matchend.', verbose=True)
    npt.assert_array_equal(result.axis_ranges[0], expected_ds.axis_ranges[0], err_msg='Values are not eequal for axis_ranges[0]', verbose=True)
    assert result.data_label == expected_ds.data_label
    assert result.data_unit == expected_ds.data_unit
    assert result.axis_labels[0] == expected_ds.axis_labels[0]
    assert result.axis_labels[1] == expected_ds.axis_labels[1]
    assert np.all(np.diff(result.axis_ranges[1][~np.isnan(result.axis_ranges[1])]) >= 0), "result.axis_ranges[1] is not in ascending order (ignoring NaNs)."

test_cases_1d= [ds_case13_exe, ds_case14_exe]
@pytest.mark.parametrize("case", test_cases_1d)        
def test_execute_with_various_cases_1d(plugin_fixture, case):    
    plugin = plugin_fixture
    
    ds_in = case.create_simple_input_ds_1d()
    expected_ds = case.create_output_ds()
    
    result, _ = plugin.execute(ds_in)

    npt.assert_allclose(result.array, expected_ds.array, rtol=5e-10, atol=1e-15, equal_nan=True, err_msg='Tolerance not matchend.', verbose=True)
    npt.assert_allclose(expected_ds.array[2,:], np.mean([case.d_mean_neg, case.d_mean_pos], axis=0), rtol=1e-5, atol=1e-8, equal_nan=True, err_msg='Tolerance not matchend.', verbose=True)
    npt.assert_allclose(result.axis_ranges[1], expected_ds.axis_ranges[1], rtol=1e-05, atol=1e-05, equal_nan=True, err_msg='Tolerance not matchend.', verbose=True)
    npt.assert_array_equal(result.axis_ranges[0], expected_ds.axis_ranges[0], err_msg='Values are not eequal for axis_ranges[0]', verbose=True)
    assert result.data_label == expected_ds.data_label
    assert result.data_unit == expected_ds.data_unit
    assert result.axis_labels[0] == expected_ds.axis_labels[0]
    assert result.axis_labels[1] == expected_ds.axis_labels[1]
    assert np.all(np.diff(result.axis_ranges[1][~np.isnan(result.axis_ranges[1])]) >= 0), "result.axis_ranges[1] is not in ascending order (ignoring NaNs)."



@pytest.mark.parametrize("invalid_input", [
    [1, 2, 3],                   # List input
    np.array([1, 2, 3]),          # Numpy array input
    (1, 2, 3)                     # Tuple input
])
def test_execute_with_invalid_input(plugin_fixture, invalid_input):
    plugin = plugin_fixture
    with pytest.raises((AttributeError, UserConfigError)):
        plugin.execute(invalid_input)

@pytest.mark.parametrize("data, expected_error_message", [
    (np.array(1), "Dataset has to be 1D or 2D."),  # ndim = 0
    (np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]), "Dataset has to be 1D or 2D.")  # ndim = 3
])
def test_execute_invalid_ndim(plugin_fixture, data, expected_error_message):
    ds = Dataset(data)
    with pytest.raises(UserConfigError, match=expected_error_message):
        plugin_fixture.execute(ds)

 
@pytest.fixture
def base_execute_dataset():
    return Dataset(np.random.default_rng(seed=42).random((6, 5)),
        axis_labels={0:'chi', 1:'0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'},
        axis_units={0: 'deg', 1: ''},
        axis_ranges={0:np.arange(6), 1:np.arange(5)},
        metadata={},
        data_unit='',
        data_label='position / nm; area / (cts * nm); FWHM / nm;background at peak / cts; total count intensity / cts',       
    )

@pytest.mark.parametrize("missing_field, removal_key, expected_error_message", [
    ("position", 1, 'Key containing "position" is missing. Check your dataset.'), 
    ("chi", 0, "chi is missing. Check your dataset."),  
    ("position / ", 3, "Unit not found for parameter: position"),
    ("chi_unit", 4, "Unit dummy not allowed for chi.")
   ])
def test_execute_with_missing_field(plugin_fixture, base_execute_dataset, missing_field, removal_key, expected_error_message):
    """Test the execute function with missing axis labels."""    
    plugin = plugin_fixture
    test_ds =  base_execute_dataset    
    
    # Modify axis_labels by removing or adjusting the necessary field
    if removal_key == 0:  # Removing 'chi'
        test_ds.update_axis_label(0, 'dummy')
    elif removal_key == 1:  # Modifying 'position'
        test_ds.update_axis_label(1, '0: area; 1: FWHM; 2: background at peak; 3: total count intensity')
        test_ds.data_label='area / (cts * nm); FWHM / nm;background at peak / cts; total count intensity / cts'
    elif removal_key == 3: 
        test_ds.data_label = 'area / (cts * nm); FWHM / nm;background at peak / cts; total count intensity / cts'
    elif removal_key == 4:
        test_ds.update_axis_unit(0, 'dummy')
     
    with pytest.raises(UserConfigError, match=expected_error_message):
        plugin.execute(test_ds)

@pytest.mark.parametrize("fit_label, data_label, expected_units_dict", [
    ('0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity', 
     'position / nm; area / (cts * nm); FWHM / nm;background at peak / cts; total count intensity / cts',
     {0: ['position','nm'] , 1: ['area', '(cts * nm)'], 2:['FWHM', 'nm'], 3:['background at peak', 'cts'],
      4:['total count intensity','cts'], 5:['chi', 'deg']}),
    ('0:position; 1:area', 'position / nm; area / (cts * nm)', {0: ['position','nm'] , 1: ['area', '(cts * nm)'], 2:['chi', 'deg']}),
    ('0:position', 'position / nm', {0: ['position','nm'] , 1: ['chi', 'deg']}),
    ('1: area; 2: FWHM; 3: background at peak; 4: position', 
     'area / (cts * nm); FWHM / nm;background at peak / cts; position / nm',
     {1: ['area', '(cts * nm)'], 2:['FWHM', 'nm'], 3:['background at peak', 'cts'], 
      4:['position', 'nm'],5:['chi', 'deg']}),
])
def test__extract_units_validation(plugin_fixture, base_execute_dataset, fit_label, data_label, expected_units_dict):
    plugin = plugin_fixture
    test_ds = base_execute_dataset
    
    #overwrite the axis_labels and data_label
    test_ds.update_axis_label(1, fit_label)
    test_ds.data_label = data_label
    
    # Test the function
    result = plugin._extract_units(test_ds)
    assert result == expected_units_dict   
 
 
@pytest.mark.parametrize("fit_label, data_label, expected_error_message", [
    ('0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity', 
     'position / nmm; area / (cts * nm); FWHM / nm;background at peak / cts; total count intensity / cts',
     'Unit nmm not allowed for position.'),
    ('0:position; 1:area', 'position / nmm; area / (cts * nm)', 'Unit nmm not allowed for position.'),
    ('0:position', 'position / nmm', 'Unit nmm not allowed for position.'),
    ('1: area; 2: FWHM; 3: background at peak; 4: position', 
     'area / (cts * nm); FWHM / nm;background at peak / cts; position / nmm', 'Unit nmm not allowed for position.'),
    ('0:position', 'position / nm^-1', r'Unit nm\^\-1 not allowed for position.'),
    ('0:position', 'position / A^-1', r'Unit A\^\-1 not allowed for position.'),    
    ('0:position', 'position / 2th_deg', r'Unit 2th_deg not allowed for position.'), # currently not allowed, but for sin^psi relevant
    ('0:position', 'position / 2th_rad', r'Unit 2th_rad not allowed for position.')
])
def test__chi_pos_unit_verification_error_position_unit(plugin_fixture, base_execute_dataset,
                                           fit_label, data_label, expected_error_message):
    plugin = plugin_fixture
    test_ds = base_execute_dataset
    #overwrite the axis_labels and data_label
    test_ds.update_axis_label(1, fit_label)
    test_ds.data_label = data_label
    
    with pytest.raises(UserConfigError, match=expected_error_message):
        plugin._chi_pos_unit_verification(test_ds)
        
@pytest.mark.parametrize('fit_label, data_label',
                         [
                         ('1:position', 'position / nm'),
                         ('1:position', 'position / A'),
                         ])
def test__chi_pos_unit_verification_valid_position_unit(plugin_fixture, base_execute_dataset, fit_label, data_label):
    plugin = plugin_fixture
    test_ds = base_execute_dataset 
    test_ds.update_axis_label(1,fit_label)
    test_ds.data_label=data_label
    try:
        plugin._chi_pos_unit_verification(test_ds)
    except Exception as e:
        pytest.fail(f"Function raised an unexpected exception: {e}")

        
def test__chi_pos_unit_verification_valid_chi_unit(plugin_fixture, base_execute_dataset):
    plugin = plugin_fixture
    test_ds = base_execute_dataset
    try:
        plugin._chi_pos_unit_verification(test_ds)
    except Exception as e:
        pytest.fail(f"Function raised an unexpected exception: {e}")
    
@pytest.mark.parametrize("chi_unit, expected_error_message", [
    ('def', 'Unit def not allowed for chi.'),
    ('rad', 'Unit rad not allowed for chi.'),
    ('r_mm', 'Unit r_mm not allowed for chi.' ) 
])
def test__chi_pos_unit_verification_error_chi_unit(plugin_fixture, base_execute_dataset, chi_unit, expected_error_message):
    plugin = plugin_fixture
    test_ds = base_execute_dataset
    test_ds.update_axis_unit(0, chi_unit)
    
    with pytest.raises(UserConfigError, match=expected_error_message):
        plugin._chi_pos_unit_verification(test_ds)

@pytest.mark.parametrize("ds_units_dict, pos_index, expected_param_with_unit",[
    ({0: ['position','nm'] , 1: ['area', '(cts * nm)'], 2:['chi', 'deg']}, 0, ('position', 'nm')),
    ({0: ['position','A'] , 1: ['area', '(cts * nm)'], 2:['chi', 'deg']}, 0, ('position', 'A')),
    ({1: ['position','nm']}, 1, ('position', 'nm')),
])
def test__get_param_unit_at_index_validation(plugin_fixture, ds_units_dict, pos_index, expected_param_with_unit):
    plugin = plugin_fixture
    
    result = plugin._get_param_unit_at_index(ds_units_dict, pos_index)
    
    assert result == expected_param_with_unit


        
# Testing for various Dataset modifications for create_final_result_sin2chi_method
@pytest.fixture
def base_dataset():
    return Dataset(
        np.array([[1, 2, 3, 4], [5, 6, 7, 8]], dtype=float), 
        axis_ranges={0: [0, 1], 1: [0, 1, 2, 3]},
        axis_labels={0: '0: d-, 1: d+', 1: LABELS_SIN2CHI},
        axis_units={0: UNITS_DEGREE, 1: ''},
        data_unit=UNITS_NANOMETER, 
        data_label='0: position_neg, 1: position_pos'
    )
    
@pytest.mark.parametrize("modifications, expected_array", [
    # No modifications
    ([], np.array([[1, 2, 3, 4], [5, 6, 7, 8], [3, 4, 5, 6]])),
    # Set first value of d- to np.nan
    ([(0, 0, np.nan)], np.array([[np.nan, 2, 3, 4], [5, 6, 7, 8], [np.nan, 4, 5, 6]])),
    # Set second value of d+ to np.nan
    ([(1, 1, np.nan)], np.array([[1, 2, 3, 4], [5, np.nan, 7, 8], [3, np.nan, 5, 6]])),
])
def test__create_final_result_sin2chi_method(plugin_fixture, base_dataset, modifications, expected_array):
    plugin = plugin_fixture
    plugin._config["input_shape"] = (4, 5) #chose 5 in position 0 to avoid padding as above
    
    
    # Apply modifications
    for i, j, value in modifications:
        base_dataset.array[i, j] = value
    
    result = plugin._create_final_result_sin2chi_method(base_dataset)
    
    # Expected attributes for the resulting Dataset
    expected = Dataset(
        expected_array,
        axis_ranges={0: [0, 1, 2], 1: [0, 1, 2, 3]},
        axis_labels={0: '0: d-, 1: d+, 2: d_mean', 1: LABELS_SIN2CHI},
        data_unit=UNITS_NANOMETER,
        data_label='d_spacing'
    )
    
    # Compare array data
    assert np.array_equal(result.array, expected.array, equal_nan=True)
    
    # Compare axis ranges
    for key in expected.axis_ranges:
        assert key in result.axis_ranges
        assert np.array_equal(result.axis_ranges[key], expected.axis_ranges[key])
    
    # Compare axis labels
    assert result.axis_labels == expected.axis_labels
    
    # Compare data labels and units
    assert result.data_label == expected.data_label
    assert result.data_unit == expected.data_unit
    
    
# Test the Dataset against the expected values
@pytest.fixture
def data_values():
    data_val = np.array([3, 2, 1, 5, 4])
    axis_val = np.array([5, 4, 3, 2, 1]) / 10
    ds = Dataset(
        data_val.copy(),
        axis_units={0: "um"},
        data_label=LABELS_POSITION,
        data_unit=UNITS_NANOMETER,
        axis_labels={0: "x"},
        axis_ranges={0: axis_val.copy()},
    )
    return data_val, axis_val, ds


def test_unsorted(data_values):
    data_val, axis_val, ds = data_values
    assert np.array_equal(axis_val, ds.axis_ranges[0])
    assert np.array_equal(data_val, ds.array)


def test_sort(data_values):
    data_val, axis_val, ds = data_values
    # inplace sorting
    ds.sort(
        axis=0
    )  # sorts only the values in the array, but not the metadata (axis values). Metadata not aligned with sorted array

    sorted_arr_idx = np.argsort(data_val)

    print("comparison", ds.array, np.sort(data_val))
    assert np.allclose(ds.array, np.sort(data_val))
    assert np.allclose(ds.axis_ranges[0], axis_val[sorted_arr_idx])


def test_sort_explicit():
    ds = Dataset(
        np.array([3, 2, 1, 5, 4]),
        axis_units={0: "um"},
        data_label=LABELS_POSITION,
        data_unit=UNITS_NANOMETER,
        axis_labels={0: "x"},
        axis_ranges={0: np.array([0.5, 0.4, 0.3, 0.2, 0.1])},
    )

    assert np.allclose(ds.array, np.array([3, 2, 1, 5, 4]))
    assert np.allclose(ds.axis_ranges[0], np.array([0.5, 0.4, 0.3, 0.2, 0.1]))
    ds.sort(axis=0)  # in place sorting does not work on metadata
    assert np.allclose(ds.array, np.array([1, 2, 3, 4, 5]))
    assert np.allclose(ds.axis_ranges[0], [0.3, 0.4, 0.5, 0.1, 0.2])


def test_argsort(data_values):
    data_val, axis_val, ds = data_values
    sorted_arr_idx = ds.argsort(axis=0)

    ds_sorted = ds[sorted_arr_idx]

    assert np.allclose(ds_sorted.array, data_val[sorted_arr_idx])
    assert np.allclose(ds_sorted.axis_ranges[0], axis_val[sorted_arr_idx])


def test_argsort_axis(data_values):
    data_val, axis_val, ds = data_values
    sorted_axis_idx = np.argsort(ds.axis_ranges[0], axis=0)
    ds_sorted = ds[sorted_axis_idx]

    assert np.allclose(ds_sorted.array, data_val[sorted_axis_idx])
    assert np.allclose(ds_sorted.axis_ranges[0], axis_val[sorted_axis_idx])


def test_numpy_indexing_with_list():
    ds = Dataset(
        np.array([3, 2, 1, 5, 4]),
        axis_units={0: "um"},
        data_label=LABELS_POSITION,
        data_unit=UNITS_NANOMETER,
        axis_labels={0: "x"},
        axis_ranges={0: np.array([0.5, 0.4, 0.3, 0.2, 0.1])},
    )

    assert np.allclose(ds.array, np.array([3, 2, 1, 5, 4]))
    assert np.allclose(ds.axis_ranges[0], np.array([0.5, 0.4, 0.3, 0.2, 0.1]))

    ds_sorted = ds[[2, 3, 4, 0, 1]]

    assert np.allclose(ds_sorted.array, np.array([1, 5, 4, 3, 2]))
    assert np.allclose(ds_sorted.axis_ranges[0], [0.3, 0.2, 0.1, 0.5, 0.4])


def test_numpy_indexing_with_ndarray():
    ds = Dataset(
        np.array([3, 2, 1, 5, 4]),
        axis_units={0: "um"},
        data_label=LABELS_POSITION ,
        data_unit=UNITS_NANOMETER,
        axis_labels={0: "x"},
        axis_ranges={0: np.array([0.5, 0.4, 0.3, 0.2, 0.1])},
    )

    assert np.allclose(ds.array, np.array([3, 2, 1, 5, 4]))
    assert np.allclose(ds.axis_ranges[0], np.array([0.5, 0.4, 0.3, 0.2, 0.1]))

    ds_sorted = ds[np.array([2, 3, 4, 0, 1])]

    assert np.allclose(ds_sorted.array, np.array([1, 5, 4, 3, 2]))
    assert np.allclose(ds_sorted.axis_ranges[0], [0.3, 0.2, 0.1, 0.5, 0.4])


# Regression test to document partially wrong behaviour of  __reimplement_numpy_method
@pytest.fixture
def array_mean_fixture():
    arr=np.ones ( (4,4))
    arr[::2,::2] = 0
    arr[:,1::2]=3
    return arr


@pytest.fixture
def dataset_mean_fixture():
    arr=np.ones ((4,4))
    arr[::2,::2] = 0
    arr[:,1::2]=3

    ds = Dataset(
        arr.copy()
        )
    
    return ds


def test_array_mean_base(array_mean_fixture):
    arr = array_mean_fixture
    
    # Check that base is None for mean operations
    assert arr.mean().base is None, "Expected base to be None for np.ndarray.mean()"
    assert arr.mean(axis=0).base is None, "Expected base to be None for np.ndarray.mean(axis=0)"
    assert arr.mean(axis=1).base is None, "Expected base to be None for np.ndarray.mean(axis=1)"
    assert np.mean(arr).base is None, "Expected base to be None for np.mean()"

def test_Dataset_mean_base(dataset_mean_fixture):
    ds = dataset_mean_fixture  
    
    # Check that base is None for mean operations
    assert np.mean(ds).base is None, "Expected base to be None for np.mean(Dataset)"
    assert ds.mean().base is None, "Expected base to be None for Dataset.mean()"