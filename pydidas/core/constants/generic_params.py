# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The generic_params module holds the dictionary with information required for creating
generic Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_METADATA"]


from .generic_params_data_import import GENERIC_PARAMS_DATA_IMPORT
from .generic_params_experiment import GENERIC_PARAMS_EXPERIMENT
from .generic_params_image_ops import GENERIC_PARAMS_IMAGE_OPS
from .generic_params_other import GENERIC_PARAMS_OTHER
from .generic_params_pyfai import GENERIC_PARAMS_PYFAI
from .generic_params_scan import GENERIC_PARAMS_SCAN
from .generic_params_settings import GENERIC_PARAMS_SETTINGS
from .generic_params_fit import GENERIC_PARAMS_FIT

GENERIC_PARAMS_METADATA = (
    GENERIC_PARAMS_DATA_IMPORT
    | GENERIC_PARAMS_EXPERIMENT
    | GENERIC_PARAMS_IMAGE_OPS
    | GENERIC_PARAMS_OTHER
    | GENERIC_PARAMS_PYFAI
    | GENERIC_PARAMS_SCAN
    | GENERIC_PARAMS_SETTINGS
    | GENERIC_PARAMS_FIT
)
