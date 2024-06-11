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

import os
import h5py as h5
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
import matplotlib.cm as cm
from scipy.optimize import curve_fit
from pydidas.core import Dataset
from pydidas.data_io import import_data


from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


import pytest
import ipytest
ipytest.autoconfig() 

def print_compmat(matrix):
    """
    Prints a NumPy array compactly with each element formatted to two decimal places,
    handling large matrices and NaN values effectively.
    
    Parameters:
    - matrix (np.ndarray): The NumPy array to be printed with formatted values.
    """
    np.set_printoptions(precision=4, suppress=True, linewidth=100, threshold=np.inf, nanstr='nan')
    print(matrix)
    np.set_printoptions()  # Reset to default after printing

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

# Example usage:
#y_range = np.arange(2, 8)
#x_range = np.arange(0, 5)
# Labels string with potentially custom metrics not predefined
#extended_labels = '0: mystery; 1: position; 2: area; 3: background at peak; 4: total count intensity'
#result = generate_spatial_fit_res(y_range, x_range, fit_labels=extended_labels)
#print(result.shape)  # Expect (6, 5, 36, 5) for a 4D array with custom and predefined labels

def adding_noise_d_spacing(ds1, scaling=7e-2):
    '''
    ds [Dataset], two-dimensional Dataset, expecting in first column d-spacing values.
    '''
    #Introducing seed and random noise for d_spacing
    rng = np.random.default_rng(seed=9973)
    ds1[:,0]+=(0.5-rng.random(ds1.shape[0]))*scaling
    
    return ds1     


#visualisation
def plot_d_spacing_vs_chi(result_array, chi, positions):
    """
    Plots d_spacing vs chi for specified (x, y) positions in the result array using Matplotlib's OOP interface.

    Parameters:
        result_array (numpy.ndarray): The 4D array containing measurement data.
        chi (numpy.ndarray): The array of chi values.
        positions (list of tuples): A list of (x_index, y_index) tuples specifying the positions to plot.
    """
    
    fig, ax = plt.subplots()
    for (x_index, y_index) in positions:
        # Extract d_spacing for the specific position
        d_spacing = result_array[x_index, y_index, :, 0]  # d_spacing is the first property in the last dimension
        
        # Plotting using the axes object
        ax.plot(chi, d_spacing, label=f'(x={x_index}, y={y_index})', marker='o', linestyle='--')
    
    ax.set_xlabel('chi [deg]')
    ax.set_ylabel('d_spacing')
    ax.set_title('d_spacing vs chi for various x,y')
    ax.grid(True)
    
    ax.legend()
    plt.show()
    
    
def chi_pos_verification(ds):
    '''
    Verification if dataset ds contains 'chi' and 'position' for d-spacing.
    Returns:
        chi_key: The index associated with 'chi'.
        position_key: A tuple where the first element is the index in axis_labels where 'position' descriptor is found, and the second element is the key in the structured string resembling a dict.    
    '''
    if not isinstance(ds, Dataset):
        raise TypeError('Input has to be of type Dataset.')
        
    axis_labels=ds.axis_labels
    
    # Collect indices where 'chi' is found
    chi_indices = [key for key, value in axis_labels.items() if value == 'chi']

    # Check for multiple 'chi'
    if len(chi_indices) > 1:
        raise KeyError('Multiple "chi" found. Check your dataset.')

    # Check for absence of 'chi'
    if not chi_indices:
        raise ValueError('chi is missing. Check your dataset.')

    # Assuming there's exactly one 'chi', get the index
    chi_key = chi_indices[0]

    reverse_axis_labels = dict(zip(axis_labels.values(), axis_labels.keys()))

    # Process to find 'position' in the complex structured string
    position_key = None
    for value, position_index in reverse_axis_labels.items():
        if isinstance(value, str) and 'position' in value:
            parts = value.split(';')
            for part in parts:
                if 'position' in part:
                    # Assume the part is structured as 'key: description'
                    part_key, _ = part.split(':')
                    part_key = int(part_key.strip())  # Convert the key part to integer
                    position_key = (position_index, part_key)
                    break
            if position_key is not None:
                break

    # Check if 'position' is found
    if position_key is None:
        raise ValueError('Key containing "position" is missing. Check your dataset.')

    return (chi_key, position_key)


def extract_d_spacing(ds1, pos_key, pos_idx):
    '''
    Extracts d-spacing
    
    Parameters: 
    - ds1 (Dataset): A Dataset object
    - pos_key (int): Key containing 'position' information
    - pos_idx (int): Index containing 'position' information in substring 
    
    '''    
    _slices = []
    for _dim in range(ds1.ndim):
        if _dim != pos_key:
            _slices.append(slice(None, None))
        elif _dim == pos_key:
            _slices.append(slice(pos_idx, pos_idx + 1))
        #print(f"Dimension {_dim}, Slices: {_slices}")
        
    d_spacing = ds1[*_slices]
    d_spacing = d_spacing.squeeze()
        
    return d_spacing
    
def ds_slicing(ds1):
    '''
    Extracts d-spacing values and associated chi values from a Dataset object for one scan position.

    Parameters:
    - ds1 (Dataset): A Dataset object. 

    Returns:
    - chi (array-like): Array of chi values associated with the extracted d-spacing values.
    - d_spacing (array-like): Array of d-spacing values extracted from the Dataset object.

    Raises:
    - TypeError: If the input is not of type Dataset.
    - ValueError: If the dimension of the d_spacing is not 1.
    '''

    if not isinstance(ds1, Dataset):
        raise TypeError('Input has to be of type Dataset.')
      
    chi_key, (pos_key, pos_idx) = chi_pos_verification(ds1)
    
    #select the chi values
    chi=ds1.axis_ranges[chi_key]
    
    # Extract d-spacing values
    d_spacing = extract_d_spacing(ds1, pos_key, pos_idx)
    
    if d_spacing.size == 0: 
        #Should check for empty arrays in case of slicing beyond bounds
        raise ValueError('Array is empty.')
    
    if not d_spacing.ndim == 1: 
        raise ValueError('Dimension mismatch.')
                       
    return chi, d_spacing

def main():
    
    #Creating of dummy data
    delta_chi = 10
    chi_start= -180
    chi_stop= 180
    phase_shift = 70
    chi=chi_gen(chi_start, chi_stop, delta_chi)
    print(chi)
    print('Laenge chi', len(chi))

    #x, y in um
    y = np.arange(2, 8)
    x = np.arange(0, 5)

    #labels
    fit_labels= '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    fit_labels_dict = {int(item.split(":")[0].strip()): item.split(":")[1].strip() for item in fit_labels.split(";")}
    num_labels = len(fit_labels_dict)
    
    #creation of Pydidas Dataset
    axis_labels= ['y', 'x', 'chi', fit_labels]
    axis_ranges = {0: y, 1:x, 2: chi , 3: np.arange(num_labels)} 
    
   
    result_array_spatial = generate_spatial_fit_res(y, x, chi_start,chi_stop, delta_chi, fit_labels , spatial_var=True, phase_shift=phase_shift)
    #result_array = generate_spatial_fit_res(y, x, chi_start,chi_stop, delta_chi, fit_labels , spatial_var=False)
    print('Result array spatial', result_array_spatial.shape)

    
    #visualisation
    #positions = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    #plot_d_spacing_vs_chi(result_array_spatial, chi, positions)
    #plot_d_spacing_vs_chi(result_array, chi, positions)


    ds = Dataset(result_array_spatial,  axis_labels=axis_labels, axis_ranges=axis_ranges)
    axis_labels = ds.axis_labels
    print(axis_labels)
    print(ds.shape)
    
    #choose random location in ds
    y_idx = 5
    x_idx = 3
    
    # slice Dataset based on location
    ds1 = ds[y_idx, x_idx]
      
    print('Shape of ds1 dataset before ', ds1.shape)
    
    #Introducing seed and random noise for d_spacing
    ds1 = adding_noise_d_spacing(ds1, scaling=4e-2)
    
    #Introducing np.nan 
    #print('Content ds1 array',  ds1.array[:,0])
    #ds1.array[0:9:2,0] = np.nan
    #ds1.array[18:28:2,0] = np.nan
        
    print('Shape of ds1 dataset ', ds1.shape)
    print('Content ds1 array after',  ds1.array[:,0])
      
    chi_key, (pos_key, pos_idx) = chi_pos_verification(ds1)
    print(chi_key, pos_key, pos_idx)
    
    chi, d_spacing = ds_slicing(ds1)    
    
    d_spacing_pos, d_spacing_neg=group_d_spacing_by_chi(d_spacing, chi)
    print('s2c_pos', d_spacing_pos.axis_ranges[0])
    print('d_spacing_pos', d_spacing_pos.array)
    print('s2c_neg', d_spacing_neg.axis_ranges[0])
    print('d_spacing_neg', d_spacing_neg.array)
    
    d_spacing_combined = combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg)
    print(d_spacing_combined) 
    
    d_diff= np.diff(d_spacing_combined.array, axis=0).squeeze()
    x_diff = np.sin(2*np.arcsin(np.sqrt(d_spacing_combined.axis_ranges[1])))
    
    print('d_diff', d_diff)
    print('x_diff', x_diff)
    print(d_spacing_combined.axis_ranges[1])
    
    fig, ax = plt.subplots()
    ax.plot(x_diff, d_diff, linestyle='None', marker='o')
    ax.set_title('d(+) - d(-) vs sin(2*chi)')
    ax.set_xlabel('sin(2*chi)')
    ax.set_ylabel('d(+) - d(-) [nm]')
    ax.grid()
    fig.show()
    
    

def allclose_ignore_nan(a, b, atol=1e-15):
    '''
    Compare arrays a and b element-wise, ignoring np.nan values and considering only numerical values.
    
    Parameters:
    - a (np.ndarray): First array to compare.
    - b (np.ndarray): Second array to compare.
    - atol (float): Absolute tolerance for the comparison.
    
    Returns:
    - bool: True if the numerical values in the arrays are element-wise equal within the given tolerance, ignoring np.nan values.
    '''
    # Mask to identify valid (non-nan) elements in both arrays
    valid_mask_a = ~np.isnan(a)
    valid_mask_b = ~np.isnan(b)
    
    # Combined mask to filter out positions where either a or b has np.nan
    combined_mask = valid_mask_a & valid_mask_b
    
    # Filtered arrays
    filtered_a = a[combined_mask]
    filtered_b = b[combined_mask]
    
    # Compare the filtered arrays
    return np.allclose(filtered_a, filtered_b, atol=atol)


def combine_sort_d_spacing_pos_neg(d_spacing_pos, d_spacing_neg):
    '''
    Combines the positive and negative slopes of d_spacing and sorts them in ascending order of sin2chi.
    Parameters:
    - d_spacing_pos (Dataset): Dataset of d_spacing values for positive slopes.
    - d_spacing_neg (Dataset): Dataset of d_spacing values for negative slopes.
    Returns:
    - d_spacing_combined (Dataset): Dataset of combined d_spacing values.
    '''
    # Check if the input is of type Dataset
    if not isinstance(d_spacing_pos, Dataset) or not isinstance(d_spacing_neg, Dataset):
        raise TypeError('Input has to be of type Dataset.')
    
    # Check if the axis labels are the same
    if d_spacing_pos.axis_labels != d_spacing_neg.axis_labels:
        raise ValueError('Axis labels do not match.')
    
    # Check if the axis ranges are the same, 
    # Create a mask for non-nan values in both arrays
    s2c_axis_pos = d_spacing_pos.axis_ranges[0]
    s2c_axis_neg = d_spacing_neg.axis_ranges[0]
    
    print('Axis ranges pos', s2c_axis_pos)
    print('Axis ranges neg', s2c_axis_neg)

    # Check if the axis ranges are the same, atol=1e-15 relative tolerance
    comparison = allclose_ignore_nan(s2c_axis_pos, s2c_axis_neg, atol=1e-15)
    if not comparison:
        raise ValueError('Axis ranges do not match.')

    if s2c_axis_pos.shape != s2c_axis_neg.shape:
        raise ValueError("Axis ranges do not have the same length.")

    # Make copies of the arrays
    s2c_axis_pos_copy = np.copy(s2c_axis_pos)
    d_spacing_pos_copy = np.copy(d_spacing_pos)
    s2c_axis_neg_copy = np.copy(s2c_axis_neg)
    d_spacing_neg_copy = np.copy(d_spacing_neg)
    
    # Get the indices that would sort s2c_mean_pos_copy in ascending order
    sorted_idx_pos = np.argsort(s2c_axis_pos_copy, kind='mergesort')
    sorted_idx_neg = np.argsort(s2c_axis_neg_copy, kind='mergesort')
    
    # Sorting the arrays
    s2c_axis_pos_sorted = s2c_axis_pos_copy[sorted_idx_pos]
    d_spacing_pos_sorted = d_spacing_pos_copy[sorted_idx_pos]
    s2c_axis_neg_sorted = s2c_axis_neg_copy[sorted_idx_neg]
    d_spacing_neg_sorted = d_spacing_neg_copy[sorted_idx_neg]
     
    d_spacing_combi_arr = np.vstack((d_spacing_neg_sorted, d_spacing_pos_sorted))
       
      
    d_spacing_combined = Dataset(d_spacing_combi_arr , 
                                 axis_ranges={0: np.arange(2), 1:  s2c_axis_pos_sorted}, 
                                 axis_labels={0: ['d-', 'd+'], 1: 'sin2chi'})
    
    print(d_spacing_combined.shape)
    print(d_spacing_combined.axis_ranges)
    
    fig, ax =plt.subplots()
    ax.plot(d_spacing_combined.axis_ranges[1], d_spacing_combined.array[0,:], label='d-', linestyle='None', marker='s')
    ax.plot(d_spacing_combined.axis_ranges[1], d_spacing_combined.array[1,:], label='d+',linestyle='None',  marker='o')
    ax.plot(d_spacing_combined.axis_ranges[1], np.nanmean(d_spacing_combined.array[:,:], axis=0), label ="'d+'+'d-'/2", linestyle='None',  marker='x')
    ax.set_ylabel('d [nm]')
    ax.set_xlabel('sin^2(chi)')
    ax.set_title('sin^2(chi) vs d_spacing')
    fig.legend()
    ax.grid()
    fig.show()
    # (d+ +d-)/2 in general np.mean(d+,d-)
    # d(+) - d(-) vs sin(2*chi)  #different graph, linear fit, force through 0
    
    
    
    return d_spacing_combined
    

def idx_s2c_grouping(chi, tolerance=1e-4):
        
    '''
    Find all chis belonging to the same sin(chi)**2 values within the tolerance value. 
    Parameters:
    - chi (np.ndarray): Array of chi angles in degrees. This should be a 1D numpy array.
    - tolerance (float, optional): The tolerance level for grouping sin^2(chi) values.
        Defaults to 1e-4. This ensures all different groups are caught. 

    Returns:
    - n_components (int): The number of unique groups formed.
    - s2c_labels (np.ndarray): An array of the same shape as chi, where each element
        is an integer label corresponding to the group of its sin^2(chi) value.
        
    Raises:
    - TypeError: If the input `chi` is not a numpy ndarray.
        
    '''
    if not isinstance(chi, np.ndarray):
        raise TypeError('Chi needs to be an np.ndarray.')


    s2c=np.sin(np.deg2rad(chi))**2
    arr=s2c

    # Create the similarity matrix
    similarity_matrix = np.abs(arr - arr[:, np.newaxis]) < tolerance

    # Convert boolean matrix to sparse matrix
    sparse_matrix = csr_matrix(similarity_matrix.astype(int))

    # Find connected components
    n_components, s2c_labels = connected_components(csgraph=sparse_matrix, directed=False, return_labels=True)

    return n_components, s2c_labels

def group_d_spacing_by_chi(d_spacing, chi, tolerance=1e-4):
    '''
    Parameters:
    - chi (np.ndarray): Array of chi angles in degrees. This should be a 1D numpy array.
    - d_spacing (pydidas Dataset): Dataset of d_spacing values. 
    - tolerance (float): The tolerance level for grouping sin^2(chi) values.
    Defaults to 1e-4. This ensures all different groups are caught. 
    '''

    if not isinstance(chi, np.ndarray):
        raise TypeError('Chi has to be of type np.ndarray')
    
    if not isinstance(d_spacing, Dataset):
        raise TypeError('d_spacing has to be of type Pydidas Dataset.')
    
    
    # n_components: number of groups after grouping
    # s2c_lables: sin2chi divided into different groups 
    n_components, s2c_labels = idx_s2c_grouping(chi, tolerance=tolerance)
        
    # Calculate sin2chi
    s2c=np.sin(np.deg2rad(chi))**2
    
    # both are ordered in ascending order of increasing sin2chi
    s2c_unique_labels = np.unique(s2c_labels)
    s2c_unique_values = s2c[s2c_unique_labels]
        
    
    print('s2c_labels', s2c_labels)
    print('chi', chi)
    print('s2c_values', s2c)
    print('s2c unique labels', np.unique(s2c_labels))
    print('s2c unique values', s2c[np.unique(s2c_labels)])
    print('s2c', s2c.shape, s2c)
    
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
    categories[(first_derivative >= -zero_threshold) & (first_derivative <= zero_threshold)] = 1
        
    #Filter
    # values close to zero (categories == 1) are added to both sides of the maximum or minimum
    mask_pos = (categories == 2) | (categories == 1 )
    mask_neg = (categories == 0)  | (categories == 1 )
    
    idx_pos_slope= np.zeros_like(chi)
    idx_neg_slope= np.zeros_like(chi)
    
    # Applying the mask. Set values to 1 where True, 0 otherwise
    idx_pos_slope[mask_pos] = 1
    idx_neg_slope[mask_neg] = 1
    
    # Print the result
    print("idx_pos_slope:", np.flatnonzero(idx_pos_slope))
    print("idx_neg_slope:", np.flatnonzero(idx_neg_slope)) 

    
    # Advanced indexing 
    # Here, s2c_labels specifies the row indices, and np.arange(s2c_num_elements) specifies the column indices. 
    s2c_advanced_idx = (s2c_labels, np.arange(s2c.size))
    
    s2c_labels_matrix = np.full((s2c_unique_labels.size, s2c.size), np.nan)
    s2c_labels_matrix[*s2c_advanced_idx] = s2c_labels
    
    
    d_spacing_matrix = np.full((s2c_unique_labels.size, s2c.size), np.nan)
    d_spacing_matrix[*s2c_advanced_idx] = d_spacing
    
    s2c_matrix = np.full((s2c_unique_labels.size, s2c.size), np.nan)
    s2c_matrix[*s2c_advanced_idx] = s2c
    
    
    # Create filtered matrices based on the slopes
    d_spacing_pos_slope_matrix = np.full_like(d_spacing_matrix, np.nan)  
    d_spacing_neg_slope_matrix = np.full_like(d_spacing_matrix, np.nan) 
    s2c_pos_slope_matrix = np.full_like(d_spacing_matrix, np.nan)  
    s2c_neg_slope_matrix = np.full_like(d_spacing_matrix, np.nan)  
    
    # Apply masks to create filtered matrices
    # Combination of advanced indexing and conditional assignment with np.where
    d_spacing_pos_slope_matrix[*s2c_advanced_idx] = np.where(mask_pos, d_spacing, np.nan)
    s2c_pos_slope_matrix[*s2c_advanced_idx] = np.where(mask_pos, s2c, np.nan)

    d_spacing_neg_slope_matrix[*s2c_advanced_idx] = np.where(mask_neg, d_spacing, np.nan)
    s2c_neg_slope_matrix[*s2c_advanced_idx] = np.where(mask_neg, s2c, np.nan)
    
    # Averaging, positive slope
    s2c_mean_pos = np.nanmean(s2c_pos_slope_matrix, axis=1)
    d_spacing_mean_pos = np.nanmean(d_spacing_pos_slope_matrix, axis=1)
    
    # Averaging, negative slope
    s2c_mean_neg = np.nanmean(s2c_neg_slope_matrix, axis=1)
    d_spacing_mean_neg = np.nanmean(d_spacing_neg_slope_matrix, axis=1)
    
    # Aim for a complete common s2c_mean_pos/neg without NaN values
    s2c_mean = np.nanmean(np.vstack((s2c_mean_pos, s2c_mean_neg)), axis=0)
    #TODO:
    #The x-axis values are given by 0..max(s2c_labels) because of the way how the matrices are populated.
    #This has also the advantage of automatic sorting in ascending order.
    #Hence, I think s2c_mean = s2c[s2c_unique_labels] is correct
    print('Comparison of s2c selection:', np.allclose(s2c_mean, s2c[s2c_unique_labels]))
    #If we want s2c[s2c_unique_labels] for the axis_ranges for sin2chi,
    # we don't need to populate the matrixes for s2c_pos_slope_matrix like this
    
    #If we don't use s2c_mean, sometimes on of the s2c_mean_pos or s2c_mean_neg has np.nan    
    print('s2c_mean', s2c_mean) 
    print( 's2c_mean_pos', s2c_mean_pos)
    print('s2c_mean_neg', s2c_mean_neg)
    #create Datasets for output
    #TODO: later to change to s2c[s2c_unique_labels] for s2c_mean
    #d_spacing_pos=Dataset(d_spacing_mean_pos, axis_ranges = {0 : s2c_mean_pos}, axis_labels={0 : 'sin2chi'} )   
    #d_spacing_neg=Dataset(d_spacing_mean_neg, axis_ranges = {0 : s2c_mean_neg}, axis_labels={0 : 'sin2chi'} ) 
    d_spacing_pos=Dataset(d_spacing_mean_pos, axis_ranges = {0 : s2c_mean}, axis_labels={0 : 'sin2chi'} )   
    d_spacing_neg=Dataset(d_spacing_mean_neg, axis_ranges = {0 : s2c_mean}, axis_labels={0 : 'sin2chi'} ) 
    
    
    
    print("Positive Slope Filtered d_spacing:")
    print_compmat(d_spacing_pos_slope_matrix)
    print('\n')
    print_compmat(s2c_pos_slope_matrix)

    print(40*'-')
    print("Negative Slope Filtered d_spacing:")
    print_compmat(d_spacing_neg_slope_matrix)
    print('\n')
    print_compmat(s2c_neg_slope_matrix)

    
    
    print("Mean of Positive Slope Filtered s2c:")
    print_compmat(s2c_mean_pos)
    print('\n')
    print("Mean of Positive Slope Filtered d_spacing:")
    print_compmat(d_spacing_mean_pos)
    
    print(40*'-')
    print("Mean of Negative Slope Filtered s2c:")
    print_compmat(s2c_mean_neg)
    print('\n')
    print("Mean of Negative Slope Filtered d_spacing:")
    print_compmat(d_spacing_mean_neg)
    
    
    fig5, ax5 = plt.subplots()
    im=ax5.imshow(s2c_labels_matrix, origin='lower', interpolation='nearest')
    ax5.set_xlabel('indices')
    ax5.set_ylabel('group')
    ax5.set_title('s2c_labels_matrix')
    fig5.colorbar(im, ax=ax5)
    fig5.show()

    fig, ax =plt.subplots()
    plt.imshow(s2c_matrix, origin='lower',  interpolation='nearest')
    ax.set_title('s2c_values_matrix')
    ax.set_xlabel('indices')
    ax.set_ylabel('group')
    plt.colorbar()
    fig.show()

    bool_arrary_pos_slope = ~np.isnan(s2c_pos_slope_matrix) 
    bool_arrary_neg_slope = ~np.isnan(s2c_neg_slope_matrix)
    
    fig2, axs2 = plt.subplots(2)
    axs2[0].imshow(bool_arrary_pos_slope, origin='lower', interpolation='nearest')
    im=axs2[1].imshow(bool_arrary_neg_slope, origin='lower', interpolation='nearest')
    axs2[0].set_title('Positive slope')
    axs2[0].set_xlabel('indices')

    axs2[0].set_ylabel('group')
    axs2[1].set_title('Negative slope')
    axs2[1].set_xlabel('indices')
    axs2[1].set_ylabel('group')
    fig2.subplots_adjust(hspace=0.5)  # Adjust horizontal space
    fig2.colorbar(im, ax=axs2.ravel().tolist())
    fig2.show()

    
    fig3, ax3 = plt.subplots(2)
    im=ax3[0].imshow(d_spacing_pos_slope_matrix, vmin=0, vmax=26, origin='lower', interpolation='nearest')
    im=ax3[1].imshow(d_spacing_neg_slope_matrix, vmin=0, vmax=26,  origin='lower', interpolation='nearest')
    ax3[0].set_title('Positive slope')
    ax3[0].set_xlabel('indices')
    ax3[0].set_ylabel('group')
    ax3[1].set_title('Negative slope')
    ax3[1].set_xlabel('indices')
    ax3[1].set_ylabel('group')
    # Adjust the spacing
    fig3.subplots_adjust(hspace=0.5)  # Adjust horizontal space
    fig3.colorbar(im, ax=ax3.ravel().tolist())
    fig3.show()

    print('d_spacing', d_spacing.size, d_spacing.array)
    print('dmean_pos',d_spacing_mean_pos)
    print('s2c_mean_pos',s2c_mean_pos)
    
    print('dmean_neg',d_spacing_mean_neg)
    print('s2c_mean_neg',s2c_mean_neg)
    print('s2c_labels', s2c_labels)
        
    
    print('d_spacing_pos',d_spacing_pos.array)
    print('d_axis_ran_pos',d_spacing_pos.axis_ranges[0])
    
    print('d_spacing_neg',d_spacing_neg.array)
    print('d_axis_ran_neg',d_spacing_neg.axis_ranges[0])
    
    fig4, ax4 = plt.subplots()
    ax4.plot(d_spacing_pos.axis_ranges[0], d_spacing_pos.array, label='pos', linestyle='None', marker='o', color='r')
    ax4.plot(d_spacing_neg.axis_ranges[0], d_spacing_neg.array, label='neg', linestyle='None', marker='x', color='b')
    ax4top=ax4.twiny()
    ax4top.set_xlim(ax4.get_xlim())
    x_index = np.arange(0, len(chi), step=4) #step=4 equals interval=4
    formatted_labels = [f'{val:.2f}' for val in chi[x_index]]
    ax4top.set_xticks(x_index)
    ax4top.set_xticklabels(formatted_labels)
    ax4top.set_xlabel('chi [deg]')
    fig4.suptitle('d_spacing_pos, d_spacing_neg vs. sin2chi')
    fig4.supylabel('d_spacing')
    fig4.supxlabel(d_spacing_pos.axis_labels[0])
    fig4.legend()
    ax4.grid()
    fig4.show()
    
    # ----------  2nd way of validation 
    print('2nd way of validation')
    unique_groups = np.unique(s2c_labels)
        
    
    fig3, ax3 = plt.subplots()
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()

    cmap1 = plt.get_cmap('inferno')
    #reversing the original colormap using reversed() function 
    cmap2 = plt.get_cmap('viridis')
    cmap2r = cmap2.reversed() 
    cmap3 = plt.get_cmap('rainbow')
    cmap3r = cmap3.reversed() 
    
    
    #Dynamic length of matrices
    max_len = 0
    for group in unique_groups:
        mask_pos = (s2c_labels == group) & ((categories == 2) | (categories == 1 ))
        mask_neg = (s2c_labels == group) & ((categories == 0) | (categories == 1 ))
        
        d_pos = d_spacing[mask_pos]
        d_neg = d_spacing[mask_neg]
        
        len_d_pos = len(d_pos)  
        len_d_neg = len(d_neg)  
        
        current_max = max(len_d_pos, len_d_neg)
        
        if current_max > max_len:
            max_len = current_max

    print('max_len', max_len)  
    #array creation with initialization           
    data_pos = np.full((n_components, max_len +2), np.nan) #group, max value for d_spacing for pos slope, average = max_len+2 
    data_neg = np.full((n_components, max_len +2), np.nan)
    data = np.full((n_components, 2*max_len+1), np.nan)
    
    #Chi indices
    idx_chi= np.arange(0,len(chi),1)  
    
    for group in unique_groups:
        
        mask_pos = (s2c_labels == group) & ((categories == 2) | (categories == 1 ))
        mask_neg = (s2c_labels == group) & ((categories == 0) | (categories == 1 ))
        
        chi_combi_pos = chi[mask_pos]
        chi_combi_neg = chi[mask_neg]
        
        d_pos = d_spacing[mask_pos]
        d_neg = d_spacing[mask_neg]
        
        print('group', group)
        print('pos branch, neg branch')
        print(chi_combi_pos, chi_combi_neg)
        print(np.sin(np.deg2rad(chi_combi_pos))**2, np.sin(np.deg2rad(chi_combi_neg))**2)
        print(d_pos.array, d_neg.array)
        
        
        idx_chi_pos =  idx_chi[mask_pos]
        idx_chi_neg =  idx_chi[mask_neg]
        #print('idx', idx_chi_pos, idx_chi_neg)

        data_pos[group,0] = group
        data_neg[group,0] = group
        data[group,0] = group

        # Check the length of d_pos to see if it should be assigned
        if len(d_pos) > 0:
            data_pos[group, 1:len(d_pos)+1] = d_pos
            print('Hallo here', d_pos.array, np.nanmean(data_pos[group, 1:len(d_pos)+1]))
            data_pos[group, -1] = np.nanmean(data_pos[group, 1:len(d_pos)+1])
            
            #replace nan with 0 after averaging
            #data_pos[group,:]=np.nan_to_num(data_pos[group,:], nan=0.0)            
            
            data[group, 1:len(d_pos)+1] = d_pos


        # Check the length of d_neg to see if it should be assigned
        if len(d_neg) > 0:
            data_neg[group, 1:len(d_neg)+1] = d_neg
            data_neg[group, -1] = np.nanmean(data_neg[group, 1:len(d_neg)+1])
            
            #replace nan with 0 after averaging
            #data_neg[group,:]=np.nan_to_num(data_neg[group,:], nan=0.0)   
            
            data[group, -len(d_neg):] = d_neg

        
        #Visualisation for development
        color1 = cmap1(group / (len(unique_groups) - 1)) 
        color2 =  cmap2r(group / (len(unique_groups) - 1)) 
        color3 = cmap3(group / (len(unique_groups) - 1)) 
        color3r = cmap3r(group / (len(unique_groups) - 1)) 
        
        ax.plot(idx_chi_pos, s2c[idx_chi_pos], label=f'{group}$^{{+}}$', marker='o', linestyle='None', markerfacecolor='None', markersize=11, color=color1)
        ax.plot(idx_chi_neg, s2c[idx_chi_neg], label=f'{group}$^{{-}}$', marker='s', linestyle='None', markerfacecolor='None', markersize=6, color=color2)
        ax.set_xlabel('sector index')
        ax.set_ylabel('sin2chi')
        
        ax2.plot(s2c[idx_chi_pos], d_pos, label=f'{group} d$^{{+}}$', marker='o', linestyle='None', markerfacecolor='None', markersize=11, color=color1)
        ax2.plot(s2c[idx_chi_neg], d_neg, label=f'{group} d$^{{-}}$', marker='s', linestyle='None', markerfacecolor='None', markersize=6, color=color2)
    
        
        ax2.plot(np.nanmean(s2c[idx_chi_pos]), np.nanmean(d_pos), marker = 'P', label=f'{group} d$^{{+}}_{{avg}}$', linestyle='None', color=color3)
        ax2.plot(np.nanmean(s2c[idx_chi_neg]), np.nanmean(d_neg), marker = 'X', label=f'{group} d$^{{-}}_{{avg}}$', linestyle='None', color=color3r)

    print('Data:')
    print(data)
    print(30*'-')
    print('Data pos:')
    print(data_pos)
    print('data_pos, last column', data_pos[:,-1].T)
    print(d_spacing_mean_pos)
    print(30*'-')
    print('Data neg:')
    print(data_neg)
    print('data_neg, last column', data_neg[:,-1].T)
    print(d_spacing_mean_neg)
    print(30*'-')
    
    print('Comparison the two methods:')   
    # Use np.isclose to compare numerical values and check for NaN equality
    res_pos=np.isclose(data_pos[:,-1].T, d_spacing_mean_pos, equal_nan=True)
    res_neg=np.isclose(data_neg[:,-1].T, d_spacing_mean_neg,  equal_nan=True)
    print('Comparison pos result:', res_pos)
    print('Comparison neg result:', res_neg)
      

    #Plot d_spacing against chi
    ax3.plot(chi, d_spacing, linestyle='None', marker='*')
    ax3.set_xlabel('chi [degree]')
    ax3.set_ylabel('d_spacing')
    # Create a secondary x-axis for radians
    ax3b = ax3.twiny()  # Create a second x-axis sharing the same y-axis
    ax3b.set_xlim(ax3.get_xlim())  # Ensure the limits of secondary x-axis match the primary
    # Function to convert degree ticks to radians using np.deg2rad
    def degree_to_radian(x):
        return ["{:.2f}".format(deg) for deg in np.deg2rad(x)]
    # Set the radian values based on the degree ticks dynamically
    ax3b.set_xticks(ax3.get_xticks())  # Use the same ticks as the primary axis
    ax3b.set_xticklabels(degree_to_radian(ax3.get_xticks()))  # Convert these ticks to radians
    ax3b.set_xlabel('Radians')
    ax3.set_title('d_spacing vs chi')
    ax3.grid()
    fig3.show()
    

    # Put a legend to the right of the current axis
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.05))
    secax = ax.secondary_xaxis('top')
    interval = 4
    x_index = np.arange(0, len(chi), interval)
    # Limiting the number of decimal places to 2 for the labels
    formatted_labels = [f'{val:.2f}' for val in chi[x_index]]
    secax.set_xticks(x_index)
    secax.set_xticklabels(formatted_labels)
    secax.set_xlabel('chi [deg]')
    ax.grid()
    fig.show()

    # Put a legend to the right of the current axis
    ax2top=ax2.twiny()
    ax2top.set_xlim(ax2.get_xlim())
    formatted_labels = [f'{val:.2f}' for val in chi[x_index]]
    ax2top.set_xticks(x_index)
    ax2top.set_xticklabels(formatted_labels)
    ax2top.set_xlabel('chi [deg]')
    ax2.legend(loc='upper right', bbox_to_anchor=(1.2, 1.05))
    ax2.set_ylabel('d [nm]')
    ax2.set_xlabel('sin^2(chi)')
    ax2.set_title('sin^2(chi) vs d_spacing')
    ax2.grid()
    fig2.show()
   
    
    print('s2c_values', s2c) 
    print('s2c_labels', s2c_labels)  
    print('s2c_val_index_by_lables', s2c[s2c_unique_labels])
    print('chi', chi)
    
    
    print('d_spacing', d_spacing.array)
    print('s2c_mean', s2c_mean)
    #frag David braucht man chi+, chi-
    #Dataset sin2chi und d+, d-
    # fitting for the slope 
    #identify the outliners after averaging, if there is an outliner discard also the corresponding data point (d+ or d-)
    return (d_spacing_pos, d_spacing_neg)
  

if __name__ == "__main__":
    main()
    
    
%%ipytest -vv --tb=long -s  --showlocals

# or at the end ipytest.run('-vv')


def generate_result_array_spatial(x=np.arange(0, 5), fit_labels = None):
  
    y = np.arange(2, 8)  # y-range is always given

    if fit_labels == None:
        fit_labels = '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    
    return generate_spatial_fit_res(y, x, chi_start=-175, chi_stop=180, delta_chi=10, fit_labels=fit_labels, spatial_var=True)

# Example
#res_4d = generate_result_array_spatial()  # This uses both y and x by default
#res_3d = generate_result_array_spatial(None)  # This forces the function to use only y


def test_chi_pos_verification_success():
    
    fit_labels= '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    
    result_array_spatial = generate_result_array_spatial()
    
    axis_labels=['y', 'x', 'chi', fit_labels]
    
    ds=Dataset(result_array_spatial,  axis_labels=axis_labels)
    chi_pos_verification(ds)
        
def test_chi_pos_verification_missing_chi():

    fit_labels= '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'

    result_array_spatial = generate_result_array_spatial()
    
    axis_labels=['y', 'x', 'omega', fit_labels]
    
    ds=Dataset(result_array_spatial,  axis_labels=axis_labels)
       
    with pytest.raises(ValueError) as excinfo:
        chi_pos_verification(ds)
    assert 'chi is missing' in str(excinfo.value)   
       
def test_chi_pos_verification_missing_position():
    
    fit_labels= '0: energy; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    
    result_array_spatial = generate_result_array_spatial(fit_labels=fit_labels)

    axis_labels=['y', 'x', 'chi', fit_labels]

    ds=Dataset(result_array_spatial,  axis_labels=axis_labels)
    with pytest.raises(ValueError) as excinfo:
        chi_pos_verification(ds)
    assert 'Key containing "position" is missing' in str(excinfo.value)  

def test_chi_pos_verification_wrong_input_type():
    
    with pytest.raises(TypeError) as excinfo:
        chi_pos_verification([])  # Pass a list instead of a Dataset
    assert 'Input has to be of type Dataset.' in str(excinfo.value), "Error message should indicate wrong type for Dataset."

    
def test_chi_pos_verification_all_labels_missing():
   
    result_array_spatial = generate_result_array_spatial()
    
    #labels are missing while creating a Dataset
    ds = Dataset(result_array_spatial)
    with pytest.raises(ValueError) as excinfo:
        chi_pos_verification(ds)
    assert 'chi is missing' in str(excinfo.value)
    
def test_multiple_chis_in_labels():

    fit_labels = '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    result_array_spatial = generate_result_array_spatial()
    axis_labels = {0: 'y', 1: 'chi', 2: 'chi', 3: fit_labels}  # 'chi' appears twice, simulated by the same value at different keys
    ds=Dataset(result_array_spatial,  axis_labels=axis_labels)

    with pytest.raises(KeyError) as excinfo:
        chi_pos_verification(ds)
    
    assert "Multiple \"chi\" found" in str(excinfo.value), "Error message should indicate multiple 'chi' were found"


def test_position_not_at_zero():
    
    fit_labels = '1: area; 2: position; 3: FWHM; 4: background at peak; 0: total count intensity'
    
    result_array_spatial = generate_result_array_spatial(fit_labels=fit_labels)
    axis_labels = {0: 'y', 1: 'x', 2: 'chi', 3: fit_labels}
    ds=Dataset(result_array_spatial,  axis_labels=axis_labels)
   
    _, position_key = chi_pos_verification(ds)
    assert position_key == (3, 2), "Expected position key to be (3, 2)"
    
    
def test_position_not_at_zero_3d():
    fit_labels = '1: area; 2: position; 3: FWHM; 4: background at peak; 0: total count intensity'
    results_array_spatial_3d= generate_result_array_spatial(None, fit_labels=fit_labels)
    axis_labels = {0: 'y', 1: 'chi', 2: fit_labels}
    ds=Dataset(results_array_spatial_3d,  axis_labels=axis_labels)
    _, position_key = chi_pos_verification(ds)
    assert position_key == (2, 2), "Expected position key to be (2, 2)"

    
def test_ds_slicing_type_error():
    with pytest.raises(TypeError) as excinfo: 
        ds_slicing([])  # Pass an empty list instead of a Dataset
    assert 'Input has to be of type Dataset.' in str(excinfo.value), "Error message should indicate wrong type for Dataset."
        
def test_ds_slicing_valid():
    fit_labels = '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    result_array_spatial = generate_result_array_spatial()
    axis_labels = {0: 'y', 1: 'x', 2: 'chi', 3: fit_labels}
    ds=Dataset(result_array_spatial,  axis_labels=axis_labels)
    ds = ds[0,0]
    chi, d_spacing = ds_slicing(ds)
    
    assert isinstance(chi, np.ndarray) and isinstance(d_spacing, Dataset)
    
def test_ds_slicing_beyond_bounds():
    fit_labels = '5: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    result_array_spatial = generate_result_array_spatial(fit_labels=fit_labels)
    # position 5 is out of bounds 
    axis_labels = {0: 'y', 1: 'x', 2: 'chi', 3: fit_labels}
    ds=Dataset(result_array_spatial,  axis_labels=axis_labels) 
       
    with pytest.raises(ValueError) as excinfo:
        ds_slicing(ds)
    assert 'Array is empty' in str(excinfo.value), "Error message should indicate that slicing beyond bounds."
    
def test_ds_slicing_dimension_mismatch():
    
    fit_labels = '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    result_array_spatial = generate_result_array_spatial()
    axis_labels = {0: 'y', 1: 'x', 2: 'chi', 3: fit_labels}
    ds=Dataset(result_array_spatial,  axis_labels=axis_labels) 
    
    with pytest.raises(ValueError) as excinfo:
        test=ds_slicing(ds)
    assert 'Dimension mismatch' in str(excinfo.value), "Error message should indicate that d_spacing has a larger dimension."
    
def test_ds_slicing_dimension_mismatch_3d():
    fit_labels = '0: position'
    results_array_spatial_3d= generate_result_array_spatial(None, fit_labels=fit_labels)
    axis_labels = {0: 'y', 1: 'chi', 2: fit_labels}
    ds_3d=Dataset(results_array_spatial_3d,  axis_labels=axis_labels)
    with pytest.raises(ValueError) as excinfo:
        ds_slicing(ds_3d)
    assert 'Dimension mismatch' in str(excinfo.value), "Error message should indicate that d_spacing has a larger dimension."
    


def test_extract_d_spacing_valid():

    fit_labels = '0: position; 1: area; 2: FWHM; 3: background at peak; 4: total count intensity'
    result_array_spatial = generate_result_array_spatial()
    axis_labels = {0: 'y', 1: 'x', 2: 'chi', 3: fit_labels}
    ds=Dataset(result_array_spatial,  axis_labels=axis_labels) 
    pos_key_exp=3
    pos_idx_exp=0
    ds_expected=ds[:, :,:, pos_idx_exp:pos_idx_exp+1].squeeze()
    assert np.array_equal(extract_d_spacing(ds, pos_key_exp, pos_idx_exp), ds_expected)
    
def test_idx_s2c_grouping_basic():
    chi=np.arange(-175, 185, 10)
    n_components, s2c_labels = idx_s2c_grouping(chi, tolerance=1e-3)
    assert n_components > 0
    assert len(s2c_labels) == len(chi)
    
def test_idx_s2c_grouping_tolerance_effectiveness():
    chi = np.array([0, 0.001, 0.002, 0.003])
    n_components, labels = idx_s2c_grouping(chi, tolerance=0.00001)
    assert n_components == 1  # All should be in one group due to small variation and tight tolerance

def test_idx_s2c_grouping_type_error():
    with pytest.raises(TypeError):
        idx_s2c_grouping([0, 30, 60])  # Passing a list instead of np.ndarray
        
def test_idx_s2c_grouping_empty_array():
    chi = np.array([])
    n_components, labels = idx_s2c_grouping(chi)
    assert n_components == 0  # No components should be found
    assert len(labels) == 0  # No labels should be assigned
    
def test_idx_s2c_grouping_extreme_values():
    chi = np.array([-360, 360])
    n_components, labels = idx_s2c_grouping(chi)
    assert n_components == 1  # Extreme but equivalent values should be grouped together

def test_idx_s2c_grouping_very_small_array():
    chi = np.array([0])
    n_components, labels = idx_s2c_grouping(chi)
    assert n_components == 1  # Single value should form one group
    assert len(labels) == 1  # One label for the one value 
    
def test_group_d_spacing_by_chi_basic():
    chi = np.arange(-175, 185, 10)
    d_spacing = Dataset(np.arange(0, len(chi)), axis_ranges={0: chi}, axis_labels={0: 'chi'})
    d_spacing_pos, d_spacing_neg = group_d_spacing_by_chi(d_spacing, chi, tolerance=1e-3)
    assert d_spacing_pos.size == d_spacing_neg.size
    assert d_spacing_pos.size > 0
    assert d_spacing_neg.size > 0
    

    

   