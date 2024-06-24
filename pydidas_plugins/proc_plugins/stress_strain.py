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
Module for stress-strain analysis.
"""

__author__ = "Gudrun Lotze"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"

import os
import h5py as h5
import numpy as np

from pydidas.core import Dataset
from pydidas.data_io import import_data

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

#TODO: d_spacing is d-spacing. Or do we want to have q in nm^-1?

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

def extract_units(ds):
    """
    Extract units from data_label in a Pydidas.Dataset, corresponding to parameters in fit_labels.

    Parameters:
    ds (pydidas.Dataset): The dataset containing fit_labels and data_label.

    Returns:
    dict: A dictionary where each key is the index of a fit label, and the value is a list 
          containing the fit label and its corresponding unit. 
          
    Raises:
    TypeError: If ds is not an instance of pydidas.Dataset.
    ValueError: If a unit for any fit label is not found.
    """
        
    # Ensure ds is an instance of Dataset
    if not isinstance(ds, Dataset):
        raise TypeError("Input must be an instance of pydidas.Dataset")
       
    
    chi_key, (pos_key, _) = chi_pos_verification(ds)
            
    data_label = ds.data_label
    fit_labels = ds.axis_labels[pos_key]
    
    # Step 1: Extract parameter names from fit_labels using dictionary comprehension
    fit_labels_dict = {int(item.split(":")[0].strip()): item.split(":")[1].strip() for item in fit_labels.split(";")}
   
    # Step 2: Extract units from data_label
    data_label_dict = {}
    data_label_parts = data_label.split(';')
    for part in data_label_parts:
        if '/' in part:
            name, unit = part.split('/')
            name = name.split(':')[-1].strip()
            unit = unit.strip()
            data_label_dict[name] = unit
    
    # Step 3: Create a mapping of fit_labels (with their indices) to their corresponding units
    result = {}
    for index, param in fit_labels_dict.items():
        try:
            unit = data_label_dict[param]
        except KeyError:
            raise ValueError(f"Unit not found for parameter: {param}")
        result[index] = [param, unit]
    
    return result

def chi_pos_unit_verification(ds):
    """
    Verification of units for chi and position are correct.
    
    Parameters:
    ds (Dataset): A Pydidas Dataset with fitting results. Position contains d_spacing values
    
    Returns:
    bool: True if the units are correct, False otherwise.

    Raises:
    TypeError:  If ds is not an instance of pydidas.Dataset.
    ValueError: If the units for chi or position are not allowed.
  
    """
    if not isinstance(ds, Dataset):
        raise TypeError("Input must be an instance of pydidas.Dataset")
    
    ds_units = extract_units(ds)
    
    #position/pos contains the unit for d_spacing
    pos_units_allowed = ['nm', 'A']
    #TODO: Currently only chi in degree is allowed. If chi [rad] has to be allowed, adjust the calculation of sin^2(chi).
    chi_units_allowed = ['deg']
    
    params_to_check = ['position', 'chi']
    
    for item, val in ds_units.items():
        if item in params_to_check:
            if item == 'position':
                if val not in pos_units_allowed:
                    raise ValueError(f"Unit {val} not allowed for {item}.")
            if item == 'chi':
                if val not in chi_units_allowed:
                    raise ValueError(f"Unit {val} not allowed for {item}.")
    
    return True


def get_param_unit_at_index(ds_units, pos_idx):
    """
    Retrieve the parameter name and unit from the dictionary `ds_units` at a specified index `pos_idx`.
    Verify that 'position' is the parameter name at the specified pos_idx.

    Parameters:
    ds_units (dict): The dictionary containing parameter name and unit pairs.
    pos_idx (int): The index of the parameter to retrieve.

    Returns:
    tuple: A tuple containing the parameter name and its corresponding unit.

    Raises:
    IndexError: If pos_idx is out of range for the dictionary keys.
    ValueError: If 'position' is not the parameter name at the specified pos_idx.
    """
    if pos_idx not in ds_units:
        raise IndexError(f"pos_idx {pos_idx} is out of range for the dictionary keys")

    param_info = ds_units[pos_idx]
    param_name, unit = param_info

    if param_name != 'position':
        raise ValueError(f"The parameter name at pos_idx {pos_idx} is not 'position'")

    return param_name, unit

def extract_d_spacing(ds1, pos_key, pos_idx):
    '''
    Extracts d-spacing
    
    Parameters: 
    - ds1 (Dataset): A Dataset object
    - pos_key (int): Key containing 'position' information
    - pos_idx (int): Index containing 'position' information in substring 
    
    '''    
       
    ds_units = extract_units(ds1)
    key_at_pos_idx, unit_at_pos_idx = get_param_unit_at_index(ds_units, pos_idx)
    
    #slice(None, None, None) is equivalent to "":"" in one dimension of the array. Explicit representation of the slice object shows all three parameters, even if the step parameter is not explicitly provided.
    _slices = []
    for _dim in range(ds1.ndim):
        if _dim != pos_key:
            _slices.append(slice(None, None))
        elif _dim == pos_key:
            _slices.append(slice(pos_idx, pos_idx + 1))
        print(f"Dimension {_dim}, Slices: {_slices}")
     
        
    d_spacing = ds1[*_slices]
    d_spacing = d_spacing.squeeze()
    
    #TODO: Slicing does not work on the data_label
    d_spacing.data_label = key_at_pos_idx
    d_spacing.data_unit = unit_at_pos_idx
        
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
    
    # Identification of chi and position    
    chi_key, (pos_key, pos_idx) = chi_pos_verification(ds1)
    
    #Verification of units for chi and position
    try:
        chi_pos_unit_verification(ds1)
    except (TypeError, ValueError) as e:
        # Handle the error or raise it further if needed
        raise e
  
    
    #select the chi values
    chi=ds1.axis_ranges[chi_key]
    
    # Extract d-spacing values
    d_spacing = extract_d_spacing(ds1, pos_key, pos_idx)
           
    # Slicing out of indeces/bounds returns an empty array
    # Check for empty array
    if d_spacing.size == 0: 
        #Should check for empty arrays in case of slicing beyond bounds
        raise ValueError('Array is empty, slicing out of bounds.')
    
    if not d_spacing.ndim == 1: 
        print('d_spacing.ndim',d_spacing.ndim)
        print(d_spacing)
        raise ValueError('Dimension mismatch.')
                       
    return chi, d_spacing




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
        
    
    #print('s2c_labels', s2c_labels)
    #print('chi', chi)
    #print('s2c_values', s2c)
    #print('s2c unique labels', np.unique(s2c_labels))
    #print('s2c unique values', s2c[np.unique(s2c_labels)])
    #print('s2c', s2c.shape, s2c)
    
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
        
    # Advanced indexing 
    # Here, s2c_labels specifies the row indices, and np.arange(s2c_num_elements) specifies the column indices. 
    s2c_advanced_idx = (s2c_labels, np.arange(s2c.size))
    # expected shape for future matrices
    s2c_groups_matrix_shape = s2c_unique_labels.size, s2c.size
    #print('s2c_groups_matrix_shape', s2c_groups_matrix_shape)
    
    # s2c_label_matrix and d_spacing_matrix are useful for quality assurance via visual inspection
    s2c_labels_matrix = np.full(s2c_groups_matrix_shape, np.nan)
    s2c_labels_matrix[*s2c_advanced_idx] = s2c_labels
    #print('s2c_labels_matrix\n', s2c_labels_matrix)
    
    d_spacing_matrix = np.full(s2c_groups_matrix_shape, np.nan)
    d_spacing_matrix[*s2c_advanced_idx] = d_spacing
    
    s2c_matrix = np.full(s2c_groups_matrix_shape, np.nan)
    s2c_matrix[*s2c_advanced_idx] = s2c
    
    # Create pre-filled matrices for filtering based on the slopes and groups
    d_spacing_pos_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)  
    d_spacing_neg_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan) 
    s2c_pos_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)  
    s2c_neg_slope_matrix = np.full(s2c_groups_matrix_shape, np.nan)  
        
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
    #print('Comparison of s2c selection:', np.allclose(s2c_mean, s2c[s2c_unique_labels]))
    #If we want s2c[s2c_unique_labels] for the axis_ranges for sin2chi,
    # we don't need to populate the matrixes for s2c_pos_slope_matrix like this
    #If we don't use s2c_mean, sometimes one of the s2c_mean_pos or s2c_mean_neg has np.nan, for example, if chi = [0,90] only.
    # This is due to the fact, that the matrices are prepopulated with np.nan.   
    # A way around is to use s2c_mean=s2c[s2c_unique_labels] and this could reduce code above.
    #print('s2c_mean', s2c_mean) 
    #print( 's2c_mean_pos', s2c_mean_pos)
    #print('s2c_mean_neg', s2c_mean_neg)

    
    #create Datasets for output
    #TODO: if wished later to be changed to s2c[s2c_unique_labels] for s2c_mean
    d_spacing_pos=Dataset(d_spacing_mean_pos, axis_ranges = {0 : s2c_mean}, axis_labels={0 : 'sin^2(chi)'}, data_label=f'{d_spacing.data_label}_pos', data_unit=d_spacing.data_unit)   
    d_spacing_neg=Dataset(d_spacing_mean_neg, axis_ranges = {0 : s2c_mean}, axis_labels={0 : 'sin^2(chi)'}, data_label=f'{d_spacing.data_label}_neg', data_unit=d_spacing.data_unit) 
        
    return (d_spacing_pos, d_spacing_neg)

#TODO: Fix this function, no copying
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
    
    if s2c_axis_pos.shape != s2c_axis_neg.shape:
        raise ValueError("Axis ranges do not have the same length.")
       
    comparison = np.allclose(s2c_axis_pos, s2c_axis_neg, atol=1e-15)   
    if not comparison:
        raise ValueError('Axis ranges do not match.')

    #TODO: Is this really necessary?! Probably not.
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
       
    #TODO: Is the data_label how we want them to be?
    d_spacing_combined = Dataset(d_spacing_combi_arr , 
                                 axis_ranges={0: np.arange(2), 1:  s2c_axis_pos_sorted}, 
                                 axis_labels={0: '0: d-, 1: d+', 1: 'sin^2(chi)'}, #TODO: previous: sin2chi
                                 data_label=f'0: {d_spacing_neg.data_label}, 1: {d_spacing_pos.data_label}',
                                 data_unit=d_spacing_pos.data_unit)


    return d_spacing_combined


def pre_regression_calculation(d_spacing_combined):
        ''' 

        Prepares data for regression analysis based on d-spacing values.

        Parameters:
        d_spacing_combined (Dataset): Pydidas Dataset with d-spacing values vs sin^2(chi) values.
            - Shape (2, N) where d_spacing_combined[0, :] represents d(-) values and
            d_spacing_combined[1, :] represents d(+) values.
            - If a value in either d(+) or d(-) is missing (np.nan), it is not taken into account for the calculations.

        Returns:
        d_spacing_avg (Dataset): Pydidas Dataset containing the average of (d(+) + d(-))/2 vs sin^2(chi).
            - axis_ranges[0] corresponds to sin^2(chi).
            - axis_labels[0] is 'sin^2(chi)'.
            - data_label is 'd_spacing_mean'.

        d_spacing_diff (Dataset): Pydidas Dataset containing the difference of d(+) - d(-) vs sin(2*chi).
            - axis_ranges[0] corresponds to sin(2*chi).
            - axis_labels[0] is 'sin(2*chi)'.
            - data_label is 'd_spacing_diff'.
     
        '''
        # Check if d_spacing_combined is an instance of Dataset
        if not isinstance(d_spacing_combined, Dataset):
            raise TypeError("Input d_spacing_combined must be an instance of Dataset.")

        
        #d_spacing_combined[0,5] = np.nan
        # This is the case where one part of the d_spacing pair is missing and not taken into account for the average
        #d_spacing_avg= np.mean(d_spacing_combined, axis=0)
        d_spacing_avg= d_spacing_combined.mean(axis=0)
        d_spacing_avg.data_unit=d_spacing_combined.data_unit
        print(50*"\N{fire}")
        print('d_spacing_avg\n\n', d_spacing_avg)
        print(50*"\N{fire}")
        print('d_spacing_combined.axis_ranges[1]', d_spacing_combined.axis_ranges[1])
        #d_spacing_avg.axis_ranges={0: d_spacing_combined.axis_ranges[1]}
        #d_spacing_avg.axis_labels={0: 'sin^2(chi)'}
        #d_spacing_avg.data_label='position mean'
                
        
        #d-, d+
        #d[1,1]-d[0,1]
        #vs sin(2*chi)
        d_spacing_diff= np.diff(d_spacing_combined, axis=0).squeeze()
        d_spacing_diff.data_unit=d_spacing_combined.data_unit
        d_spacing_diff.data_label='position diff'
        d_spacing_diff.axis_labels={0: 'sin(2*chi)'} #or #TODO 'sin(2chi)' or 'sin_2chi'
        #calculation of sin(2*chi) from sin^2(chi)
        d_spacing_diff.axis_ranges ={0: np.sin(2*np.arcsin(np.sqrt(d_spacing_combined.axis_ranges[1])))}
        return d_spacing_avg, d_spacing_diff




