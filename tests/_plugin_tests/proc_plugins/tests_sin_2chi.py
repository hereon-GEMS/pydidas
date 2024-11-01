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
Tests for the DspacingSin_2chi class / plugin.
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
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED

from pydidas.core import Dataset, UserConfigError

from pydidas_plugins.proc_plugins.sin_2chi import (PARAMETER_KEEP_RESULTS, LABELS_SIN2CHI, LABELS_SIN_2CHI, LABELS_SIN2CHI,
                                                            LABELS_DIM0, UNITS_NANOMETER, UNITS_ANGSTROM)


@pytest.fixture
def plugin_fixture():
    return PluginCollection().get_plugin_by_name('DspacingSin_2chi')()


@pytest.fixture()
def base_dataset_factory():
    def factory(unit):
        
        data_array=np.array([[1]*5, [3]*5, [2]*5])
    
        # For x =np.arctan(2) [rad], it is sin^2(x) =  sin(2*x)
        # This simplfies this test case. 
        # Needs probably adjusment in the low energy regime, where psi is used instead of chi.
        
        return Dataset(
            data_array,
            axis_labels={0: LABELS_DIM0, 1: LABELS_SIN2CHI},
            axis_ranges = {
            0: np.arange(data_array.shape[0]),
            1: np.full((1, data_array.shape[1]), np.sin(np.arctan(2))**2)
            },
            axis_units={0: '' , 1:''},
            data_label= 'd_spacing', 
            data_unit = unit,
        )
    return factory

@pytest.mark.parametrize("unit, expected_unit", [
    (UNITS_ANGSTROM, UNITS_ANGSTROM),
    (UNITS_NANOMETER, UNITS_NANOMETER)
]) 
def test_execute_validation_basic(plugin_fixture, base_dataset_factory, unit, expected_unit):
    dataset = base_dataset_factory(unit)
    result , _ = plugin_fixture.execute(dataset)
    
    print('Result axis_ranges[1]', result.axis_ranges[1].shape)
    
    assert result is not None
    assert result.data_unit == expected_unit
    assert result.data_label == 'Difference of d(+) - d(-)'
    assert result.axis_labels[0] == '0: d-, 1: d+, 2: d(+)-d(-)'
    assert result.axis_labels[1] == LABELS_SIN_2CHI
    assert result.axis_units[0] == ''
    assert result.axis_units[1] == ''
    assert np.all(result.axis_ranges[0] == dataset.axis_ranges[0])
    # See comment in base_dataset_factory for line below
    assert np.all(result.axis_ranges[1] == np.full((1, result.shape[1]), np.sin(2*np.arctan(2))))
    assert np.all(result.data == np.array([[1]*5, [3]*5, [2]*5]))   
    assert result.shape == (3, 5)
    assert result.shape[1] == result.axis_ranges[1].shape[1]
    

        
@pytest.mark.parametrize("input_vals, expected_output", [
    (np.array([0]), np.array([0])),           # sin²(chi) = 0 should return sin(2*chi) = 0
    (np.array([0.25]), np.array([0.8660254])),  # sin²(chi) = 0.25 → sin(2*chi) ≈ 0.8660254
    (np.array([0.5]), np.array([1.0])),         # sin²(chi) = 0.5 → sin(2*chi) ≈ 1.0
    (np.array([1]), np.array([0]))             # sin²(chi) = 1 should return sin(2*chi) = 0
])
def test__calculate_sin2_chi_values_valid_inputs(plugin_fixture, input_vals, expected_output):
    result = plugin_fixture._calculate_sin_2chi_values(input_vals)
    npt.assert_allclose(result, expected_output, rtol=1e-6, atol=1e-6)
    
    
# Test input validation for non-ndarray input types
@pytest.mark.parametrize("invalid_input", [
    [0, 0.25, 0.5, 1],  # list input
    "0.25",              # string input
    0.25,                # scalar input
    None,                # NoneType input
])
def test__calculate_sin2_chi_values_invalid_input_type(plugin_fixture, invalid_input):
    with pytest.raises(UserConfigError, match="Input must be an instance of np.ndarray."):
        plugin_fixture._calculate_sin_2chi_values(invalid_input)   

@pytest.mark.parametrize("invalid_value", [
    np.array([-0.1]),  # value below 0
    np.array([1.1])    # value above 1
])
def test__calculate_sin2_chi_values_invalid_s2c_values(plugin_fixture, invalid_value):
    with pytest.raises(UserConfigError, match="Values in s2c_values must be between 0 and 1 inclusive."):
        plugin_fixture._calculate_sin_2chi_values(invalid_value)


@dataclass
class DSpacingTest:
    d_neg: np.ndarray
    d_pos: np.ndarray
    d_mean: np.ndarray
    s2c_values: np.ndarray
    s_2c_values_expected: np.ndarray
    d_diff_expected: np.ndarray
    
    def create_input_ds(self):
        return Dataset(
            np.array([self.d_neg, self.d_pos, self.d_mean]),
            axis_labels={0: LABELS_DIM0, 1: LABELS_SIN2CHI},
            axis_ranges={ 0: np.arange(3), 1: self.s2c_values},
            axis_units={0: '' , 1:''},
            data_label= 'd_spacing', 
            data_unit = UNITS_ANGSTROM,
        )


case1 = DSpacingTest(
    d_neg=np.array([1, 2, 3, 5, 6]),
    d_pos=np.array([2, 3, 4, 4, 5]),
    d_mean=np.array([1.5, 2.5, 3.5, 4.5, 5.5]),
    s2c_values=np.full((1,5), [0.5]),
    s_2c_values_expected=np.full((1, 5), [1.0]),
    d_diff_expected=np.array([1, 1, 1, -1, -1])
)

case2= DSpacingTest(
    d_neg=np.array([1, np.nan, 3, np.nan, 6]),
    d_pos=np.array([np.nan, 3, np.nan, 4, 5]),
    d_mean=np.array([np.nan, np.nan, np.nan, np.nan, 5.5]),
    s2c_values=np.full((1,5), np.pi/4),
    s_2c_values_expected=np.full((1, 5), 8.21091684e-01),
    d_diff_expected=np.array([np.nan, np.nan, np.nan, np.nan, -1]),
)

case3 = DSpacingTest(
    d_neg = np.array([-5,-4,-3,-2,-1]),
    d_pos= np.array([-4,-3,-2,-1,0]),
    d_mean= np.array([-4.5,-3.5,-2.5,-1.5,-0.5]),
    s2c_values=np.full((1,5), 0.5),
    s_2c_values_expected=np.full((1, 5), [1.0]),
    d_diff_expected=np.array([1, 1, 1, 1, 1])
)
 
 
case4 = DSpacingTest(
    d_neg = np.array([-5,-4,-3,-2,-1]),
    d_pos= np.array([1,-5,-6,1,1]),
    d_mean= np.array([-2,-4.5, -4.5,-0.5,0]),
    s2c_values=np.full((1,5), 0.5),
    s_2c_values_expected=np.full((1, 5), [1.0]),
    d_diff_expected=np.array([6, -1, -3, 3, 2])
)   
    

test_cases = [case1, case2, case3, case4]
@pytest.mark.parametrize("case", test_cases)
def test_execute_validation(plugin_fixture, case):
    plugin = plugin_fixture
    ds = case.create_input_ds()
    result, _ = plugin.execute(ds)
    
    # Validate the results
    np.testing.assert_array_almost_equal(result[2, :], case.d_diff_expected)
    np.testing.assert_array_almost_equal(result.axis_ranges[1], case.s_2c_values_expected)
    assert result.data_unit == UNITS_ANGSTROM
    assert result.data_label == 'Difference of d(+) - d(-)'
    assert result.axis_labels[0] == '0: d-, 1: d+, 2: d(+)-d(-)'
    assert result.axis_labels[1] == LABELS_SIN_2CHI
    assert result.shape[0] ==3 
    assert result.shape[1] == ds.shape[1]
    
    
    

