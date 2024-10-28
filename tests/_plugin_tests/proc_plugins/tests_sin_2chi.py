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
        
        return Dataset(
            data_array,
            axis_labels={0: LABELS_DIM0, 1: LABELS_SIN2CHI},
            axis_ranges={ 0: np.arange(data_array.shape[0]), 1: np.full((1, data_array.shape[1]),np.sin(np.arctan(2)))**2},
            axis_units={0: '' , 1:''},
            data_label= 'd_spacing', 
            data_unit = unit,
        )
    return factory


def test_execute_validation(plugin_fixture, base_dataset_factory):
    dataset = base_dataset_factory(UNITS_NANOMETER)
    result , _ = plugin_fixture.execute(dataset)
    
    assert result is not None
    assert result.data_unit == UNITS_NANOMETER
    assert result.data_label == 'Difference of d(+) - d(-)'
    assert result.axis_labels[0] == '0: d-, 1: d+, 2: d(+)-d(-)'
    assert result.axis_labels[1] == LABELS_SIN_2CHI
    assert result.axis_units[0] == ''
    assert result.axis_units[1] == ''
    assert np.all(result.axis_ranges[0] == dataset.axis_ranges[0])
    assert np.all(result.axis_ranges[1] == np.full((1, result.shape[1]), np.sin(2*np.arctan(2))))
    assert np.all(result.data == np.array([[1]*5, [3]*5, [2]*5]))   

