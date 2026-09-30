# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Package with miscellaneous individual QWidgets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from .configure_binary_decoding_widget import ConfigureBinaryDecodingWidget
from .hdf5_dataset_selector import Hdf5DatasetSelector
from .integration_roi_param_container import IntegrationRoiParamContainer
from .points_for_beamcenter_widget import PointsForBeamcenterWidget
from .select_data_frame_widget import SelectDataFrameWidget


__all__ = [
    "ConfigureBinaryDecodingWidget",
    "Hdf5DatasetSelector",
    "IntegrationRoiParamContainer",
    "PointsForBeamcenterWidget",
    "SelectDataFrameWidget",
]
