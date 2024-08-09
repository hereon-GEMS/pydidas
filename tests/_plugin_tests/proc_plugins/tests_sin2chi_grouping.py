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
from typing import Callable
from numbers import Real
from dataclasses import dataclass

from pydidas.plugins import PluginCollection
from pydidas.plugins import ProcPlugin
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED


from pydidas.core import Dataset, UserConfigError

from pydidas_plugins.proc_plugins.sin2chi_grouping import PARAMETER_KEEP_RESULTS, LABELS_SIN2CHI


@pytest.fixture
def plugin_fixture():
    return PluginCollection().get_plugin_by_name('DspacingSin2chiGrouping')()


def test_plugin_initialization(plugin_fixture):
    # Test if the plugin is initialized correctly
    plugin = plugin_fixture
      
    assert plugin.plugin_name == "Group d-spacing according to sin^2(chi) method"
    assert plugin.basic_plugin == False
    assert plugin.plugin_type == PROC_PLUGIN
    assert plugin.plugin_subtype == PROC_PLUGIN_INTEGRATED
    assert plugin.input_data_dim == -1
    assert plugin.output_data_dim == 2
    assert plugin.output_data_label == "0: position_neg, 1: position_pos, 2: Mean of 0: position_neg, 1: position_pos"
    assert plugin.new_dataset == True
    
    #check plugin is initialised with autosave option
    assert plugin.params.get_value(PARAMETER_KEEP_RESULTS) == True
    
    
def test_plugin_inheritance():  
    plugin_obj =  PluginCollection().get_plugin_by_name('DspacingSin2chiGrouping')
    assert issubclass(plugin_obj, ProcPlugin), "Plugin is not a subclass of ProcPlugin"
    

def test_plugin_pre_execute_sets_keep_results(plugin_fixture):
    #Test if the keep_results parameter is set to True in the pre_execute method.
    plugin = plugin_fixture

    plugin.params.set_value(PARAMETER_KEEP_RESULTS, False)
    plugin.pre_execute()
    assert plugin.params.get_value(PARAMETER_KEEP_RESULTS) == True
    
    
@pytest.mark.parametrize(
    "input_shape, result_shape",
    [
        ((10, 20), (3, 6)),   # Test case 1
        ((20, 40), (3, 11)),  # Test case 2
        ((15, 30), (3, 9)),   # Test case 3
    ]
)
def test_calulate_result_shape(plugin_fixture, input_shape, result_shape):
    plugin = plugin_fixture
    plugin._config["input_shape"] = input_shape
    
    plugin.calculate_result_shape()
    
    assert plugin._config["result_shape"] == result_shape



@pytest.mark.parametrize(
    "input_shape",
    [
        None,   # Test case 1: input_shape is None
        [],     # Test case 2: input_shape is an empty list
    ]
)
def test_calculate_result_shape_raises_error(plugin_fixture, input_shape):
    plugin = plugin_fixture
    plugin._config["input_shape"] = input_shape
    
    with pytest.raises(UserConfigError) as e:
        plugin.calculate_result_shape()
   
    # Update the assertion to match the full error message
    assert "Cannot calculate the result shape for the" \
           f' "{plugin.plugin_name}" plugin because the input shape is unknown or invalid.' in str(e.value)




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
    if metric_name == "position":
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
def test_group_d_spacing_by_chi_result(plugin_fixture, case):
    plugin = plugin_fixture
    
    chi = chi_gen(case.chi_start, case.chi_stop, case.delta_chi)
    d_spacing = Dataset(
        case.d_spacing_func(chi),
        axis_ranges={0: np.arange(0, len(chi))},
        axis_labels={0: "d_spacing"},
    )

    (d_spacing_pos, d_spacing_neg) = plugin._group_d_spacing_by_chi(
        d_spacing, chi, tolerance=1e-4
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
    
    
def test__chi_pos_verification_success(plugin_fixture):
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
    with pytest.raises(ValueError) as excinfo:
        plugin._chi_pos_verification(ds)
    assert 'Key containing "position" is missing' in str(excinfo.value)
    
def test_chi_pos_verification_wrong_input_type(plugin_fixture):
    
    plugin = plugin_fixture
    
    with pytest.raises(TypeError) as excinfo:
        plugin._chi_pos_verification([])  # Pass a list instead of a Dataset
    assert "Input must be an instance of Dataset." in str(excinfo.value), "Error message should indicate wrong type for Dataset."

    
def test__chi_pos_verification_all_labels_missing(plugin_fixture):
    
    plugin = plugin_fixture
    
    result_array_spatial = generate_result_array_spatial()

    # labels are missing while creating a Dataset
    ds = Dataset(result_array_spatial)
    with pytest.raises(ValueError) as excinfo:
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

    with pytest.raises(KeyError) as excinfo:
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
    
    with pytest.raises(TypeError) as excinfo:
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
    Ugly test due to pre-allocation requirements in pydidas, dynamic allocation is currently not yet supported. 
    I delibertly left the Dataset expected as it is, as this is the future version when dynamic allocation is supported,
    see also second test below.
    """
    
    _, _, d_spacing_combined = d_spacing_datasets
    
    plugin = plugin_fixture
    # This is currently required due to pre-allocation requirements in pydidas, dynamic allocation is not yet supported
    # We can deduct the incoming length of chi-values via the length of the sin2chi axis
    plugin._config["input_shape"] = (2*(d_spacing_combined.axis_ranges[1].size-1), 5)
        

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
    
    #The desired length of the output array    
    desired_length = int(np.ceil(plugin._config["input_shape"][0] / 2 + 1))
   
    # I pad here, because technically this is only necessary due to the pre-allocation requirements in pydidas, dynamic allocation is not yet supported
    # Padding length needed to reach the desired length
    padding_length = desired_length - expected.array.shape[1]

    # Pad only the column dimension (2nd dimension) at the end
    padded_array = np.pad(expected.array, ((0, 0), (0, padding_length)), mode='constant', constant_values=np.nan)
    padded_axis_ranges = np.pad(expected.axis_ranges[1], (0, padding_length), mode='constant', constant_values=1)

    #Calculation for test
    result = plugin._create_final_result_sin2chi_method(d_spacing_combined)

    assert nan_allclose(result.array, padded_array, atol=1e-8) #due to dummy allocation necessary instead of np.allclose rtol=1e-5, atol=1e-8
    assert np.allclose(result.axis_ranges[1], padded_axis_ranges)
    assert np.allclose(result.axis_ranges[0], expected.axis_ranges[0])
    assert result.data_label == expected.data_label
    assert result.data_unit == expected.data_unit
    
def test__create_final_result_sin2chi_method_precision2(plugin_fixture, d_spacing_datasets):
       
    _, _, d_spacing_combined = d_spacing_datasets
    
    plugin = plugin_fixture
    # This is currently required due to pre-allocation requirements in pydidas, dynamic allocation is not yet supported
    # We can deduct the incoming length of chi-values via the length of the sin2chi axis
    plugin._config["input_shape"] = (18, 5)
        

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

    assert np.allclose(result.array, expected.array,rtol=1e-5, atol=1e-8) 
    assert np.allclose(result.axis_ranges[1], expected.axis_ranges[1])
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
    plugin._config["input_shape"] = (5, 5) #chose this to avoid padding as above
    
    
    d_spacing_combined, d_spacing_result = results_sin2chi_method_fixture
    
    result = plugin._create_final_result_sin2chi_method(d_spacing_combined)
    

    assert np.array_equal(result.array, d_spacing_result.array)
    # Compare each key-value pair in the axis_ranges
    for key, value in result.axis_ranges.items():
        assert key in d_spacing_result.axis_ranges.keys()
        assert np.array_equal(value, d_spacing_result.axis_ranges[key])
    assert result.axis_labels == d_spacing_result.axis_labels
    assert result.data_label == 'd_spacing'
    assert result.data_unit == d_spacing_result.data_unit