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
 

"""

__author__ = "Gudrun Lotze"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"
__all__ = ["DspacingSin_2chi"]

import numpy as np

from pydidas.core import Dataset, UserConfigError
from typing import List, Tuple, Dict

from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED
from pydidas.plugins import ProcPlugin


LABELS_SIN_2CHI = 'sin(2*chi)'
LABELS_SIN2CHI = "sin^2(chi)"
LABELS_DIM0=  '0: d-, 1: d+, 2: d_mean'
UNITS_NANOMETER = "nm"
UNITS_ANGSTROM = "A"

PARAMETER_KEEP_RESULTS = 'keep_results'

class DspacingSin_2chi(ProcPlugin):
    """
    This plugin calculates the d-spacing from the sin(2*chi) values.
    """
    plugin_name = "D-spacing from sin(2*chi)"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_group = PROC_PLUGIN_INTEGRATED
    input_data_dim = 2
    output_data_dim = 2
    #TODO: to be decided
    output_data_label = "0: position_neg, 1: position_pos, 2: Difference of 1: position_pos, 0: position_neg"
    new_dataset=True
    
    # modification of the keep_results parameter to ensure results are always stored
    _generics = ProcPlugin.generic_params.copy()
    _generics[PARAMETER_KEEP_RESULTS].value = True
    _generics[PARAMETER_KEEP_RESULTS].choices = [True]
    generic_params = _generics
    
    
    def pre_execute(self):
        pass

    def execute(self, ds: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        
        print(30*"\N{banana}") 
        print('Incoming ds: ', ds)
        print(30*"\N{banana}")  
        
        d_output_sin_2chi_method = self._calculate_diff_d_spacing_vs_sin_2chi(ds)
        
        
        return d_output_sin_2chi_method, kwargs


    def calculate_result_shape(self) -> None:
        _shape = self._config.get("input_shape", None)
        if _shape is None:
            raise UserConfigError(
                "Cannot calculate the output shape because the input shape is unknown."
            )
        self._config["result_shape"] = (3, _shape[1])  
        

    def _ensure_dataset_instance(self, ds: Dataset) -> None:
        """
        Ensure the input is an instance of Dataset.

        Parameters:
        ds (Dataset): The input to check.

        Raises:
        TypeError: If ds is not an instance of Dataset.
        """
        if not isinstance(ds, Dataset):
            raise TypeError("Input must be an instance of Dataset.")
        
    def _ensure_axis_labels(self, ds: Dataset) -> None:
        """
        Ensure the axis labels for dimension 0 and 1 are as expected.

        Parameters:
        ds (Dataset): The input to check.

        Raises:
        UserConfigError: If the axis labels are not as expected.
        """
        if ds.axis_labels[0] != LABELS_DIM0:
            raise UserConfigError(f"Expected axis label '{LABELS_DIM0=}', but got '{ds.axis_labels[0]}'")
        
        if ds.axis_labels[1] != LABELS_SIN2CHI:
            raise UserConfigError(f"Expected axis label '{LABELS_SIN2CHI}', but got '{ds.axis_labels[1]}'")
          
            
    def _calculate_diff_d_spacing_vs_sin_2chi(self, ds: Dataset) -> Dataset:
        """
        My docstring
        """
        # d-, d+
        # d[1,1]-d[0,1]
        # vs sin(2*chi)
        #(d(+) - d(-) ) vs sin(2*psi)"
        #currently: 
        #(d(+) - d(-) ) vs sin(2*chi)"
        
        self._ensure_dataset_instance(ds)
        self._ensure_axis_labels(ds)
        if not ds.shape[0] == 3:
            raise UserConfigError(f"Incoming dataset expected to have 3 rows, {LABELS_DIM0}. Please verify your Dataset.")                   
        
        if not ds.data_unit in [UNITS_NANOMETER, UNITS_ANGSTROM]:
            raise UserConfigError(f"Incoming dataset expected to have units in {UNITS_NANOMETER} or {UNITS_ANGSTROM}. Please verify your Dataset.")
    
        #TODO: remove later   
        #Two approaches:
        delta_d_direct = ds[1, :] - ds[0, :]
        delta_d_diff =  np.diff(ds[:2, :], axis=0)
        #if not np.all(delta_d_diff == delta_d_direct): 
        #np.allclose is required due to np.nan values in the dataset
        if not np.allclose(delta_d_diff, delta_d_direct, rtol=1e-09, atol=1e-10, equal_nan=True):
            print(np.all(delta_d_diff == delta_d_direct))
            raise UserConfigError("Difference of d(+) - d(-) calculated in two different ways. Please verify your Dataset.")  
        
        #Overwriting the incoming dataset 
        ds[2,:] = delta_d_diff.data
        ds.data_label = "Difference of d(+) - d(-)" 
        ds.axis_labels = {0: '0: d-, 1: d+, 2: d(+)-d(-)', 1: LABELS_SIN_2CHI} 
        #TODO: needs adjustment for the low energy case
        ds.axis_ranges = {
                1: np.sin(2 * np.arcsin(np.sqrt(ds.axis_ranges[1])))
            }
        
        return ds