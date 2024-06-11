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
The dataset module includes the Dataset subclasses of numpy.ndarray with additional
embedded metadata.
"""

__author__ = "Gudrun Lotze"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"


from pydidas.core import Dataset
from dataclasses import dataclass
from typing import Callable
from numbers import Real, Integral 


def chi_gen(chi_start, chi_stop, delta_chi):
    if chi_start >= chi_stop:
        raise ValueError('chi_start has to be smaller than chi_stop')
    return np.arange(chi_start, chi_stop, delta_chi)


def predefined_metric_calculation(metric_name, chi, x, y, d0, spatial_var, phase_shift):
    """ Calculate predefined metric based on name, applying spatial variation even if x is not provided. """
    # Handle spatial variation by introducing a default or random x if none is provided
    if x is None and spatial_var:
        x = np.random.uniform(0, 1)  #A random x between 0 and 5
    if metric_name == "position":
        return 0.2832*np.sin(np.deg2rad(chi+phase_shift))**2 + d0 + (0.01 * x if spatial_var else 0)
    if metric_name == "area":
        return np.random.uniform(6, 37, size=len(chi)) + 0.1 * y
    if metric_name == "FWHM":
        return np.random.uniform(0.35, 0.75, size=len(chi))
    if metric_name == "background at peak":
        return np.random.uniform(2.3, 5.3, size=len(chi))
    if metric_name == "total count intensity":
        return np.random.uniform(80, 800, size=len(chi))
    return np.random.uniform(1.5708, 3.141, size=len(chi))  # Fallback for unknown metrics

def generate_spatial_fit_res(y_range, x_range=None, chi_start=-175, chi_stop=180, delta_chi=10, fit_labels=None, spatial_var=True, phase_shift=0):
    '''
    chi [degree]
    phase_shift [degree]
    '''
    
    if fit_labels is None:
        fit_labels = '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    fit_labels_dict = {int(k.split(':')[0].strip()): k.split(':')[1].strip() for k in fit_labels.replace(', ', ';').split(';')}

    chi = chi_gen(chi_start, chi_stop, delta_chi)
    d0 = 25  # in nm

    # Determine the dimensions based on x_range
    if x_range is not None:
        result_array = np.empty((len(y_range), len(x_range), len(chi), len(fit_labels_dict)))
    else:
        result_array = np.empty((len(y_range), len(chi), len(fit_labels_dict)))
        x_range = [None]  # Simulate the absence of x values

    # Perform calculations for each y and x, and across all metrics
    for j, y in enumerate(y_range):
        for i, x in enumerate(x_range):
            fit_results = []
            for idx in sorted(fit_labels_dict.keys()):
                metric_name = fit_labels_dict[idx]
                result = predefined_metric_calculation(metric_name, chi, x, y, d0, spatial_var, phase_shift)
                fit_results.append(result)

            fit_results = np.array(fit_results)
            # Adjust how results are stored based on the presence of x_range
            # Debug print statements
            #print(f"fit_results.T.shape: {fit_results.T.shape}, j: {j}, i: {i}")
            #print('x_range:', x_range)
            if x is not None:
                result_array[j, i, :, :] = fit_results.T
            else:
                result_array[j, :, :] = fit_results.T  # Ensure dimensionality matches expected (len(chi), len(fit_labels_dict))

    return result_array

def generate_result_array_spatial(x=np.arange(0, 5), fit_labels = None):
  
    y = np.arange(2, 8)  # y-range is always given

    if fit_labels == None:
        fit_labels = '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    
    return generate_spatial_fit_res(y, x, chi_start=-175, chi_stop=180, delta_chi=10, fit_labels=fit_labels, spatial_var=True)

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
    d0= 25
    phase_shift=70
    return 0.2832*np.sin(np.deg2rad(chi+phase_shift))**2 + d0

def d_spacing_simu_noise(chi):
    d0=25
    phase_shift=70
    d_spacing=0.2832*np.sin(np.deg2rad(chi+phase_shift))**2 + d0

    mean_value = 1
    # Define the scale parameter for the Laplace distribution
    scale = 0.03 
    # Generate Laplace noise centered around the mean value
    d_spacing_noise = np.random.default_rng(seed=10).laplace(mean_value, scale, size=d_spacing.shape)
    return d_spacing + d_spacing_noise

