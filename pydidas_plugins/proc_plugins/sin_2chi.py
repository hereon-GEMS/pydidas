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
    output_data_label = "to be decided"
    
    
def pre_execute(self):
    pass

def execute(self, ds: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
    
    pass


def calculate_result_shape(self) -> None:
    _shape = self._config.get("input_shape", None)
    self._config["result_shape"] = (3, _shape[0])  
        
        