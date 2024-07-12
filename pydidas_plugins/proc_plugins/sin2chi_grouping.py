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
A module for grouping d-spacing values according the sin^2(chi) values, a necessary step for the sin^2(chi) method.
This module expects a pydidas Dataset with d-spacing values [nm, A] and chi values [deg]. Label for d-spacing is `position`.
"""

__author__ = "Gudrun Lotze"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"
__all__ = ["DspacingSin2chiGrouping"]

import numpy as np
from enum import StrEnum, IntEnum
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from pydidas.core import Dataset
from typing import List, Tuple, Dict

class Labels(StrEnum):
    CHI: str = "chi"
    POSITION: str = "position"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}.{self.name}({self.value!r})'
    
class Units(StrEnum):
    NANOMETER: str = "nm"
    ANGSTROM: str = "A"
    DEGREE: str = "deg"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}.{self.name}({self.value!r})'
   
# Define the Enum
# 1 is close to zero
# 2 is positive
# 0 is negative
class Category(IntEnum):
    NEGATIVE: int = 0
    ZERO: int = 1
    POSITIVE: int = 2


from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED
from pydidas.plugins import ProcPlugin


class DspacingSin2chiGrouping(ProcPlugin):
    """
    Grouping of d-spacing values according to the slopes in sin^2(chi) and similiarity in sin^2(chi) values. chi is the azimuthal angle of one diffraction image.
    Output: Mean of d-spacing branches vs. sin^2(chi) , difference of d-spacing branches vs. sin(2*chi), and
    both d-spacing branches for each group.
    
    In a fist step, the grouping is done by a clustering algorithm which uses sin^2(chi) and its values as reference. Similar values are identified as one group.
    In a second step, the algorithm will group the d-spacing values into groups based on similiarity of sin^2(chi) values and its slope sign (positive or negative)
    After the grouping, d-spacing values are categorized by their group labels and the slope sign. In each d-spacing branch, positive or negative, multiple groups can be identified.
    d-spacing values for each group and slope sign follow. 
    The mean of positive and negative d-spacing values vs. sin^2(chi) is calculated, and in a final step, the difference of positive and negative d-spacing values vs. sin(2*chi) is calculated.
    
    NOTE: This plugin expects position (d-spacing) in [nm, A] and chi in [deg] as input data.
    
    """
    plugin_name = "Group d-spacing values according to sin^2(chi)"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = ProcPlugin.base
    advanced_parameters = ProcPlugin.advanced_parameters

    def process(self, dataset: Dataset) -> Dataset:
        """
        Group d-spacing values according to the sin^2(chi) values.
        The grouping is done by a clustering algorithm which uses the sin^2(chi) values as the distance metric.
        The algorithm will group the d-spacing values into clusters of d-spacing values with similar sin^2(chi) values.
        The algorithm will return the cluster number for each d-spacing value.
        """
        # Get the d-spacing values
        d_spacing = dataset.get_data("d_spacing")
        # Get the chi values
        chi = dataset.get_data("chi")
        # Calculate the sin^2(chi) values
        sin2chi = np.sin(np.deg2rad(chi)) ** 2
        # Calculate the distance matrix
        distance_matrix = np.abs(sin2chi[:, np.newaxis] - sin2chi)
        # Create the adjacency matrix
        adjacency_matrix = distance_matrix < 0.1
        # Create the sparse matrix
        sparse_matrix = csr_matrix(adjacency_matrix)
        # Calculate the connected components
        _, labels = connected_components(sparse_matrix)
        # Add the labels to the dataset
        dataset.add_data("sin2chi_group", labels, labels=Labels.POSITION)
        return dataset

    def get_output_labels(self) -> List[str]:
        """
        Get the output labels for the plugin.
        """
        return [Labels.POSITION]

    def get_output_units(self) -> Dict[str, str]:
        """
        Get the output units for the plugin.
        """
        return {Labels.POSITION: Units.NANOMETER}

    def get_output_shapes(self) -> Dict[str, Tuple[int]]:
        """
        Get the output shapes for the plugin.